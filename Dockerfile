# Dockerfile.backend

# Usa una imagen base oficial de Python.
FROM python:3.12-slim

ARG CACHE_BUSTER=1


# Establece variables de entorno para un comportamiento óptimo de Python en Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copia el archivo de requerimientos primero para aprovechar el cache de Docker.
COPY requirements.txt .

# Instala las dependencias del proyecto.
# Añadimos 'unzip' por si reflex lo necesita internamente.
RUN apt-get update && apt-get install -y unzip  && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación al directorio de trabajo.
COPY . .

# Expone el puerto que usará el backend. Render lo mapeará automáticamente.
# Render te dará una variable de entorno $PORT, que usaremos en el CMD.
EXPOSE 8000

# El comando para iniciar SOLAMENTE el backend.
# - Se enlaza a 0.0.0.0 para ser accesible desde fuera del contenedor.
# - Usa la variable $PORT que Render provee.
# - --no-frontend evita que intente iniciar el servidor de Node.js.
CMD ["sh", "-c", "exec reflex run --env prod --backend-only --backend-host 0.0.0.0 --backend-port ${PORT}"]