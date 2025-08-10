# asistente_legal_constitucional_con_ia/pages/transcription_page.py
"""Página para transcripción de audio."""

import reflex as rx
from ..components.layout import main_layout
from ..states.transcription_state import TranscriptionState


def transcription_page() -> rx.Component:
    """Página de transcripción de audio."""
    
    content = rx.vstack(
        # Header
        rx.heading("Transcripción de Audio", size="8", color="blue", margin_bottom="2rem"),
        
        # Upload area
        rx.card(
            rx.vstack(
                rx.heading("Subir archivo de audio", size="5"),
                rx.text("Formatos soportados: MP3", size="2", color="gray"),
                rx.text("Límite: 5 GB por archivo (usando AssemblyAI)", size="2", color="green"),
                
                rx.upload(
                    rx.vstack(
                        rx.button(
                            "📁 Seleccionar archivo MP3",
                            color="rgb(107, 99, 246)",
                            bg="white",
                            border="1px solid rgb(107, 99, 246)",
                        ),
                        rx.text(
                            "Arrastra y suelta un archivo MP3 aquí o haz clic para seleccionar",
                            size="2",
                            color="gray"
                        ),
                        align_items="center",
                        spacing="2",
                    ),
                    id="upload_mp3",
                    border="2px dashed rgb(107, 99, 246)",
                    padding="2em",
                    border_radius="lg",
                    width="100%",
                    accept={"audio/mpeg": [".mp3"]},
                    max_files=1,
                    disabled=TranscriptionState.uploading_audio | TranscriptionState.transcribing,
                    multiple=False,
                ),
                
                # Mostrar archivos seleccionados (siguiendo documentación de Reflex)
                rx.hstack(
                    rx.foreach(
                        rx.selected_files("upload_mp3"), 
                        lambda file_name: rx.hstack(
                            rx.icon("file-audio", color="blue"),
                            rx.text(file_name),
                            spacing="2"
                        )
                    )
                ),
                
                # Mostrar archivos ya subidos
                rx.foreach(
                    TranscriptionState.uploaded_files,
                    lambda filename: rx.hstack(
                        rx.icon("check-check", color="green"),
                        rx.text(f"Subido: {filename}"),
                        spacing="2"
                    )
                ),
                
                # Información sobre el proceso
                rx.cond(
                    TranscriptionState.transcribing | TranscriptionState.uploading_audio,
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.spinner(size="2"),
                                rx.text("🎙️ Procesando:", weight="bold", size="3", color="blue"),
                                spacing="2",
                                align="center"
                            ),
                            rx.cond(
                                TranscriptionState.progress_message != "",
                                rx.text(TranscriptionState.progress_message, size="2", color="blue", font_style="italic"),
                                rx.fragment()
                            ),
                            spacing="2",
                            align="start"
                        ),
                        bg="blue.50",
                        border="1px solid",
                        border_color="blue.200",
                        width="100%"
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("📋 Instrucciones:", weight="bold", size="3"),
                            rx.text("1. Haz clic en 'Seleccionar archivo MP3'", size="2"),
                            rx.text("2. Elige un archivo MP3", size="2"),
                            rx.text("3. Haz clic en 'Transcribir Audio'", size="2"),
                            rx.text("4. Espera a que termine el proceso", size="2"),
                            rx.text("5. Se creará automáticamente un notebook", size="2"),
                            spacing="1",
                            align="start"
                        ),
                        bg="gray.50",
                        border="1px solid",
                        border_color="gray.200",
                        width="100%"
                    )
                ),
                
                # Botón eliminado - ya no es necesario porque el upload procesa automáticamente
                
                rx.button(  
                    "🎙️ Transcribir Audio",
                    on_click=TranscriptionState.handle_upload(
                        rx.upload_files(upload_id="upload_mp3")
                    ),
                    loading=TranscriptionState.uploading_audio | TranscriptionState.transcribing,
                    disabled=TranscriptionState.uploading_audio | TranscriptionState.transcribing,
                    size="3",
                    margin_top="1rem",
                    color_scheme="green"
                ),
                
                spacing="4",
                align="center",
                width="100%"
            ),
            width="100%"
        ),
        
        # Estado de progreso
        rx.cond(
            TranscriptionState.transcribing | TranscriptionState.uploading_audio,
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.spinner(size="2"),
                        rx.text(TranscriptionState.progress_message, weight="bold"),
                        spacing="3",
                        align="center"
                    ),
                    spacing="2",
                    align="center"
                ),
                width="100%",
                bg="blue.50",
                border="1px solid",
                border_color="blue.200"
            ),
            rx.fragment()
        ),
        
        # Mensaje de éxito
        rx.cond(
            TranscriptionState.current_transcription == "SUCCESS",
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("check", color="green", size=24),
                        rx.heading("¡Notebook generado exitosamente!", size="5", color="green"),
                        spacing="2",
                        align="center"
                    ),
                    rx.text(
                        "Se ha creado automáticamente un notebook con tu transcripción.",
                        size="3",
                        color="gray.700"
                    ),
                    rx.hstack(
                        rx.button(
                            "📓 Ver Mis Notebooks",
                            on_click=rx.redirect("/notebooks"),
                            variant="solid",
                            color_scheme="green"
                        ),
                        rx.button(
                            "🎙️ Nueva Transcripción",
                            on_click=TranscriptionState.clear_current_transcription,
                            variant="outline",
                            color_scheme="blue"
                        ),
                        spacing="3"
                    ),
                    spacing="4",
                    align="center",
                    width="100%"
                ),
                width="100%",
                bg="green.50",
                border="2px solid",
                border_color="green.300",
                padding="2rem"
            ),
            rx.fragment()
        ),
        
        # Historial de transcripciones
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Transcripciones anteriores", size="5"),
                    rx.spacer(),
                    rx.button(
                        "Actualizar",
                        on_click=TranscriptionState.load_user_transcriptions_simple,
                        variant="ghost",
                        size="2"
                    ),
                    width="100%",
                    align="center"
                ),
                
                rx.cond(
                    TranscriptionState.transcriptions,
                    rx.vstack(
                        rx.foreach(
                            TranscriptionState.transcriptions,
                            lambda t: transcription_item(t)
                        ),
                        spacing="3",
                        width="100%"
                    ),
                    rx.text("No hay transcripciones anteriores.", color="gray", text_align="center")
                ),
                
                spacing="4",
                width="100%"
            ),
            width="100%"
        ),
        
        # Mensaje de error
        rx.cond(
            TranscriptionState.error_message != "",
            rx.callout.root(
                rx.callout.icon(rx.icon("triangle-alert")),
                rx.callout.text(TranscriptionState.error_message),
                color_scheme="red"
            ),
            rx.fragment()
        ),
        
        spacing="6",
        width="100%",
        on_mount=[
            TranscriptionState.load_user_transcriptions_simple,
            TranscriptionState.reset_upload_state  # Limpiar estado al cargar página
        ]
    )
    
    return main_layout(content)


def transcription_item(transcription: rx.Var) -> rx.Component:
    """Componente para mostrar una transcripción en el historial."""
    
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(transcription.filename, weight="bold", size="3"),
                rx.text(transcription.created_at[:10], size="2", color="gray"),
                align="start",
                spacing="1"
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    "📓 Ver Notebook",
                    on_click=rx.redirect(f"/notebooks/{transcription.notebook_id}"),
                    variant="soft",
                    size="2",
                    disabled=transcription.notebook_id == 0
                ),
                rx.button(
                    "🗑️ Eliminar",
                    on_click=TranscriptionState.delete_transcription(transcription.id),
                    variant="outline",
                    size="2",
                    color_scheme="red"
                ),
                spacing="2"
            ),
            width="100%",
            align="center"
        ),
        width="100%",
        variant="ghost"
    )
