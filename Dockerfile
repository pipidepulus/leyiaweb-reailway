# Dockerfile Refactorizado y Corregido para Render

# ====================================================================
# Etapa 1: Builder
# Construye las dependencias y el frontend de la aplicación.
# ====================================================================
FROM python:3.12-slim AS builder

# Instalar dependencias del sistema necesarias para la compilación
# AÑADIDO 'unzip' que es requerido por el instalador de Bun de Reflex
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

# ¡Paso clave! Pre-compilar el frontend.
# Esto se hace UNA VEZ durante el build, no en cada arranque.
# RUN reflex export --frontend-only

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
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copiar la aplicación y el frontend pre-compilado desde el builder
COPY --from=builder --chown=appuser:appuser /app /home/appuser

# Activar el entorno virtual
# Nota: WORKDIR ya está establecido a /home/appuser, por lo que el venv estará en el PATH relativo
ENV PATH="/home/appuser/opt/venv/bin:$PATH"

# Exponer el puerto que Render utilizará (documentación)
# Render establece la variable $PORT a 10000 por defecto
EXPOSE 10000

# El comando de inicio: simple, directo y robusto.
# No necesita un script complejo. Lee $PORT de Render.
CMD ["sh", "-c", "exec reflex run --env prod --backend-host 0.0.0.0 --backend-port $PORT"]