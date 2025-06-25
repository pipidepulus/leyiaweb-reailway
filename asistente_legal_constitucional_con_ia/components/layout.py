# ruta: components/layout.py
"""Layout principal de la aplicación."""
import reflex as rx
from .sidebar import sidebar

def main_layout(content: rx.Component, use_container: bool = True) -> rx.Component:
    """El layout principal que envuelve todas las páginas."""
    content_wrapper = rx.container if use_container else rx.box
    
    return rx.box(
        rx.hstack(
            rx.desktop_only(sidebar()),
            content_wrapper(
                content,
                padding="2em",
                flex_grow=1,  # Correcto: Crece para llenar el espacio sobrante
                height="100%",
                overflow_y="auto",
            ),
            align="start",
            height="100vh",
            width="100%",
        ),
        height="100vh",
        width="100%",
    )