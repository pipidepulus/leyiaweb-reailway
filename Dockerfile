# Usa una imagen base oficial de Python.
# La etiqueta 'slim' es una buena opción para producción al ser más ligera.
FROM python:3.12-slim

# Establece variables de entorno para un comportamiento óptimo de Python en Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# ---- LÍNEA AÑADIDA ----
# Instala las dependencias del sistema operativo. 'unzip' es requerido por Reflex.
RUN apt-get update && apt-get install -y unzip curl && rm -rf /var/lib/apt/lists/*
# ---------------------

# Copia el archivo de requerimientos primero para aprovechar el cache de Docker.
COPY requirements.txt .

# Instala las dependencias del proyecto.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación al directorio de trabajo.
COPY . .



# Expone los puertos que Reflex utiliza.

EXPOSE 8000

# ---- LA CMD DEFINITIVA ----
# 1. Compilamos el frontend explícitamente PRIMERO con `reflex export`.
# 2. Luego iniciamos el backend con `reflex run` y el flag `--no-frontend`.
#    Esto evita que se levante el servidor de Node.js en el puerto 3000.
CMD ["sh", "-c", "reflex export --backend-only && reflex run --env prod --no-frontend --backend-host 0.0.0.0 --backend-port ${PORT:-8000}"]