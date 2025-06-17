import reflex as rx
import reflex_local_auth
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH, PADDING_TOP
from asistente_legal_constitucional_con_ia.states.auth_state import AuthState 

def login_error() -> rx.Component:
    """Render the login error message."""
    return rx.cond(
        AuthState.error_message != "",
        rx.callout(
            AuthState.error_message,
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def login_form_fields() -> rx.Component:
    """Render the login form fields."""
    return rx.vstack(
        rx.heading("Iniciar Sesión", size="7", margin_bottom="1em"),
        login_error(),
        rx.text("Nombre de usuario", margin_bottom="0.2em"),
        input_100w("username", placeholder="Tu nombre de usuario"),
        rx.text("Contraseña", margin_bottom="0.2em", margin_top="0.5em"),
        input_100w("password", type="password", placeholder="Tu contraseña"),
        rx.button("Entrar", width="100%", margin_top="1em"),
        rx.center(
            rx.link(
                "¿No tienes cuenta? Regístrate", 
                on_click=lambda: rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE),
                margin_top="0.5em"
            ),
            width="100%",
        ),
        min_width=MIN_WIDTH,
        align_items="stretch", # Para que los inputs y botones ocupen el ancho
        spacing="3" # Espaciado entre elementos del vstack
    )

def login_page_content() -> rx.Component:
    """Content for the login page."""
    return rx.card(login_form_fields())


def login_page() -> rx.Component:
    """The login page."""
    return rx.center(
        rx.cond(
            AuthState.is_hydrated,
            rx.form(
                login_page_content(),
                on_submit=AuthState.login,
            ),
            rx.chakra.spinner(size="lg"),
        ),
        padding_top=PADDING_TOP,
        min_height="85vh",
        width="100%",
    )
