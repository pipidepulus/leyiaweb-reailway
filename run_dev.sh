#!/usr/bin/env bash
set -euo pipefail
source venv/bin/activate
export FRONTEND_PORT=${FRONTEND_PORT:-3000}
export PORT=${PORT:-8000}

if [[ -z "${DATABASE_URL:-}" ]]; then
	echo "ERROR: DATABASE_URL no está definida. Exporta una URL Postgres antes de continuar." >&2
	exit 1
fi

echo "Iniciando Reflex (modo local único) con backend en ${PORT} y frontend en ${FRONTEND_PORT}" 
reflex run --backend-host 0.0.0.0 --backend-port ${PORT}
