# Componente para mostrar la lista de archivos subidos
import reflex as rx
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState

# ¡CORRECCIÓN! Usamos "gray" que es un color válido.
INFO_TEXT_COLOR = "gray" 

def file_list() -> rx.Component:
    """Muestra la lista de archivos recientes con estilo unificado."""
    archivos = ChatState.file_info_list
    hay_archivos = archivos.length() > 0

    def file_row(f: rx.Var[dict]) -> rx.Component:
        """Renderiza una fila de archivo con estilo consistente."""
        return rx.hstack(
            rx.icon("file-text", size=16, color_scheme=INFO_TEXT_COLOR, flex_shrink=0),
            rx.text(
                f["filename"],
                size="2",
                color_scheme=INFO_TEXT_COLOR, # Ahora usa "gray"
                flex_grow=1,
                white_space="nowrap",
                overflow="hidden",
                text_overflow="ellipsis",
            ),
            rx.icon_button(
                "trash-2", size="1", color_scheme="gray", variant="ghost",
                on_click=ChatState.delete_file(f["file_id"]),
                title="Eliminar archivo", cursor="pointer",
            ),
            spacing='3', width="100%", align_items="center",
        )

    return rx.box(
        rx.heading(
            "Archivos Recientes", size="3", weight="medium",
            color="blue", margin_bottom="0.5em",
        ),
        rx.vstack(
            rx.foreach(archivos, file_row),
            rx.cond(
                ~hay_archivos,
                rx.text(
                    "No hay archivos subidos.", size="2", color="blue",
                    font_style="italic", text_align="center", padding_y="1em", font_weight="bold",
                )
            ),
            spacing="2", width="100%",
        ),
        width="100%",
    )