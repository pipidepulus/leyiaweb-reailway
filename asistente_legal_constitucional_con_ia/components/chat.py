"""Componente del área de chat, versión estable con input controlado."""

import reflex as rx
from ..states.chat_state import ChatState

# Constante para el color principal de la UI del chat
ACCENT_COLOR = "indigo"

def message_bubble(message: rx.Var[dict]) -> rx.Component:
    """Crea una burbuja de mensaje con estilo diferenciado."""
    is_user = message["role"] == "user"
    return rx.box(
        rx.hstack(
            # Volvemos a los avatares simples para garantizar estabilidad
             rx.flex(
                 rx.cond(
                     is_user,
                     rx.avatar(
                         src="/usuario.png",
                         fallback="US",
                    size="2",
                    color_scheme="blue",
                    variant="solid",
                    flex_shrink="0",
                ),
                rx.avatar(
                    src="/balanza.png",
                    fallback="BT",
                    size="2",
                    color_scheme="green",
                    variant="solid",
                    flex_shrink="0",
                ),
             ),            
            spacing="2",
        ),
            rx.box(
                rx.markdown(
                    message["content"],
                    class_name="prose prose-base max-w-none break-words",                    
                ),
                rx.cond(
                    ~is_user,
                    rx.icon_button(
                        "copy",
                        on_click=rx.set_clipboard(message["content"]),
                        size="1", variant="ghost", color_scheme="gray",
                        class_name="absolute top-2 right-2 opacity-50 hover:opacity-100 transition-opacity",
                        title="Copiar texto",
                    ),
                ),
                padding_x="1em",
                padding_y="0.75em",
                border_radius="var(--radius-4)",
                bg=rx.cond(is_user, "#e0e7ff", "#d3dff8"),
                color=rx.cond(is_user, "black", "black"),
                position="relative",
                max_width="85%",
                min_width="0",  # Permite que se encoja
                word_wrap="break-word",
                overflow_wrap="break-word",
                style={
                    "word-break": "break-word",
                    "overflow-wrap": "break-word",
                    "hyphens": "auto",
                },
            ),
            spacing="3",
            align_items="start",
            flex_direction=rx.cond(is_user, "row-reverse", "row"),
            width="100%",
            min_width="0",  # Permite que el hstack se encoja
        ),
        width="100%",
        min_width="0",
        padding_x="0.5rem",  # Pequeño padding lateral   
        margin_bottom="0.75rem",  # Espacio entre mensajes     
    )

def chat_input_area() -> rx.Component:
    """Área de entrada de texto con soporte para texto largo."""
    return rx.box(
        rx.form(
            rx.hstack(
                rx.el.textarea(
                    name="prompt",
                    id="chat-input-box",
                    placeholder="Escribe tu pregunta aquí... para enviar pulsa ➤",
                    value=ChatState.current_question,
                    on_change=ChatState.set_current_question,
                    disabled=ChatState.processing,
                    resize="vertical",
                    min_height="60px",
                    max_height="200px",
                    py="0.5em",
                    enter_key_submit=True,
                    class_name="flex-1 border-0 focus:outline-none focus:ring-0 bg-transparent",
                    style={
                        "font-size": "16px",
                        "white-space": "pre-wrap",
                        "word-wrap": "break-word", 
                        "overflow-wrap": "break-word",
                    },
                    
                ),
                rx.icon_button(
                    rx.cond(
                        ChatState.processing,
                        rx.spinner(size="3"),
                        rx.icon("send", size=20)
                    ),
                    type="submit",
                    disabled=ChatState.processing | (ChatState.current_question.strip() == ""),
                    size="3",
                    color_scheme=ACCENT_COLOR,
                ),
                align_items="end",
                spacing="3",
            ),
            on_submit=ChatState.send_message,
            reset_on_submit=False,
            width="100%",
        ),
        padding_x="1em",
        padding_y="0.5em",
        border="1px solid var(--gray-4)",
        border_radius="var(--radius-4)",
        bg="white",
        position="sticky",
        bottom="1em",
        width="calc(100% - 2em)",
        margin_x="1em",
        margin_bottom="1em",
        box_shadow="0 0 15px rgba(0,0,0,0.05)",
    )

def chat_area() -> rx.Component:
    """Área principal del chat con autoscroll automático y sin desbordamiento horizontal."""
    return rx.vstack(
        rx.box(
            rx.foreach(ChatState.messages, message_bubble),
            id="chat-messages-container",
            padding_x="1rem",
            padding_y="1rem",
            width="100%",
            flex_grow=1,
            overflow_y="auto",
            overflow_x="hidden",  # Previene scroll horizontal
            style={
                "scroll-behavior": "smooth",
                "display": "flex",
                "flex-direction": "column",
                "max-width": "100%",  # Asegura que no exceda el contenedor
            },
        ),
        chat_input_area(),
        spacing="1",
        height="100%",
        width="100%",
        max_width="100%",  # Previene desbordamiento del contenedor principal
        align_items="stretch",
    )

def chat() -> rx.Component:
    """Componente principal de chat exportado."""
    return rx.box(
        chat_area(),
        height="100vh",
        width="100%",
        class_name="bg-gray-50",
         # ¡ESTE ES EL CAMBIO CLAVE!
        # Llama al evento initialize_chat cuando el componente se monta.
        on_mount=ChatState.initialize_chat,
    )