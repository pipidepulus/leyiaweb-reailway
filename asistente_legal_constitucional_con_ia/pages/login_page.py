import reflex as rx
from reflex_local_auth import require_login
from asistente_legal_constitucional_con_ia.states.auth_state import AuthState
from asistente_legal_constitucional_con_ia.components.sidebar import sidebar


@rx.page(route="/login", title="Login")
@require_login
def login_page() -> rx.Component:
    """The UI for the login page."""
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.h1("Login", class_name="text-2xl font-bold mb-4"),
            rx.el.p(
                "Aquí irá el formulario de login (placeholder).",
                class_name="text-lg text-gray-600",
            ),
            class_name="flex flex-col items-center justify-center h-full w-full",
        ),
        class_name="flex h-screen font-['Inter'] bg-gray-50 dark:bg-gray-900",
    )

    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "⚖️ Asistente Legal Constitucional",
                class_name="text-2xl font-bold text-gray-800",
            ),
            rx.el.p(
                "Acceso Requerido",
                class_name="text-gray-600",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "Usuario",
                        class_name="text-sm font-medium",
                    ),
                    rx.el.input(
                        name="username",
                        type="text",
                        placeholder="admin",
                        required=True,
                        class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    class_name="w-full",
                ),
                rx.el.div(
                    rx.el.label(
                        "Contraseña",
                        class_name="text-sm font-medium",
                    ),
                    rx.el.input(
                        name="password",
                        type="password",
                        placeholder="password123",
                        required=True,
                        class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    class_name="w-full",
                ),
                rx.el.button(
                    "Iniciar Sesión",
                    type="submit",
                    class_name="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-md shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                ),
                on_submit=AuthState.login,
                class_name="space-y-4",
            ),
            rx.cond(
                AuthState.error_message != "",
                rx.el.p(
                    AuthState.error_message,
                    class_name="text-red-500 text-sm mt-2",
                ),
            ),
            class_name="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg border",
        ),
        class_name="flex items-center justify-center min-h-screen bg-gray-50 font-['Inter']",
    )