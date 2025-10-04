import reflex as rx
import os

"""Configuración de Reflex.

Objetivo del cambio:
Solucionar el 404 (Not Found) en Render. El problema ocurría porque el contenedor
se ejecutaba sólo con el backend (`--backend-only`), por lo que no se servía el
frontend y al abrir la URL de Render el navegador no encontraba recursos.

Estrategia:
- Unificar frontend + backend en el mismo servicio (single service en Render).
- Evitar forzar `api_url` absoluta en producción para permitir llamadas relativas
  (el frontend y backend comparten dominio). Esto simplifica CORS y evita
  desajustes si Render cambia el hostname.
"""

# Detecta si estamos en Render (Render siempre inyecta la variable RENDER)
IS_RENDER = os.environ.get("RENDER") is not None

# Puerto que Render expone vía env var PORT (fallback 8000 para local)
PORT = int(os.environ.get("PORT", 8000))

# Base de datos: en Render preferimos PostgreSQL si está configurado;
# localmente usamos SQLite.
if IS_RENDER:
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///legal_assistant.db")
else:
    DATABASE_URL = "sqlite:///legal_assistant.db"

if IS_RENDER:
    # Single service: frontend y backend comparten dominio.
    # Usamos origen relativo -> no definimos api_url explícitamente.
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    # Aun así listamos el dominio para CORS en caso de que Reflex lo use.
    cors_origins = [f"https://{hostname}"] if hostname else []

    config = rx.Config(
        app_name="asistente_legal_constitucional_con_ia",
        backend_host="0.0.0.0",
        backend_port=PORT,
        # api_url OMITIDO: llamadas relativas (evita 404 y problemas de CORS)
        cors_allowed_origins=cors_origins,
        tailwind=None,
        show_built_with_reflex=False,
        db_url=DATABASE_URL,
    )
else:
    # Entorno de desarrollo: frontend corre en 3000 y backend en 8000.
    config = rx.Config(
        app_name="asistente_legal_constitucional_con_ia",
        backend_host="0.0.0.0",
        backend_port=PORT,
        frontend_port=3000,
        api_url="http://localhost:8000",
        cors_allowed_origins=["http://localhost:3000"],
        tailwind=None,
        show_built_with_reflex=False,
        db_url=DATABASE_URL,
    )