# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",

    # Dejamos el plugin de Tailwind porque tu UI lo usa
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],
)