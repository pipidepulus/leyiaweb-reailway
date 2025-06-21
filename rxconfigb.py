# ruta: rxconfig.py
"""
Configuración principal de la aplicación Reflex.
Define el nombre, la URL de la API, los plugins y las dependencias de frontend.
"""
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",

    # Configuración del tema base de Radix para la aplicación
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="teal"
    ),

    # Habilita el uso de Tailwind CSS a través de la propiedad `class_name`
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],

    # Lista de paquetes de npm necesarios para el frontend
    frontend_packages=[
        "@clerk/localizations",
        "@chakra-ui/system",
        "chakra-react-select",
    ],
)