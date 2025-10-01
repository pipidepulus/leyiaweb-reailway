#!/bin/sh
set -euo pipefail

echo "[start] REFLEX_ENV=${REFLEX_ENV:-prod}"
BACKEND_PORT=${BACKEND_PORT:-10001}
PORT=${PORT:-8080}
DB_WAIT_RETRIES=${DB_WAIT_RETRIES:-40}
DB_WAIT_INTERVAL=${DB_WAIT_INTERVAL:-2}

echo "[start] Will listen publicly on :$PORT (nginx) and internally backend:$BACKEND_PORT frontend:3000"

if [ -n "${DATABASE_URL:-}" ] && printf '%s' "${DATABASE_URL}" | grep -qi '^postgres'; then
  echo "[start] Waiting for Postgres..."
  python - <<'PY'
import os, time
import psycopg2
url=os.environ.get('DATABASE_URL','')
retries=int(os.environ.get('DB_WAIT_RETRIES','40'))
interval=int(os.environ.get('DB_WAIT_INTERVAL','2'))
for i in range(1, retries+1):
    try:
        psycopg2.connect(url).close()
        print(f"[start] DB reachable on attempt {i}")
        break
    except Exception as e:
        print(f"[start] DB not ready ({i}/{retries}): {e}")
        if i == retries:
            print('[start] WARNING: proceeding without confirmed DB connection')
        time.sleep(interval)
PY
else
  echo "[start] No postgres DATABASE_URL; skipping wait"
fi

echo "[start] Running migrations"
alembic upgrade head || { echo "[start] Alembic failed"; exit 1; }

echo "[start] Launching Reflex (backend:$BACKEND_PORT frontend:3000)"
reflex run --env prod --backend-host 0.0.0.0 --backend-port "$BACKEND_PORT" &
REFLEX_PID=$!

# Asegurar directorio nginx
mkdir -p /etc/nginx

# Generar config nginx sustituyendo variables
echo "[start] Generating nginx config"
export BACKEND_PORT PORT
if ! envsubst '${BACKEND_PORT} ${PORT}' < /app/nginx.conf.template > /etc/nginx/nginx.conf; then
  echo "[start] ERROR generando /etc/nginx/nginx.conf" >&2
  kill $REFLEX_PID || true
  exit 2
fi

echo "[start] Starting nginx (PID 1)"
exec nginx -g 'daemon off;'
