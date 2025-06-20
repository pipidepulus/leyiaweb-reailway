import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",
    plugins=[rx.plugins.TailwindV3Plugin()],
    frontend_packages=[
        "@clerk/localizations",
    ],
)