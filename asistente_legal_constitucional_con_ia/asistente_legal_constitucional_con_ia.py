# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""Versión de la aplicación SIN Clerk para depuración final."""

# --- Importaciones (SIN CLERK) ---
import reflex as rx
from dotenv import load_dotenv

# Quita las importaciones de páginas que dependen de Clerk o del layout
# from .pages.prompts_page import prompts_page
# from .pages.proyectos_page import proyectos_page
# from .pages.asistente_page import asistente_page
# from .components.layout import main_layout # ¡IMPORTANTE! Quitamos el layout

# --- Carga de Entorno y Definición de la App ---
load_dotenv()
app = rx.App()

# --- Definición de la Página Principal (SIN EL LAYOUT) ---
@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
    """La página de inicio, ahora sin el layout de Clerk."""
    # Contenido específico de la página de inicio
    # Este es tu código original, que está perfecto.
    return rx.el.div(
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
            "Prueba sin Clerk.",
            class_name="text-lg text-gray-700 font-bold",
        ),
        class_name="flex flex-col items-center justify-center w-full h-full text-center",
    )