"""Archivo de configuración de Reflex para despliegue en Render.

Configuración optimizada para producción en Render.com que asigna automáticamente
el puerto 10000 para todos los servicios.
"""

import os
import reflex as rx

# Configuración específica para Render
# Render asigna automáticamente el puerto a través de la variable PORT
config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    
    # Puerto dinámico asignado por Render
    backend_port=int(os.getenv("PORT", "8000")),
    frontend_port=int(os.getenv("PORT", "8000")),
    
    # Base de datos
    db_url=os.getenv(
        "DATABASE_URL",
        "postgresql://leyia:leyia@db:5432/leyia"
    ),
    
    # Redis opcional
    redis_url=os.getenv("REDIS_URL", None),
    
    # Entorno de producción
    env=rx.Env.PROD,
    
    # CORS para Render
    cors_allowed_origins=[
        "https://leyiaweb.onrender.com",
        "https://*.onrender.com",
        "*",  # Permitir todos los orígenes en producción
    ],
    
    # Configuración de producción
    telemetry_enabled=False,
    timeout=120,
    
    # Hosts para Render
    backend_host="0.0.0.0",
    frontend_host="0.0.0.0",
    
    # Deshabilitar plugin de sitemap que genera warnings
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)

# Notas para Render:
# - Render asigna automáticamente puerto 10000
# - DATABASE_URL se configura automáticamente
# - Variables de entorno requeridas:
#   * OPENAI_API_KEY
#   * ASSEMBLYAI_API_KEY  
#   * TAVILY_API_KEY
