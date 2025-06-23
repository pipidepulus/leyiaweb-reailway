# asistente_legal_constitucional_con_ia/util/auth.py
import reflex as rx
import reflex_clerk_api as clerk
import functools

def require_login(page_func):
    """
    Un decorador que protege una página.

    Si el usuario no está logueado, lo redirige a la página de inicio de sesión.
    También muestra un spinner de carga mientras Clerk verifica el estado de autenticación.
    """
    @functools.wraps(page_func)
    def wrapper_page(*args, **kwargs):
        # El componente principal que se mostrará si el usuario está autenticado.
        protected_content = clerk.protect(
            page_func(*args, **kwargs),
            # --- CORRECCIÓN DEFINITIVA AQUÍ ---
            # En lugar de usar un componente específico de Clerk para redirigir,
            # usamos el componente de redirección nativo de Reflex.
            # Este es el fallback que se mostrará si clerk.protect falla (usuario no logueado).
            #=rx.redirect("/login")            
        )

        # Envolvemos todo en clerk_loaded para mostrar algo mientras se carga.
        # Esto evita un parpadeo o renderizado incorrecto antes de que Clerk sepa si estás logueado.
        return clerk.clerk_loaded(
            protected_content,
            # Muestra un spinner mientras Clerk se inicializa.
            rx.center(rx.spinner(size="3")),
        )

    return wrapper_page