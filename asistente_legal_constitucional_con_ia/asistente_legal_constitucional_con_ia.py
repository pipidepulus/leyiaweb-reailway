# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""
Archivo principal de la aplicación.
"""
import os
import reflex as rx
from dotenv import load_dotenv
from fastapi import FastAPI

from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page
from .pages.asistente_page import asistente_page
from .components.layout import main_layout

load_dotenv()

# --- MÉTODO MODERNO PARA AÑADIR RUTAS API ---
# 1. Crea una instancia de FastAPI.
fastapi_app = FastAPI()

# 2. Define tu endpoint de salud en esta instancia.
@fastapi_app.get("/health")
def health():
    """Endpoint de chequeo de salud para Render."""
    return {"status": "ok"}

# 3. Define una función "transformer" que montará la API de Reflex.
def api_transformer(reflex_api: FastAPI) -> FastAPI:
    """Monta la API de Reflex en la aplicación FastAPI principal."""
    fastapi_app.mount(path="/", app=reflex_api)
    return fastapi_app

# --- DEFINICIÓN DE LA APP (Usando el transformer) ---
app = rx.App(
    api_transformer=api_transformer,
)


# --- Definición de la Página Principal (Index) ---
@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
    """La página de inicio, envuelta en el layout principal."""
    content = rx.el.div(
        rx.image(
            src="/balanza.png",
            alt="Balanza de la Justicia",
            width="256px",
            height="auto",
            margin_bottom="1rem",
        ),
        rx.el.h1(
            "Bienvenido al Asistente Legal Constitucional",
            class_name="text-3xl font-bold mb-2",
        ),
        rx.el.p(
            "Sistema especializado en análisis de jurisprudencia, leyes, "
            "propuestas de leyes con ayuda de inteligencia artificial.",
            class_name="text-lg text-gray-600 mb-4",
        ),
        rx.el.p(
            "Selecciona una opción del menú para comenzar.",
            class_name="text-lg text-gray-700 font-bold",
        ),
        class_name="flex flex-col items-center justify-center w-full h-full text-center",
    )
    return main_layout(content)


# --- Añadimos todas las páginas a la aplicación ---
app.add_page(asistente_page)
app.add_page(proyectos_page)
app.add_page(prompts_page)

