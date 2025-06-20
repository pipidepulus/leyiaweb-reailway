# Usa una imagen base oficial de Python.
# La etiqueta 'slim' es una buena opción para producción al ser más ligera.
FROM python:3.12-slim

# Establece variables de entorno para un comportamiento óptimo de Python en Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia el archivo de requerimientos primero para aprovechar el cache de Docker.
# La instalación de dependencias solo se re-ejecutará si este archivo cambia.
COPY requirements.txt .

# Instala las dependencias del proyecto.
# --no-cache-dir reduce el tamaño de la imagen.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación al directorio de trabajo.
# Se copia la carpeta principal de la app, el archivo de configuración de Reflex y los assets.
COPY asistente_legal_constitucional_con_ia/ ./asistente_legal_constitucional_con_ia/
COPY rxconfig.py .
COPY assets/ ./assets/

# Expone los puertos que Reflex utiliza por defecto.
# El frontend corre en el 3000 y el backend en el 8000.
EXPOSE 3000
EXPOSE 8000

# El comando para iniciar la aplicación.
# Se usa --frontend-host y --backend-host para que la app sea accesible
# desde fuera del contenedor.
CMD ["reflex", "run", "--env", "prod", "--frontend-port", "3000", "--backend-port", "8000"]
