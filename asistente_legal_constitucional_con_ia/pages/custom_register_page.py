import reflex as rx
import reflex_local_auth
from asistente_legal_constitucional_con_ia.states.register_state import MyRegisterState
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH, PADDING_TOP

def register_error() -> rx.Component:
    return rx.cond(
        MyRegisterState.error_message != "",
        rx.callout(
            MyRegisterState.error_message,
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def register_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.heading("Crear una cuenta", size="7"),
            register_error(),
            rx.text("Nombre de usuario"),
            input_100w("username"),
            rx.text("Email"),
            input_100w("email"),
            rx.text("Contraseña"),
            input_100w("password", type="password"),
            rx.text("Confirmar contraseña"),
            input_100w("confirm_password", type="password"),
            rx.button("Registrarse", width="100%"),
            rx.center(
                rx.link("Iniciar sesión", on_click=lambda: rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)),
                width="100%",
            ),
            min_width=MIN_WIDTH,
        ),
        on_submit=MyRegisterState.handle_registration_email,
    )

def register_page() -> rx.Component:
    return rx.center(
        rx.cond(
            MyRegisterState.success,
            rx.vstack(
                rx.text("¡Registro exitoso!"),
            ),
            rx.card(register_form()),
        ),
        padding_top=PADDING_TOP,
    )
