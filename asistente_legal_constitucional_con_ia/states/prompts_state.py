# asistente_legal_constitucional_con_ia/states/prompts_state.py
import reflex as rx
from .app_state import AppState

# ID único para el contenedor de scroll de la página de prompts
PROMPTS_CONTAINER_ID = "prompts-scroll-area"

class PromptsState(AppState):
    """Estado para manejar la interactividad de la página de prompts."""

    # La variable que "recordará" la posición del scroll entre navegaciones.
    scroll_position: int = 0

    # Evento que GUARDA la posición actual del scroll.
    # Se llamará desde el frontend cada vez que el usuario haga scroll.
    def set_scroll_position(self, scroll_top: int):
        """
        Recibe los datos del evento on_scroll y actualiza la variable de estado.
        Reflex pasa un diccionario con la información del evento.
        """
        # Extraemos el valor de scrollTop del diccionario.
        self.scroll_position = int(scroll_top)
        # La línea de arriba es segura y no fallará si los datos no vienen como esperamos.
        # print(f"Scroll position saved: {self.scroll_position}") # Descomenta para depurar

    # Evento que RESTAURA la posición del scroll guardada.
    # Se llamará cuando la página de prompts se monte.
    def restore_scroll_position(self):
        """
        Ejecuta un script para establecer la posición del scroll del contenedor
        al valor que tenemos guardado en self.scroll_position.
        """
        return rx.call_script(
            f"""
            const container = document.getElementById('{PROMPTS_CONTAINER_ID}');
            if (container) {{
                container.scrollTop = {self.scroll_position};
            }}
            """
        )