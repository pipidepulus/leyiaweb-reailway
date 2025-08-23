import reflex as rx


class SharedState(rx.State):
    """Estado compartido para sincronización entre páginas."""

    # Contadores para forzar actualizaciones
    transcriptions_updated: int = 0
    notebooks_updated: int = 0

    @rx.event
    async def notify_transcription_change(self):
        """Notifica cambios en transcripciones."""
        self.transcriptions_updated += 1
        print(f"DEBUG: Notificación de cambio en transcripciones: {self.transcriptions_updated}")

    @rx.event
    async def notify_notebook_change(self):
        """Notifica cambios en notebooks."""
        self.notebooks_updated += 1
        print(f"DEBUG: Notificación de cambio en notebooks: {self.notebooks_updated}")
