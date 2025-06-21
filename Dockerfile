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
COPY asistente_legal_constitucional_con_ia/ ./asistente_legal_constitucional_con_ia/
COPY rxconfig.py .
COPY assets/ ./assets/

# Expone los puertos que Reflex utiliza.
EXPOSE 3000
EXPOSE 8000

# El comando para iniciar la aplicación en modo producción.
CMD ["sh", "-c", "echo '--- DIAGNOSTICO: LISTANDO ARCHIVOS ---' && ls -la && echo '--- DIAGNOSTICO: LISTANDO PAQUETES PIP ---' && pip list && echo '--- DIAGNOSTICO: INICIANDO REFLEX ---' && reflex run --env prod --frontend-port 3000 --backend-port 8000"]