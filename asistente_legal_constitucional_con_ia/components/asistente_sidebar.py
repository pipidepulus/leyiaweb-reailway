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
            rx.button(
                "Regresar a pantalla principal",
                on_click=rx.redirect("/"),
                class_name="mt-6 w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-md py-2 px-4"
            ),
            class_name="flex flex-col gap-4 p-4 h-full"
        ),
        class_name="w-80 bg-white dark:bg-gray-900 border-r flex flex-col h-full shadow-lg z-10"
    )
