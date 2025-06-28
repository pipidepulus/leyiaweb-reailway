# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""
Archivo principal de la aplicación.
"""
import os
import reflex as rx
from dotenv import load_dotenv
import reflex_clerk_api as clerk
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState

# --- Carga de variables de entorno ---
load_dotenv()

# ### CAMBIO 1: Importa tus páginas, incluida la de login ###
from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page, ProyectosState
from .pages.asistente_page import asistente_page
from .pages.login_page import login_page  # <-- ¡Importante!
# Si tienes una página de registro, impórtala también:
# from .pages.signup_page import signup_page 
from .components.layout import main_layout

# 1. Primero, crea la instancia de la aplicación Reflex.
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="grass",

           ),    
    stylesheets=[
        "/global.css",  # La ruta es relativa a assets y debe iniciar con /
    ],
)


# --- Página Principal (Index) ---
# La página de inicio no necesita protección, ya que gestiona ambos casos (logueado/deslogueado).
@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
    """La página de inicio, envuelta en el layout principal."""
    content = rx.center( # Usamos center para alinear todo
        # Muestra el contenido principal solo si el usuario ha iniciado sesión
        clerk.signed_in(
            rx.vstack(
                rx.image(
                    src="/balanza.png",
                    width="256px",
                    height="auto",
                    margin_bottom="1rem",
                ),
                rx.heading(
                    "Bienvenido al Asistente Legal Constitucional",
                    size="7",
                    margin_bottom="1rem",
                    color_scheme="blue",
                    weight="bold",
                    text_align="center",
                    class_name="text-shadow",  # Añadimos una clase para sombra de texto
                ),
                rx.text(
                    "Sistema especializado en análisis de jurisprudencia y leyes con IA.",
                    size="4",
                    color_scheme="blue",
                    margin_bottom="1.5rem",
                ),
                rx.text(
                    "Selecciona una opción del menú lateral para comenzar.",
                    size="5",
                    weight="bold",
                    color_scheme="blue",
                    margin_bottom="2rem",
                ),
                align="center",
                spacing="3",
                on_mount=ChatState.limpiar_chat,
            )
        ),
        # Muestra un mensaje y botón de inicio de sesión si no está autenticado
        clerk.signed_out(
            rx.vstack(
                # --- CÓDIGO CORRECTO PARA ESTE ENFOQUE ---
        clerk.sign_in_button(
            rx.button(
                "Iniciar Sesión",
                size="3",
                variant="solid",
                style={
                    "background_color": "blue",  # azul
                    "color": "white",               # texto blanco
                },
            )
        ),
        rx.vstack(
        rx.text("¿No tienes cuenta?"),
        clerk.sign_up_button(
            rx.link(
                "Regístrate aquí.", 
                # Añadimos un poco de estilo para que parezca un enlace real
                color_scheme="blue",
                text_decoration="underline",
            )
        ),
        spacing="1",          # Espaciado mínimo entre los dos textos
        align="center",       # Centra los elementos horizontalmente
        margin_top="1.5em",   # Un poco de espacio por encima
    )
            )
        ),
        height="80vh",
    )
    
    # Importante: La página de inicio también debe usar el layout para tener la barra lateral
    return main_layout(content)

# --- Añadimos todas las páginas a la aplicación ---

# ### CAMBIO 3: Añade TUS páginas de login y registro ###
# Aquí es donde le dices a Reflex que la URL '/login' debe usar tu archivo login_page.py
app.add_page(login_page, route="/login", title="Iniciar Sesión")
# Si tienes una página de registro, añádela también:
# app.add_page(signup_page, route="/sign-up", title="Registro")


# Estas páginas DEBEN estar protegidas, así que aquí aplicaremos el decorador.
# Asegúrate de que en cada uno de estos archivos (`asistente_page.py`, etc.)
# hayas añadido el decorador @require_login como vimos antes.
app.add_page(asistente_page, route="/asistente", title="Asistente Constitucional")
app.add_page(
    proyectos_page, 
    route="/proyectos", 
    title="Proyectos de Ley", 
    on_load=ProyectosState.scrape_proyectos  # <-- Pasamos el evento on_load aquí
)
app.add_page(prompts_page, route="/prompts")

# ### CORRECCIÓN DEFINITIVA: USAMOS wrap_app AL FINAL ###
# Este es el método correcto según la documentación de reflex-clerk-api.
# Envuelve la aplicación completa y configura tanto el backend como el frontend.
app = clerk.wrap_app(
    app,
    publishable_key=os.getenv("CLERK_PUBLISHABLE_KEY"),
    secret_key=os.getenv("CLERK_SECRET_KEY"),
    register_user_state=True,
    localization={"language": "es_ES",} 
)