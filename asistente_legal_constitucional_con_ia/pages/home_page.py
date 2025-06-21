import reflex as rx
from ..components.layout import main_layout


@rx.page(route="/", title="Inicio")
def home_page() -> rx.Component:
    """Página de inicio de la aplicación."""
    return main_layout(
        rx.center(
            rx.vstack(
                rx.image(
                    src="/balanza.png",
                    alt="Balanza de la Justicia",
                    width="256px",
                    height="auto",
                    margin_bottom="1rem",
                ),
                rx.heading(
                    "Bienvenido al Asistente Legal Constitucional",
                    size="2xl",
                    text_align="center",
                ),
                rx.text(
                    "Sistema especializado en análisis de jurisprudencia, leyes, y propuestas de leyes con ayuda de inteligencia artificial.",
                    text_align="center",
                ),
                rx.text(
                    "Selecciona una opción del menú para comenzar.",
                    font_weight="bold",
                    text_align="center",
                ),
                spacing="4",
                align="center",
                width="100%",
                max_width="800px",
                padding="4",
            ),
            width="100%",
            height="100%",
        )
    )
