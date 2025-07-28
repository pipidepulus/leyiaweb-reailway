"""Barra de navegación principal que incluye un panel contextual inteligente."""
import reflex as rx
from .asistente_sidebar import asistente_sidebar
from ..states.app_state import AppState
from ..states.chat_state import ChatState
import reflex_local_auth

class SidebarState(reflex_local_auth.LocalAuthState):
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
                # Enlaces principales - TODOS requieren autenticación ahora
                rx.cond(
                    SidebarState.is_authenticated,
                    rx.vstack(
                        rx.link("🤖 Asistente Constitucional", href="/asistente", width="100%", style={"color":"blue", "font-weight": "bold"}, on_click=link_click_handler),
                        rx.link("📋 Explorar Proyectos de Ley", href="/proyectos", width="100%", style={"color":"blue", "font-weight": "bold"}, on_click=link_click_handler),
                        rx.link("📚 Biblioteca de Prompts", href="/prompts", width="100%", style={"color":"blue", "font-weight": "bold"}, on_click=link_click_handler),
                        
                        rx.divider(margin_y="1rem"),
                        
                        rx.text("Herramientas Avanzadas", size="2", weight="bold", color="gray"),
                        rx.link("📝 Mis Notebooks", href="/notebooks", width="100%", style={"color":"green", "font-weight": "bold"}, on_click=link_click_handler),
                        rx.link("🎤 Transcripción de Audio", href="/transcription", width="100%", style={"color":"green", "font-weight": "bold"}, on_click=link_click_handler),
                        
                        rx.divider(margin_y="1rem"),
                        
                        # Información del usuario
                        rx.vstack(
                            rx.text(f"👤 Usuario: {SidebarState.authenticated_user.username}", size="2", color="gray"),
                            rx.button(
                                "🚪 Cerrar Sesión", 
                                width="100%", 
                                style={"color":"red", "font-weight": "bold"}, 
                                on_click=reflex_local_auth.LocalAuthState.do_logout,
                                variant="ghost"
                            ),
                            spacing="2",
                            width="100%",
                            align_items="start",
                        ),
                        
                        spacing="3",
                        width="100%",
                        align_items="start",
                    ),
                    # Estado no autenticado - solo mostrar opciones de login
                    rx.vstack(
                        rx.callout.root(
                            rx.callout.icon(rx.icon("lock")),
                            rx.callout.text("🔐 Acceso Restringido"),
                            color_scheme="blue",
                            margin_bottom="1rem"
                        ),
                        
                        rx.text("Esta aplicación requiere autenticación para proteger los recursos de IA.", 
                               size="2", color="gray", text_align="center", margin_bottom="1rem"),
                        
                        rx.vstack(
                            rx.text("Servicios Disponibles:", size="2", weight="bold", color="blue"),
                            rx.text("• 🤖 Asistente Legal con IA", size="1", color="gray"),
                            rx.text("• 📋 Análisis de Proyectos", size="1", color="gray"),
                            rx.text("• 📚 Biblioteca de Prompts", size="1", color="gray"),
                            rx.text("• 📝 Notebooks Personales", size="1", color="gray"),
                            rx.text("• 🎤 Transcripción de Audio", size="1", color="gray"),
                            spacing="2",
                            width="100%",
                            align_items="start",
                            margin_bottom="1rem"
                        ),
                        
                        rx.vstack(
                            rx.link(
                                rx.button(
                                    "🔐 Iniciar Sesión",
                                    width="100%",
                                    size="3",
                                    color_scheme="blue"
                                ),
                                href=reflex_local_auth.routes.LOGIN_ROUTE,
                                width="100%",
                                on_click=link_click_handler
                            ),
                            rx.link(
                                rx.button(
                                    "📝 Crear Cuenta",
                                    width="100%",
                                    size="3",
                                    variant="outline",
                                    color_scheme="green"
                                ),
                                href=reflex_local_auth.routes.REGISTER_ROUTE, 
                                width="100%",
                                on_click=link_click_handler
                            ),
                            spacing="3",
                            width="100%"
                        ),
                        
                        spacing="3",
                        width="100%",
                        align_items="start",
                    )
                ),
                
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