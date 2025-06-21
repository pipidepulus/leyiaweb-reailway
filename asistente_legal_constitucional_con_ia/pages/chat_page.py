import reflex as rx
from ..components.layout import main_layout


@rx.page(route="/chat", title="Chat")
def chat_page() -> rx.Component:
    """Página de chat simple para demostración."""
    return main_layout(
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
            height="100%",
        )
    )
