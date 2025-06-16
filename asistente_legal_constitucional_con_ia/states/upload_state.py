import reflex as rx

class UploadState(rx.State):
    uploaded_files: list[str] = []
    last_processed: str = ""
    process_message: str = ""

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            data = await file.read()
            path = rx.get_upload_dir() / file.name
            with path.open("wb") as f:
                f.write(data)
            self.uploaded_files.append(file.name)
            # Procesar y enviar al asistente inmediatamente
            self.process_file(file.name)

    @rx.event
    def process_file(self, filename: str):
        # Aquí deberías llamar a la función de extracción y procesamiento real
        self.last_processed = filename
        self.process_message = f"Archivo '{filename}' procesado y enviado al asistente."
