# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""
Archivo principal de la aplicación.
Aplicando un parche para forzar la URL del WebSocket en el AppState.
"""
import os
import reflex as rx
import reflex_clerk_api as clerk
from dotenv import load_dotenv

from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page
from .pages.asistente_page import asistente_page
from .components.layout import main_layout

load_dotenv()

# --- EL PARCHE (WORKAROUND) ---
# Creamos un estado personalizado que hereda del estado base de la app.
# Sobreescribimos la URL del socket para forzarla a usar el dominio correcto.
class CustomAppState(rx.AppState):
    @rx.var
    def socket_url(self) -> str:
        # Esto ignora cualquier configuración automática y usa nuestro dominio.
        return "wss://www.globaltelecom.site"

# --- DEFINICIÓN DE LA APP ---
# Le decimos a la app que use nuestro estado base personalizado.
app = rx.App(
    state=CustomAppState
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

clerk.add_sign_in_page(app)
clerk.add_sign_up_page(app)


# --- Envolvemos la App con el Provider de Clerk (MÉTODO OFICIAL) ---
clerk.wrap_app(
    app,
    publishable_key=os.environ.get("CLERK_PUBLISHABLE_KEY"),
    secret_key=os.environ.get("CLERK_SECRET_KEY"),
    register_user_state=True,
)