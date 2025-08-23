"""Panel contextual de archivos, con estilo unificado."""

import reflex as rx

from .file_list import file_list
from .file_uploader import file_uploader


def asistente_sidebar() -> rx.Component:
    """
    Renderiza el panel de gestión de archivos con un estilo visual
    coherente con el resto de la barra de navegación.
    """
    return rx.vstack(
        rx.divider(),
        rx.text(
            "Archivos de Contexto",
            size="4",
            weight="bold",
            color="blue",
            padding_top="1em",
        ),
        file_uploader(),
        rx.divider(margin_y="0.5em"),
        file_list(),
        spacing="4",
        width="100%",
    )
