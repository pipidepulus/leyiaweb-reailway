import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",

    # Tu plugin de Tailwind se mantiene igual.
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],

    # Mantenemos tus paquetes de frontend y añadimos los que faltan.
    # Esta es la forma moderna de añadir dependencias de JS,
    # reemplazando al antiguo 'custom_components'.
    frontend_packages=[
        "@clerk/localizations",
        "@chakra-ui/system",     # <--- Añadido
        "chakra-react-select",   # <--- Añadido
    ],
)