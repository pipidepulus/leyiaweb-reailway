# Dockerfile Refactorizado y Final para Render (v12 - Permisos Definitivos)

FROM python:3.12-slim

# Instalar todas las dependencias de sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    gnupg \
    unzip \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# Crear un usuario no-root para la aplicación
RUN useradd --system --create-home appuser

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar todos los archivos de la aplicación
COPY . .

# --- LA SOLUCIÓN CLAVE ---
# Cambiar la propiedad de TODO el directorio de la aplicación al usuario no-root.
# Esto debe hacerse ANTES de cambiar de usuario.
RUN chown -R appuser:appuser /app

# AHORA, cambiar al usuario no-root
USER appuser

# Crear y activar un entorno virtual (ahora appuser tiene permisos para hacerlo)
ENV VENV_PATH=/app/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que Render utilizará
EXPOSE 8000

# El comando de inicio. Ahora `reflex run` (como appuser) podrá crear
# el directorio .web dentro de /app sin problemas.
CMD ["reflex", "run", "--env", "prod"]