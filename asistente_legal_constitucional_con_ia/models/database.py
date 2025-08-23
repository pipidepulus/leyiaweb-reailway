"""Modelos de base de datos para la aplicación."""

from datetime import datetime
from typing import Optional

import reflex as rx

# CAMBIO 1: SQLModel → rx.Model


class Notebook(rx.Model, table=True):
    """Modelo para almacenar notebooks generados."""

    title: str
    content: str  # JSON con el contenido del notebook
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    notebook_type: str = "analysis"
    source_data: Optional[str] = None
    workspace_id: str = "public"


# CAMBIO 2: SQLModel → rx.Model


class AudioTranscription(rx.Model, table=True):
    """Modelo para almacenar transcripciones de audio."""

    filename: str
    transcription_text: str  # Consistente con el estado
    audio_duration: str = "0:00"  # ← CAMBIAR: Valor por defecto directo
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    notebook_id: Optional[int] = None
    workspace_id: str = "public"
