#!/usr/bin/env sh
set -euo pipefail

echo "[entrypoint] Iniciando contenedor Reflex (modo prod)."

# Opciones
DB_MAX_RETRIES="${DB_MAX_RETRIES:-30}"
DB_WAIT_SECONDS="${DB_WAIT_SECONDS:-2}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-0}"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "[entrypoint][ERROR] DATABASE_URL no está definida. Aborting." >&2
  exit 10
fi

if [ "${REFLEX_ENV:-}" != "prod" ]; then
  echo "[entrypoint] REFLEX_ENV != prod (=${REFLEX_ENV:-}). Continuando igualmente."
fi

echo "[entrypoint] Esperando a Postgres (${DATABASE_URL})..."
python - <<'PY'
import os, time, sys
import sqlalchemy
url = os.environ.get('DATABASE_URL')
engine = sqlalchemy.create_engine(url, pool_pre_ping=True, future=True)
max_retries = int(os.environ.get('DB_MAX_RETRIES','30'))
wait_s = float(os.environ.get('DB_WAIT_SECONDS','2'))
for attempt in range(1, max_retries+1):
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text('SELECT 1'))
        print(f"[entrypoint] Postgres disponible en intento {attempt}.")
        break
    except Exception as e:
        print(f"[entrypoint] Intento {attempt}/{max_retries} fallo: {e}")
        if attempt == max_retries:
            print("[entrypoint][ERROR] No se pudo conectar a Postgres.", file=sys.stderr)
            sys.exit(2)
        time.sleep(wait_s)
PY

echo "[entrypoint] Conexión a BD verificada."

if [ "$SKIP_MIGRATIONS" = "1" ]; then
  echo "[entrypoint] SKIP_MIGRATIONS=1 -> Omitiendo 'alembic upgrade head'."
else
  if command -v alembic >/dev/null 2>&1; then
    echo "[entrypoint] Ejecutando migraciones Alembic (upgrade head)..."
    if alembic upgrade head; then
      echo "[entrypoint] Migraciones aplicadas correctamente."
    else
      echo "[entrypoint][WARN] Falló alembic upgrade head. Continuando (las tablas pueden ser creadas por Reflex)." >&2
    fi
  else
    echo "[entrypoint][WARN] 'alembic' no instalado en PATH. Saltando migraciones."
  fi
fi

# Lanzar aplicación Reflex en modo producción.
PORT="${PORT:-10000}"
BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"

echo "[entrypoint] Iniciando Reflex single-port en ${PORT} ..."
exec reflex run --env prod --backend-host "${BACKEND_HOST}" --backend-port "${PORT}" 2>&1
