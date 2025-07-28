# asistente_legal_constitucional_con_ia/states/transcription_state.py
"""Estado para transcripción de audio con AssemblyAI."""

import json
import os
import reflex as rx
from datetime import datetime
from typing import List, Dict, Any, Optional
from reflex_local_auth import LocalAuthState
import assemblyai
from ..models.database import Notebook, AudioTranscription, get_db_session
from sqlmodel import select
from dotenv import load_dotenv
import dataclasses

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


class TranscriptionState(LocalAuthState):
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
        if not self.is_authenticated:
            self.error_message = "Debes estar autenticado para transcribir audio."
            yield rx.toast.error(self.error_message)
            return
        
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
            assemblyai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
            
            if not assemblyai.settings.api_key:
                self.error_message = "API key de AssemblyAI no configurada"
                return ""
            
            transcriber = assemblyai.Transcriber()
            
            config = assemblyai.TranscriptionConfig(
                speaker_labels=True,
                language_code="es",
                format_text=True
            )
            
            transcript = transcriber.transcribe(audio_data, config=config)
            
            if transcript.status == assemblyai.TranscriptStatus.error:
                self.error_message = f"Error de AssemblyAI: {transcript.error}"
                return ""
            
            transcription_text = transcript.text
            
            if transcript.utterances:
                formatted_text = "## Transcripción con Identificación de Hablantes\n\n"
                for utterance in transcript.utterances:
                    speaker = f"Hablante {utterance.speaker}"
                    formatted_text += f"**{speaker}:** {utterance.text}\n\n"
                transcription_text = formatted_text
            
            return transcription_text
            
        except Exception as e:
            self.error_message = f"Error en la transcripción: {str(e)}"
            return ""

    async def _create_transcription_notebook(self, transcription_text: str, title: str, filename: str):
        """Crea un notebook con la transcripción."""
        try:
            with get_db_session() as session:
                user_id = str(self.authenticated_user.id) if self.authenticated_user else None
                print(f"DEBUG: Creando notebook para user_id: {user_id}")
                
                # Crear el notebook
                notebook = Notebook(
                    title=title,
                    content=transcription_text,
                    user_id=user_id,
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
                    user_id=user_id,
                    notebook_id=notebook.id,
                    audio_duration="0:00",
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
        """Carga las transcripciones del usuario autenticado."""
        if not self.is_authenticated:
            return
            
        try:
            with get_db_session() as session:
                statement = select(AudioTranscription).where(
                    AudioTranscription.user_id == str(self.authenticated_user.id) if self.authenticated_user else None
                ).order_by(AudioTranscription.created_at.desc())
                
                transcriptions = session.exec(statement).all()
                
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
        if not self.is_authenticated:
            return
            
        try:
            with get_db_session() as session:
                # Buscar la transcripción
                statement = select(AudioTranscription).where(
                    AudioTranscription.id == transcription_id,
                    AudioTranscription.user_id == str(self.authenticated_user.id) if self.authenticated_user else None
                )
                transcription = session.exec(statement).first()
                
                if transcription:
                    # Eliminar el notebook asociado si existe
                    if transcription.notebook_id:
                        notebook_statement = select(Notebook).where(
                            Notebook.id == transcription.notebook_id,
                            Notebook.user_id == str(self.authenticated_user.id) if self.authenticated_user else None
                        )
                        notebook = session.exec(notebook_statement).first()
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
        """Limpia la transcripción actual."""
        self.current_transcription = ""
