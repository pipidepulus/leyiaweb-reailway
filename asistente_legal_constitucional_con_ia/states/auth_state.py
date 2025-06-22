# ruta: asistente_legal_constitucional_con_ia/states/auth_state.py
"""Estado para gestionar la autenticación con Clerk."""
import reflex as rx
import reflex_clerk as clerk

class AuthState(rx.State):
    """
    Estado para gestionar la autenticación.
    Delega la lógica a reflex_clerk.
    """
    is_authenticated: bool = clerk.is_authenticated
    user: dict = clerk.user
    user_id: str = clerk.user_id
