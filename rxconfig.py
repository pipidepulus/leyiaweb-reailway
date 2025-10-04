# rxconfig.py (Versión Final para Producción)

import os
import reflex as rx

# La URL pública de tu aplicación. Es CRUCIAL para que los WebSockets funcionen.
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Orígenes permitidos para CORS, leídos desde una variable de entorno.
CORS_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# El puerto que Render nos asigna.
# Usaremos esta misma variable para ambos, frontend y backend.
RENDER_PORT = int(os.getenv("PORT", "8000"))

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    
    # --- LA SOLUCIÓN CLAVE ---
    # Forzar al backend Y al frontend a usar el mismo puerto.
    # En producción, esto le indica a Reflex que ejecute un servidor integrado.
    backend_host="0.0.0.0",
    backend_port=RENDER_PORT,
    frontend_port=RENDER_PORT,
    
    # Configuración de la API y la Base de Datos
    api_url=API_URL,
    db_url=os.getenv("DATABASE_URL"),
    
    # Configuración del entorno y CORS
    env=rx.Env.PROD,
    cors_allowed_origins=CORS_ORIGINS,
    
    # Silenciar advertencia del sitemap para tener logs más limpios
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # Configuraciones adicionales de producción recomendadas
    telemetry_enabled=False,
    timeout=120,
)