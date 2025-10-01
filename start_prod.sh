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

echo "[start] Generating nginx config (sin envsubst)"
cat > /etc/nginx/nginx.conf <<'EOF'
events {}
http {
  sendfile on;
  tcp_nopush on;
  tcp_nodelay on;
  keepalive_timeout 65;
  map $http_upgrade $connection_upgrade { default upgrade; '' close; }

  upstream reflex_frontend { server 127.0.0.1:3000; }
  upstream reflex_backend { server 127.0.0.1:BACKEND_PORT_PLACEHOLDER; }

  server {
    listen PORT_PLACEHOLDER;
    server_name _;

    location ~ ^/(_event|_ws|api|auth) {
      proxy_pass http://reflex_backend;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $connection_upgrade;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /_ws {
      proxy_pass http://reflex_backend;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $connection_upgrade;
      proxy_set_header Host $host;
    }

    location / {
      proxy_pass http://reflex_frontend;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header X-Forwarded-Proto $scheme;
    }
  }
}
EOF

sed -i "s/BACKEND_PORT_PLACEHOLDER/${BACKEND_PORT}/g; s/PORT_PLACEHOLDER/${PORT}/g" /etc/nginx/nginx.conf || {
  echo "[start] ERROR sustituyendo variables en nginx.conf" >&2
  kill $REFLEX_PID || true
  exit 2
}

echo "[start] Starting nginx (PID 1)"
exec nginx -g 'daemon off;' 
