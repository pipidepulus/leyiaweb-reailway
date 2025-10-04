#!/usr/bin/env bash
set -euo pipefail
source venv/bin/activate
export REFLEX_ENV=dev
export FRONTEND_PORT=${FRONTEND_PORT:-3000}
export PORT=${PORT:-8000}
# Puedes añadir orígenes extra: export DEV_EXTRA_ORIGINS="http://localhost:3100"
reflex run --backend-host 0.0.0.0 --backend-port ${PORT}
