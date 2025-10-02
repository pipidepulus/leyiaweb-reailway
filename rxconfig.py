import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from typing import Any, Dict
import reflex as rx

"""Configuración central de Reflex.

Objetivos de esta revisión:
1. Evitar que en producción (Render) se levante un frontend dev separado (puerto 3000).
2. Forzar uso de PostgreSQL en producción (error si falta DATABASE_URL) y eliminar fallback SQLite prod.
3. No incrustar 'http://localhost' en el bundle de producción: permitir API relativa o usar RENDER_EXTERNAL_URL.
4. CORS dinámico incluyendo dominio externo si existe.
5. Mantener experiencia DX completa en desarrollo (hot reload, watch, frontend_port).
"""

# Carga de variables de entorno temprana
load_dotenv()

ENV = os.getenv("REFLEX_ENV", "dev").lower()
IS_PROD = ENV == "prod"
PORT = int(os.getenv("PORT", "8000"))  # Puerto backend (único en prod)

# --- Base de Datos ---
if IS_PROD:
    DB_URL = os.getenv("DATABASE_URL")
    if not DB_URL:
        raise RuntimeError("DATABASE_URL es obligatorio en producción (PostgreSQL).")
    if DB_URL.startswith("sqlite:"):
        raise RuntimeError("En producción no se permite SQLite. Proporciona un DATABASE_URL PostgreSQL.")
else:
    # En desarrollo permitimos fallback SQLite para simplificar.
    DB_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/legal_assistant_dev.db")

UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "/tmp/legalassistant_uploads")

# --- API URL ---
# En producción preferimos rutas relativas (api_url=None) para que el frontend use el mismo origen.
# Si el usuario define API_URL explícito, lo respetamos; si no, intentamos RENDER_EXTERNAL_URL solo para CORS, no como api_url.
explicit_api_url = os.getenv("API_URL")
render_external = os.getenv("RENDER_EXTERNAL_URL")  # P.e. https://leyiaweb.onrender.com
API_URL = None
if not IS_PROD:
    # En dev sí necesitamos apuntar explícitamente al backend (cuando frontend dev corre en otro puerto)
    API_URL = explicit_api_url or f"http://localhost:{PORT}"
else:
    # En prod: sólo usar API_URL si el usuario lo forzó explícitamente.
    if explicit_api_url:
        API_URL = explicit_api_url.rstrip("/")

# --- Frontend Port ---
# En producción NO definimos frontend_port para evitar servidor adicional (un solo puerto servido por backend).
FRONTEND_PORT_DEV = int(os.getenv("FRONTEND_PORT", "3000"))

# --- Flags de recarga sólo relevantes en dev ---
DISABLE_RELOAD = os.getenv("REFLEX_DISABLE_RELOAD", "0").lower() in {"1", "true", "yes"}
DISABLE_WATCH = os.getenv("REFLEX_DISABLE_WATCH", "0").lower() in {"1", "true", "yes"}
DISABLE_HOT = os.getenv("REFLEX_DISABLE_HOT", "0").lower() in {"1", "true", "yes"}

# --- Plugins (sitemap opcional) ---
ENABLE_SITEMAP = os.getenv("REFLEX_ENABLE_SITEMAP", "0").lower() in {"1", "true", "yes"}
SITEMAP_PLUGIN: Any = None
if ENABLE_SITEMAP:
    try:  # type: ignore[attr-defined]
        from reflex.plugins.sitemap import SitemapPlugin as _SitemapPlugin  # type: ignore

        SITEMAP_PLUGIN = _SitemapPlugin
    except Exception:
        SITEMAP_PLUGIN = None

# --- CORS ---
default_cors = []
if not IS_PROD:
    default_cors = [
        f"http://localhost:{FRONTEND_PORT_DEV}",
        f"http://127.0.0.1:{FRONTEND_PORT_DEV}",
    ]
cors_env = os.getenv("CORS_ALLOWED_ORIGINS")
if cors_env:
    cors_allowed = [o.strip() for o in cors_env.split(",") if o.strip()]
else:
    cors_allowed = default_cors

# Añadimos dominio externo de Render si está definido y no se incluyó.
if render_external:
    parsed = urlparse(render_external)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in cors_allowed:
        cors_allowed.append(origin)

# --- Construcción dinámica de kwargs ---
config_kwargs: Dict[str, Any] = dict(
    app_name="asistente_legal_constitucional_con_ia",
    backend_host="0.0.0.0",
    backend_port=PORT,
    api_url=API_URL,  # Puede ser None (Reflex debería manejar relativo)
    cors_allowed_origins=cors_allowed,
    tailwind=None,
    show_built_with_reflex=False,
    db_url=DB_URL,
    upload_folder=UPLOAD_DIR,
    env=rx.Env.PROD if IS_PROD else rx.Env.DEV,
    reload=False if IS_PROD else (not DISABLE_RELOAD),
    watch=False if IS_PROD else (not DISABLE_WATCH),
    hot_reload=False if IS_PROD else (not DISABLE_HOT),
    plugins=([SITEMAP_PLUGIN] if ENABLE_SITEMAP and SITEMAP_PLUGIN is not None else []),
    disable_plugins=([] if ENABLE_SITEMAP else ["reflex.plugins.sitemap.SitemapPlugin"]),
)

if not IS_PROD:
    # Sólo en desarrollo levantamos frontend separado
    config_kwargs["frontend_port"] = FRONTEND_PORT_DEV

config = rx.Config(**config_kwargs)

# Log simpático (visible en import) para confirmar modo y DB.
print(f"[rxconfig] ENV={ENV} backend_port={PORT} frontend_port={'disabled' if IS_PROD else FRONTEND_PORT_DEV} DB={DB_URL.split(':',1)[0]} api_url={'(relative)' if API_URL is None else API_URL}")
