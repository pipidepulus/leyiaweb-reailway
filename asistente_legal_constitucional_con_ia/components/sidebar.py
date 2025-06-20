"""Barra de navegación principal que incluye un panel contextual inteligente."""

import reflex as rx
import reflex_clerk_api as clerk
from .asistente_sidebar import asistente_sidebar


class SidebarState(rx.State):
    """Estado para controlar la visibilidad de los componentes de la barra lateral."""

    @rx.var
    def is_on_asistente_page(self) -> bool:
        """Comprueba si la ruta actual es la página del asistente."""
        # El panel de archivos solo se mostrará en la ruta /asistente.
        return self.router.page.path == "/asistente"


def sidebar() -> rx.Component:
    """La barra de navegación principal de la aplicación."""
    return rx.el.div(
        rx.vstack(
            # Sección superior con logo y enlaces de navegación
            rx.vstack(
                rx.hstack(
                    rx.image(src="/balanza.png", height="2em"),
                    rx.heading("Asistente Legal", size="6"),
                    width="100%",
                ),
                rx.divider(),
                rx.link("Inicio", href="/", style={"width": "100%"}),
                rx.link("Asistente Constitucional", href="/asistente", style={"width": "100%"}),
                rx.link("Explorar Proyectos de Ley", href="/proyectos", style={"width": "100%"}),
                rx.link("Prompts", href="/prompts", style={"width": "100%"}),
                spacing="5",
                width="100%",
                align_items="start",
            ),
            
            # ¡LÓGICA CORRECTA! Panel contextual que solo aparece en la página del asistente.
            # Ocupa el espacio directamente debajo de los enlaces.
            rx.cond(
                SidebarState.is_on_asistente_page,
                asistente_sidebar(),
                rx.fragment(),  # No renderiza nada en otras páginas
            ),

            rx.spacer(),  # Un solo spacer para empujar el botón de usuario al fondo

            # Sección inferior con la información y botón del usuario
            rx.vstack(
                rx.divider(),
                clerk.user_button(after_sign_out_url="/"),
                width="100%",
                padding_bottom="1em",  # Añade un poco de espacio en la parte inferior
            ),
            spacing="5",
            width="100%",
            height="100vh",
            padding="1em",
        ),
        class_name="w-[350px] border-r bg-white shadow-md",
    )