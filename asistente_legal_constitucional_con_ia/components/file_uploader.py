# Componente para subir archivos
import reflex as rx
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState

MAX_FILES = 3
SUPPORTED_TYPES = ["pdf", "docx", "txt"]


def file_uploader() -> rx.Component:
    selected_files = rx.selected_files("sidebar_upload")
    archivos_usados = ChatState.file_info_list.length() if hasattr(ChatState.file_info_list, 'length') else len(ChatState.file_info_list)
    disponibles = MAX_FILES - archivos_usados

    return rx.vstack(
        rx.text(f"Archivos soportados: {', '.join(SUPPORTED_TYPES).upper()} | {archivos_usados}/{MAX_FILES} usados, {disponibles} disponibles", font_size="sm", color="blue", mb=1),
        
        rx.upload(
            rx.text(
                "Selecciona archivos", 
                color="cyan-700", 
                font_weight="bold", 
                font_size="xs", 
                line_height="1"  # Added line_height
            ),
            id="sidebar_upload",
            accept=",".join(f".{ext}" for ext in SUPPORTED_TYPES),
            multiple=False,
            disabled=disponibles <= 0,
            display="flex", 
            align_items="center", 
            justify_content="center",
            class_name="bg-gray-200 hover:bg-gray-300 cursor-pointer", 
            border="2px solid #888888",
            border_radius="8px",        
            align_self="flex-start", 
            height="20px", # Reverted to explicit height
            # Removed: min_width, min_height, background_color, cursor, _hover, white_space from text
        ),
        
        rx.text(rx.cond(selected_files.length() > 0, f"Seleccionado: {selected_files[0]}", ""), color="blue", mb=1),
        rx.button(
            "Procesar archivo",
            size="2",
            color_scheme="teal",
            on_click=[
                ChatState.handle_upload(rx.upload_files("sidebar_upload")),
                rx.call_script("window.document.getElementById('sidebar_upload').value = ''")
            ],
            mt=2,
            disabled=(selected_files.length() == 0) | (disponibles <= 0),
        ),
        # New Vstack for feedback messages
        rx.vstack(
            rx.text(
                rx.cond(
                    ChatState.ocr_progress != "",
                    ChatState.ocr_progress,
                    rx.cond(
                        ChatState.uploading,
                        "Subiendo archivo...",
                        "" # Empty string when no message
                    )
                ),
                color="blue",
                font_weight="bold",
                bg=rx.cond(ChatState.ocr_progress != "", "#FFF3CD", rx.cond(ChatState.uploading, "#D1ECF1", "transparent")),
                padding="8px",
                border_radius="6px",
                width="100%", # Ensure text takes full width for background
                style=rx.cond((ChatState.ocr_progress == "") & (~ChatState.uploading), {"display": "none"}, {})
            ),
            rx.hstack(
                rx.spinner(color="blue", size="2"),
                rx.text(
                    "Procesando archivo... (esto puede tardar varios minutos si es escaneado)",
                    color="blue",
                    # mt=2, # No longer needed here, parent vstack has spacing
                    bg="#D1ECF1",
                    padding="8px",
                    border_radius="6px"
                ),
                spacing="2",
                width="100%", # Ensure hstack takes full width for background
                style=rx.cond(~ChatState.uploading, {"display": "none"}, {}) # This hstack is only for "Procesando"
            ),
            rx.text(
                ChatState.upload_error,
                color="red",
                # mt=2, # No longer needed here
                bg="#F8D7DA",
                padding="8px",
                border_radius="6px",
                width="100%", # Ensure text takes full width for background
                style=rx.cond(ChatState.upload_error == "", {"display": "none"}, {})
            ),
            rx.text(
                rx.cond((ChatState.upload_progress == 100) & (ChatState.upload_error == ""), "Archivo subido y procesado exitosamente!", ""), 
                color="green", 
                font_weight="bold",
                # mt=2, # No longer needed here
                width="100%", # Ensure text takes full width for background
                style=rx.cond(~((ChatState.upload_progress == 100) & (ChatState.upload_error == "")), {"display": "none"}, {})
            ),
            width="100%",
            max_height="135px", # Max height for the message area, increased from 120px
            overflow_y="auto",  # Scroll if messages exceed max_height
            spacing="2",        # Spacing between messages
            align_items="stretch", # Messages take full width
            mt=3 # Margin from the 'Procesar archivo' button
        ),
        bg="#e3e3ff",
        min_height="350px", # Changed back from 280px to 350px
        padding="16px",
        border_radius="10px",
    )
