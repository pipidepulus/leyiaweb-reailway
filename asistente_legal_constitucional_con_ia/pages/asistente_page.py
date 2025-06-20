"""Página del asistente, que ahora solo muestra el componente de chat."""

import reflex as rx
from ..components.layout import main_layout
from ..components.chat import chat


@rx.page(route="/asistente", title="Asistente Constitucional")
def asistente_page() -> rx.Component:
    """
    Define el contenido de la página del asistente, que ahora es solo el chat.
    El layout principal se encarga del resto.
    """
    return main_layout(chat())