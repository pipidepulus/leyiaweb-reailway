# ruta: asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
"""
Archivo principal de la aplicación.
"""
import os
import reflex as rx
from dotenv import load_dotenv
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState

# --- Carga de variables de entorno ---
load_dotenv()

# ### CAMBIO 1: Importa tus páginas ###
from .pages.prompts_page import prompts_page
from .pages.proyectos_page import proyectos_page, ProyectosState
from .pages.asistente_page import asistente_page
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
    content = rx.center(
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
                class_name="text-shadow",
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
        ),
        height="80vh",
    )
    
    return main_layout(content)

# --- Añadimos todas las páginas a la aplicación ---

app.add_page(asistente_page, route="/asistente", title="Asistente Constitucional")
app.add_page(
    proyectos_page, 
    route="/proyectos", 
    title="Proyectos de Ley", 
    on_load=ProyectosState.scrape_proyectos
)
app.add_page(prompts_page, route="/prompts")
