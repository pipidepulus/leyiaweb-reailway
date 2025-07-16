import reflex as rx
import os

# Render setea estas variables automáticamente
IS_RENDER = os.environ.get("RENDER") is not None
PORT = int(os.environ.get("PORT", 8000))

if IS_RENDER:
    # En Render - configuración especial para WebSockets
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    api_url = f"https://{hostname}"
    cors_origins = [api_url]
    
    # CONFIGURACIÓN ESPECÍFICA PARA RENDER:
    backend_config = {
        "backend_host": "0.0.0.0",
        "backend_port": PORT,
        "api_url": api_url,
        "cors_allowed_origins": cors_origins,
        # Configuraciones adicionales para WebSockets en Render:
        "backend_transport": "websocket",
        "frontend_path": "/",
    }
else:
    # Desarrollo local
    api_url = "http://localhost:8000"
    cors_origins = ["http://localhost:3000"]
    
    backend_config = {
        "backend_host": "0.0.0.0",
        "backend_port": PORT,
        "frontend_port": 3000,
        "api_url": api_url,
        "cors_allowed_origins": cors_origins,
    }

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    tailwind=None,
    **backend_config
)