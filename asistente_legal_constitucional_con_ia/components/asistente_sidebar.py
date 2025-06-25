"""Panel contextual de archivos, con estilo unificado."""

import reflex as rx
from .file_uploader import file_uploader
from .file_list import file_list


def asistente_sidebar() -> rx.Component:
    """
    Renderiza el panel de gestión de archivos con un estilo visual
    coherente con el resto de la barra de navegación.
    """
    return rx.desktop_only(
            rx.vstack(
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
        )