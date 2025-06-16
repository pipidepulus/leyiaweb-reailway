import reflex as rx
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState
from asistente_legal_constitucional_con_ia.states.auth_user_state import MyLocalAuthState


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
            class_name="px-2 py-2",  # Quitado flex-1, añadido padding vertical
        ),
        rx.el.div(flex_grow=1),  # Espaciador añadido
        # Contenedor para todos los elementos inferiores, empujado hacia abajo
        rx.el.div(
            # Login/Logout y Modo Claro/Oscuro
            rx.el.div(
                rx.el.ul(
                    rx.el.li(
                        rx.link("Login/Logout", href="/login", class_name="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-800 dark:text-gray-200 font-semibold"),
                        class_name="my-1"  # Espaciado vertical
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
                        class_name="my-1"  # Espaciado vertical
                    ),
                ),
                class_name="px-2 pt-2" # Padding arriba para separar del borde si es necesario
            ),
            # Información del usuario autenticado
            rx.el.div(
                rx.cond(
                    MyLocalAuthState.is_authenticated,
                    rx.el.div(
                        rx.el.p(
                            rx.cond(
                                MyLocalAuthState.authenticated_user_info,
                                rx.fragment(
                                    rx.el.span("Correo: ", class_name="font-semibold"),
                                    rx.el.span(MyLocalAuthState.authenticated_user_info.email, class_name="text-sm break-all"),
                                ),
                                rx.el.span("Correo no disponible", class_name="text-sm text-gray-400"),
                            ),
                            class_name="p-4 border-t text-gray-700 dark:text-gray-200", # Mantenemos p-4 y border-t aquí
                        ),
                    ),
                ),
            ),
        ),
        class_name="w-80 bg-white dark:bg-gray-900 border-r flex flex-col h-full",
    )