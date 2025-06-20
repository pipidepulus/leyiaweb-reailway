# asistente_legal_constitucional_con_ia/asistente_legal_constitucional_con_ia.py
import reflex as rx

def index():
    # Una página que no puede fallar. Solo un texto.
    return rx.text("Hola, mundo!")

# La inicialización más simple posible.
app = rx.App()
app.add_page(index)
app.compile()