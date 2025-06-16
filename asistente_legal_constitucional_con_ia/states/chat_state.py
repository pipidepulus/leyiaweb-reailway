import reflex as rx
from typing import TypedDict
import os
import io
import tempfile
import json
import asyncio
from openai import OpenAI, APIError
from dotenv import load_dotenv
from asistente_legal_constitucional_con_ia.util.text_extraction import extract_text_from_bytes
from asistente_legal_constitucional_con_ia.util.scraper import (
    scrape_proyectos_recientes_camara,
)
import logging
import fitz
import pytesseract
from pdf2image import convert_from_bytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asistente_legal")

load_dotenv()


class Message(TypedDict):
    role: str
    content: str


class FileInfo(TypedDict):
    file_id: str
    filename: str


class ChatState(rx.State):
    """Manages the chat interface, file uploads, and AI interaction."""

    messages: list[Message] = []
    thread_id: str | None = None
    file_info_list: list[FileInfo] = []
    processing: bool = False
    uploading: bool = False
    upload_progress: int = 0
    ocr_progress: str = ""
    proyectos_recientes_df: str = ""
    assistant_id: str = os.getenv(
        "ASSISTANT_ID_CONSTITUCIONAL", ""
    )
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    streaming_response: str = ""
    streaming: bool = False
    thinking_seconds: int = 0
    upload_error: str = ""
    focus_chat_input: bool = False # NUEVA VARIABLE

    @staticmethod
    def get_client(api_key: str):
        if api_key:
            return OpenAI(api_key=api_key)
        return None

    @rx.var
    def has_api_keys(self) -> bool:
        return bool(
            self.assistant_id and self.openai_api_key
        )

    @rx.var
    def proyectos_data(self) -> list[dict]:
        if not self.proyectos_recientes_df:
            return []
        try:
            return json.loads(self.proyectos_recientes_df)
        except json.JSONDecodeError:
            return []

    @rx.event
    async def handle_upload(
        self, files: list[rx.UploadFile]
    ):
        logger.info(f"handle_upload: {len(files) if files else 0} archivos recibidos")
        self.upload_error = ""
        if not files:
            logger.warning("No se seleccionaron archivos.")
            self.upload_error = "No se seleccionaron archivos."
            yield rx.toast.error(
                "No se seleccionaron archivos."
            )
            return
        self.uploading = True
        self.upload_progress = 0
        self.ocr_progress = ""
        yield
        client = ChatState.get_client(self.openai_api_key)
        if not client:
            logger.error("Credenciales de OpenAI no configuradas.")
            self.upload_error = "Credenciales de OpenAI no configuradas."
            yield rx.toast.error(
                "Credenciales de OpenAI no configuradas."
            )
            self.uploading = False
            return
        for i, file in enumerate(files):
            # Validar si el archivo ya fue subido por nombre
            if any(f["filename"] == file.name for f in self.file_info_list):
                logger.warning(f"Archivo duplicado: {file.name}")
                self.upload_error = f"El archivo '{file.name}' ya fue subido."
                yield rx.toast.error(f"El archivo '{file.name}' ya fue subido.")
                continue
            try:
                logger.info(f"Procesando archivo: {file.name}")
                upload_data = await file.read()
                ocr_progress_ref = self
                def progress_callback(page, total):
                    ocr_progress_ref.ocr_progress = f"OCR página {page}/{total} de '{file.name}'"
                # Extracción directa
                extracted_text = extract_text_from_bytes(
                    upload_data, file.name
                )
                # Si fue PDF y la extracción directa no obtuvo suficiente texto, hacer OCR aquí
                if file.name.lower().endswith(".pdf") and (not extracted_text or len(extracted_text.strip()) < 100):
                    self.uploading = False  # Detener mensaje de subida antes de mostrar OCR
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(upload_data)
                        tmp_path = tmp.name
                    try:
                        images = convert_from_bytes(upload_data, dpi=200)
                        total_pages = len(images)
                        ocr_text = ""
                        for i, image in enumerate(images):
                            self.ocr_progress = f"Procesando OCR: página {i+1}/{total_pages} de '{file.name}'"
                            logger.info(f"[UI FEEDBACK] {self.ocr_progress}")
                            yield
                            await asyncio.sleep(0.5)
                            ocr_text += pytesseract.image_to_string(image, lang="spa+eng") + "\n"
                        extracted_text = ocr_text
                    finally:
                        os.remove(tmp_path)
                # Limpiar ocr_progress solo al final
                self.ocr_progress = ""
                if (
                    not extracted_text
                    or not extracted_text.strip()
                ):
                    logger.warning(f"No se pudo extraer texto de '{file.name}'.")
                    self.upload_error = f"No se pudo extraer texto de '{file.name}'."
                    yield rx.toast.warning(
                        f"No se pudo extraer texto de '{file.name}'."
                    )
                    continue
                with tempfile.NamedTemporaryFile(
                    mode="w+",
                    delete=False,
                    suffix=".txt",
                    encoding="utf-8",
                ) as tmp_file:
                    tmp_file.write(extracted_text)
                    tmp_path = tmp_file.name
                try:
                    with open(tmp_path, "rb") as f_obj:
                        response = client.files.create(
                            file=f_obj, purpose="assistants"
                        )
                    self.file_info_list.append(
                        {
                            "file_id": response.id,
                            "filename": file.name,
                        }
                    )
                    logger.info(f"'{file.name}' procesado y subido con id {response.id}.")
                    self.upload_error = ""
                    yield rx.toast.success(
                        f"'{file.name}' procesado y subido."
                    )
                except APIError as e:
                    logger.error(f"Error al subir '{file.name}': {e.message}")
                    self.upload_error = f"Error al subir '{file.name}': {e.message}"
                    yield rx.toast.error(
                        f"Error al subir '{file.name}': {e.message}"
                    )
                finally:
                    os.remove(tmp_path)
            except Exception as e:
                logger.error(f"Error procesando '{file.name}': {str(e)}")
                self.upload_error = f"Error procesando '{file.name}': {str(e)}"
                yield rx.toast.error(
                    f"Error procesando '{file.name}': {str(e)}"
                )
            self.upload_progress = round(
                (i + 1) / len(files) * 100
            )
            yield
        self.uploading = False
        self.ocr_progress = ""
        logger.info("handle_upload: proceso terminado")
        yield

    @rx.event
    def delete_file(self, file_id: str):
        client = ChatState.get_client(self.openai_api_key)
        if not client:
            yield rx.toast.error(
                "Credenciales de OpenAI no configuradas."
            )
            return
        filename = next(
            (
                f["filename"]
                for f in self.file_info_list
                if f["file_id"] == file_id
            ),
            "archivo",
        )
        try:
            client.files.delete(file_id)
            self.file_info_list = [
                f
                for f in self.file_info_list
                if f["file_id"] != file_id
            ]
            yield rx.toast.success(
                f"'{filename}' eliminado."
            )
        except APIError as e:
            yield rx.toast.error(
                f"Error eliminando '{filename}': {e.message}"
            )

    @rx.event(background=True)
    async def scrape_proyectos(self):
        async with self:
            self.proyectos_recientes_df = ""
        df = scrape_proyectos_recientes_camara(15)
        async with self:
            if df is not None:
                self.proyectos_recientes_df = df.to_json(
                    orient="records"
                )
            else:
                self.proyectos_recientes_df = "[]"
                yield rx.toast.error(
                    "No se pudieron obtener los proyectos."
                )

    @rx.event(background=True) # Convertido a tarea de fondo
    async def thinking_timer(self):
        async with self: # Envolver la inicialización en el contexto asíncrono
            self.thinking_seconds = 0
        logger.info(f"thinking_timer: Iniciado (background). self.processing={self.processing}")
        while self.processing: # self.processing se lee, no se modifica aquí directamente en el bucle while
            await asyncio.sleep(1) 
            async with self: # Envolver la modificación de estado en el contexto asíncrono
                self.thinking_seconds += 1
        logger.info(f"thinking_timer: Detenido (background). self.processing={self.processing}, self.thinking_seconds={self.thinking_seconds}s")

    @rx.event
    def send_message(self, form_data: dict):
        user_prompt = form_data.get("prompt", "").strip()
        logger.info(f"send_message: INICIO. prompt='{user_prompt}', current self.processing={self.processing}")
        if not user_prompt or self.processing:
            logger.warning("Prompt vacío o ya procesando.")
            return
        if not self.has_api_keys:
            logger.error("Las credenciales de OpenAI no están configuradas en el servidor.")
            return rx.toast.error(
                "Las credenciales de OpenAI no están configuradas en el servidor."
            )
        self.processing = True
        self.streaming = True
        self.streaming_response = ""
        self.thinking_seconds = 0 # Esto está bien aquí, send_message no es background
        self.messages.append(
            {"role": "user", "content": user_prompt}
        )
        self.messages.append(
            {"role": "assistant", "content": "Estoy pensando..."}
        )
        logger.info("send_message: Disparando thinking_timer y generate_response_streaming. self.processing ahora es True.")
        yield ChatState.thinking_timer
        yield
        yield ChatState.generate_response_streaming # Volvemos a generate_response_streaming
        # yield ChatState.simple_background_test # Comentamos la prueba
        logger.info("send_message: FIN (eventos en segundo plano iniciados).")

    @rx.event(background=True)
    async def simple_background_test(self):
        logger.info("simple_background_test: INICIO Y FIN")
        async with self:
            # Simular un pequeño trabajo y resetear processing para la prueba
            self.messages[-1]["content"] = "Respuesta de prueba de simple_background_test"
            self.processing = False
            self.streaming = False
            self.thinking_seconds = 0
        logger.info(f"simple_background_test: self.processing ahora es {self.processing}")

    @rx.event(background=True)
    async def generate_response_streaming(self):
        logger.info(f"generate_response_streaming: INICIO. self.processing={self.processing}, self.thread_id={self.thread_id}")
        client = ChatState.get_client(self.openai_api_key)
        
        try:
            last_user_message = next((m["content"] for m in reversed(self.messages) if m["role"] == "user"), None)
            if not last_user_message:
                logger.error("No se encontró el último mensaje del usuario.")
                async with self:
                    self.messages[-1]["content"] = "Error: No se encontró el mensaje del usuario."
                    self.processing = False
                    self.streaming = False
                    self.thinking_seconds = 0
                return

            if not self.thread_id:
                thread = await asyncio.to_thread(client.beta.threads.create)
                async with self:
                    self.thread_id = thread.id
            logger.info(f"generate_response_streaming: thread_id actualizado a {self.thread_id}")

            attachments_for_message = []
            if self.file_info_list:
                files_to_attach = self.file_info_list[-3:]
                attachments_for_message = [
                    {"file_id": fi["file_id"], "tools": [{"type": "file_search"}]} 
                    for fi in files_to_attach
                ]
            
            await asyncio.to_thread(
                client.beta.threads.messages.create,
                thread_id=self.thread_id,
                role="user",
                content=last_user_message,
                attachments=attachments_for_message,
            )
            logger.info("generate_response_streaming: Mensaje de usuario creado en el thread.")

            # Usar stream=True para la respuesta del asistente
            run_stream = await asyncio.to_thread(
                client.beta.threads.runs.create,
                thread_id=self.thread_id,
                assistant_id=self.assistant_id,
                stream=True
            )
            logger.info("generate_response_streaming: Run creado con stream=True.")

            first_chunk_processed = False
            accumulated_response = ""
            for event in run_stream:
                if event.event == 'thread.message.delta':
                    delta = event.data.delta
                    if delta.content:
                        text_chunk = delta.content[0].text.value
                        if text_chunk:
                            async with self:
                                if not first_chunk_processed:
                                    self.messages[-1]["content"] = "" # Limpiar "Estoy pensando..."
                                    self.streaming_response = ""
                                    first_chunk_processed = True
                                accumulated_response += text_chunk
                                self.streaming_response = accumulated_response # Actualizar para el estado
                                self.messages[-1]["content"] = accumulated_response # Actualizar para la UI
                            yield # Actualizar UI con el nuevo chunk
                
                elif event.event == 'thread.run.requires_action':
                    logger.info(f"Run requires action: {event.data.required_action.submit_tool_outputs.tool_calls}")
                    # Aquí se manejarían las tool calls. Por ahora, si file_search es la única,
                    # OpenAI debería manejarla internamente si los archivos están adjuntos.
                    # Si se necesitan enviar tool_outputs explícitos:
                    # run_id = event.data.id
                    # tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
                    # tool_outputs = []
                    # for call in tool_calls:
                    #    # Procesar llamada y generar output
                    #    tool_outputs.append({"tool_call_id": call.id, "output": "..."})
                    #
                    # # Re-subir el stream con los outputs
                    # run_stream = await asyncio.to_thread(
                    # client.beta.threads.runs.submit_tool_outputs,
                    # thread_id=self.thread_id,
                    # run_id=run_id,
                    # tool_outputs=tool_outputs,
                    # stream=True
                    # )
                    # logger.info("Tool outputs submitted, continuing stream.")
                    # continue # Para continuar procesando el nuevo stream
                    pass # Por ahora, asumimos que file_search se maneja sin intervención explícita aquí.

                elif event.event == 'thread.run.completed':
                    logger.info("Stream: Run completed.")
                    async with self: # Asegurar que el estado final de streaming_response sea el completo
                        self.streaming_response = accumulated_response
                    break 
                elif event.event == 'thread.run.failed':
                    logger.error(f"Stream: Run failed. Run data: {event.data}")
                    error_message = "Error del asistente."
                    if event.data.last_error:
                        error_message = f"Error del asistente: {event.data.last_error.message}"
                    async with self:
                        self.messages[-1]["content"] = error_message
                    break
                elif event.event == 'error': # Evento de error genérico del stream
                    logger.error(f"Stream: Error event: {event.data}")
                    async with self:
                        self.messages[-1]["content"] = "Error en el stream del asistente."
                    break
            
            logger.info("generate_response_streaming: Streaming con iteración manual completado.")

        except APIError as e:
            logger.error(f"Error de API de OpenAI: {e.message}")
            async with self:
                self.messages[-1]["content"] = f"Error de API: {e.message}"
        except Exception as e:
            logger.error(f"Error inesperado en generate_response_streaming: {str(e)}", exc_info=True)
            async with self:
                self.messages[-1]["content"] = f"Error inesperado: {str(e)}"
        finally:
            logger.info(f"generate_response_streaming: BLOQUE FINALLY. self.processing ANTES: {self.processing}, self.streaming ANTES: {self.streaming}")
            async with self:
                self.processing = False
                self.streaming = False 
                self.thinking_seconds = 0
                self.focus_chat_input = True # ACTIVAR EL DISPARADOR
            yield 
            
            # Programar el reseteo del disparador
            yield ChatState.reset_focus_trigger
            # REMOVER el rx.call_script anterior
            logger.info(f"generate_response_streaming: FIN. self.processing DESPUÉS: {self.processing}, self.streaming DESPUÉS: {self.streaming}")

    @rx.event # No longer async, no async with self
    def reset_focus_trigger(self):
        """Resetea el disparador de enfoque para que pueda ser usado de nuevo."""
        self.focus_chat_input = False
        # No yield here, direct state modification

    def _get_available_functions(self) -> list[dict]:
        """
        Devuelve un diccionario de funciones que el asistente puede llamar.
        Por ahora, solo tenemos 'file_search' que es manejado internamente por OpenAI.
        Si tuviéramos funciones personalizadas (custom tools), se mapearían aquí.
        """
        logger.info("Llamando a _get_available_functions. Actualmente no hay funciones personalizadas mapeadas.")
        return {}

    # Si tienes otras funciones de estado o métodos, van aquí...