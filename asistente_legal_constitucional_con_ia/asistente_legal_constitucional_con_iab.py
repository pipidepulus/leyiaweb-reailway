"""Archivo principal de la aplicación, ahora usando un layout centralizado."""

from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page
from .pages.asistente_page import asistente_page
import reflex as rx
import reflex_clerk_api as clerk
from dotenv import load_dotenv
from .components.layout import main_layout  # Importamos nuestro nuevo layout
from .test_page import test_page

load_dotenv()

app = rx.App()


@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
#    """La página de inicio, ahora envuelta en el layout principal."""
#    # Contenido específico de la página de inicio
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
    # Envolvemos el contenido en el layout principal
    return main_layout(content)


# Añadimos las otras páginas. El layout se aplicará dentro de cada una.
app.add_page(asistente_page)
app.add_page(proyectos_page)
app.add_page(prompts_page)

# Añadimos las páginas de Clerk necesarias para las rutas /sign-in y /sign-up
clerk.add_sign_in_page(app)
clerk.add_sign_up_page(app)

# --- AÑADE LA NUEVA PÁGINA DE PRUEBA ---
app = rx.App(
   #theme=rx.theme(
    #    appearance="light", has_background=True, radius="large", accent_color="teal"
    #),
    #plugins=[rx.plugins.TailwindV3Plugin()], # Mantenemos esto por ahora
)

# Registra SÓLO la página de prueba en la ruta principal
#app.add_page(test_page, route="/") 

#app.compile()