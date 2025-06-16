import reflex as rx
from reflex_local_auth import require_login
from asistente_legal_constitucional_con_ia.components.sidebar import sidebar

@rx.page(route="/chat", title="Chat")
@require_login
def chat_page() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.center(
            rx.box(
                rx.heading("Chat", size="lg"),
                rx.text("Página de chat en construcción."),
                width="100%",
                max_width="600px",
                padding="4",
                border_radius="lg",
                box_shadow="md",
                bg=rx.color_mode_cond("white", "gray.800"),
            ),
            width="100%",
            height="100vh",
            class_name="bg-gray-50 dark:bg-gray-900 w-full h-full",
        ),
        align="start",
        width="100%",
        class_name="bg-gray-50 dark:bg-gray-900 min-h-screen w-full",
    )
