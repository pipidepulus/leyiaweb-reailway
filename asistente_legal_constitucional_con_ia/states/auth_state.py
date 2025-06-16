import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()


class AuthState(rx.State):
    """Manages user authentication and session status."""

    correct_username: str = os.getenv(
        "APP_USERNAME", "admin"
    )
    correct_password: str = os.getenv(
        "APP_PASSWORD", "password123"
    )
    in_session: bool = False
    login_attempts: int = 0
    error_message: str = ""

    @rx.event
    def login(self, form_data: dict):
        """Handle user login."""
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        if (
            username == self.correct_username
            and password == self.correct_password
        ):
            self.in_session = True
            self.error_message = ""
            self.login_attempts = 0
            return rx.redirect("/")
        else:
            self.in_session = False
            self.error_message = (
                "Usuario o contraseña incorrectos."
            )
            self.login_attempts += 1
            return rx.toast.error(self.error_message)

    @rx.event
    def logout(self):
        """Handle user logout."""
        self.in_session = False
        self.reset()
        return rx.redirect("/login")

    @rx.event
    def check_session(self):
        """Check if the user is in session, otherwise redirect to login."""
        if not self.in_session:
            return rx.redirect("/login")