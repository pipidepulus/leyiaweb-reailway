# Dockerfile multi-stage para aplicación Reflex
# Optimizado para despliegue en Render.com

# ============================================
# Stage 1: Builder - Instalación de dependencias
# ============================================
FROM python:3.12-slim AS builder

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    libpq-dev \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js 20.x (requerido por Reflex para el frontend)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalación de Node.js y npm
RUN node --version && npm --version

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python en un entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Actualizar pip y instalar dependencias
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime - Imagen final
# ============================================
FROM python:3.12-slim

# Instalar dependencias del sistema runtime
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    postgresql-client \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js 20.x (necesario para el frontend de Reflex)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/uploaded_files /app/.web && \
    chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser

# Establecer directorio de trabajo
WORKDIR /app

# Copiar entorno virtual desde el builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Activar el entorno virtual
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copiar el código de la aplicación
COPY --chown=appuser:appuser . .

# Asegurar permisos correctos en directorios críticos
RUN chmod -R 755 /app && \
    chmod -R 777 /app/uploaded_files /app/.web

# Variables de entorno por defecto
ENV REFLEX_ENV=prod
ENV PORT=8000
ENV FRONTEND_PORT=3000
ENV PYTHONPATH=/app

# Exponer puertos (Render usa PORT automáticamente)
EXPOSE 8000 3000

# Script de inicio para manejar migraciones y arranque
COPY --chown=appuser:appuser <<'EOF' /app/entrypoint.sh
#!/bin/bash
set -e

echo "🚀 Iniciando aplicación Reflex..."
echo "📍 Directorio actual: $(pwd)"
echo "🐍 Python: $(python --version)"
echo "📦 Node: $(node --version)"

# Función para esperar a que la base de datos esté lista
wait_for_db() {
    echo "⏳ Esperando a que PostgreSQL esté listo..."
    
    # Extraer componentes de DATABASE_URL
    if [ -n "$DATABASE_URL" ]; then
        echo "🔍 DATABASE_URL detectada"
        
        # Parsear DATABASE_URL para obtener host, puerto, etc.
        # Formato: postgresql://user:pass@host:port/dbname o postgresql://user:pass@host/dbname
        
        # Extraer el host (puede incluir .a para Render interno)
        DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|')
        
        # Extraer puerto (si existe, sino usar 5432)
        if echo "$DATABASE_URL" | grep -qE '@[^/]+:[0-9]+/'; then
            DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')
        else
            DB_PORT=5432
        fi
        
        # Extraer usuario
        DB_USER=$(echo "$DATABASE_URL" | sed -E 's|.*://([^:]+):.*|\1|')
        
        # Extraer nombre de base de datos (todo después de la última /)
        DB_NAME=$(echo "$DATABASE_URL" | sed -E 's|.*/([^/?]+)(\?.*)?$|\1|')
        
        echo "🔍 DB Host: $DB_HOST"
        echo "🔍 DB Port: $DB_PORT"
        echo "🔍 DB User: $DB_USER"
        echo "🔍 DB Name: $DB_NAME"
        
        # Esperar hasta que PostgreSQL acepte conexiones
        retries=${DB_WAIT_RETRIES:-90}
        interval=${DB_WAIT_INTERVAL:-3}
        
        echo "⏳ Intentando conectar a PostgreSQL (máximo $retries intentos)..."
        
        for i in $(seq 1 $retries); do
            # Intentar conexión con pg_isready
            if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
                echo "✅ PostgreSQL está listo y aceptando conexiones!"
                return 0
            fi
            
            echo "⏳ Intento $i/$retries: PostgreSQL no está listo. Esperando ${interval}s..."
            sleep $interval
        done
        
        echo "❌ ERROR: PostgreSQL no está disponible después de $retries intentos"
        echo "💡 Sugerencia: Verifica que DATABASE_URL sea correcta y que el servicio PostgreSQL esté activo en Render"
        return 1
    else
        echo "⚠️  DATABASE_URL no está configurada, saltando verificación de DB"
        echo "⚠️  La aplicación puede fallar si intenta usar la base de datos"
    fi
}

