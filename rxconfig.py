# rxconfig.py (Versión Canónica)

import os
import reflex as rx

# El puerto que Render nos asigna.
RENDER_PORT = int(os.getenv("PORT", "8000"))

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    
    # SOLO definimos el backend.
    # En producción, Reflex es lo suficientemente inteligente para saber
    # que el backend también debe servir al frontend en este puerto.
    backend_host="0.0.0.0",
    backend_port=RENDER_PORT,
    
    # La URL pública es crucial
    api_url=os.getenv("API_URL"),
    
    # Base de datos y entorno
    db_url=os.getenv("DATABASE_URL"),
    env=rx.Env.PROD,
    
    # CORS y plugins
    cors_allowed_origins=os.getenv("CORS_ALLOWED_ORIGINS", "").split(","),
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # Opcional: Configuraciones de producción
    telemetry_enabled=False,
    timeout=120,
)