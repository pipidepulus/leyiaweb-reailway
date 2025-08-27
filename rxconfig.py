import os

import reflex as rx
from typing import List, Any

ENABLE_SITEMAP = os.getenv("REFLEX_ENABLE_SITEMAP", "0").lower() in {"1", "true", "yes"}
SITEMAP_PLUGIN: Any = None
if ENABLE_SITEMAP:
    try:
        from reflex.plugins.sitemap import SitemapPlugin as _SitemapPlugin  # type: ignore

        SITEMAP_PLUGIN = _SitemapPlugin
    except Exception:
        # If plugin import fails, we'll fall back to default behavior.
        SITEMAP_PLUGIN = None

PORT = int(os.getenv("PORT", "8000"))
ENV = os.getenv("REFLEX_ENV", "dev").lower()
IS_PROD = ENV == "prod"

API_URL = os.getenv("API_URL", f"http://localhost:{PORT}")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3000"))
# In dev, keep the SQLite DB outside the workspace to avoid file-watcher reloads
# when the database file changes. In prod, preserve the existing on-repo path
# unless DATABASE_URL is explicitly provided.
default_dev_db = "sqlite:////tmp/legal_assistant_dev.db"
default_prod_db = "sqlite:///db/legal_assistant.db"
DB_URL = os.getenv("DATABASE_URL", default_prod_db if IS_PROD else default_dev_db)
UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "/tmp/legalassistant_uploads")


# Allow disabling dev reload/watch via env flags without forcing prod mode
DISABLE_RELOAD = os.getenv("REFLEX_DISABLE_RELOAD", "0").lower() in {"1", "true", "yes"}
DISABLE_WATCH = os.getenv("REFLEX_DISABLE_WATCH", "0").lower() in {"1", "true", "yes"}
DISABLE_HOT = os.getenv("REFLEX_DISABLE_HOT", "0").lower() in {"1", "true", "yes"}

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    backend_host="0.0.0.0",
    backend_port=PORT,
    frontend_port=FRONTEND_PORT,
    api_url=API_URL,
    cors_allowed_origins=os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    tailwind=None,
    show_built_with_reflex=False,
    db_url=DB_URL,
    upload_folder=UPLOAD_DIR,
    env=rx.Env.PROD if IS_PROD else rx.Env.DEV,
    # Permitir desactivar recarga/observación en dev con variables de entorno
    reload=False if IS_PROD else (not DISABLE_RELOAD),
    watch=False if IS_PROD else (not DISABLE_WATCH),
    hot_reload=False if IS_PROD else (not DISABLE_HOT),
    # Plugins: disable sitemap by default; when enabled, add explicitly to silence warnings
    plugins=([SITEMAP_PLUGIN] if ENABLE_SITEMAP and SITEMAP_PLUGIN is not None else []),
    disable_plugins=([] if ENABLE_SITEMAP else ["reflex.plugins.sitemap.SitemapPlugin"]),
)
