import reflex as rx
from asistente_legal_constitucional_con_ia.states.chat_state import ChatState


# message_bubble con distinción usuario/bot y botón de copiar para el bot
def message_bubble(message: rx.Var[dict]) -> rx.Component:
    is_user = message["role"] == "user"
    
    # Contenido del mensaje renderizado con Markdown
    # Cambiado a text-[20px] para un tamaño de fuente de 20px
    content_markdown = rx.markdown(
        message["content"],
        class_name="prose text-[20px] max-w-none break-words", 
    )

    # Burbuja del Usuario
    user_bubble_layout = rx.el.div(
        rx.icon("user", class_name="text-indigo-500", size=24, flex_shrink=0),
        rx.el.div(
            content_markdown,
            class_name="bg-indigo-400 text-white rounded-l-xl rounded-t-xl p-3", # Cambiado bg-indigo-500 a bg-indigo-400
        ),
        class_name="flex justify-end items-start gap-2",
        # Ocultar si no es mensaje de usuario
        style=rx.cond(~is_user, {"display": "none"}, {}),
    )

    # Burbuja del Bot (con botón de copiar)
    bot_bubble_layout = rx.el.div(
        rx.icon("bot", class_name="text-green-600", size=24, flex_shrink=0),
        rx.el.div(
            content_markdown,
            # Botón de copiar
            rx.button(
                rx.icon("copy", size=16),
                on_click=rx.set_clipboard(message["content"]),
                size="1", # Botón pequeño
                variant="ghost", # Menos intrusivo
                color_scheme="gray",
                class_name="mt-2 ml-auto block", # Margen superior, alineado a la derecha del contenido
                title="Copiar texto",
            ),
            # Fondo gris claro para el bot, para contraste con el fondo índigo del chat_area
            class_name="bg-gray-100 text-gray-800 rounded-r-xl rounded-t-xl p-3 w-full", 
        ),
        class_name="flex justify-start items-start gap-2",
        # Ocultar si es mensaje de usuario
        style=rx.cond(is_user, {"display": "none"}, {}),
    )

    # Devolver ambas layouts. CSS controlará la visibilidad.
    return rx.fragment(
        user_bubble_layout,
        bot_bubble_layout,
    )


# def chat_input() -> rx.Component: ... # Esta función parece estar sin usar

def chat_area() -> rx.Component:
    """Chat con lista de mensajes y caja de input funcional, sin condicionales complejos."""
    return rx.el.main(
        rx.auto_scroll( # rx.auto_scroll ahora es el contenedor scrollable
            rx.foreach(ChatState.messages, message_bubble),
            class_name="space-y-4 flex-1 p-6 bg-indigo-100", # Clases para scroll y estilo
            id="chat-history",
        ),
        rx.el.div(
            rx.el.form(
                rx.el.input(
                    name="prompt",
                    id="chat-input-box", # El ID al que apuntamos
                    placeholder="Escribe tu consulta aquí...",
                    disabled=ChatState.processing,
                    # Cambiado a text-[20px] para un tamaño de fuente de 20px
                    class_name="flex-1 p-3 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-[20px]",
                ),
                rx.el.button(
                    rx.box( 
                        rx.icon("send", size=20, style=rx.cond(ChatState.processing, {"display": "none"}, {"display": "inline"})),
                        rx.spinner(size="1", style=rx.cond(~ChatState.processing, {"display": "none"}, {"display": "inline"})),
                    ),
                    type="submit",
                    disabled=ChatState.processing,
                    class_name="p-3 bg-indigo-600 text-white rounded-r-lg hover:bg-indigo-700 disabled:bg-indigo-300 flex items-center justify-center w-[50px]",
                ),
                # REMOVER el rx.focus(...) incorrecto de aquí
                on_submit=ChatState.send_message,
                reset_on_submit=True,
                class_name="flex",
            ),
            class_name="p-4 border-t",
        ),
        # Añadir rx.script condicional aquí
        rx.cond(
            ChatState.focus_chat_input,
            rx.script(f"document.getElementById('chat-input-box')?.focus();"),
            rx.fragment() # Renderizar nada si no se debe enfocar
        ),
        class_name="flex-1 flex flex-col h-full min-h-0",
    )


def chat() -> rx.Component:
    return rx.el.div(
        rx.el.div( # Sección de subida de archivos RESTAURADA
            rx.el.h2("Sube tus archivos para análisis", class_name="text-xl font-semibold mb-2"),
            rx.el.div(
                # Aquí puedes usar el uploader si tienes uno, por ejemplo:
                # file_uploader(),
                class_name="mb-4"
            ),
        ),
        chat_area(),
        class_name="flex-1 h-full bg-white dark:bg-gray-800 rounded-lg shadow p-4 flex flex-col gap-4"
    )