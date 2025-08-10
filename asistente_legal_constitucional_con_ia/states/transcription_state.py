# asistente_legal_constitucional_con_ia/states/transcription_state.py
"""Estado para transcripción de audio con AssemblyAI."""

import json
import os
import reflex as rx
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.database import Notebook, AudioTranscription
from dotenv import load_dotenv
import dataclasses
import assemblyai

load_dotenv()


@dataclasses.dataclass
class TranscriptionType:
    """Tipo para representar una transcripción en el frontend."""
    id: int
    filename: str
    transcription_text: str
    audio_duration: str
    created_at: str
    updated_at: str
    notebook_id: int


class TranscriptionState(rx.State):
    """Estado para gestionar transcripciones de audio."""
    
    transcriptions: list[TranscriptionType] = []
    current_transcription: Optional[str] = ""
    uploading_audio: bool = False
    transcribing: bool = False
    progress_message: str = ""
    error_message: str = ""
    uploaded_files: list[str] = []
    
    @rx.event
    async def handle_upload(self, files: List[rx.UploadFile]):
        """Maneja la subida de archivos MP3 siguiendo el patrón exacto de Reflex."""
        for file in files:
            try:
                # Verificar que sea un archivo MP3
                if not file.content_type == 'audio/mpeg':
                    yield rx.toast.error(f"'{file.name}' no es un archivo MP3 válido.")
                    continue
                
                # Leer datos del archivo
                data = await file.read()
                
                # Guardar el archivo siguiendo el patrón de Reflex
                path = rx.get_upload_dir() / file.name
                with path.open("wb") as f:
                    f.write(data)
                
                # Agregar a la lista de archivos subidos
                self.uploaded_files.append(file.name)
                
                # Iniciar transcripción
                self.uploading_audio = True
                self.transcribing = True
                self.progress_message = f"Transcribiendo {file.name}..."
                yield
                
                # Transcribir con AssemblyAI usando los datos ya leídos
                transcription_text = await self._transcribe_audio(data, file.name)
                
                if transcription_text:
                    # Crear notebook con la transcripción
                    notebook_title = f"Transcripción - {os.path.splitext(file.name)[0]}"
                    await self._create_transcription_notebook(
                        transcription_text, 
                        notebook_title, 
                        file.name
                    )
                    
                    # Mostrar mensaje de éxito
                    self.current_transcription = "SUCCESS"
                    
                    # Limpiar archivos subidos después del éxito
                    self.uploaded_files = []
                    
                    # Recargar la lista de transcripciones
                    await self.load_user_transcriptions()
                    
                    yield rx.toast.success(f"¡Notebook generado! Transcripción de '{file.name}' completada.")
                else:
                    yield rx.toast.error(f"Error al transcribir '{file.name}'.")
                    
            except Exception as e:
                self.error_message = f"Error procesando {file.name}: {str(e)}"
                yield rx.toast.error(self.error_message)
            finally:
                self.transcribing = False
                self.uploading_audio = False
                yield
                
    async def _transcribe_audio(self, audio_data: bytes, filename: str) -> str:
        """Transcribe audio usando AssemblyAI."""
        try:
            # Verificar API key
            api_key = os.getenv("ASSEMBLYAI_API_KEY")
            if not api_key:
                self.error_message = "API key de AssemblyAI no configurada en .env"
                return ""
            
            assemblyai.settings.api_key = api_key
            
            # Actualizar mensaje de progreso
            self.progress_message = f"Conectando con AssemblyAI para transcribir {filename}..."
            
            transcriber = assemblyai.Transcriber()
            
            config = assemblyai.TranscriptionConfig(
                speaker_labels=True,
                language_code="es",
                format_text=True
            )
            
            # Subir archivo y transcribir
            self.progress_message = f"Subiendo {filename} a AssemblyAI..."
            
            transcript = transcriber.transcribe(audio_data, config=config)
            
            # Verificar estado
            if transcript.status == assemblyai.TranscriptStatus.error:
                self.error_message = f"Error de AssemblyAI: {transcript.error}"
                return ""
            
            # Procesar respuesta
            transcription_text = transcript.text
            
            if transcript.utterances:
                formatted_text = "## Transcripción con Identificación de Hablantes\n\n"
                for utterance in transcript.utterances:
                    speaker = f"Hablante {utterance.speaker}"
                    formatted_text += f"**{speaker}:** {utterance.text}\n\n"
                transcription_text = formatted_text
            
            self.progress_message = f"Transcripción de {filename} completada exitosamente"
            return transcription_text
            
        except Exception as e:
            error_msg = f"Error en la transcripción de {filename}: {str(e)}"
            self.error_message = error_msg
            print(f"DEBUG: {error_msg}")
            return ""

    async def _create_transcription_notebook(self, transcription_text: str, title: str, filename: str):
        """Crea un notebook con la transcripción."""
        try:
            with rx.session() as session:
                print(f"DEBUG: Creando notebook para workspace público")

                # Importar aquí para evitar circular imports
                from ..models.database import Notebook
                
                # Convertir transcripción a formato notebook JSON
                notebook_content = self._convert_transcription_to_notebook(transcription_text, title, filename)
                
                # Crear el notebook
                notebook = Notebook(
                    title=title,
                    content=json.dumps(notebook_content),  # Guardar como JSON
                    workspace_id="public",
                    notebook_type="transcription",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(notebook)
                session.commit()
                session.refresh(notebook)
                
                print(f"DEBUG: Notebook creado con ID: {notebook.id}")
                
                # Crear el registro de transcripción
                transcription = AudioTranscription(
                    filename=filename,
                    transcription_text=transcription_text,
                    notebook_id=notebook.id,
                    audio_duration="0:00",
                    workspace_id="public",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(transcription)
                session.commit()
                
                print(f"DEBUG: Transcripción creada con ID: {transcription.id}")
                
        except Exception as e:
            print(f"DEBUG: Error creando notebook: {str(e)}")
            self.error_message = f"Error creando notebook: {str(e)}"

    @rx.event
    async def load_user_transcriptions(self):
        """Carga las transcripciones."""
        try:
            with rx.session() as session:
                transcriptions = session.exec(
                    AudioTranscription.select().where(
                        AudioTranscription.workspace_id == "public"
                    ).order_by(AudioTranscription.created_at.desc())
                ).all()
                
                
                self.transcriptions = [
                    TranscriptionType(
                        id=t.id,
                        filename=t.filename,
                        transcription_text=t.transcription_text[:200] + "..." if len(t.transcription_text) > 200 else t.transcription_text,
                        audio_duration=t.audio_duration,
                        created_at=t.created_at.strftime("%d/%m/%Y %H:%M"),
                        updated_at=t.updated_at.strftime("%d/%m/%Y %H:%M"),
                        notebook_id=t.notebook_id
                    ) for t in transcriptions
                ]
                
        except Exception as e:
            self.error_message = f"Error cargando transcripciones: {str(e)}"

    @rx.event
    async def load_user_transcriptions_simple(self):
        """Versión simple para cargar transcripciones."""
        await self.load_user_transcriptions()

    @rx.event
    async def delete_transcription(self, transcription_id: int):
        """Elimina una transcripción."""
        try:
            with rx.session() as session:
                # Buscar la transcripción
                transcription = session.exec(
                    AudioTranscription.select().where(
                        AudioTranscription.id == transcription_id,
                        AudioTranscription.workspace_id == "public"
                    )
                ).first()
                
                if transcription:
                    # Eliminar el notebook asociado si existe
                    if transcription.notebook_id:
                        notebook = session.exec(
                            Notebook.select().where(
                                Notebook.id == transcription.notebook_id,
                                Notebook.workspace_id == "public"
                            )
                        ).first()
                        if notebook:
                            session.delete(notebook)
                    
                    # Eliminar la transcripción
                    session.delete(transcription)
                    session.commit()
                    
                    # Recargar la lista
                    await self.load_user_transcriptions()
                    yield rx.toast.success("Transcripción eliminada correctamente.")
                else:
                    yield rx.toast.error("Transcripción no encontrada.")
                    
        except Exception as e:
            self.error_message = f"Error eliminando transcripción: {str(e)}"
            yield rx.toast.error(self.error_message)

    @rx.event
    async def clear_error(self):
        """Limpia el mensaje de error."""
        self.error_message = ""

    @rx.event
    async def clear_current_transcription(self):
        """Limpia la transcripción actual y resetea el estado."""
        self.current_transcription = ""
        self.uploaded_files = []  # Limpiar archivos subidos
        self.progress_message = ""  # Limpiar mensaje de progreso
        self.error_message = ""  # Limpiar errores

    @rx.event
    async def reset_upload_state(self):
        """Resetea completamente el estado de subida para una nueva transcripción."""
        self.uploaded_files = []
        self.current_transcription = ""
        self.uploading_audio = False
        self.transcribing = False
        self.progress_message = ""
        self.error_message = ""

    def _convert_transcription_to_notebook(self, transcription_text: str, title: str, filename: str) -> Dict[str, Any]:
        """Convierte una transcripción a formato notebook JSON."""
        cells = []
        
        # Celda de título
        cells.append({
            "cell_type": "markdown",
            "source": [f"# {title}\n\n", f"**Archivo:** {filename}\n\n", f"**Generado:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}\n\n", "---\n\n"]
        })
        
        # Celda con la transcripción
        cells.append({
            "cell_type": "markdown", 
            "source": [f"## 📝 Transcripción Completa\n\n", f"{transcription_text}\n\n"]
        })
        
        return {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Audio Transcription",
                    "language": "markdown", 
                    "name": "audio_transcription"
                }
            }
        }
