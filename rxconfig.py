# rxconfig.py
import reflex as rx
import os

# Configuración base que se usará en todos los entornos.
config_dict = {
    "app_name": "asistente_legal_constitucional_con_ia",
    "plugins": [
        rx.plugins.TailwindV3Plugin(),
    ],
}

# Render proporciona la URL pública en esta variable de entorno.
render_url = os.environ.get("RENDER_EXTERNAL_URL")

# Si la variable existe (es decir, estamos en el entorno de Render),
# la añadimos al diccionario de configuración.
# Si no existe (estamos en local), no se añade `api_url`, y Reflex
# usará su valor por defecto (localhost), que es lo correcto.
if render_url:
    config_dict["api_url"] = render_url

# Creamos el objeto de configuración final desempaquetando el diccionario.
config = rx.Config(**config_dict)