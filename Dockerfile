# Dockerfile Refactorizado y Final para Render (v11 - Permisos Corregidos)

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

# Crear el entorno virtual COMO ROOT, pero asignarlo al appuser.
# De esta forma, el appuser puede usarlo pero no crearlo en un directorio root.
ENV VENV_PATH=/app/venv
RUN python -m venv $VENV_PATH && \
    chown -R appuser:appuser $VENV_PATH

# Activar el entorno virtual para los siguientes comandos
ENV PATH="$VENV_PATH/bin:$PATH"

# Copiar solo los archivos de requerimientos primero para aprovechar la caché de Docker
COPY --chown=appuser:appuser requirements.txt .

# Instalar dependencias de Python COMO ROOT (algunos paquetes lo necesitan)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY --chown=appuser:appuser . .

# AHORA, cambiar al usuario no-root para la ejecución final
USER appuser

# Exponer el puerto que Render utilizará
EXPOSE 10000

# El comando de inicio. Reflex se encargará de compilar el frontend
# la primera vez que arranque el contenedor.
CMD ["reflex", "run", "--env", "prod"]