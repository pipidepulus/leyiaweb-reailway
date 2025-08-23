# /home/pipid/legalcolrag/asistente_legal_constitucional_con_ia/pages/asistente_page.py
"""Página del asistente, que ahora solo muestra el componente de chat."""

import reflex as rx

from ..components.chat import chat
from ..components.layout import main_layout


def asistente_page() -> rx.Component:
    """
    Define el contenido de la página del asistente, que ahora es solo el chat.
    El layout principal se encarga del resto.
    """
    # El contenido de la página no necesita cambiar en absoluto.
    return main_layout(chat(), use_container=False)
