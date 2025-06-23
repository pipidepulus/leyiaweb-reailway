# ruta: asistente_legal_constitucional_con_ia/pages/login_page.py
"""Página de inicio de sesión con el componente de Clerk."""
import reflex as rx
import reflex_clerk_api as clerk

from ..components.layout import main_layout

@rx.page(route="/login", title="Login")
def login_page() -> rx.Component:
    """
    Página que muestra los componentes de inicio de sesión y registro de Clerk.
    Utiliza <clerk.sign_in_button> y <clerk.sign_up_button>.
    """
    content = rx.el.div(
        rx.el.p(
            "Haz clic en los botones a continuación para iniciar sesión o registrarte.",
            class_name="text-lg text-gray-600 mb-4",
        ),
        clerk.sign_in_button(),
        clerk.sign_up_button(),
        class_name="flex flex-col items-center justify-center w-full h-full text-center",
    )
    return main_layout(content)
