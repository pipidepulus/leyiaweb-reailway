import reflex as rx
import os

"""Configuración de Reflex.

Modos soportados localmente sin Docker:
 - Desarrollo: `REFLEX_ENV=dev` (default) -> frontend (3000) + backend (8000)
 - Producción local: `REFLEX_ENV=prod` -> build y sirve frontend estático desde mismo backend (solo puerto 8000)

En Render: se detecta por la variable de entorno `RENDER` y se asume single service.
"""

REFLEX_ENV = os.environ.get("REFLEX_ENV", "dev").lower()
IS_RENDER = os.environ.get("RENDER") is not None
IS_LOCAL_PROD = REFLEX_ENV == "prod" and not IS_RENDER

PORT = int(os.environ.get("PORT", 8000))

# Base de datos: permitir override por DATABASE_URL.
# Reglas endurecidas:
#  - En Render: DATABASE_URL es OBLIGATORIA (si falta -> error para evitar pérdida de datos).
#  - En producción local (IS_LOCAL_PROD): se recomienda forzar Postgres; si falta, se lanza error.
#  - En desarrollo: se permite fallback a SQLite para conveniencia.
_env_db_url = os.environ.get("DATABASE_URL")
if IS_RENDER and not _env_db_url:
    raise RuntimeError(
        "DATABASE_URL no está definida en Render. Configura un servicio Postgres o la variable en el dashboard; se bloquea el uso de SQLite para evitar datos efímeros."
    )
if IS_LOCAL_PROD and not _env_db_url:
    raise RuntimeError(
        "Producción local sin DATABASE_URL. Define una URL de Postgres en .env (ej: postgresql://user:pass@localhost:5432/leyia)."
    )
if _env_db_url:
    DATABASE_URL = _env_db_url
else:
    # Sólo dev: fallback permitido.
    DATABASE_URL = "sqlite:///legal_assistant.db"

if IS_RENDER:
    # Modo Render (backend-only + static site separado):
    #  - El servicio backend se despliega como Web Service (python) ejecutando: reflex run --env prod --backend-only
    #  - El frontend se sirve como Static Site con 'reflex export --frontend-only'
    #  - Necesitamos un api_url absoluto para que el JS del static site apunte al backend.
    # Variables de entorno esperadas (configuradas manualmente en Render):
    #   API_BASE = https://<dominio-del-backend> (en backend puede omitirse y se infiere)
    #   FRONTEND_ORIGIN = https://<dominio-del-static-site> (para CORS)
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    inferred_backend = f"https://{hostname}" if hostname else None
    api_base = os.environ.get("API_BASE", inferred_backend or "")
    frontend_origin = os.environ.get("FRONTEND_ORIGIN")
    cors_list = []
    if api_base:
        cors_list.append(api_base)
    if frontend_origin:
        cors_list.append(frontend_origin)
    config = rx.Config(
        app_name="asistente_legal_constitucional_con_ia",
        backend_host="0.0.0.0",
        backend_port=PORT,  # Render asigna $PORT al backend service
        api_url=api_base if api_base else None,
        cors_allowed_origins=cors_list,
        show_built_with_reflex=False,
        tailwind=None,
        db_url=DATABASE_URL,
        disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    )
elif IS_LOCAL_PROD:
    # Producción local: comportamiento similar a Render, pero en localhost.
    # No especificamos frontend_port para que Reflex sirva el build estático.
    prod_extra_raw = os.environ.get("PROD_EXTRA_ORIGINS", "")
    prod_extra = [o.strip() for o in prod_extra_raw.split(",") if o.strip()]
    # Incluimos puertos comunes usados por Reflex en build prod (3000) y loopback 127.0.0.1
    cors_list = {
        f"http://localhost:{PORT}",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
    cors_list.update(prod_extra)
    config = rx.Config(
        app_name="asistente_legal_constitucional_con_ia",
        backend_host="0.0.0.0",
        backend_port=PORT,
        cors_allowed_origins=sorted(cors_list),
        show_built_with_reflex=False,
        tailwind=None,
        db_url=DATABASE_URL,
        disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    )
else:
    # Desarrollo: frontend (Next) corre en FRONTEND_PORT (default 3000) con hot-reload.
    frontend_port = int(os.environ.get("FRONTEND_PORT", 3000))
    # Permite añadir orígenes adicionales separados por comas: DEV_EXTRA_ORIGINS="http://localhost:3100,http://127.0.0.1:3000"
    extra_origins_raw = os.environ.get("DEV_EXTRA_ORIGINS", "")
    extra_origins = [o.strip() for o in extra_origins_raw.split(",") if o.strip()]
    # Siempre incluimos también el puerto 3000 (valor por defecto) para evitar ruido si cambias de puerto.
    cors_list = {f"http://localhost:{frontend_port}", "http://localhost:3000"}
    cors_list.update(extra_origins)
    config = rx.Config(
        app_name="asistente_legal_constitucional_con_ia",
        backend_host="0.0.0.0",
        backend_port=PORT,
        frontend_port=frontend_port,
        api_url=f"http://localhost:{PORT}",
        cors_allowed_origins=sorted(cors_list),
        show_built_with_reflex=False,
        tailwind=None,
        db_url=DATABASE_URL,
        disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    )