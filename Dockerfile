# Dockerfile Refactorizado y Final para Render (v3)

# ====================================================================
# Etapa 1: Builder
# Construye las dependencias y el frontend de la aplicación.
# ====================================================================
FROM python:3.12-slim AS builder

# Instalar dependencias del sistema necesarias para la compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js (requerido por Reflex para construir el frontend)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Crear y activar un entorno virtual
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# --- SOLUCIÓN PARA EL BUILD ---
# 1. Proveer una URL de BD falsa para el tiempo de construcción.
ENV DATABASE_URL="sqlite:///dummy_build.db"

# 2. ¡NUEVO PASO! Crear las tablas en la BD "dummy".
# Esto es necesario para que `reflex export` pueda consultar las tablas sin fallar.
# Asume que tu archivo principal se llama como tu app.
# Si tu archivo principal se llama diferente (ej: `app.py`), cámbialo abajo.
RUN python -c "import reflex as rx; from sqlmodel import SQLModel; import asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia; engine = rx.db.get_engine(); SQLModel.metadata.create_all(engine)"

# 3. ¡Paso clave! Pre-compilar el frontend.
RUN reflex export --frontend-only
# --- FIN DE LA SOLUCIÓN ---


# ====================================================================
# Etapa 2: Runtime
# Crea la imagen final, ligera y segura para producción.
# ====================================================================
FROM python:3.12-slim AS runtime

# Instalar solo las dependencias de sistema necesarias para ejecutar
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Crear un usuario no-root para mayor seguridad
RUN useradd --system --create-home appuser
WORKDIR /home/appuser
USER appuser

# Copiar el entorno virtual con las dependencias de Python desde el builder
COPY --from-builder --chown=appuser:appuser /opt/venv /opt/venv

# Copiar la aplicación y el frontend pre-compilado desde el builder
COPY --from-builder --chown=appuser:appuser /app /home/appuser

# Activar el entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Exponer el puerto que Render utilizará (documentación)
EXPOSE 10000

# El comando de inicio: simple, directo y robusto.
CMD ["sh", "-c", "exec reflex run --env prod --backend-host 0.0.0.0 --backend-port $PORT"]