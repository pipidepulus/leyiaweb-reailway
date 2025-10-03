#!/bin/sh
set -euo pipefail

echo "[entrypoint] REFLEX_ENV=${REFLEX_ENV:-dev}"
echo "[entrypoint] DATABASE_URL=${DATABASE_URL:-'(default sqlite)'}"

RUN_MIGRATIONS=${RUN_MIGRATIONS:-1}
DB_WAIT_RETRIES=${DB_WAIT_RETRIES:-30}
DB_WAIT_INTERVAL=${DB_WAIT_INTERVAL:-2}

# If a Postgres URL is provided, wait for connectivity before running migrations.
if [ -n "${DATABASE_URL:-}" ] && printf '%s' "$DATABASE_URL" | grep -qi '^postgres'; then
  echo "[entrypoint] Waiting for PostgreSQL to be reachable..."
  python - <<'PY'
import os, time, sys
import psycopg2

url = os.environ.get('DATABASE_URL', '')
retries = int(os.environ.get('DB_WAIT_RETRIES', '30'))
interval = int(os.environ.get('DB_WAIT_INTERVAL', '2'))

for attempt in range(1, retries+1):
    try:
        conn = psycopg2.connect(url)
        conn.close()
        print(f"[entrypoint] PostgreSQL reachable on attempt {attempt}.")
        break
    except Exception as e:
        print(f"[entrypoint] Attempt {attempt}/{retries} - DB not ready: {e}")
        if attempt == retries:
            print('[entrypoint] ERROR: Database not reachable, aborting.')
            sys.exit(1)
        time.sleep(interval)
PY
fi

if [ "${RUN_MIGRATIONS}" = "1" ] && [ -d "/app/alembic" ]; then
  echo "[entrypoint] Running Alembic migrations (upgrade head)";
  alembic upgrade head || {
    echo "[entrypoint] Alembic migration failed";
    exit 1;
  }
else
  echo "[entrypoint] Skipping migrations (RUN_MIGRATIONS=${RUN_MIGRATIONS}, alembic dir exists? $( [ -d /app/alembic ] && echo yes || echo no ))";
fi

# --- Optional seed of initial admin user (only if table empty) ---
if [ "${SEED_ADMIN:-0}" = "1" ]; then
  if printf '%s' "${DATABASE_URL:-}" | grep -qi '^postgres'; then
    echo "[entrypoint] Checking for existing users in localuser table (seed mode)."
    python - <<'PY'
import os, sys, bcrypt, psycopg2

url = os.environ.get('DATABASE_URL')
username = os.environ.get('ADMIN_USERNAME', 'admin')
password = os.environ.get('ADMIN_PASSWORD', '')
if not password:
    print('[seed] ADMIN_PASSWORD no definido; omitiendo seed por seguridad.')
    sys.exit(0)

try:
    conn = psycopg2.connect(url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM localuser')
    count = cur.fetchone()[0]
    if count == 0:
        print(f'[seed] Tabla localuser vacía. Creando usuario inicial "{username}" ...')
        pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cur.execute('INSERT INTO localuser (username, password_hash, enabled) VALUES (%s, %s, %s)', (username, psycopg2.Binary(pwd_hash), True))
        print('[seed] Usuario creado.')
    else:
        print(f'[seed] Tabla localuser ya tiene {count} usuario(s). No se crea usuario inicial.')
except Exception as e:
    print('[seed] Error sembrando usuario inicial:', e)
finally:
    try:
        cur.close(); conn.close()
    except Exception:
        pass
PY
  else
    echo "[entrypoint] SEED_ADMIN=1 pero DATABASE_URL no es Postgres; omitiendo seed."
  fi
fi

echo "[entrypoint] Starting Reflex (backend :${PORT:-8000} / frontend :${FRONTEND_PORT:-3000})..."
exec reflex run --env "${REFLEX_ENV:-dev}" --backend-host "${BACKEND_HOST:-0.0.0.0}" --backend-port "${PORT:-8000}" "$@"
