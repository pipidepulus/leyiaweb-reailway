# ruta: rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",

    # El plugin de Tailwind, que es NECESARIO por tu uso de `class_name`
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],

    # Paquetes para los componentes interactivos como rx.Select
    frontend_packages=[
        "@chakra-ui/system",
        "chakra-react-select",
    ],
)