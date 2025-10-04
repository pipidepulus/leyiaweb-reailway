# rxconfig.py

import os
import reflex as rx

# La URL pública de tu aplicación. Es CRUCIAL para que los WebSockets funcionen.
# Render la inyectará a través de una variable de entorno que configurarás.
API_URL = os.getenv("API_URL")
if not API_URL:
    # Esta advertencia es útil para el desarrollo local si olvidas configurar la URL.
    print("⚠️  ADVERTENCIA: La variable de entorno API_URL no está configurada.")
    print("   En producción, esto causará que los WebSockets fallen.")
    print("   Estableciendo un valor predeterminado para desarrollo local: http://localhost:8000")
    API_URL = "http://localhost:8000"


# Orígenes permitidos para CORS, leídos desde una variable de entorno.
# En Render, deberías establecer esto a la URL de tu frontend, ej: "https://tu-app.onrender.com"
CORS_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")


config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    
    # Configuración de red para Render
    backend_host="0.0.0.0",  # Imprescindible para escuchar dentro de un contenedor Docker
    backend_port=int(os.getenv("PORT", "8000")), # Render asigna el puerto a través de esta variable
    api_url=API_URL, # Informa al frontend dónde encontrar el backend
    
    # Configuración de base de datos
    # Render inyectará automáticamente la URL de tu base de datos PostgreSQL aquí
    db_url=os.getenv("DATABASE_URL"),
    
    # Forzar siempre el entorno de producción
    env=rx.Env.PROD,
    
    # Orígenes CORS
    cors_allowed_origins=CORS_ORIGINS,
    
    # Configuraciones adicionales de producción recomendadas
    telemetry_enabled=False,
    timeout=120, # Aumentar el timeout para tareas largas
)