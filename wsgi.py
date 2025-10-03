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

# Importar y configurar la aplicación Reflex
import reflex as rx
from asistente_legal_constitucional_con_ia.asistente_legal_constitucional_con_ia import app

# Compilar la aplicación en modo producción
print("🔧 Compilando aplicación Reflex para producción...")
try:
    # Compilar la aplicación
    app.compile(force_compile=True)
    print("✅ Aplicación compilada exitosamente")
except Exception as e:
    print(f"⚠️ Error compilando aplicación: {e}")
    # Continuar de todos modos

# Exportar la aplicación ASGI
application = app.backend.app

# Para compatibilidad con gunicorn
app_instance = application

print("🚀 Aplicación ASGI lista para Render")