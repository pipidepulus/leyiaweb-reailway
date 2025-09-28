## Dockerfile simplificado para uso LOCAL de la aplicación Reflex
## Objetivos:
##  - Entorno reproducible para desarrollo / pruebas locales
##  - Sin OCR (eliminado para reducir dependencias) solo extracción PDF vía PyMuPDF
##  - Usuario no root
##  - Permitir alternar entre modo dev y prod con REFLEX_ENV
##  - Sin Node (Reflex gestiona el toolchain interno en runtime si lo necesita)

FROM python:3.12-slim

ARG UID=1000
ARG GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REFLEX_ENV=dev \
    PORT=8000 \
    FRONTEND_PORT=3000 \
    HOME=/home/appuser \
    REFLEX_DIR=/home/appuser/.local/share/reflex \
    PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# Dependencias SISTEMA mínimas necesarias en runtime
# (OCR removido: no tesseract, no poppler)
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl unzip \
        libxml2 libxslt1.1 libpq5 ca-certificates; \
    rm -rf /var/lib/apt/lists/*

# Copiar sólo requirements para cache de dependencias
COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge || true

# Copiar código fuente
COPY . .

# Crear usuario local (mismo UID/GID que host opcionalmente para evitar problemas en volúmenes)
RUN groupadd -g ${GID} appuser || true && \
    useradd -u ${UID} -g ${GID} -d /home/appuser -m -s /bin/bash appuser || true && \
    mkdir -p /app/db /app/uploaded_files ${REFLEX_DIR} && \
    chown -R appuser:appuser /app /home/appuser

USER appuser

EXPOSE 8000 3000

# Variable opcional para elegir host de backend (default 0.0.0.0 para acceso desde host)
ENV BACKEND_HOST=0.0.0.0

# Copiar entrypoint que ejecuta migraciones antes de iniciar Reflex (evita 'no such table').
COPY docker-entrypoint.sh /entrypoint.sh

# Variables para controlar migraciones automáticas y espera de DB (Postgres)
ENV RUN_MIGRATIONS=1 \
    DB_WAIT_RETRIES=30 \
    DB_WAIT_INTERVAL=2

# Usar entrypoint (puedes desactivar migraciones con -e RUN_MIGRATIONS=0)
CMD ["sh", "/entrypoint.sh"]