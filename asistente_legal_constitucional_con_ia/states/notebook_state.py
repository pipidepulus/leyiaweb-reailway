# asistente_legal_constitucional_con_ia/states/notebook_state.py
"""Estado para gestión de notebooks persistentes."""

import json
import reflex as rx
from datetime import datetime
from typing import List, Dict, Any, Optional
import reflex_local_auth
from ..models.database import Notebook, get_db_session
from sqlmodel import select
import dataclasses


@dataclasses.dataclass
class NotebookType:
    """Tipo para representar un notebook en el frontend."""
    id: int
    title: str
    content: str  # Cambiado de dict a str para markdown
    created_at: str
    updated_at: str
    notebook_type: str
    source_data: str


class NotebookState(reflex_local_auth.LocalAuthState):
    """Estado para gestionar notebooks del usuario."""
    
    notebooks: list[NotebookType] = []
    current_notebook: Optional[NotebookType] = None
    current_notebook_id: int = 0
    loading: bool = False
    error_message: str = ""
    
    # Estados para edición
    is_editing: bool = False
    edit_content: str = ""
    
    def set_edit_content(self, value: str):
        """Actualiza el contenido en edición."""
        self.edit_content = value
    
    # Propiedades computadas para el visor de notebooks
    @rx.var
    def current_notebook_content(self) -> str:
        """Obtiene el contenido markdown del notebook actual."""
        if self.current_notebook:
            return self.current_notebook.content
        return ""
    
    @rx.event
    async def create_notebook_from_chat(self, title: str, chat_messages: List[Dict[str, str]]):
        """Crea un notebook a partir de la conversación del chat."""
        if not self.is_authenticated:
            self.error_message = "Debes estar autenticado para crear notebooks."
            return
            
        self.loading = True
        try:
            # Convertir mensajes del chat a formato notebook
            notebook_content = self._convert_chat_to_notebook(chat_messages, title)
            
            with rx.session() as session:
                new_notebook = Notebook(
                    title=title,
                    content=json.dumps(notebook_content),
                    user_id=str(self.authenticated_user.id),
                    notebook_type="analysis"
                )
                session.add(new_notebook)
                session.commit()
                
                # Actualizar lista local
                await self.load_user_notebooks()
                
            yield rx.toast.success(f"Notebook '{title}' creado exitosamente.")
            
        except Exception as e:
            self.error_message = f"Error al crear notebook: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.loading = False
    
    @rx.event
    async def load_user_notebooks(self):
        """Carga todos los notebooks del usuario autenticado."""
        if not self.is_authenticated:
            self.notebooks = []
            return
            
        self.loading = True
        try:
            with rx.session() as session:
                statement = select(Notebook).where(
                    Notebook.user_id == self.authenticated_user.id
                ).order_by(Notebook.updated_at.desc())
                
                db_notebooks = session.exec(statement).all()
                
                self.notebooks = [
                    NotebookType(
                        id=nb.id,
                        title=nb.title,
                        content=nb.content,  # Ahora contenido directo
                        created_at=nb.created_at.isoformat(),
                        updated_at=nb.updated_at.isoformat(),
                        notebook_type=nb.notebook_type,
                        source_data=nb.source_data
                    )
                    for nb in db_notebooks
                ]
                
        except Exception as e:
            self.error_message = f"Error al cargar notebooks: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.loading = False
    
    @rx.event
    async def save_notebook(self, notebook_id: int, content: Dict[str, Any]):
        """Guarda cambios en un notebook existente."""
        if not self.is_authenticated:
            return
            
        self.loading = True
        try:
            with rx.session() as session:
                statement = select(Notebook).where(
                    Notebook.id == notebook_id,
                    Notebook.user_id == self.authenticated_user.id
                )
                notebook = session.exec(statement).first()
                
                if notebook:
                    notebook.content = json.dumps(content)
                    notebook.updated_at = datetime.now()
                    session.add(notebook)
                    session.commit()
                    
                    await self.load_user_notebooks()
                    yield rx.toast.success("Notebook guardado exitosamente.")
                else:
                    yield rx.toast.error("Notebook no encontrado.")
                    
        except Exception as e:
            self.error_message = f"Error al guardar notebook: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.loading = False
    
    @rx.event
    async def delete_notebook(self, notebook_id: int):
        """Elimina un notebook."""
        if not self.is_authenticated:
            return
            
        self.loading = True
        try:
            with rx.session() as session:
                statement = select(Notebook).where(
                    Notebook.id == notebook_id,
                    Notebook.user_id == self.authenticated_user.id
                )
                notebook = session.exec(statement).first()
                
                if notebook:
                    session.delete(notebook)
                    session.commit()
                    
                    # Recargar la lista de notebooks
                    async for event in self.load_user_notebooks():
                        yield event
                    yield rx.toast.success("Notebook eliminado exitosamente.")
                else:
                    yield rx.toast.error("Notebook no encontrado.")
                    
        except Exception as e:
            self.error_message = f"Error al eliminar notebook: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.loading = False

    @rx.event
    async def set_current_notebook(self, notebook_id: int):
        """Establece el notebook actual para edición."""
        if not self.is_authenticated:
            return
            
        try:
            with rx.session() as session:
                statement = select(Notebook).where(
                    Notebook.id == notebook_id,
                    Notebook.user_id == self.authenticated_user.id
                )
                notebook = session.exec(statement).first()
                
                if notebook:
                    self.current_notebook = NotebookType(
                        id=notebook.id,
                        title=notebook.title,
                        content=notebook.content,  # Contenido directo
                        created_at=notebook.created_at.isoformat(),
                        updated_at=notebook.updated_at.isoformat(),
                        notebook_type=notebook.notebook_type,
                        source_data=notebook.source_data
                    )
                else:
                    self.error_message = "Notebook no encontrado."
                    
        except Exception as e:
            self.error_message = f"Error al cargar notebook: {str(e)}"

    @rx.event
    async def load_notebook_from_url(self, notebook_id: str):
        """Carga un notebook específico desde el ID de la URL."""
        try:
            self.current_notebook_id = int(notebook_id)
            await self.set_current_notebook(self.current_notebook_id)
        except (ValueError, TypeError):
            self.error_message = "ID de notebook inválido"

    def _convert_chat_to_notebook(self, chat_messages: List[Dict[str, str]], title: str) -> Dict[str, Any]:
        """Convierte mensajes del chat a formato notebook."""
        cells = []
        
        # Celda de título
        cells.append({
            "cell_type": "markdown",
            "source": [f"# {title}\n\n", f"*Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"]
        })
        
        # Convertir cada intercambio usuario-asistente
        for i, message in enumerate(chat_messages):
            if message["role"] == "user":
                cells.append({
                    "cell_type": "markdown",
                    "source": [f"## Consulta {(i//2) + 1}\n\n", f"{message['content']}\n\n"]
                })
            elif message["role"] == "assistant":
                cells.append({
                    "cell_type": "markdown", 
                    "source": [f"### Respuesta\n\n", f"{message['content']}\n\n"]
                })
        
        return {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

    @rx.event
    async def download_notebook_file(self, notebook_id: int):
        """Permite descargar un notebook como archivo .ipynb."""
        if not self.is_authenticated:
            yield rx.toast.error("Debes estar autenticado para descargar notebooks.")
            return
            
        try:
            with rx.session() as session:
                notebook = session.exec(
                    select(Notebook).where(
                        Notebook.id == notebook_id,
                        Notebook.user_id == self.authenticated_user.id
                    )
                ).first()
                
                if not notebook:
                    yield rx.toast.error("Notebook no encontrado.")
                    return
                
                # Crear archivo markdown para descarga
                filename = f"{notebook.title.replace(' ', '_')}.md"
                
                yield rx.download(
                    data=notebook.content,  # Contenido markdown directo
                    filename=filename
                )
                
        except Exception as e:
            yield rx.toast.error(f"Error descargando notebook: {str(e)}")
    
    @rx.event
    async def start_editing(self):
        """Inicia el modo de edición."""
        if self.current_notebook:
            self.is_editing = True
            self.edit_content = self.current_notebook.content
    
    @rx.event
    async def cancel_editing(self):
        """Cancela el modo de edición."""
        self.is_editing = False
        self.edit_content = ""
    
    @rx.event
    async def save_notebook(self):
        """Guarda los cambios del notebook."""
        if not self.current_notebook or not self.is_editing:
            return
            
        self.loading = True
        try:
            with get_db_session() as session:
                statement = select(Notebook).where(
                    Notebook.id == self.current_notebook.id,
                    Notebook.user_id == str(self.authenticated_user.id)
                )
                notebook = session.exec(statement).first()
                
                if notebook:
                    notebook.content = self.edit_content
                    notebook.updated_at = datetime.now()
                    session.add(notebook)
                    session.commit()
                    
                    # Actualizar el notebook actual
                    self.current_notebook.content = self.edit_content
                    self.is_editing = False
                    self.edit_content = ""
                    
                    yield rx.toast.success("Notebook guardado exitosamente.")
                else:
                    yield rx.toast.error("Notebook no encontrado.")
                    
        except Exception as e:
            self.error_message = f"Error al guardar notebook: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.loading = False
