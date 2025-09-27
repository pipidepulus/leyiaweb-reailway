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

# Dependencias del sistema (OCR/pdf + utilidades). Añadimos curl para healthcheck y descargas.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip tesseract-ocr tesseract-ocr-spa poppler-utils \
  && rm -rf /var/lib/apt/lists/*

# Copiamos requerimientos primero para aprovechar cache de capas.
COPY requirements.txt ./

# (Opcional) upgrade de pip para evitar warnings de build.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

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

# Script de arranque (incluye migraciones). Se copia/crea en la build.
CMD ["./start.sh"]