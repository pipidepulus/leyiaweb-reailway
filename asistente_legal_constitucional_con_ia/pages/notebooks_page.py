# asistente_legal_constitucional_con_ia/pages/notebooks_page.py
"""Página para gestionar notebooks del usuario."""

import reflex as rx

from ..components.layout import main_layout
from ..states.notebook_state import NotebookState


def notebooks_page() -> rx.Component:
    """Página de gestión de notebooks."""

    content = rx.vstack(
        # Header
        rx.hstack(
            rx.heading("Mis Notebooks", size="8", color="blue"),
            rx.spacer(),
            rx.button("Actualizar", on_click=NotebookState.load_user_notebooks, loading=NotebookState.loading, variant="outline"),
            width="100%",
            align="center",
            margin_bottom="2rem",
        ),
        # Estado de carga
        rx.cond(
            NotebookState.loading,
            rx.center(rx.spinner(size="3"), height="200px"),
            # Lista de notebooks
            rx.cond(
                NotebookState.notebooks.length() > 0,
                rx.vstack(rx.foreach(NotebookState.notebooks, lambda notebook: notebook_card(notebook)), spacing="4", width="100%"),
                # Estado vacío
                rx.center(
                    rx.vstack(
                        rx.icon("book", size=48, color="gray"),
                        rx.heading("No tienes notebooks aún", size="6", color="gray"),
                        rx.text("Los notebooks se crean automáticamente cuando usas el asistente.", color="gray"),
                        spacing="3",
                        align="center",
                    ),
                    height="300px",
                    width="100%",
                ),
            ),
        ),
        # Mensaje de error
        rx.cond(
            NotebookState.error_message != "",
            rx.callout.root(rx.callout.icon(rx.icon("triangle-alert")), rx.callout.text(NotebookState.error_message), color_scheme="red", margin_top="1rem"),
            rx.fragment(),
        ),
        spacing="4",
        width="100%",
        on_mount=NotebookState.load_user_notebooks,
    )

    return main_layout(content)


def notebook_card(notebook: rx.Var) -> rx.Component:
    """Componente para mostrar un notebook en la lista."""

    return rx.card(
        rx.vstack(
            # Header del notebook
            rx.hstack(
                rx.vstack(
                    rx.heading(notebook.title, size="5", weight="bold"),
                    rx.text(rx.cond(notebook.notebook_type == "transcription", "📝 Transcripción", "🔍 Análisis"), size="2", color="blue"),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(rx.icon("eye"), "Ver", on_click=rx.redirect(f"/notebooks/{notebook.id}"), variant="soft", size="2"),
                    rx.button(rx.icon("trash-2"), on_click=lambda: NotebookState.delete_notebook(notebook.id), variant="soft", color_scheme="red", size="2"),
                    spacing="2",
                ),
                width="100%",
                align="center",
            ),
            # Metadata
            rx.hstack(
                rx.text(f"Creado: {notebook.created_at[:10]}", size="1", color="gray"),
                rx.text(f"Actualizado: {notebook.updated_at[:10]}", size="1", color="gray"),
                rx.cond(notebook.source_data, rx.text(f"Fuente: {notebook.source_data}", size="1", color="gray"), rx.fragment()),
                spacing="4",
            ),
            # Preview del contenido
            rx.text("Notebook disponible para visualización", size="2", color="gray"),
            spacing="3",
            align="start",
            width="100%",
        ),
        width="100%",
    )


# Página para visualizar/editar un notebook específico
def notebook_viewer_page() -> rx.Component:
    """Página para visualizar y editar un notebook específico."""

    content = rx.vstack(
        rx.cond(
            NotebookState.current_notebook,
            rx.vstack(
                # Header
                rx.hstack(
                    rx.button(rx.icon("arrow-left"), "Volver", on_click=rx.redirect("/notebooks"), variant="ghost"),
                    rx.spacer(),
                    rx.heading(NotebookState.current_notebook.title, size="7"),
                    rx.spacer(),
                    rx.cond(
                        NotebookState.is_editing,
                        rx.hstack(
                            rx.button("💾 Guardar", on_click=NotebookState.save_notebook, color_scheme="green", loading=NotebookState.loading),
                            rx.button("❌ Cancelar", on_click=NotebookState.cancel_editing, variant="outline"),
                            spacing="2",
                        ),
                        rx.hstack(
                            rx.button("✏️ Editar", on_click=NotebookState.start_editing, color_scheme="blue"),
                            rx.button("� Copiar", on_click=rx.set_clipboard(NotebookState.current_notebook_content), color_scheme="green"),
                            spacing="2",
                        ),
                    ),
                    width="100%",
                    align="center",
                ),
                # Contenido del notebook - Editor o visor markdown
                rx.cond(
                    NotebookState.is_editing,
                    # Modo edición
                    rx.box(
                        rx.text_area(
                            value=NotebookState.edit_content,
                            on_change=NotebookState.set_edit_content,
                            placeholder="Escribe el contenido markdown aquí...",
                            width="100%",
                            min_height="500px",
                            max_height="70vh",
                            resize="vertical",
                            style={
                                "& textarea": {
                                    "font_size": "16px",
                                    "font_family": "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                                    "font_weight": "400",
                                    "line_height": "1.7",
                                    "letter_spacing": "0.025em",
                                    "color": "var(--gray-12)",
                                    "background": "transparent",
                                    "border": "none",
                                    "outline": "none",
                                    "padding": "0",
                                }
                            },
                        ),
                        width="100%",
                        padding="2rem",  # Mismo padding que el modo visualización
                        background="white",
                        border_radius="lg",
                        border="1px solid var(--gray-6)",
                        max_height="70vh",
                        overflow="auto",
                        min_height="400px",  # Mismo min_height que el modo visualización
                    ),
                    # Modo visualización
                    rx.cond(
                        NotebookState.current_notebook_content,
                        rx.box(
                            rx.markdown(NotebookState.current_notebook_content, width="100%"),
                            width="100%",
                            padding="2rem",
                            background="white",
                            border_radius="lg",
                            border="1px solid var(--gray-6)",
                            max_height="70vh",
                            overflow="auto",
                            min_height="400px",
                        ),
                        rx.text("No hay contenido en el notebook", color="gray", text_align="center"),
                    ),
                ),
                spacing="4",
                width="100%",
            ),
            rx.center(rx.vstack(rx.spinner(size="3"), rx.text("Cargando notebook...", color="gray"), spacing="3"), height="400px"),
        ),
        spacing="4",
        width="100%",
        on_mount=NotebookState.load_notebook_on_page_load,
    )

    return main_layout(content)
