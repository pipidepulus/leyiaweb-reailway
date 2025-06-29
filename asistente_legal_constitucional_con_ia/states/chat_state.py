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
from asistente_legal_constitucional_con_ia.util.tools import buscar_en_internet

import logging
import fitz
import pytesseract
from pdf2image import convert_from_bytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asistente_legal")

load_dotenv()

# Define la herramienta para que el Asistente la entienda
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "buscar_en_internet",
            "description": "Busca en internet información actualizada cuando la respuesta no se encuentra en los documentos del knowledge base. Útil para noticias, datos recientes o para encontrar fuentes externas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La consulta de búsqueda precisa para buscar en internet. Debe ser específica."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Un mapa para llamar a tus funciones Python fácilmente
AVAILABLE_TOOLS = {
    "buscar_en_internet": buscar_en_internet,
}
# --- FIN DEL NUEVO CÓDIGO ---

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
    focus_chat_input: bool = False
    
    # ÚNICO CAMBIO: Añadimos esta variable para el input controlado
    current_question: str = ""
    
    # Variables que estaban en tu código original, las mantenemos por si acaso
    chat_history: list = []
    current_answer: str = ""
    error_message: str = ""
    is_uploading: bool = False
    uploaded_file_name: str = ""
    file_context: str = ""

    @staticmethod
    def get_client(api_key: str):
        if api_key:
            return OpenAI(api_key=api_key)
        return None

    def scroll_to_bottom(self):
        """Hacer scroll al final del chat de forma suave"""
        return rx.call_script("""
            const container = document.getElementById('chat-messages-container');
            if (container) {
                // Usar requestAnimationFrame para mejor performance durante streaming
                requestAnimationFrame(() => {
                    container.scrollTop = container.scrollHeight;
                });
            }
        """)

    def focus_input(self):
        """Posicionar el cursor en el input del usuario"""
        return rx.call_script("""
            setTimeout(() => {
                const input = document.getElementById('chat-input-box');
                if (input) {
                    input.focus();
                    // Posicionar cursor al final del texto
                    input.setSelectionRange(input.value.length, input.value.length);
                }
            }, 200);
        """)

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
        logger.info(
            f"handle_upload: {len(files) if files else 0} archivos recibidos")
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
                extracted_text = extract_text_from_bytes(
                    upload_data, file.name
                )
                if file.name.lower().endswith(".pdf") and (not extracted_text or len(extracted_text.strip()) < 100):
                    self.uploading = False
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
                            ocr_text += pytesseract.image_to_string(
                                image, lang="spa+eng") + "\n"
                        extracted_text = ocr_text
                    finally:
                        os.remove(tmp_path)
                self.ocr_progress = ""
                if (
                    not extracted_text
                    or not extracted_text.strip()
                ):
                    logger.warning(
                        f"No se pudo extraer texto de '{file.name}'.")
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
                    logger.info(
                        f"'{file.name}' procesado y subido con id {response.id}.")
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

    @rx.event(background=True)
    async def thinking_timer(self):
        async with self:
            self.thinking_seconds = 0
        logger.info(
            f"thinking_timer: Iniciado (background). self.processing={self.processing}")
        while self.processing:
            await asyncio.sleep(1)
            async with self:
                self.thinking_seconds += 1
        logger.info(
            f"thinking_timer: Detenido (background). self.processing={self.processing}, self.thinking_seconds={self.thinking_seconds}s")

    @rx.event
    def send_message(self, form_data: dict):
        # ÚNICO CAMBIO: Usamos self.current_question en lugar de form_data
        user_prompt = self.current_question.strip()
        logger.info(
            f"send_message: INICIO. prompt='{user_prompt}', current self.processing={self.processing}")
        if not user_prompt or self.processing:
            logger.warning("Prompt vacío o ya procesando.")
            return
        
        # Limpiamos el input en la UI
        self.current_question = ""

         # --- CAMBIO CLAVE: LIMPIAR EL INPUT EN EL FRONTEND ---
        # Le decimos al navegador que encuentre el textarea por su ID y vacíe su valor.
        yield rx.call_script("document.getElementById('chat-input-box').value = ''")
        
        if not self.has_api_keys:
            logger.error(
                "Las credenciales de OpenAI no están configuradas en el servidor.")
            return rx.toast.error(
                "Las credenciales de OpenAI no están configuradas en el servidor."
            )
        self.processing = True
        self.streaming = True
        self.streaming_response = ""
        self.thinking_seconds = 0
        self.messages.append(
            {"role": "user", "content": user_prompt}
        )
        self.messages.append(
            {"role": "assistant", "content": "Estoy pensando..."}
        )
        logger.info(
            "send_message: Disparando thinking_timer y generate_response_streaming. self.processing ahora es True.")
        yield ChatState.scroll_to_bottom  # Autoscroll al agregar mensaje del usuario
        yield ChatState.thinking_timer
        #yield
        yield ChatState.generate_response_streaming
        logger.info("send_message: FIN (eventos en segundo plano iniciados).")

    @rx.event(background=True)
    async def simple_background_test(self):
        logger.info("simple_background_test: INICIO Y FIN")
        async with self:
            self.messages[-1]["content"] = "Respuesta de prueba de simple_background_test"
            self.processing = False
            self.streaming = False
            self.thinking_seconds = 0
        logger.info(
            f"simple_background_test: self.processing ahora es {self.processing}")

    @rx.event(background=True)
    async def generate_response_streaming(self):
        logger.info(
            f"generate_response_streaming: INICIO. self.processing={self.processing}, self.thread_id={self.thread_id}")
        client = ChatState.get_client(self.openai_api_key)

        try:
            last_user_message = next((m["content"] for m in reversed(
                self.messages) if m["role"] == "user"), None)
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
            logger.info(
                f"generate_response_streaming: thread_id actualizado a {self.thread_id}")

            attachments_for_message = []
            if self.file_info_list:
                files_to_attach = self.file_info_list[-3:]
                attachments_for_message = [
                    {"file_id": fi["file_id"], "tools": [
                        {"type": "file_search"}]}
                    for fi in files_to_attach
                ]

            await asyncio.to_thread(
                client.beta.threads.messages.create,
                thread_id=self.thread_id,
                role="user",
                content=last_user_message,
                attachments=attachments_for_message,
            )
            logger.info(
                "generate_response_streaming: Mensaje de usuario creado en el thread.")

              # --- INICIO DE LA SOLUCIÓN ---
            # 1. Definimos las herramientas que vamos a usar para este run específico.
            #    Empezamos con las herramientas de función que siempre están disponibles.
            tools_for_run = TOOLS_DEFINITION.copy()

            # 2. Si hay adjuntos, significa que queremos usar file_search.
            #    Lo añadimos a la lista de herramientas para este run.
            if attachments_for_message:
                logger.info("Habilitando la herramienta 'file_search' para este run.")
                tools_for_run.append({"type": "file_search"})

            # 3. Creamos el run pasándole la lista COMPLETA de herramientas disponibles.
            run_stream = await asyncio.to_thread(
                client.beta.threads.runs.create,
                thread_id=self.thread_id,
                assistant_id=self.assistant_id,
                tools=tools_for_run,  # <-- Usamos nuestra lista dinámica
                stream=True
            )
            # --- FIN DE LA SOLUCIÓN ---
            logger.info(
                "generate_response_streaming: Run creado con stream=True.")

            first_chunk_processed = False
            accumulated_response = ""
                # --- INICIO DEL CAMBIO CLAVE: BUCLE WHILE ---
            while True:
                should_break_outer_loop = False
                
                # Itera sobre los eventos del stream actual
                for event in run_stream:
                    if event.event == 'thread.message.delta':
                        delta = event.data.delta
                        if delta.content:
                            text_chunk = delta.content[0].text.value
                            if text_chunk:
                                async with self:
                                    if not first_chunk_processed:
                                        self.messages[-1]["content"] = ""
                                        first_chunk_processed = True
                                    accumulated_response += text_chunk
                                    self.messages[-1]["content"] = accumulated_response
                                yield
                                if len(accumulated_response) % 100 == 0:
                                    yield ChatState.scroll_to_bottom

                    elif event.event == 'thread.run.requires_action':
                        logger.info("Run requires action...")
                        run_id = event.data.id
                        tool_outputs = []

                            # --- CAMBIO IMPORTANTE: Actualizar la UI una sola vez antes de la herramienta ---
                        # Para evitar múltiples yields que puedan causar problemas de conexión.
                        async with self:
                            # Obtenemos la primera query para mostrar al usuario
                            first_query = json.loads(event.data.required_action.submit_tool_outputs.tool_calls[0].function.arguments).get('query', '...')
                            self.messages[-1]["content"] = f"Buscando en internet: '{first_query}'..."
                        yield # Un solo yield para actualizar la UI
                        
                        for tool_call in event.data.required_action.submit_tool_outputs.tool_calls:
                            function_name = tool_call.function.name
                            arguments = json.loads(tool_call.function.arguments)
                            if function_name in AVAILABLE_TOOLS:                                
                                output = await asyncio.to_thread(AVAILABLE_TOOLS[function_name], **arguments)
                                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})

                        if tool_outputs:
                            logger.info("Enviando resultados de la herramienta...")
                            # Creamos un NUEVO stream con los resultados
                            run_stream = await asyncio.to_thread(
                                client.beta.threads.runs.submit_tool_outputs,
                                thread_id=self.thread_id,
                                run_id=run_id,
                                tool_outputs=tool_outputs,
                                stream=True
                            )
                            # Rompemos el bucle INTERNO para que el bucle WHILE continúe con el NUEVO stream
                            break 
                    
                    # --- CAMBIO CLAVE: Manejo de finalización ---
                    elif event.event in ['thread.run.completed', 'thread.run.failed', 'error']:
                        if event.event == 'thread.run.completed':
                            logger.info("Stream: Run completed.")
                        else:
                            error_message = f"Stream: Run fallido o con error. Evento: {event.event}, Data: {event.data}"
                            logger.error(error_message)
                            async with self:
                                self.messages[-1]["content"] = "Se produjo un error al procesar la solicitud."
                        
                        # Marcamos que el bucle EXTERNO debe terminar
                        should_break_outer_loop = True
                        # Rompemos el bucle INTERNO
                        break 

                # Si se marcó la finalización, rompemos el bucle EXTERNO
                if should_break_outer_loop:
                    break
            # --- FIN DEL CAMBIO CLAVE: BUCLE WHILE ---
            
            logger.info("generate_response_streaming: Bucle principal completado.")

        except APIError as e:
            logger.error(f"Error de API de OpenAI: {e.message}")
            async with self:
                self.messages[-1]["content"] = f"Error de API: {e.message}"
        except Exception as e:
            logger.error(
                f"Error inesperado en generate_response_streaming: {str(e)}", exc_info=True)
            async with self:
                self.messages[-1]["content"] = f"Error inesperado: {str(e)}"
        finally:
            logger.info(
                f"generate_response_streaming: BLOQUE FINALLY. self.processing ANTES: {self.processing}, self.streaming ANTES: {self.streaming}")
            async with self:
                self.processing = False
                self.streaming = False
                self.thinking_seconds = 0
                self.focus_chat_input = True
            yield
            # Hacer autoscroll al final después de completar la respuesta
            yield ChatState.scroll_to_bottom
            # Posicionar cursor en el input del usuario
            yield ChatState.focus_input
            yield ChatState.reset_focus_trigger
            logger.info(
                f"generate_response_streaming: FIN. self.processing DESPUÉS: {self.processing}, self.streaming DESPUÉS: {self.streaming}")

    @rx.event
    def reset_focus_trigger(self):
        self.focus_chat_input = False

    def _get_available_functions(self) -> list[dict]:
        logger.info(
            "Llamando a _get_available_functions. Actualmente no hay funciones personalizadas mapeadas.")
        return {}

    def _get_context(self) -> str:
        return ""

   # ÚNICO CAMBIO REQUERIDO EN ESTE ARCHIVO
    @rx.event
    def limpiar_chat(self):
        """Reinicia el estado del chat y los archivos a sus valores iniciales."""
        self.messages = []
        self.thread_id = None
        self.file_info_list = []
        self.processing = False
        self.uploading = False
        self.upload_progress = 0
        self.ocr_progress = ""
        self.streaming_response = ""
        self.streaming = False
        self.thinking_seconds = 0
        self.upload_error = ""
        self.focus_chat_input = False
        self.current_question = ""
        self.chat_history = []  # Asegurándonos de que esta también se limpie
        logger.info("[DEBUG] ChatState.limpiar_chat ejecutado y estado reseteado.")
        # Finalmente, llamamos al inicializador para que vuelva a poner el mensaje
        yield self.initialize_chat()


        @rx.event
        def limpiar_chat_y_redirigir(self):
            self.limpiar_chat() 
            return rx.redirect("/")
        
        # 2. CREAMOS UN EVENTO PARA INICIALIZAR EL CHAT
    @rx.event
    def initialize_chat(self):
        """Añade el mensaje de bienvenida al cargar la página."""
        # Solo añade el mensaje si el chat está vacío
        if not self.messages:
            self.messages = [
                {
                    "role": "assistant",
                    "content": "¡Hola! Soy tu Asistente Legal Constitucional. Puedes hacerme una pregunta o subir un documento para analizarlo."
                }
            ]

    
    def scroll_to_bottom(self):
        """
        Evento que ejecuta un script para desplazar el contenedor de chat hasta el final.
        """
        return rx.call_script(
            """
            const chat = document.getElementById('chat-messages-container');
            if (chat) {
                chat.scrollTop = chat.scrollHeight;
            }
            """
        )