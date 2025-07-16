import reflex as rx
import os

# Render setea estas variables automáticamente
IS_RENDER = os.environ.get("RENDER") is not None
PORT = int(os.environ.get("PORT", 8000))

if IS_RENDER:
    # En Render - backend separado
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    api_url = f"https://{hostname}"
    
    # CORS: dominios del frontend que pueden acceder al backend
    cors_origins = [
        "https://legalcolrag-frontend.onrender.com",
        "https://lawyer-ai.co",
        "https://www.lawyer-ai.co",
        api_url,  # El propio backend también
    ]
    
    config = rx.Config(
        app_name="asistente_legal_constitucional_con_ia",
        backend_host="0.0.0.0",
        backend_port=PORT,
        api_url=api_url,
        cors_allowed_origins=cors_origins,
        tailwind=None,
        show_reflex_links=False,
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
        show_reflex_links=False,
    )