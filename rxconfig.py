import os
import reflex as rx

PORT = int(os.getenv("PORT", "8000"))
ENV = os.getenv("REFLEX_ENV", "dev").lower()
IS_PROD = ENV == "prod"

API_URL = os.getenv("API_URL", f"http://localhost:{PORT}")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3000"))
DB_URL = os.getenv("DATABASE_URL", "sqlite:///db/legal_assistant.db")
UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "/tmp/legalassistant_uploads")


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
    # Solo desactivar hot reload si se fuerza prod
    reload=not IS_PROD,
    watch=not IS_PROD,
    hot_reload=not IS_PROD,
)