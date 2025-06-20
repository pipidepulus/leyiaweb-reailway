import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",

    # Moviendo el theme aquí, que es su lugar correcto en esta versión
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="teal"
    ),

    # Tus plugins, que ya estaban en el lugar correcto en el config anterior,
    # pero ahora nos aseguramos de que SÓLO estén aquí.
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],

    # Tus paquetes de frontend, que son cruciales para el error original.
    frontend_packages=[
        "@clerk/localizations",
        "@chakra-ui/system",
        "chakra-react-select",
    ],
)