# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="tu_app",
    api_url="http://localhost:8000", # Esto será sobreescrito en producción
)