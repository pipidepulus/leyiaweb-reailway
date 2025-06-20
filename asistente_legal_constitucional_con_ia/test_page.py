# asistente_legal_constitucional_con_ia/test_page.py
import reflex as rx

def test_page():
    return rx.box(
        rx.heading("Página de Prueba"),
        rx.text("Si ves esto, la configuración base funciona correctamente.")
    )