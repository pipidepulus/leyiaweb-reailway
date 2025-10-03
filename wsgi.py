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
import reflex as rx

print("🚀 Preparando aplicación ASGI para Render...")

# En modo producción, Reflex necesita compilar primero
try:
    # Compilar la aplicación para producción
    print("🔧 Compilando aplicación para producción...")
    rx.export.export(frontend=True, backend=False, zip=False)
    print("✅ Frontend compilado exitosamente")
except Exception as e:
    print(f"⚠️ Error compilando frontend: {e}")

# Obtener la aplicación ASGI directamente del módulo app
try:
    # En Reflex, la aplicación ASGI está en app.app
    application = app.app
    print("✅ Aplicación ASGI obtenida correctamente")
except AttributeError:
    try:
        # Método alternativo: usar la app directamente
        application = app
        print("✅ Usando aplicación directamente como fallback")
    except Exception as e:
        print(f"❌ Error obteniendo aplicación: {e}")
        raise

# Para compatibilidad con gunicorn
app_instance = application

print("🌐 Aplicación lista para servir en Render")