# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    plugins=[
        rx.plugins.TailwindV3Plugin(),
    ],
    frontend_packages=[
        #"@clerk/localizations",
        "@chakra-ui/system",
        #"chakra-react-select",
    ],
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://legalcolrag.onrender.com",
        "https://www.globaltelecom.site",
    ],
)