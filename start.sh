#!/usr/bin/env bash
set -euo pipefail

echo "[start] REFLEX_ENV=$REFLEX_ENV PORT=${PORT:-8000}"

# Esperar a Postgres si DATABASE_URL apunta a host remoto.
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "[start] Detectada DATABASE_URL. Intentando migraciones Alembic..."
  # Intentar reconexión simple antes de migrar (hasta 10 intentos)
  ATTEMPTS=0
  MAX_ATTEMPTS=10
  until alembic upgrade head || [[ $ATTEMPTS -ge $MAX_ATTEMPTS ]]; do
    ATTEMPTS=$((ATTEMPTS+1))
    echo "[start] Migración fallida. Reintentando ($ATTEMPTS/$MAX_ATTEMPTS) en 3s..."
    sleep 3
  done
  if [[ $ATTEMPTS -ge $MAX_ATTEMPTS ]]; then
    echo "[start][warn] No se pudieron aplicar migraciones después de $MAX_ATTEMPTS intentos. Continuando de todos modos." >&2
  else
    echo "[start] Migraciones aplicadas correctamente."
  fi
else
  echo "[start] No hay DATABASE_URL explícita. Saltando migraciones (usa SQLite)."
fi

# Ejecutar la aplicación Reflex (full stack, sin --backend-only)
exec reflex run --env prod --backend-host 0.0.0.0 --backend-port ${PORT:-8000}
