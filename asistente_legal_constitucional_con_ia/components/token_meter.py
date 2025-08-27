import reflex as rx

from ..states.chat_state import ChatState


def token_meter() -> rx.Component:
    # ...existing code...
    return rx.box(
        rx.card(
            rx.hstack(
                # Modelo
                rx.text("Modelo:", weight="bold"),
                rx.badge(
                    rx.cond(ChatState.model_name == "", "desconocido", ChatState.model_name),
                    variant="soft",
                ),
                rx.spacer(),
                # Última respuesta
                rx.badge(
                    rx.hstack(
                        rx.text("Última:"),
                        rx.text(ChatState.last_total_tokens),
                        rx.text("tok"),
                        spacing="1",
                        align="center",
                    ),
                    color_scheme="blue",
                ),
                rx.badge(
                    rx.hstack(rx.text("In:"), rx.text(ChatState.last_prompt_tokens), spacing="1"),
                    variant="soft",
                ),
                rx.badge(
                    rx.hstack(rx.text("Out:"), rx.text(ChatState.last_completion_tokens), spacing="1"),
                    variant="soft",
                ),
                rx.spacer(),
                # Acumulado
                rx.badge(
                    rx.hstack(
                        rx.text("Acumulado:"),
                        rx.text(ChatState.total_tokens),
                        rx.text("tok"),
                        spacing="1",
                        align="center",
                    ),
                    color_scheme="green",
                ),
                # Costo
                rx.badge(
                    rx.hstack(
                        rx.text("Costo aprox: $"),
                        rx.text(ChatState.cost_usd),
                        spacing="1",
                        align="center",
                    ),
                    color_scheme="orange",
                ),
                # En vivo
                rx.cond(
                    ChatState.approx_output_tokens > 0,
                    rx.badge(
                        rx.hstack(rx.text("En vivo Out≈"), rx.text(ChatState.approx_output_tokens), spacing="1", align="center"),
                        variant="soft",
                    ),
                    rx.fragment(),
                ),
                rx.spacer(),
                rx.button("Reiniciar", size="2", on_click=ChatState.reset_token_counters, variant="surface"),
                spacing="3",
                align="center",
                width="100%",
            ),
            padding="0.6rem",
            width="100%",
            bg="white",
            border_bottom="1px solid var(--gray-4)",
        ),
        # Fija el medidor arriba y por encima del scroll de los mensajes
        position="sticky",
        top="0px",
        z_index=10,
        width="100%",
        bg="white",
    )