# Función para ejecutar migraciones
run_migrations() {
    if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
        echo "🔄 Ejecutando migraciones de Alembic..."
        
        # Verificar si alembic está configurado
        if [ -f "alembic.ini" ]; then
            # Ejecutar migraciones
            alembic upgrade head || {
                echo "⚠️  Advertencia: Migraciones fallaron o no hay migraciones pendientes"
                # No fallar el contenedor si las migraciones fallan
            }
            echo "✅ Migraciones completadas"
        else
            echo "⚠️  No se encontró alembic.ini, saltando migraciones"
        fi
    else
        echo "⏭️  Migraciones deshabilitadas (RUN_MIGRATIONS=0)"
    fi
}

# Función para inicializar Reflex
init_reflex() {
    echo "🔧 Inicializando aplicación Reflex..."
    
    # Limpiar cache anterior si existe
    if [ -d ".web/_next/cache" ]; then
        echo "🧹 Limpiando cache de Next.js..."
        rm -rf .web/_next/cache
    fi
    
    # Instalar Reflex (instala dependencias de Node.js y compila frontend)
    reflex init || {
        echo "❌ ERROR: reflex init falló"
        return 1
    }
    
    # No necesitamos sirv en Render - Reflex maneja todo integrado
    echo "✅ Skipping sirv install - using integrated Reflex server"
    
    echo "✅ Reflex inicializado correctamente"
}

# Función para exportar frontend estático (opcional)
export_frontend() {
    if [ "${EXPORT_FRONTEND:-0}" = "1" ]; then
        echo "📦 Exportando frontend estático..."
        reflex export || {
            echo "⚠️  Advertencia: Export de frontend falló"
        }
    fi
}

# Función principal
main() {
    # Esperar a la base de datos
    wait_for_db || exit 1
    
    # Ejecutar migraciones
    run_migrations
    
    # Inicializar Reflex
    init_reflex || exit 1
    
    # Exportar frontend (opcional)
    export_frontend
    
    echo "🎯 Iniciando aplicación con gunicorn + uvicorn..."
    echo "🌐 Puerto de Render: $PORT"
    
    # Inicializar aplicación Reflex sin servidor
    echo "🔧 Inicializando aplicación Reflex..."
    reflex init --name asistente_legal_constitucional_con_ia || true
    
    # Iniciar usando gunicorn con uvicorn workers (ASGI) - comando simplificado
    exec gunicorn wsgi:application \
        --bind 0.0.0.0:$PORT \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers 1 \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile -
}

# Ejecutar función principal
main
EOF

# Hacer el script ejecutable
RUN chmod +x /app/entrypoint.sh

# Comando de inicio
CMD ["/bin/bash", "/app/entrypoint.sh"]

# Healthcheck para Render
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ping || exit 1

# Notas de despliegue en Render:
# ===============================
# 1. Variables de entorno requeridas:
#    - DATABASE_URL (proporcionada automáticamente si usas Render PostgreSQL)
#      Formato: postgresql://usuario:password@host/database
#      Ejemplo Render: postgresql://leyia_postgres_user:pass@dpg-xxx-a/leyia_postgres
#    - OPENAI_API_KEY
#    - ASSEMBLYAI_API_KEY
#    - TAVILY_API_KEY
#    - REFLEX_ENV=prod
#    - RUN_MIGRATIONS=1 (para ejecutar migraciones automáticamente)
#    - DB_WAIT_RETRIES=90 (incrementado para Render)
#    - DB_WAIT_INTERVAL=3 (incrementado para Render)
#
# 2. Configuración de Render:
#    - Build Command: docker build -t reflex-app .
#    - Start Command: (se usa el CMD del Dockerfile)
#    - Port: 8000 (Render lo configura automáticamente en $PORT)
#
# 3. Servicio de PostgreSQL:
#    - Crear un servicio PostgreSQL en Render
#    - Render automáticamente configura DATABASE_URL
#    - IMPORTANTE: Usar la URL INTERNA (con -a) para mejor conectividad
#
# 4. Disco persistente:
#    - Montar volumen en /app/uploaded_files para archivos subidos
#
# 5. Redis (opcional pero recomendado):
#    - Agregar servicio Redis en Render
#    - Configurar REDIS_URL en variables de entorno
