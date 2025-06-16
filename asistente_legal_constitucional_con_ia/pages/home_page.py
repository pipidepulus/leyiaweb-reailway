import reflex as rx
from asistente_legal_constitucional_con_ia.components.sidebar import sidebar
import reflex_local_auth

@rx.page(route="/", title="Bienvenido")
@reflex_local_auth.require_login
def home_page():
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.image(
                src="/balanza.png",
                alt="Balanza de la Justicia",
                width="256px", 
                height="auto",
                margin_bottom="1rem"
            ),
            rx.el.h1(
                "Bienvenido al Asistente Legal Constitucional", 
                class_name="text-3xl font-bold mb-2"
            ),
            rx.el.p(
                "Sistema especializado en análisis de jurisprudencia, leyes, propuestas de leyes con ayuda de inteligencia artificial.", 
                class_name="text-lg text-gray-600 mb-4"
            ),
            rx.el.p(
                "Selecciona una opción del menú para comenzar.", 
                class_name="text-lg text-gray-700 font-bold"
            ),
            class_name="flex flex-col items-center justify-center w-full h-full text-center p-8"
        ),
        class_name="flex h-screen w-full bg-gray-50 dark:bg-gray-900",
    )
