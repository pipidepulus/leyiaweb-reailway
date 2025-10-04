#!/usr/bin/env bash
set -euo pipefail
source venv/bin/activate
export REFLEX_ENV=prod
export PORT=${PORT:-8000}
# Construye y sirve versión producción (frontend estático)
reflex run --env prod --backend-host 0.0.0.0 --backend-port ${PORT}
