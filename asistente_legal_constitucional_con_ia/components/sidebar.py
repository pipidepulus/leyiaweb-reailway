import reflex as rx
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState
from asistente_legal_constitucional_con_ia.states.auth_state import AuthState # Importar AuthState
import reflex_local_auth # Importar reflex_local_auth


def project_explorer() -> rx.Component:
    columns = [
        {"key": "Número", "title": "Número"},
        {"key": "Título", "title": "Título"},
        {"key": "Estado", "title": "Estado"},
        {"key": "Enlace", "title": "Enlace"},
    ]
    return rx.el.div(
        rx.el.h3(
            "Explorar Proyectos de Ley",
            class_name="font-semibold text-gray-700",
        ),
        rx.el.p(
            "Consulta últimas propuestas (Cámara).",
            class_name="text-xs text-gray-500",
        ),
        rx.el.button(
            "Consultar Propuestas",
            on_click=ChatState.scrape_proyectos,
            class_name="w-full mt-2 py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-md shadow-sm",
        ),
        rx.el.div(
            rx.data_table(
                data=ChatState.proyectos_data,
                columns=columns,
                pagination=True,
                search=True,
                sort=True,
            ),
            rx.cond(
                ChatState.proyectos_data.length() == 0,
                rx.el.p(
                    "No hay proyectos disponibles.",
                    class_name="text-gray-400 text-center py-4",
                ),
            ),
            class_name="mt-4 max-h-64 overflow-y-auto",
        ),
        class_name="space-y-2",
    )


def sidebar() -> rx.Component:
    """Sidebar de navegación con links y logout/reflex auth."""
    return rx.el.aside(
        rx.el.div(
            rx.el.h2(
                "⚖️ Asistente Legal Constitucional",
                class_name="text-xl font-bold",
            ),
            class_name="flex items-center p-4 border-b",
        ),
        rx.el.nav(
            rx.el.ul(
                rx.el.li(
                    rx.link("Asistente Constitucional", href="/asistente", class_name="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold"),
                    class_name="my-1"  # Espaciado vertical
                ),
                rx.el.li(
                    rx.link("Explorar Proyectos de Ley", href="/proyectos", class_name="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold"),
                    class_name="my-1"  # Espaciado vertical
                ),
                rx.el.li(
                    rx.link("Prompts", href="/prompts", class_name="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold"),
                    class_name="my-1"  # Espaciado vertical
                ),
            ),
            class_name="px-2 py-2",
        ),
        rx.el.div(flex_grow=1),  # Espaciador añadido
        # Contenedor para todos los elementos inferiores, empujado hacia abajo
        rx.el.div(
            # Login/Logout y Modo Claro/Oscuro
            rx.el.div(
                rx.el.ul(
                    # Conditional rendering for Login/Logout button and user info
                    rx.cond(
                        AuthState.is_authenticated,
                        # If authenticated, show user info and Logout button
                        rx.el.li(
                            rx.vstack(
                                rx.text(
                                    rx.el.span("Usuario: ", font_weight="bold"),
                                    AuthState.authenticated_user.username,
                                    class_name="text-sm px-4 py-2 text-gray-800 dark:text-gray-200"
                                ),
                                rx.button(
                                    "Cerrar Sesión",
                                    on_click=AuthState.logout,
                                    class_name="w-full text-left py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold"
                                ),
                                align_items="left", 
                                width="100%"
                            ),
                            class_name="my-1"
                        ),
                        # If not authenticated, show Login and Register buttons
                        rx.vstack(
                            rx.el.li(
                                rx.button(
                                    "Iniciar Sesión",
                                    on_click=lambda: rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE),
                                    class_name="w-full text-left py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold"
                                ),
                                class_name="my-1 w-full"
                            ),
                            rx.el.li(
                                rx.button(
                                    "Crear Cuenta",
                                    on_click=lambda: rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE),
                                    class_name="w-full text-left py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold"
                                ),
                                class_name="my-1 w-full"
                            ),
                            width="100%",
                            align_items="left"
                        )
                    ),
                    rx.el.li(
                        rx.button(
                            rx.cond(
                                rx.color_mode == "light",
                                "🌙 Modo Oscuro",
                                "☀️ Modo Claro",
                            ),
                            on_click=rx.toggle_color_mode,
                            class_name="block w-full text-left py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold",
                        ),
                        class_name="my-1"
                    ),
                ),
                class_name="px-2 pt-2"
            ),
        ),
        class_name="w-72 bg-gray-50 dark:bg-gray-800 border-r flex flex-col h-full shadow-lg z-20",
    )