# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="https://legalcolrag.onrender.com",
    frontend_packages=[
        "@chakra-ui/system",
        "chakra-react-select",
    ],
)