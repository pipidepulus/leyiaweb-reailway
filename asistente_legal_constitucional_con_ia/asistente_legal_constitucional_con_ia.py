# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""Archivo principal de la aplicación, restaurado y funcional SIN Clerk."""

# --- Importaciones (SIN CLERK) ---
import reflex as rx
from dotenv import load_dotenv

from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page
from .pages.asistente_page import asistente_page
# NOTA: Hemos quitado 'import reflex_clerk_api' y 'import main_layout' por ahora.

# --- Carga de Entorno y Definición de la App ---
load_dotenv()
app = rx.App()

# --- Definición de la Página Principal (Index) ---
@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
    """La página de inicio, ahora SIN el layout de Clerk."""
    # Tu código de contenido es perfecto.
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
            "Funcionalidad base restaurada. Próximo paso: reintegrar autenticación.",
            class_name="text-lg text-gray-700 font-bold",
        ),
        class_name="flex flex-col items-center justify-center w-full h-full text-center",
    )
    # Devolvemos el contenido directamente.
    return content


# --- Añadimos el resto de las páginas ---
# Asumimos que estas páginas no dependen directamente del layout de Clerk.
# Si lo hacen, tendrás que modificarlas temporalmente también.
app.add_page(asistente_page)
app.add_page(proyectos_page)
app.add_page(prompts_page)

# NOTA: Las líneas de 'clerk.add_..._page(app)' han sido eliminadas.