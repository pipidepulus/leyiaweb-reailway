# Componente para mostrar la lista de archivos subidos
import reflex as rx
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState


def file_list() -> rx.Component:
    archivos = ChatState.file_info_list[-3:]
    hay_archivos = archivos.length() > 0

    def file_row(f):
        return rx.hstack(
            rx.text(f["filename"], font_size="sm", flex=1),
            rx.button(
                "🗑️",
                size="1",
                color_scheme="gray",
                on_click=ChatState.delete_file(f["file_id"]),
                title="Eliminar archivo",
            ),
            spacing='4',
            width="100%",
            mb=4  # Separación de 2px entre filas
        )

    return rx.box(
        rx.text("Archivos recientes:", font_weight="bold", mb=2),
        rx.vstack(
            rx.foreach(archivos, file_row),
            # Siempre renderizar el texto "No hay archivos", pero ocultarlo si hay archivos.
            rx.text(
                "No hay archivos", 
                font_size="sm", 
                color="gray",
                style=rx.cond(hay_archivos, {"display": "none"}, {}) # Ocultar si hay archivos
            ),
            spacing="4",   # Espacio vertical entre filas
            width="100%",
        ),
        mt=4,
    )
