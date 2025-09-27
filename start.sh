#!/usr/bin/env bash
set -euo pipefail

echo "[start] REFLEX_ENV=${REFLEX_ENV:-unset} PORT=${PORT:-8000}"
echo "[start] Python: $(python --version 2>/dev/null || echo 'no python')"
echo "[start] Which python: $(which python || true)"

# Función helper para ejecutar un módulo Python con reintentos (para alembic)
run_alembic() {
  python -m alembic upgrade head
}

if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "[start] Detectada DATABASE_URL. Intentando migraciones Alembic..."
  ATTEMPTS=0
  MAX_ATTEMPTS=10
  until run_alembic || [[ $ATTEMPTS -ge $MAX_ATTEMPTS ]]; do
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

echo "[start] Lanzando Reflex..."
exec python -m reflex run --env prod --backend-host 0.0.0.0 --backend-port ${PORT:-8000}
