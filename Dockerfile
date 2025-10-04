###############################################
# Dockerfile para despliegue en Render (Reflex)
# Objetivos:
#  - Build reproducible y ligero
#  - Frontend + backend en un solo servicio
#  - Compatible con Postgres (requiere DATABASE_URL en Render)
#  - Usa Node LTS para build del frontend
#  - Ejecuta Reflex en modo prod
###############################################

# Etapa 1: Dependencias base (Python + Node) -------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	POETRY_VIRTUALENVS_CREATE=false \
	REFLEX_ENV=prod

WORKDIR /app

# Dependencias del sistema necesarias (build, curl para node setup opcional si se quisiera otra versión)
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	curl \
	git \
	unzip \
	&& rm -rf /var/lib/apt/lists/*

# Instalar Node LTS (usando repos oficiales de NodeSource)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
	&& apt-get update && apt-get install -y --no-install-recommends nodejs \
	&& rm -rf /var/lib/apt/lists/*

# Copiamos solo requirements primero para cache de capas
COPY requirements.txt ./
# Aseguramos versión correcta de reflex (override si la imagen base trae otra).
RUN pip install --upgrade pip \
	&& pip install -r requirements.txt \
	&& pip install --no-cache-dir reflex==0.8.13

# Etapa 2: Build de la app -------------------------------------------------
FROM base AS build
COPY . .

# Validación básica de configuración obligatoria (Render la inyecta en runtime, aquí permitimos ausencia)
# Si quieres forzar build-time fail cuando falte, descomenta el bloque siguiente:
# RUN test -n "$DATABASE_URL" || echo "ADVERTENCIA: DATABASE_URL no definida en build (se requiere en runtime)."

# Pre-compilar frontend de Reflex (export) para mejorar primer arranque (opcional)
# Nota: reflex run --env prod también construirá; este paso acelera cold start.
RUN reflex export --frontend-only || echo "Continuando aunque falle export (se reconstruirá en runtime)"

# Etapa 3: Imagen final ----------------------------------------------------
FROM base AS final
WORKDIR /app

# Copiamos sólo el código (y build exportado si existe)
COPY --from=build /app /app

# Exponer el puerto que Render asignará (Render provee $PORT)
EXPOSE 8000

# Variables de entorno recomendadas (puedes overridearlas en el dashboard de Render)
ENV PORT=8000 \
	REFLEX_ENV=prod

# Healthcheck opcional (Render permite configurar un healthcheck externo). Si añades endpoint /api/health puedes usar:
# HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:8000/api/health || exit 1

# EntryPoint: ejecuta espera de Postgres + migraciones + arranque Reflex.
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

###############################################
# Notas:
# - Asegúrate de definir en Render: DATABASE_URL, SECRET_KEY, OPENAI_API_KEY (si aplica), etc.
# - Evita SQLite en producción (rxconfig ahora fuerza error sin DATABASE_URL).
###############################################
