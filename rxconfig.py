# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],
    frontend_packages=[
        "@chakra-ui/system",
        "chakra-react-select",
    ],
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://legalcolrag.onrender.com",
        "https://www.globaltelecom.site",
    ],
)