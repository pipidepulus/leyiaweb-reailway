import reflex as rx
import reflex_local_auth
from asistente_legal_constitucional_con_ia.components.asistente_sidebar import asistente_sidebar # DESCOMENTADO
from asistente_legal_constitucional_con_ia.components.chat import chat

@rx.page(route="/asistente", title="Asistente Constitucional")
@reflex_local_auth.require_login
def asistente_page():
    return rx.el.div(
        asistente_sidebar(), # DESCOMENTADO
        rx.el.div(
            chat(),
            class_name="flex-1 h-full flex flex-col p-4 overflow-auto" # Ajustado para sidebar
        ),
        class_name="flex h-screen w-full font-['Inter'] bg-gray-50 dark:bg-gray-900",
    )
