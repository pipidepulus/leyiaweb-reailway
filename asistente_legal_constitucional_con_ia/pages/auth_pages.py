import reflex as rx

class AuthState(rx.State):
    pass  # Usaremos el sistema de auth de Reflex, no lógica personalizada

def login_page() -> rx.Component:
    return rx.auth.login(
        title="Iniciar Sesión",
        description="Accede con tu usuario registrado.",
        redirect_success="/",
        redirect_register="/register",
    )

def register_page() -> rx.Component:
    return rx.auth.register(
        title="Registro de Usuario",
        description="Crea una cuenta para acceder al asistente.",
        redirect_success="/",
        redirect_login="/login",
    )
