# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="asistente_legal_constitucional_con_ia",
    api_url="http://localhost:8000", # Esto será sobreescrito en producción
    show_built_with_reflex=False
)

