# ruta: rxconfig.py
"""
Configuración final de la aplicación.
La api_url se ha actualizado para usar el dominio personalizado,
unificando la comunicación del frontend y el backend.
"""
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    
    # --- EL CAMBIO CLAVE ---
    # La URL de la API DEBE coincidir con el dominio que usas en el navegador.
    api_url="https://www.globaltelecom.site",

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