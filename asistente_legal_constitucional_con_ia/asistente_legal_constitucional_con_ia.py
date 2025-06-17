import reflex as rx
import reflex_local_auth
from reflex_local_auth import LocalAuthState # Assuming LocalAuthState is correctly imported from here
# from reflex_local_auth.local_auth import LocalAuth # Corrected import for LocalAuth - NOW COMMENTED
from asistente_legal_constitucional_con_ia.pages.home_page import home_page
from asistente_legal_constitucional_con_ia.pages.custom_register_page import register_page as custom_register_page
from asistente_legal_constitucional_con_ia.pages.custom_login_page import login_page as custom_login_page # Import custom login page
from asistente_legal_constitucional_con_ia.pages.asistente_page import asistente_page
from asistente_legal_constitucional_con_ia.pages.proyectos_page import proyectos_page
from asistente_legal_constitucional_con_ia.pages.prompts_page import prompts_page # Nueva importación

app = rx.App()

# Configura reflex-local-auth para que use su LocalUser interno por defecto
# LocalAuth(app, login_route="/login", register_route="/register") # COMMENTED OUT

app.add_page(
    # reflex_local_auth.pages.login_page, # Use custom login page
    custom_login_page,
    route=reflex_local_auth.routes.LOGIN_ROUTE,
    title="Login",
)
app.add_page(
    custom_register_page,
    route=reflex_local_auth.routes.REGISTER_ROUTE,
    title="Registro",
)

app.add_page(
    proyectos_page, 
    route="/proyectos", 
    title="Explorar Proyectos"
)

# Añadir prompts_page explícitamente
app.add_page(
    prompts_page,
    route="/prompts",
    title="Prompts"
)

# No agregues main_page ni home_page ni asistente_page aquí, el decorador @rx.page los registra automáticamente

# from reflex_local_auth import LocalAuthState, LocalAuth # Ensure this line is removed or commented
# from asistente_legal_constitucional_con_ia.models.user import LocalUser # This line is commented out
from asistente_legal_constitucional_con_ia.states.auth_state import AuthState