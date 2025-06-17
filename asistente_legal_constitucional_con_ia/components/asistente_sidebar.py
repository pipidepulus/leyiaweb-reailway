import reflex as rx
from asistente_legal_constitucional_con_ia.components.file_uploader import file_uploader
from asistente_legal_constitucional_con_ia.components.file_list import file_list

def asistente_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.h2(
                "📄 Archivos del Asistente",
                class_name="text-lg font-bold mb-2",
            ),
            file_uploader(),
            file_list(),
            # Botón para regresar a la página principal
            rx.button(
                "Ir a Página Principal",
                on_click=lambda: rx.redirect("/"), # Asumiendo que la página principal está en la ruta "/"
                class_name="mt-6 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow"
            ),
            # Se elimina la lógica de login/logout de este sidebar
            class_name="flex flex-col gap-4 p-4 h-full"
        ),
        class_name="w-80 bg-white dark:bg-gray-900 border-r flex flex-col h-full shadow-lg z-10"
    )
