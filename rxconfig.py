import reflex as rx
import os

# Render setea estas variables automáticamente
IS_RENDER = os.environ.get("RENDER") is not None
PORT = int(os.environ.get("PORT", 8000))

# Configuración de base de datos
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///legal_assistant.db")

# Configuración de la base de datos
if IS_RENDER:
    # En producción usar PostgreSQL de Render
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///legal_assistant.db")
else:
    # En desarrollo usar SQLite
    DATABASE_URL = "sqlite:///legal_assistant.db"

if IS_RENDER:
    # En Render - backend separado
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    api_url = f"https://{hostname}"
    
    # CORS: dominios que pueden acceder al backend
    cors_origins = [
        api_url,  # El propio backend: https://legalcolrag-noclerk.onrender.com
        "https://legalcolrag-noclerk-1.onrender.com",  # Tu frontend
    ]
    
    config = rx.Config(
        app_name="asistente_legal_constitucional_con_ia",
        backend_host="0.0.0.0",
        backend_port=PORT,
        api_url=api_url,
        cors_allowed_origins=cors_origins,
        tailwind=None,
        show_built_with_reflex=False,
        db_url=DATABASE_URL,
    )
else:
    # Desarrollo local
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