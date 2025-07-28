# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""
Archivo principal de la aplicación.
"""
import os
import reflex as rx
from dotenv import load_dotenv
import reflex_local_auth
from sqlmodel import create_engine, SQLModel
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState
from asistente_legal_constitucional_con_ia.models.database import Notebook, AudioTranscription

# --- Carga de variables de entorno ---
load_dotenv()

# --- Configuración de la base de datos ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///legal_assistant.db")
engine = create_engine(DATABASE_URL, echo=False)

def create_tables():
    """Crea las tablas de la base de datos."""
    SQLModel.metadata.create_all(engine)

# ### CAMBIO 1: Importa tus páginas ###
from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page, ProyectosState
from .pages.asistente_page import asistente_page
from .pages.notebooks_page import notebooks_page, notebook_viewer_page
from .pages.transcription_page import transcription_page
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
# La página de inicio permanece pública pero informa sobre la necesidad de autenticación
@rx.page(route="/", title="Inicio")
def index() -> rx.Component:
    """La página de inicio, envuelta en el layout principal."""
    content = rx.center(
        rx.vstack(
            rx.image(
                src="/balanza.png",
                width="80px",
                height="80px",
                margin_bottom="1rem",
                object_fit="contain",
                border_radius="8px",
                margin_x="auto",
            ),
            rx.heading(
                "Asistente Legal Constitucional con IA",
                size="7",
                margin_bottom="1rem",
                color_scheme="blue",
                weight="bold",
                text_align="center",
                class_name="text-shadow",
            ),
            rx.text(
                "Sistema especializado en análisis de jurisprudencia y leyes con inteligencia artificial.",
                size="4",
                color_scheme="blue",
                margin_bottom="0.8rem",
                text_align="center",
            ),
            
            # Información sobre autenticación requerida
            rx.card(
                rx.vstack(
                    rx.heading("🔐 Acceso Protegido", size="5", color="orange", text_align="center"),
                    rx.text(
                        "Para proteger los recursos de IA y personalizar tu experiencia, "
                        "todas las funcionalidades requieren autenticación.",
                        text_align="center",
                        margin_bottom="1rem"
                    ),
                    
                    rx.vstack(
                        rx.text("🌟 Funcionalidades Disponibles:", weight="bold", color="blue"),
                        rx.text("• 🤖 Asistente Legal Inteligente", size="2"),
                        rx.text("• 📋 Análisis de Proyectos de Ley", size="2"),
                        rx.text("• 📚 Biblioteca de Prompts Especializados", size="2"),
                        rx.text("• 📝 Notebooks Personales y Persistentes", size="2"),
                        rx.text("• 🎤 Transcripción de Audio con Whisper", size="2"),
                        spacing="2",
                        align="start",
                        margin_bottom="1.5rem"
                    ),
                    
                    rx.hstack(
                        rx.link(
                            rx.button(
                                "🔐 Iniciar Sesión",
                                size="4",
                                color_scheme="blue"
                            ),
                            href=reflex_local_auth.routes.LOGIN_ROUTE
                        ),
                        rx.link(
                            rx.button(
                                "📝 Crear Cuenta",
                                size="4",
                                variant="outline",
                                color_scheme="green"
                            ),
                            href=reflex_local_auth.routes.REGISTER_ROUTE
                        ),
                        spacing="4",
                        justify="center"
                    ),
                    
                    spacing="3",
                    align="center"
                ),
                max_width="600px",
                padding="2rem",
                margin="1rem"
            ),
            
            rx.text(
                "💡 Crea una cuenta gratuita para acceder a todas las herramientas.",
                size="3",
                color="gray",
                text_align="center",
                font_style="italic"
            ),
            
            align="center",
            spacing="3",
            on_mount=ChatState.limpiar_chat,
        ),
        height="80vh",
    )
    
    return main_layout(content)

# --- Añadimos todas las páginas a la aplicación ---

# Página pública de inicio (landing page)
# Solo la página de inicio permanece pública para mostrar información de la app

# Páginas protegidas por autenticación - TODAS requieren login
app.add_page(asistente_page, route="/asistente", title="Asistente Constitucional")
app.add_page(
    proyectos_page, 
    route="/proyectos", 
    title="Proyectos de Ley", 
    on_load=ProyectosState.scrape_proyectos
)
app.add_page(prompts_page, route="/prompts", title="Biblioteca de Prompts")
app.add_page(notebooks_page, route="/notebooks", title="Mis Notebooks")
app.add_page(notebook_viewer_page, route="/notebooks/[notebook_id]", title="Ver Notebook")
app.add_page(transcription_page, route="/transcription", title="Transcripción de Audio")

# Páginas de autenticación (públicas) - usando las oficiales de reflex-local-auth
app.add_page(
    reflex_local_auth.pages.login_page,
    route=reflex_local_auth.routes.LOGIN_ROUTE,
    title="Iniciar Sesión"
)
app.add_page(
    reflex_local_auth.pages.register_page,
    route=reflex_local_auth.routes.REGISTER_ROUTE,
    title="Crear Cuenta"
)

# Inicializar la base de datos al arrancar
create_tables()
