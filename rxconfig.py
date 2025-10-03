import os
import reflex as rx

"""Versión mínima de configuración para aislar problema de puerto 3000.

Objetivo: en producción (REFLEX_ENV=prod) sólo debe exponerse el puerto backend.
Si aún aparece un frontend :3000 tras esta simplificación, el origen NO es la config.
"""

ENV = os.getenv("REFLEX_ENV", "dev").lower()
IS_PROD = ENV == "prod"

# Congelamos el puerto backend: algunos procesos secundarios (build/SSR frontend) pueden
# modificar PORT=3000 antes de re-importar este módulo. Para evitar que el backend_port
# "salte" en los logs, guardamos el valor inicial en BACKEND_PORT_FIXED.
if "BACKEND_PORT_FIXED" in os.environ:
    PORT = int(os.environ["BACKEND_PORT_FIXED"])  # reutilizamos el original
else:
    PORT = int(os.getenv("PORT", "10000"))  # default típico prod
    os.environ["BACKEND_PORT_FIXED"] = str(PORT)

# Base de datos mínima
if IS_PROD:
    DB_URL = os.getenv("DATABASE_URL")
    if not DB_URL:
        raise RuntimeError("DATABASE_URL requerido en producción (PostgreSQL).")
    if DB_URL.startswith("sqlite:"):
        raise RuntimeError("No se permite SQLite en producción.")
else:
    DB_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/dev.db")

# api_url: en prod priorizar API_URL explícita, luego RENDER_EXTERNAL_URL, fallback localhost
if IS_PROD:
    api_url = os.getenv("API_URL") or os.getenv("RENDER_EXTERNAL_URL") or f"http://127.0.0.1:{PORT}"
    api_url = api_url.rstrip("/")
else:
    api_url = f"http://localhost:{PORT}"

# Config mínima: sin frontend_port en prod, sin reload/hot/watch ni plugins
config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    backend_host="0.0.0.0",
    backend_port=PORT,
    env=rx.Env.PROD if IS_PROD else rx.Env.DEV,
    db_url=DB_URL,
    api_url=api_url,
    # Desactivamos explícitamente sitemap para suprimir warnings repetidos.
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)

print(f"[rxconfig:min] ENV={ENV} backend_port={PORT} api_url={api_url} db={DB_URL.split(':',1)[0]}")
