import reflex as rx
import os
from dotenv import load_dotenv
import reflex_local_auth
from reflex_local_auth.auth_session import LocalAuthSession # Import LocalAuthSession
from sqlmodel import select # Import select

load_dotenv()


class AuthState(reflex_local_auth.LoginState):  # Inherit from LoginState
    """Manages user authentication and session status using reflex-local-auth."""

    @rx.event
    def login(self, form_data: dict):
        """Handle user login using reflex-local-auth's logic."""
        # The super().handle_login method will:
        # 1. Validate credentials against the database (User model).
        # 2. Set self.is_authenticated.
        # 3. Set self.error_message if login fails.
        # 4. Redirect on successful login.
        # 5. Return a toast on error.
        return super().handle_login(form_data)

    @rx.event
    def logout(self):
        """Logs the user out using the do_logout method from the base class and redirects."""
        self.do_logout() # Use the do_logout() method from LocalAuthState
        return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE) # Redirect to login page

    @rx.event
    def check_session(self):
        """Check if the user is in session, otherwise redirect to login."""
        # Uses is_authenticated from the parent LoginState
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)