# Dockerfile Refactorizado y Final para Render (v10 - Canónico y Simple)

# Usaremos una única imagen, sin multi-etapa, para simplificar al máximo.
FROM python:3.12-slim

# Instalar todas las dependencias de sistema necesarias para build Y runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    gnupg \
    unzip \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo y usuario
WORKDIR /app
RUN useradd --system --create-home appuser
USER appuser

# Copiar archivos y establecer propietario
COPY --chown=appuser:appuser . .

# Crear y activar un entorno virtual
ENV VENV_PATH=/app/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que Render utilizará (documentación)
EXPOSE 10000

# El comando de inicio. Reflex se encargará de compilar el frontend
# la primera vez que arranque el contenedor.
CMD ["reflex", "run", "--env", "prod"]