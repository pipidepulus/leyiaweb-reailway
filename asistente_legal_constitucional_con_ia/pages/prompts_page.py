import reflex as rx
from reflex_local_auth import require_login
from asistente_legal_constitucional_con_ia.components.sidebar import sidebar

@require_login # Reincorporar el decorador de autenticación
def prompts_page() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.center(
            rx.box(
                rx.heading("Prompts", size="5"), # Cambiado size="lg" a size="5"
                rx.text("Página de prompts en construcción."),
                width="100%",
                max_width="600px",
                padding="4",
                border_radius="lg",
                box_shadow="md",
                bg=rx.color_mode_cond("white", "gray.800"),
            ),
            width="100%",
            height="100vh",
        ),
        align="start",
        width="100%",
    )
