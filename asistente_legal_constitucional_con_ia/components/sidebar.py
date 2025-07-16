"""Barra de navegación principal que incluye un panel contextual inteligente."""
import reflex as rx
from .asistente_sidebar import asistente_sidebar
from ..states.app_state import AppState
from ..states.chat_state import ChatState

class SidebarState(rx.State):
    """Estado para controlar la visibilidad de los componentes de la barra lateral."""
    @rx.var
    def is_on_asistente_page(self) -> bool:
        """Comprueba si la ruta actual es la página del asistente."""
        return self.router.page.path == "/asistente"

def sidebar(is_in_drawer: bool = False) -> rx.Component:
    """La barra de navegación principal de la aplicación."""
    link_click_handler = AppState.toggle_drawer if is_in_drawer else None
    return rx.vstack(
        # --- SECCIÓN SUPERIOR ---
        rx.vstack(
            rx.hstack(
                rx.image(src="/balanza.png", height="2em"),
                rx.heading("Asistente Legal", size="6", color="blue", weight="bold"),
                width="100%",
            ),
            rx.divider(),
            rx.link("Nuevo Análisis", href="/", style={"width": "100%", "color":"blue", "font-weight": "bold"},
                     on_click=[handler for handler in [link_click_handler, ChatState.cleanup_session_files] if handler is not None]
            ),
            rx.vstack(
                rx.link("Asistente Constitucional", href="/asistente", width="100%", style={"color":"blue", "font-weight": "bold"}, on_click=link_click_handler),
                rx.link("Explorar Proyectos de Ley", href="/proyectos", width="100%", style={"color":"blue", "font-weight": "bold"}, on_click=link_click_handler),
                rx.link("Prompts", href="/prompts", width="100%", style={"color":"blue", "font-weight": "bold"}, on_click=link_click_handler),
                spacing="5",
                width="100%",
                align_items="start",
            ),
            spacing="5",
            width="100%",
            align_items="start",
        ),
        
        # --- PANEL CONTEXTUAL ---
        rx.cond(
            SidebarState.is_on_asistente_page,
            asistente_sidebar(),
            rx.fragment(),
        ),

        rx.spacer(),

        # --- ESTILOS DEL CONTENEDOR PRINCIPAL ---
        spacing="5",
        height="100%",
        width="100%",
        align_items="stretch"
    )