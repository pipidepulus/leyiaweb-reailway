# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""
Archivo principal de la aplicación, refactorizado para integrar Clerk
de la forma recomendada por la documentación oficial.
"""

# --- Importaciones ---
import os
import reflex as rx
import reflex_clerk_api as clerk
from dotenv import load_dotenv

# Importaciones de tus páginas y el layout principal
from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page
from .pages.asistente_page import asistente_page
from .components.layout import main_layout

# --- Carga de Entorno y Definición de la App ---
# Carga las variables de entorno desde el archivo .env (para desarrollo local)
load_dotenv()

# Se define la aplicación UNA SOLA VEZ
app = rx.App()


# --- Definición de la Página Principal (Index) ---
@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
    """La página de inicio, envuelta en el layout principal."""
    # El contenido visual de tu página de inicio
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
    # Se envuelve el contenido en el layout para mantener la consistencia visual
    return main_layout(content)


# --- Añadimos todas las páginas a la aplicación ---
app.add_page(asistente_page)
app.add_page(proyectos_page)
app.add_page(prompts_page)

# Añadimos las páginas de autenticación de Clerk
clerk.add_sign_in_page(app)
clerk.add_sign_up_page(app)


# --- Envolvemos la App con el Provider de Clerk (EL PASO CLAVE) ---
# Este es el método recomendado por la documentación para inyectar la
# autenticación a nivel global en toda la aplicación.
# Se encarga de manejar el estado y las dependencias de JavaScript.
clerk.wrap_app(
    app,
    # Carga las claves de las variables de entorno
    publishable_key=os.environ.get("CLERK_PUBLISHABLE_KEY"),
    secret_key=os.environ.get("CLERK_SECRET_KEY"),
    # Habilita el estado rx.ClerkUser para acceder a la info del usuario
    register_user_state=True,
)