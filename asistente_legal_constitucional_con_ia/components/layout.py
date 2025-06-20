"""Layout principal que ahora crea un diseño de 2 columnas."""

import reflex as rx
import reflex_clerk_api as clerk
import os
from .sidebar import sidebar


def main_layout(child: rx.Component) -> rx.Component:
    """El layout principal que envuelve toda la aplicación."""
    return clerk.clerk_provider(
        clerk.clerk_loading(
            rx.center(rx.spinner(size="3"), width="100vw", height="100vh")
        ),
        clerk.clerk_loaded(
            clerk.signed_in(
                rx.el.div(
                    sidebar(),
                    rx.el.main(
                        child,  # Aquí se renderizará el contenido de la página
                        class_name="flex-1 h-full overflow-y-auto",
                    ),
                    class_name="flex h-screen w-full",
                )
            ),
            clerk.signed_out(
                rx.center(
                    clerk.sign_in(),
                    width="100vw", height="100vh",
                    class_name="bg-gray-50",
                )
            ),
        ),
        publishable_key=os.environ.get("CLERK_PUBLISHABLE_KEY", ""),
        secret_key=os.environ.get("CLERK_SECRET_KEY", ""),
        register_user_state=True,
        locale="es-ES",
        jwt_leeway=15,
    )