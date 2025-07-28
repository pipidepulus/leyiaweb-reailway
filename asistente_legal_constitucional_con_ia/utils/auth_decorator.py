# asistente_legal_constitucional_con_ia/utils/auth_decorator.py
"""Decorador personalizado para requerir autenticación."""

import reflex as rx
from functools import wraps
import reflex_local_auth


def require_login(func):
    """
    Decorador que requiere que el usuario esté autenticado.
    Si no está autenticado, redirige a la página de login.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Usar el decorador oficial de reflex_local_auth
        return reflex_local_auth.require_login(func)(*args, **kwargs)
    
    return wrapper
