import reflex as rx
import reflex_local_auth  # Importar el módulo completo
from asistente_legal_constitucional_con_ia.components.sidebar import sidebar
# No importar project_explorer por ahora

@reflex_local_auth.require_login  # Usar el decorador con el nombre completo del módulo
def proyectos_page():
    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.h1("Página de Proyectos (Con Sidebar y Auth)"),
            rx.el.p("Contenido de prueba para la página de proyectos."),
            class_name="p-4 md:p-8 w-full overflow-y-auto"  # Estilos para el contenedor del contenido
        ),
        class_name="flex h-screen font-['Inter'] bg-gray-50 dark:bg-gray-900"  # Estilos del div principal
    )
