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
# Instalamos dependencias del sistema: curl para instalar Node (frontend build) y unzip.
RUN apt-get update && apt-get install -y curl unzip \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    # Instalar Node.js (LTS) para que Reflex pueda construir el frontend.
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copia el resto del código de tu aplicación al directorio de trabajo.
COPY . .

# Expone el puerto que usará el backend. Render lo mapeará automáticamente.
# Render te dará una variable de entorno $PORT, que usaremos en el CMD.
EXPOSE 8000

# Ejecutar la app completa (frontend + backend) en modo producción.
# Render inyecta PORT; Reflex usará ese backend_port y expondrá el frontend en el mismo servicio.
# NOTA: quitamos --backend-only para evitar el 404 del navegador.
CMD ["sh", "-c", "exec reflex run --env prod --backend-host 0.0.0.0 --backend-port ${PORT}"]