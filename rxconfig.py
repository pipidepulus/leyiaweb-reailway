# ruta: rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",

    # El theme que tenías antes (si lo quieres)
    # theme=rx.theme(
    #     appearance="light", has_background=True, radius="large", accent_color="teal"
    # ),

    # El plugin de Tailwind, que es NECESARIO por tu uso de `class_name`
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],

    # TODOS los paquetes de frontend que tu app completa necesita
    frontend_packages=[
        "@clerk/localizations",
        "@chakra-ui/system",
        "chakra-react-select",
    ],
)