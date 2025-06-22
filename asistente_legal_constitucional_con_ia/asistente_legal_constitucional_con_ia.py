# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""
Archivo principal de la aplicación.
"""
import os
import reflex as rx
from dotenv import load_dotenv
import reflex_clerk_api as clerk

from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page
from .pages.asistente_page import asistente_page
from .components.layout import main_layout

load_dotenv()

# --- DEFINICIÓN DE LA APP (Forma estándar) ---
app = rx.App()


# --- Definición de la Página Principal (Index) ---
@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
    """La página de inicio, envuelta en el layout principal."""
    content = rx.el.div(
        # Muestra el contenido principal solo si el usuario ha iniciado sesión
        clerk.signed_in(
            rx.el.div(
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
            )
        ),
        # Muestra un mensaje de bienvenida y un botón de inicio de sesión si no está autenticado
        clerk.signed_out(
            rx.el.div(
                rx.el.h1("Bienvenido", class_name="text-3xl font-bold mb-2"),
                rx.el.p(
                    "Por favor, inicia sesión para acceder al asistente.",
                    class_name="text-lg text-gray-600 mb-4",
                ),
                clerk.sign_in_button(rx.button("Iniciar Sesión")),
            )
        ),
        class_name="flex flex-col items-center justify-center w-full h-full text-center",
    )
    return main_layout(content)


# --- Añadimos todas las páginas a la aplicación ---
app.add_page(asistente_page)
app.add_page(proyectos_page)
app.add_page(prompts_page)


# --- AÑADE ESTO PARA DEPURAR ---
publishable_key_from_env = os.getenv("CLERK_PUBLISHABLE_KEY")
secret_key_from_env = os.getenv("CLERK_SECRET_KEY")

print("--- CLAVES DE CLERK (DEPURACIÓN) ---")
print(f"Publishable Key leída: {publishable_key_from_env}")
print(f"Secret Key leída: {secret_key_from_env}")
print("---------------------------------")
# ------------------------------------


# --- Configuración de Clerk ---
# Envolvemos la aplicación completa con el proveedor de Clerk para gestionar la autenticación.
# Esto asegura que el contexto de autenticación esté disponible en todas las páginas.
app = clerk.wrap_app(
    app,
    publishable_key=os.getenv("CLERK_PUBLISHABLE_KEY"),
    secret_key=os.getenv("CLERK_SECRET_KEY"),
)

# --- Añadimos las páginas de autenticación de Clerk ---
clerk.add_sign_in_page(app)
clerk.add_sign_up_page(app)

