# asistente_legal_constitucional_con_ia/models/database.py
"""Modelos de base de datos para la aplicación."""

import reflex as rx
from sqlmodel import Field, SQLModel, Session, create_engine
from typing import Optional
from datetime import datetime
import os
from contextlib import contextmanager


# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///legal_assistant.db")
engine = create_engine(DATABASE_URL, echo=False)


@contextmanager
def get_db_session():
    """Contextmanager para obtener una sesión de base de datos."""
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Notebook(SQLModel, table=True):
    """Modelo para almacenar notebooks generados."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str = Field()  # JSON con el contenido del notebook
    user_id: str = Field(max_length=100)  # ID del usuario que creó el notebook
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    notebook_type: str = Field(default="analysis")  # "analysis" o "transcription"
    source_data: Optional[str] = Field(default=None)  # Datos fuente si aplica
    

class AudioTranscription(SQLModel, table=True):
    """Modelo para almacenar transcripciones de audio."""
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    transcription: str = Field()
    user_id: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
    notebook_id: Optional[int] = Field(default=None, foreign_key="notebook.id")
