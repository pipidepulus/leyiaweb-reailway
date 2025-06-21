# ruta: components/layout.py
"""Layout principal de la aplicación."""
import reflex as rx
import reflex_clerk_api as clerk
import os
from .sidebar import sidebar

def main_layout(content: rx.Component) -> rx.Component:
    """El layout principal que envuelve todas las páginas."""
    return clerk.clerk_provider(
        rx.box(
            rx.hstack(
                sidebar(),
                rx.container(
                    content,
                    padding_top="2em",
                    max_width="100%",
                    flex_grow=1,
                ),
                align="start",
                height="100vh",
                width="100%",
            ),
            height="100vh",
            width="100%",
        ),
        # Volvemos a activar la localización
        locale="es-ES",
        secret_key=os.getenv("CLERK_SECRET_KEY"),
        publishable_key=os.getenv("CLERK_PUBLISHABLE_KEY"),
        register_user_state=True,
    )