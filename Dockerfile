# Dockerfile

# 1. Utiliza una imagen base oficial de Python. La versión 'slim' es más ligera.
FROM python:3.12-slim

# 2. Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# 3. Actualiza los repositorios de paquetes e instala las dependencias del sistema.
#    ¡Aquí está la línea clave que instala 'unzip'!
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 4. Copia el archivo de requerimientos primero para aprovechar el cache de Docker.
COPY requirements.txt .

# 5. Crea y activa un entorno virtual dentro del contenedor.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 6. Instala las dependencias de Python de tu proyecto.
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copia el resto del código de tu aplicación al contenedor.

COPY . .

# 8. Expone los puertos que tu aplicación va a usar. Railway los detectará.
EXPOSE 8080
EXPOSE 3000

# 9. Define el comando para iniciar la aplicación en modo producción.
#    Railway usará este comando para arrancar tu servicio.
# CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0", "--backend-port", "8080", "--frontend-port", "3000"]
CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0", "--backend-port", "$PORT"]