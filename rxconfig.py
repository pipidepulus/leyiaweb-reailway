"""Archivo de configuración de Reflex para la aplicación.

Este archivo define la configuración principal de la aplicación Reflex,
incluyendo el nombre de la aplicación, puertos, configuración de base de datos,
y opciones de despliegue.
"""

import os
import reflex as rx

# Obtener configuración desde variables de entorno con valores por defecto
config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    
    # Configuración de puertos
    # En Render, se usa la variable de entorno PORT
    backend_port=int(os.getenv("PORT", "8000")),
    frontend_port=int(os.getenv("FRONTEND_PORT", "3000")),
    
    # Configuración de base de datos
    # Reflex usa SQLAlchemy internamente para su estado
    db_url=os.getenv(
        "DATABASE_URL",
        "postgresql://leyia:leyia@db:5432/leyia"
    ),
    
    # Configuración de Redis (opcional pero recomendado para producción)
    # Si no se proporciona, Reflex usa un backend en memoria
    redis_url=os.getenv("REDIS_URL", None),
    
    # Configuración de entorno
    # dev: modo desarrollo con hot reload
    # prod: modo producción optimizado
    env=rx.Env(os.getenv("REFLEX_ENV", "prod")),
    
    # Configuración de API
    # Habilitar CORS para permitir peticiones desde el frontend
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        # Agregar el dominio de Render cuando se despliegue
        os.getenv("FRONTEND_URL", "*"),
    ],
    
    # Configuración de compilación
    # Deshabilitar telemetría en producción
    telemetry_enabled=False,
    
    # Timeout para conexión a base de datos (útil en despliegue)
    timeout=120,
    
    # Configuración de activos estáticos
    # Los archivos en /assets se sirven automáticamente
    
    # Configuración de compilación del frontend
    # next_compression: Habilitar compresión en Next.js
    next_compression=True,
    
    # Configuración de logs
    # En producción, reducir verbosidad
    loglevel="info" if os.getenv("REFLEX_ENV") == "prod" else "debug",
)

# Configuración adicional para producción en Render
if os.getenv("RENDER"):
    # En Render, ajustar configuraciones específicas
    config.backend_port = int(os.getenv("PORT", "8000"))
    
    # Asegurar que el frontend apunte al backend correcto
    # Render proporciona la URL del servicio en RENDER_EXTERNAL_URL
    backend_url = os.getenv("RENDER_EXTERNAL_URL", f"http://0.0.0.0:{config.backend_port}")
    config.api_url = backend_url
    
    # Configurar el origen del frontend para CORS
    frontend_url = os.getenv("FRONTEND_URL", backend_url)
    if frontend_url not in config.cors_allowed_origins:
        config.cors_allowed_origins.append(frontend_url)
    
    # En producción, usar bind 0.0.0.0 para aceptar conexiones externas
    config.backend_host = "0.0.0.0"
    config.frontend_host = "0.0.0.0"

# Notas de configuración:
# ----------------------
# 1. DATABASE_URL: Debe estar configurada en las variables de entorno de Render
#    Formato: postgresql://usuario:contraseña@host:puerto/database
#
# 2. OPENAI_API_KEY: Requerida para el asistente legal
#
# 3. ASSEMBLYAI_API_KEY: Requerida para transcripción de audio
#
# 4. TAVILY_API_KEY: Requerida para búsqueda web
#
# 5. REDIS_URL (opcional): Para mejor rendimiento en producción
#    Formato: redis://host:puerto
#
# 6. REFLEX_ENV: Configurar a "prod" en Render
#
# 7. PORT: Render lo configura automáticamente
