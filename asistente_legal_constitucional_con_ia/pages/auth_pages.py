# asistente_legal_constitucional_con_ia/pages/auth_pages.py
"""Páginas de autenticación simples."""

import reflex as rx
from reflex_local_auth import LocalAuthState
from ..components.layout import main_layout


class AuthState(LocalAuthState):
    """Estado para manejo de autenticación."""
    
    # Variables para el formulario de login
    login_username: str = ""
    login_password: str = ""
    
    # Variables para el formulario de registro
    register_username: str = ""
    register_password: str = ""
    register_confirm_password: str = ""
    
    # Variables de estado
    loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    @rx.event
    async def handle_login(self, form_data: dict):
        """Maneja el proceso de login."""
        self.loading = True
        self.error_message = ""
        
        try:
            username = form_data.get("username", "").strip()
            password = form_data.get("password", "").strip()
            
            if not username or not password:
                self.error_message = "Usuario y contraseña son requeridos."
                return
            
            # Intentar login usando reflex_local_auth
            result = await self.login(username, password)
            
            if result:
                self.success_message = "¡Login exitoso!"
                return rx.redirect("/asistente")
            else:
                self.error_message = "Usuario o contraseña incorrectos."
                
        except Exception as e:
            self.error_message = f"Error en login: {str(e)}"
        finally:
            self.loading = False
    
    @rx.event
    async def handle_register(self, form_data: dict):
        """Maneja el proceso de registro."""
        self.loading = True
        self.error_message = ""
        
        try:
            username = form_data.get("username", "").strip()
            password = form_data.get("password", "").strip()
            confirm_password = form_data.get("confirm_password", "").strip()
            
            if not username or not password:
                self.error_message = "Usuario y contraseña son requeridos."
                return
            
            if password != confirm_password:
                self.error_message = "Las contraseñas no coinciden."
                return
            
            if len(password) < 6:
                self.error_message = "La contraseña debe tener al menos 6 caracteres."
                return
            
            # Intentar registro usando reflex_local_auth
            result = await self.register(username, password)
            
            if result:
                self.success_message = "¡Registro exitoso! Puedes iniciar sesión ahora."
                return rx.redirect("/login")
            else:
                self.error_message = "Error en el registro. El usuario puede ya existir."
                
        except Exception as e:
            self.error_message = f"Error en registro: {str(e)}"
        finally:
            self.loading = False
    
    @rx.event
    async def handle_logout(self):
        """Maneja el proceso de logout."""
        await self.logout()
        return rx.redirect("/")


def login_page() -> rx.Component:
    """Página de inicio de sesión."""
    content = rx.center(
        rx.card(
            rx.vstack(
                rx.heading("🔐 Iniciar Sesión", size="6", text_align="center", margin_bottom="2rem"),
                
                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="Usuario",
                            name="username",
                            type="text",
                            required=True,
                            width="100%"
                        ),
                        rx.input(
                            placeholder="Contraseña",
                            name="password",
                            type="password",
                            required=True,
                            width="100%"
                        ),
                        
                        rx.button(
                            "Iniciar Sesión",
                            type="submit",
                            loading=AuthState.loading,
                            width="100%",
                            size="3"
                        ),
                        
                        spacing="4",
                        width="100%"
                    ),
                    on_submit=AuthState.handle_login,
                    width="100%"
                ),
                
                rx.divider(margin_y="1rem"),
                
                rx.text("¿No tienes cuenta?", size="2", color="gray"),
                rx.link(
                    "Crear cuenta",
                    href="/register",
                    size="2",
                    color="blue"
                ),
                
                # Mensajes de error/éxito
                rx.cond(
                    AuthState.error_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert")),
                        rx.callout.text(AuthState.error_message),
                        color_scheme="red",
                        margin_top="1rem"
                    ),
                    rx.fragment()
                ),
                
                rx.cond(
                    AuthState.success_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("check")),
                        rx.callout.text(AuthState.success_message),
                        color_scheme="green",
                        margin_top="1rem"
                    ),
                    rx.fragment()
                ),
                
                spacing="3",
                align="center",
                width="100%"
            ),
            max_width="400px",
            padding="2rem"
        ),
        height="100vh"
    )
    
    return main_layout(content)


def register_page() -> rx.Component:
    """Página de registro."""
    content = rx.center(
        rx.card(
            rx.vstack(
                rx.heading("📝 Crear Cuenta", size="6", text_align="center", margin_bottom="2rem"),
                
                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="Usuario",
                            name="username",
                            type="text",
                            required=True,
                            width="100%"
                        ),
                        rx.input(
                            placeholder="Contraseña",
                            name="password",
                            type="password",
                            required=True,
                            width="100%"
                        ),
                        rx.input(
                            placeholder="Confirmar Contraseña",
                            name="confirm_password",
                            type="password",
                            required=True,
                            width="100%"
                        ),
                        
                        rx.button(
                            "Crear Cuenta",
                            type="submit",
                            loading=AuthState.loading,
                            width="100%",
                            size="3",
                            color_scheme="green"
                        ),
                        
                        spacing="4",
                        width="100%"
                    ),
                    on_submit=AuthState.handle_register,
                    width="100%"
                ),
                
                rx.divider(margin_y="1rem"),
                
                rx.text("¿Ya tienes cuenta?", size="2", color="gray"),
                rx.link(
                    "Iniciar sesión",
                    href="/login",
                    size="2",
                    color="blue"
                ),
                
                # Mensajes de error/éxito
                rx.cond(
                    AuthState.error_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert")),
                        rx.callout.text(AuthState.error_message),
                        color_scheme="red",
                        margin_top="1rem"
                    ),
                    rx.fragment()
                ),
                
                rx.cond(
                    AuthState.success_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("check")),
                        rx.callout.text(AuthState.success_message),
                        color_scheme="green",
                        margin_top="1rem"
                    ),
                    rx.fragment()
                ),
                
                spacing="3",
                align="center",
                width="100%"
            ),
            max_width="400px",
            padding="2rem"
        ),
        height="100vh"
    )
    
    return main_layout(content)


def logout_page() -> rx.Component:
    """Página de logout - redirige automáticamente."""
    return rx.fragment(
        rx.script("window.location.href = '/'"),
        on_mount=AuthState.handle_logout
    )
