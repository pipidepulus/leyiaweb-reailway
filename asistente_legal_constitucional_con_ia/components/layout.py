# ruta: components/layout.py
"""
Layout principal de la aplicación.
NO incluye el ClerkProvider, ya que se inyecta globalmente
con clerk.wrap_app() en el archivo principal.
"""
import reflex as rx
import reflex_clerk_api as clerk

def navbar() -> rx.Component:
    """La barra de navegación que cambia según el estado de autenticación."""
    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.image(src="/balanza.png", height="2em"),
                    rx.heading("Asistente Legal", size="6"),
                ),
                href="/",
            ),
            rx.spacer(),
            # Estos componentes funcionan porque la app está envuelta.
            clerk.signed_in(
                rx.hstack(
                    rx.link("Asistente", href="/asistente-page"),
                    rx.link("Proyectos", href="/proyectos-page"),
                    rx.link("Prompts", href="/prompts-page"),
                    clerk.user_button(after_sign_out_url="/"),
                    spacing="4",
                    align_items="center",
                )
            ),
            clerk.signed_out(
                rx.hstack(
                    clerk.sign_in_button(
                        rx.button("Iniciar Sesión", color_scheme="blue")
                    ),
                    clerk.sign_up_button(
                        rx.button("Registrarse", variant="outline")
                    ),
                    spacing="4",
                    align_items="center",
                )
            ),
            justify="space-between",
            align_items="center",
            width="100%",
            padding_x="1rem",
        ),
        position="fixed",
        top="0px",
        left="0px",
        right="0px",
        z_index="10",
        padding_y="0.5rem",
        background_color="rgba(255, 255, 255, 0.8)",
        backdrop_filter="saturate(180%) blur(5px)",
        box_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    )

def main_layout(content: rx.Component) -> rx.Component:
    """El layout principal que envuelve el contenido de la página."""
    return rx.box(
        navbar(),
        rx.container(
            content,
            padding_top="6rem",
            max_w="container.xl",
        ),
    )