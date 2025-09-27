## Dockerfile para despliegue en Render (Full Reflex + Postgres)
## Mejores prácticas aplicadas: imagen slim, instalación mínima, usuario no root,
## migraciones automáticas Alembic, healthcheck y servidor Reflex completo.

FROM python:3.12-slim AS base

ARG CACHE_BUSTER=1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REFLEX_ENV=prod \
    PORT=8000

WORKDIR /app

# Dependencias del sistema (OCR/pdf + utilidades) + toolchain de compilación para wheels que requieran build
# Añadimos librerías nativas típicas para Pillow (jpeg, zlib, tiff, webp, openjp2), lxml (libxml2/libxslt) y psycopg2 (libpq).
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip tesseract-ocr tesseract-ocr-spa poppler-utils \
        build-essential gcc g++ libpq-dev \
        libjpeg62-turbo-dev zlib1g-dev libopenjp2-7-dev libtiff5-dev libwebp-dev \
        libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requerimientos primero para aprovechar cache de capas.
COPY requirements.txt ./

# (Opcional) upgrade de pip para evitar warnings de build.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge || true

# Copiamos el código de la aplicación.
COPY . .

# Crear directorios usados en runtime (uploads) y usuario no root.
RUN mkdir -p /app/uploads && \
    groupadd -r app && useradd -r -g app appuser && \
    chown -R appuser:app /app

USER appuser

EXPOSE 8000

# Healthcheck simple sobre la raíz (Reflex sirve /).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD curl -f http://localhost:${PORT}/ || exit 1

# Arranque directo de Reflex (sin script intermedio ni migraciones automáticas).
# Si necesitas aplicar migraciones en el Postgres remoto:
#   1. Abre shell en el servicio (Render) y ejecuta: alembic upgrade head
#   2. O agrega una etapa manual antes de este comando.
CMD ["sh", "-c", "reflex run --env prod --backend-host 0.0.0.0 --backend-port ${PORT:-8000}"]