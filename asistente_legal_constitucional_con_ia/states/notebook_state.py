# asistente_legal_constitucional_con_ia/states/notebook_state.py
"""Estado para gestión de notebooks persistentes."""

import json
import reflex as rx
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.database import Notebook
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
    source_data: Optional[str]  # Cambiar a Optional


class NotebookState(rx.State):
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
            try:
                # Intentar parsear como JSON primero
                content_data = json.loads(self.current_notebook.content)
                return self._convert_notebook_to_markdown(content_data)
            except (json.JSONDecodeError, TypeError):
                # Si no es JSON válido, asumir que es markdown directo
                return self.current_notebook.content
        return ""
    
    @rx.event
    async def create_notebook_from_chat(self, title: str, chat_messages: List[Dict[str, str]]):
        """Crea un notebook a partir de la conversación del chat."""
        self.loading = True
        try:
            # Convertir mensajes del chat a formato notebook
            notebook_content = self._convert_chat_to_notebook(chat_messages, title)
            
            with rx.session() as session:
                new_notebook = Notebook(
                    title=title,
                    content=json.dumps(notebook_content),
                    notebook_type="analysis",
                    workspace_id="public"  # Nuevo esquema sin user_id
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
        """Carga todos los notebooks del usuario."""
        self.loading = True
        try:
            with rx.session() as session:
                db_notebooks = session.exec(
                Notebook.select().where(
                    Notebook.workspace_id == "public"
                ).order_by(Notebook.updated_at.desc())
            ).all()
                
                self.notebooks = [
                    NotebookType(
                        id=nb.id,
                        title=nb.title,
                        content=nb.content,  # Ahora contenido directo
                        created_at=nb.created_at.isoformat(),
                        updated_at=nb.updated_at.isoformat(),
                        notebook_type=nb.notebook_type,
                        source_data=nb.source_data or ""  # Manejar None
                    )
                    for nb in db_notebooks
                ]
                
        except Exception as e:
            self.error_message = f"Error al cargar notebooks: {str(e)}"
            yield rx.toast.error(self.error_message)
        finally:
            self.loading = False
    
    @rx.event
    async def delete_notebook(self, notebook_id: int):
        """Elimina un notebook."""
        self.loading = True
        try:
            with rx.session() as session:
                notebook = session.exec(
                Notebook.select().where(
                    Notebook.id == notebook_id,
                    Notebook.workspace_id == "public"
                )
            ).first()
                
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

    async def _set_current_notebook_internal(self, notebook_id: int) -> bool:
        """Versión interna sin yield para poder usar con await."""
        self.loading = True
        try:
            with rx.session() as session:
                notebook = session.exec(
                    Notebook.select().where(
                        Notebook.id == notebook_id,
                        Notebook.workspace_id == "public"
                    )
                ).first()
                
                if notebook:
                    self.current_notebook = NotebookType(
                        id=notebook.id,
                        title=notebook.title,
                        content=notebook.content,  # Contenido directo
                        created_at=notebook.created_at.isoformat(),
                        updated_at=notebook.updated_at.isoformat(),
                        notebook_type=notebook.notebook_type,
                        source_data=notebook.source_data or ""  # Manejar None
                    )
                    return True
                else:
                    self.error_message = "Notebook no encontrado."
                    return False
                    
        except Exception as e:
            self.error_message = f"Error al cargar notebook: {str(e)}"
            return False
        finally:
            self.loading = False

    @rx.event
    async def set_current_notebook(self, notebook_id: int):
        """Establece el notebook actual para edición."""
        success = await self._set_current_notebook_internal(notebook_id)
        if not success:
            yield rx.toast.error(self.error_message)

    @rx.event
    async def load_notebook_on_page_load(self):
        """Carga el notebook cuando se monta la página, obteniendo el ID de la URL."""
        try:
            # Obtener el notebook_id desde el estado del router
            notebook_id = self.router.page.params.get("notebook_id")
            
            if notebook_id:
                try:
                    self.current_notebook_id = int(notebook_id)
                    
                    success = await self._set_current_notebook_internal(self.current_notebook_id)
                    if not success:
                        yield rx.toast.error(self.error_message)
                        
                except (ValueError, TypeError) as e:
                    self.error_message = f"ID de notebook inválido: {str(e)}"
                    yield rx.toast.error(self.error_message)
            else:
                self.error_message = "No se encontró el ID del notebook en la URL"
                yield rx.toast.error(self.error_message)
                
        except Exception as e:
            self.error_message = f"Error cargando notebook: {str(e)}"
            yield rx.toast.error(self.error_message)

    @rx.event
    async def load_notebook_from_url(self, notebook_id: str):
        """Carga un notebook específico desde el ID de la URL."""
        try:
            self.current_notebook_id = int(notebook_id)
            
            success = await self._set_current_notebook_internal(self.current_notebook_id)
            if not success:
                yield rx.toast.error(self.error_message)
                
        except (ValueError, TypeError) as e:
            self.error_message = f"ID de notebook inválido: {str(e)}"
            yield rx.toast.error(self.error_message)

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
        try:
            with rx.session() as session:
                notebook = session.exec(
                    Notebook.select().where(
                        Notebook.id == notebook_id,
                        Notebook.workspace_id == "public"
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
    
    def _clean_markdown_for_editing(self, markdown_content: str) -> str:
        """Convierte markdown a texto plano pero conservando la estructura visual."""
        lines = markdown_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Saltear líneas de separación
            if line_stripped == '---':
                continue
            
            # Título principal - quitar # pero mantener el texto
            if line_stripped.startswith('# '):
                title = line_stripped[2:].strip()
                cleaned_lines.append(title)
                cleaned_lines.append("")
                continue
            
            # Metadata de generación - simplificar 
            if '*Notebook generado automáticamente' in line_stripped or '*Generado automáticamente' in line_stripped:
                cleaned_lines.append(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                cleaned_lines.append("")
                continue
            
            # Respuesta del Asistente - quitar ### pero mantener emoji y texto
            if line_stripped.startswith('### 🤖 Respuesta del Asistente'):
                cleaned_lines.append("🤖 Respuesta del Asistente")
                cleaned_lines.append("")
                continue
            elif line_stripped.startswith('### Respuesta del Asistente'):
                cleaned_lines.append("🤖 Respuesta del Asistente")
                cleaned_lines.append("")
                continue
            
            # Consulta - quitar ## pero mantener emoji y texto
            if line_stripped.startswith('## 🙋 Consulta '):
                consulta_text = line_stripped[3:].strip()  # Quitar "## "
                cleaned_lines.append(consulta_text)
                cleaned_lines.append("")
                continue
            elif line_stripped.startswith('## Consulta '):
                consulta_text = line_stripped[3:].strip()  # Quitar "## "
                cleaned_lines.append(f"🙋 {consulta_text}")
                cleaned_lines.append("")
                continue
            
            # Líneas vacías - manejar espaciado
            if not line_stripped:
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue
            
            # Contenido normal - mantener tal como está
            cleaned_lines.append(line_stripped)
        
        # Limpiar múltiples líneas vacías consecutivas
        result_lines = []
        prev_empty = False
        
        for line in cleaned_lines:
            if line == "":
                if not prev_empty:
                    result_lines.append(line)
                prev_empty = True
            else:
                result_lines.append(line)
                prev_empty = False
        
        return '\n'.join(result_lines).strip()

    def _convert_plain_text_to_markdown(self, plain_text: str) -> str:
        """Convierte texto plano de vuelta a markdown para guardar."""
        lines = plain_text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Título principal (primera línea no vacía sin prefijos especiales)
            if line_stripped and not line_stripped.startswith(('🤖', '🙋', 'Generado:')):
                # Si es la primera línea significativa, tratarla como título
                if not any(ml.strip() and not ml.startswith(('*Generado', '#')) for ml in markdown_lines):
                    markdown_lines.append(f"# {line_stripped}")
                    markdown_lines.append("")
                    continue
            
            # Metadata de generación
            if line_stripped.startswith('Generado:'):
                date_part = line_stripped.replace('Generado:', '').strip()
                markdown_lines.append(f"*Notebook generado automáticamente el {date_part}*")
                markdown_lines.append("")
                continue
            
            # Respuesta del Asistente
            if line_stripped.startswith('🤖 Respuesta del Asistente'):
                markdown_lines.append("### 🤖 Respuesta del Asistente")
                markdown_lines.append("")
                continue
            
            # Consulta
            if line_stripped.startswith('🙋 Consulta '):
                markdown_lines.append(f"## {line_stripped}")
                markdown_lines.append("")
                continue
            
            # Líneas vacías
            if not line_stripped:
                if markdown_lines and markdown_lines[-1] != "":
                    markdown_lines.append("")
                continue
            
            # Contenido normal
            markdown_lines.append(line_stripped)
        
        return '\n'.join(markdown_lines).strip()

    @rx.event
    async def start_editing(self):
        """Inicia el modo de edición."""
        if self.current_notebook:
            self.is_editing = True
            # Usar contenido markdown limpio para edición más amigable
            raw_markdown = self.current_notebook_content
            self.edit_content = self._clean_markdown_for_editing(raw_markdown)
    
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
            with rx.session() as session:
                notebook = session.exec(
                    Notebook.select().where(
                        Notebook.id == self.current_notebook.id
                    )
                ).first()
                
                if notebook:
                    # Convertir el texto plano editado de vuelta a markdown
                    markdown_content = self._convert_plain_text_to_markdown(self.edit_content)
                    
                    # Guardar el contenido markdown 
                    notebook.content = markdown_content
                    notebook.updated_at = datetime.now()
                    session.add(notebook)
                    session.commit()
                    
                    # Actualizar el notebook actual con el contenido markdown
                    self.current_notebook.content = markdown_content
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

    def _convert_notebook_to_markdown(self, notebook_data: Dict[str, Any]) -> str:
        """Convierte datos de notebook a markdown para visualización."""
        if not notebook_data or "cells" not in notebook_data:
            return "# Notebook vacío\n\nEste notebook no tiene contenido."
        
        markdown_content = []
        
        for cell in notebook_data["cells"]:
            cell_type = cell.get("cell_type", "code")
            source = cell.get("source", [])
            
            # Convertir source a string si es una lista
            if isinstance(source, list):
                cell_content = "".join(source)
            else:
                cell_content = str(source)
            
            if cell_type == "markdown":
                markdown_content.append(cell_content)
            elif cell_type == "code":
                markdown_content.append(f"```python\n{cell_content}\n```")
            
        return "\n\n".join(markdown_content)
