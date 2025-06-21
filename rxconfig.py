# rxconfig.py
import reflex as rx
import os
# from dotenv import load_dotenv  # No necesitas dotenv en producción en Render

# Render proporciona la URL pública en esta variable de entorno.
# Si no existe (ej. en desarrollo local), se queda como un string vacío,
# y Reflex lo manejará correctamente usando localhost.
render_url = os.environ.get("RENDER_EXTERNAL_URL")

# Si render_url es None o una cadena vacía, Reflex sabe qué hacer.
# No es necesario un valor predeterminado como "".
# `os.environ.get` con un solo argumento devuelve None si no se encuentra.

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    # Usa la variable dinámica que obtuviste.
    # Si render_url es None, Reflex usará su valor por defecto,
    # que es perfecto para el desarrollo local.
    api_url=render_url,
    
    plugins=[
        # Nota: Tailwind ya está incluido por defecto en Reflex,
        # así que este plugin podría no ser necesario a menos que
        # estés haciendo algo muy específico con la versión.
        # Es seguro dejarlo, pero es bueno saberlo.
        rx.plugins.TailwindV3Plugin(), 
    ],
)