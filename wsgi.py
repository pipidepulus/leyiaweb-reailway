#!/usr/bin/env python3
"""
WSGI/ASGI entry point for Render deployment.

Este archivo expone la aplicación Reflex como una aplicación ASGI
que puede ser servida por gunicorn + uvicorn en Render.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar variables de entorno necesarias
os.environ.setdefault("REFLEX_ENV", "prod")

# Importar la aplicación Reflex
from asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia import app

print("🚀 Preparando aplicación ASGI para Render...")

# Obtener la aplicación ASGI directamente
# En Reflex 0.8.13, la aplicación ASGI está disponible directamente
try:
    # Método correcto para obtener la app ASGI en Reflex 0.8.13
    application = app.api
    print("✅ Aplicación ASGI obtenida correctamente")
except AttributeError:
    try:
        # Método alternativo
        application = app._app
        print("✅ Aplicación ASGI obtenida (método alternativo)")
    except AttributeError:
        # Fallback: usar la app directamente
        application = app
        print("✅ Usando aplicación directamente como fallback")

# Para compatibilidad con gunicorn
app_instance = application

print("🌐 Aplicación lista para servir en Render")