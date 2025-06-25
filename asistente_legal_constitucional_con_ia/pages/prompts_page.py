"""Página que muestra una biblioteca de prompts, usando el layout principal."""

import reflex as rx
from ..components.layout import main_layout
from typing import List, Dict, Any
from ..util.auth import require_login  # <-- 1. IMPORTAMOS EL DECORADOR

class Prompt(rx.Base):
    title: str
    description: str
    content: str

initial_data: Dict[str, List[Prompt]] = {
    "Fase 1: Comprensión Integral del Proyecto/Ley": [
        Prompt(
            title="1.1. Prompt: Resumen Ejecutivo (Zero-shot)",
            description="Este prompt busca obtener una visión general y concisa del texto normativo.",
            content="""Analiza el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) y genera un resumen ejecutivo (máximo 500 palabras) que incluya: 
1. Problema que aborda. 
2. Objetivos principales. 
3. Mecanismos o cambios clave que propone. 
4. Implicaciones preliminares más evidentes.""",
        ),
        Prompt(
            title="1.2. Prompt: Extracción Específica de la Exposición de Motivos",
            description="Este prompt se enfoca en extraer las justificaciones y metas explícitas directamente de la fuente.",
            content="""Del texto de la Exposición de Motivos del "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`), extrae y lista textualmente las frases o párrafos que describen: a) la justificación de la necesidad de la propuesta y b) los objetivos explícitos que persigue.
""",
        ),
        Prompt(
            title="1.3. Prompt: Identificación de Materia Dominante",
            description="Este prompt tiene como objetivo definir el núcleo temático de la norma.",
            content="""Analiza el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`). Identifica y describe en una frase concisa cuál es la materia dominante o el núcleo temático esencial de esta propuesta/norma. Justifica brevemente tu elección basándote en el título, el objeto (si lo tiene) y el contenido general.
""",
        ),
    ],
    "Fase 2: Identificación del Marco Constitucional Aplicable": [
        Prompt(
            title="2.1. Prompt: Listado de Principios Constitucionales",
            description="Este prompt busca mapear los principios constitucionales que podrían ser afectados o desarrollados por la norma.",
            content="""Considerando el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`), identifica y lista al menos CINCO principios constitucionales colombianos que sean directamente relevantes o que podrían verse implicados por sus disposiciones. Para cada principio, explica brevemente (1-2 frases) su conexión con el proyecto/ley.
""",
        ),
        Prompt(
            title="2.2. Prompt: Identificación de Derechos Fundamentales",
            description="Este prompt clasifica el impacto de la norma sobre los derechos fundamentales.",
            content="""Analiza el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`). Enumera los derechos fundamentales (según la Constitución Política de Colombia) que son: a) Promovidos o protegidos. b) Potencialmente limitados o restringidos por esta norma. Cita los artículos del proyecto/ley que sustentan tu identificación.
""",
        ),
    ],
    "Fase 3: Análisis de Constitucionalidad Formal (Vicios de Procedimiento)": [
        Prompt(
            title="3.1. Prompt: Análisis de Competencia y Tipo de Ley",
            description="Verifica si el Congreso tiene la facultad para legislar en la materia y si se requiere un tipo de ley especial.",
            content="""Respecto al "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`), que regula [Materia principal]:
1. ¿Tiene el Congreso de la República competencia para legislar sobre esta materia según la Constitución? Cita artículos constitucionales.
2. ¿La materia regulada exige un tipo de ley especial (orgánica, estatutaria)? Si es así, ¿el proyecto parece seguir el trámite adecuado (según la información disponible en el archivo)?
""",
        ),
        Prompt(
            title="3.2 Prompt (Análisis de Unidad de Materia - Skeleton):",
            description="Genera un borrador estructurado para analizar la unidad de materia de un proyecto de ley.",
            content="""Prepara un borrador de análisis de unidad de materia para el "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`). Tu análisis debe seguir esta estructura:
1.  Identificación del núcleo temático del proyecto.
2.  Listado de hasta TRES disposiciones que podrían considerarse ajenas a ese núcleo (si las hay).
3.  Argumentación breve para cada disposición señalada, explicando por qué podría vulnerar la unidad de materia.
4.  Conclusión preliminar.
""",
        ),
        Prompt(
            title="3.3 Prompt (Impacto Fiscal - Ley 819/2003):",
            description="Evalúa el cumplimiento del análisis de impacto fiscal según la Ley 819 de 2003.",
            content="""Analiza si la Exposición de Motivos del "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`) cumple con las exigencias del Artículo 7 de la Ley 819 de 2003 respecto al análisis del impacto fiscal de las normas que ordenan gasto o conceden beneficios. Identifica si se mencionan costos fiscales y fuentes de ingreso para cubrirlos.
""",
        ),
        Prompt(
            title="3.4 Prompt (Consulta Previa - Identificación de Necesidad):",
            description="Determina la necesidad de consulta previa para comunidades étnicas.",
            content="""Considerando el objeto y alcance del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`), determina si sus disposiciones podrían afectar directamente a comunidades indígenas o afrocolombianas. Si es así, argumenta por qué sería necesario el requisito de consulta previa según la Constitución y la jurisprudencia.
""",
        ),
    ],
    "Fase 4: Análisis de Constitucionalidad Material (Vicios de Fondo)": [
        Prompt(
            title="4.1. Prompt: Test de Proporcionalidad (Estructura Guiada)",
            description="Aplica el test de proporcionalidad a un artículo específico que limita un derecho fundamental.",
            content="""Aplica un test de proporcionalidad al Artículo [Número] del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`), el cual establece: "[Citar o resumir el artículo]". Este artículo limita el derecho a [Derecho Fundamental X] con el fin de [Fin que persigue la norma]. Evalúa:
1.  Finalidad: ¿El fin es constitucionalmente legítimo e importante?
2.  Idoneidad: ¿La medida es conducente para alcanzar el fin?
3.  Necesidad: ¿Existe una alternativa menos lesiva?
4.  Proporcionalidad estricta: ¿Los beneficios superan la afectación al derecho?
Concluye sobre su constitucionalidad.""",
        ),
        Prompt(
            title="4.2 Prompt (Identificación de Conflicto con Jurisprudencia):",
            description="Compara una norma con una sentencia específica de la Corte Constitucional.",
            content="""Analiza el Artículo [Número] del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`). Compara su contenido con la regla establecida en la Sentencia [Citar Sentencia, ej. C-XXX de AAAA] de la Corte Constitucional, que establece que [Resumir regla jurisprudencial]. ¿Existe concordancia o contradicción? Fundamenta.
""",
        ),
        Prompt(
            title="4.3 Prompt (Argumento de Inconstitucionalidad - Chain of Thought):",
            description="Construye un argumento lógico para sostener la inconstitucionalidad de un artículo.",
            content="""Construye un argumento (máximo 3 párrafos) para sostener la inconstitucionalidad del Artículo [Número] del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) por vulnerar el principio/derecho a [Principio/Derecho Constitucional]. Sigue una estructura lógica: Premisa constitucional, contenido de la norma, y la contradicción resultante.
""",
        ),
        Prompt(
            title="4.4 Prompt (Argumento de Defensa de Constitucionalidad - Rol Específico):",
            description="Presenta argumentos clave para defender la constitucionalidad de un artículo.",
            content="""Defiende la constitucionalidad del Artículo [Número] del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) frente a un cargo por presunta violación de [Principio/Derecho Constitucional]. Presenta TRES argumentos clave para la defensa.
""",
        ),
        Prompt(
            title="4.5 Prompt (Identificación de Antinomias con la Constitución):",
            description="Identifica contradicciones directas entre el proyecto/ley y la Constitución.",
            content="""Revisa el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) e identifica hasta TRES disposiciones que podrían presentar una antinomia o contradicción directa con artículos específicos de la Constitución Política de Colombia. Para cada una, cita el artículo del proyecto/ley y el artículo constitucional en conflicto, y explica brevemente la contradicción.
""",
        ),
        Prompt(
            title="4.6 Prompt (Análisis de Vaguedad o Ambigüedad con Relevancia Constitucional):",
            description="Evalúa si la vaguedad o ambigüedad de términos puede tener implicaciones constitucionales.",
            content="""Identifica si existen términos o disposiciones en el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) que por su vaguedad o ambigüedad podrían generar inseguridad jurídica o problemas de interpretación con relevancia constitucional (ej. afectando el debido proceso o la aplicación igualitaria de la ley). Señala el artículo y explica el problema.
""",
        ),
        Prompt(
            title="4.7 Prompt (Evaluación de Razonabilidad de una Prohibición/Restricción):",
            description="Analiza la razonabilidad de una prohibición o restricción impuesta por la norma.",
            content="""El Artículo [Número] del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) impone una prohibición/restricción sobre [Actividad/Derecho]. Evalúa la razonabilidad de esta medida considerando el fin que persigue y si la restricción es excesiva o arbitraria.
""",
        ),
    ],
    "Fase 5: Conclusiones y Recomendaciones": [
        Prompt(
            title="5.1. Prompt: Borrador de Conclusiones de Informe",
            description="Sintetiza los hallazgos clave del análisis en un borrador de conclusiones.",
            content="""Basado en un análisis previo del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`), donde se identificaron [Mencionar 2-3 hallazgos clave, ej. "un posible vicio de unidad de materia", "una limitación proporcionada al derecho X", "conflicto con la sentencia Y"], redacta un borrador de la sección de "Conclusiones" para un informe de constitucionalidad.
""",
        ),
        Prompt(
            title="5.2 Prompt (Sugerencia de Modificación para Mitigar Riesgo):",
            description="Propone una redacción alternativa para un artículo con riesgo de inconstitucionalidad.",
            content="""El Artículo [Número] del "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`) presenta un riesgo de inconstitucionalidad debido a [Breve descripción del riesgo]. Sugiere una redacción alternativa o una adición a este artículo que podría mitigar dicho riesgo, manteniendo el objetivo principal del legislador.
""",
        ),
        Prompt(
            title="5.3 Prompt (Identificación de Fortalezas Constitucionales del Proyecto):",
            description="Identifica y justifica aspectos del proyecto alineados con la Constitución.",
            content="""Analiza el "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`) e identifica TRES aspectos o artículos que consideres como fortalezas desde la perspectiva de su alineación con la Constitución Política de Colombia (ej. desarrollo de un mandato constitucional, protección efectiva de un derecho, etc.). Justifica brevemente cada uno.
""",
        ),
    ],
    "Fase 6: Prompts Adicionales (Técnicas Variadas)": [
        Prompt(
            title="6.1 Prompt (Análisis Comparativo Simple entre dos Artículos):",
            description="Compara dos artículos de diferentes normativas para identificar similitudes, diferencias o conflictos.",
            content="""Compara el Artículo [X] del "[Nombre del Proyecto de Ley A]" (Archivo: `[archivo_A.ext]`) con el Artículo [Y] de la "[Ley B Vigente]" (Archivo: `[archivo_B.ext]`). Describe sus similitudes, diferencias y si existe algún conflicto normativo aparente.
""",
        ),
        Prompt(
            title="6.2 Prompt (Few-shot para un tipo de cláusula específica):",
            description="Analiza una cláusula de un proyecto de ley comparándola con un ejemplo de buena práctica.",
            content="""Ejemplo de cláusula que respeta el debido proceso administrativo: "[Texto de ejemplo de cláusula correcta]".
Analiza el Artículo [Número] del "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`) que establece un procedimiento administrativo. ¿Se asemeja al espíritu del ejemplo proporcionado en cuanto a garantías procesales? Identifica deficiencias si las hay.
""",
        ),
        Prompt(
            title="6.3 Prompt (Rol Playing - Debate Simulado):",
            description="Simula un debate para explorar argumentos a favor y en contra de la constitucionalidad de un artículo.",
            content="""Simula un breve debate.
Rol 1 (Ponente): Defiende la constitucionalidad del Artículo [Número] del "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`) usando un argumento principal.
Rol 2 (Opositor): Presenta un contraargumento cuestionando su constitucionalidad.
Presenta ambos argumentos.""",
        ),
        Prompt(
            title="6.4 Prompt (Generación de Preguntas para Debate Legislativo):",
            description="Formula preguntas críticas para el debate legislativo sobre un proyecto de ley.",
            content="""Basado en el "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`), formula CINCO preguntas críticas que deberían ser abordadas durante el debate legislativo para asegurar la constitucionalidad y conveniencia de la propuesta.
""",
        ),
        Prompt(
            title="6.5 Prompt (Simplificación de Argumento Constitucional Complejo):",
            description="Explica un argumento constitucional complejo en términos más sencillos.",
            content="""La Exposición de Motivos del "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`) contiene el siguiente argumento para justificar [Aspecto X]: "[Citar un párrafo complejo de la exposición de motivos]". Explica este argumento en términos más sencillos (máximo 100 palabras) sin perder su esencia constitucional.
""",
        ),
        Prompt(
            title="6.6 Prompt (Evaluación de Coherencia Interna con Principios Enunciados):",
            description="Analiza si el articulado de un proyecto es coherente con los principios enunciados en su exposición de motivos.",
            content="""La Exposición de Motivos del "[Nombre del Proyecto de Ley]" (Archivo: `[nombre_del_archivo.ext]`) enuncia que se basa en los principios de [Principio A] y [Principio B]. Analiza si el articulado del proyecto es coherente y desarrolla efectivamente dichos principios. Señala inconsistencias si existen.
""",
        ),
        Prompt(
            title="6.7 Prompt (Análisis de Progresividad y No Regresividad de Derechos Sociales):",
            description="Evalúa si una modificación a la regulación de un derecho social cumple con los principios de progresividad y no regresividad.",
            content="""Si el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) modifica la regulación de un derecho social (ej. salud, educación, vivienda), evalúa si la nueva propuesta cumple con el principio de progresividad y la prohibición de regresividad en materia de derechos sociales, conforme a la jurisprudencia constitucional colombiana.
""",
        ),
        Prompt(
            title="6.8 Prompt (Identificación de Impacto en Minorías o Grupos Vulnerables):",
            description="Identifica si disposiciones de un proyecto podrían tener un impacto desproporcionado en minorías o grupos vulnerables.",
            content="""Analiza el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) e identifica si alguna de sus disposiciones podría tener un impacto desproporcionado (positivo o negativo) o un trato diferencial hacia minorías étnicas, grupos LGBTIQ+, personas con discapacidad, u otros grupos de especial protección constitucional.
""",
        ),
        Prompt(
            title="6.9 Prompt (Verificación de Sanciones y Debido Proceso Sancionatorio):",
            description="Verifica si un régimen sancionatorio propuesto respeta los principios del debido proceso.",
            content="""Si el "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`) establece un régimen sancionatorio, verifica si las sanciones propuestas y el procedimiento para imponerlas respetan los principios del debido proceso (legalidad, tipicidad, favorabilidad, non bis in idem, derecho de defensa, etc.).
""",
        ),
        Prompt(
            title="6.10 Prompt (Concepto Final Breve - Combinación):",
            description="Emite un concepto breve sobre la constitucionalidad general de un proyecto, destacando fortalezas y riesgos.",
            content="""Emite un concepto breve (máximo TRES párrafos) sobre la constitucionalidad general del "[Nombre del Proyecto de Ley/Ley]" (Archivo: `[nombre_del_archivo.ext]`), destacando su principal fortaleza constitucional y su principal riesgo o vicio de inconstitucionalidad.
""",
        ),
    ],
}

class PromptsState(rx.State):
    """Maneja el estado y la lógica para la página de la biblioteca de prompts."""
    prompt_phases: Dict[str, List[Prompt]] = initial_data
    copied_feedback: Dict[str, bool] = {}

    def handle_prompt_change(self, phase_key: str, index: int, new_content: str):
        self.prompt_phases[phase_key][index].content = new_content
        prompt_unique_id = f"{phase_key}-{index}"
        if self.copied_feedback.get(prompt_unique_id):
            new_feedback_state = self.copied_feedback.copy()
            new_feedback_state[prompt_unique_id] = False
            self.copied_feedback = new_feedback_state

    def copy_to_clipboard_and_show_feedback(self, content: str, phase_key: str, index: int):
        prompt_unique_id = f"{phase_key}-{index}"
        current_feedback_state = {k: False for k in self.copied_feedback}
        current_feedback_state[prompt_unique_id] = True
        self.copied_feedback = current_feedback_state
        return rx.set_clipboard(content)

def render_prompt_card(prompt: Prompt, phase_key: str, index: int) -> rx.Component:
    """Crea una tarjeta interactiva para un solo prompt."""
    prompt_unique_id = f"{phase_key}-{index}"
    return rx.card(
        rx.vstack(
            rx.heading(prompt.title, size="4", margin_bottom="0.5em"),
            rx.text(prompt.description, color_scheme="gray", size="2", margin_bottom="1em"),
            rx.text_area(
                value=prompt.content,
                on_change=lambda new_content: PromptsState.handle_prompt_change(phase_key, index, new_content),
                placeholder="Edita el prompt aquí...",
                size="3",
                width="100%",
                min_height="200px",
                style={"font_family": "monospace"},
            ),
            rx.hstack(
                rx.cond(
                    PromptsState.copied_feedback.get(prompt_unique_id, False),
                    rx.text("¡Copiado!", color_scheme="green", weight="bold"),
                    rx.text(""),
                ),
                rx.spacer(),
                rx.button(
                    "Copiar Prompt",
                    rx.icon(tag="copy", margin_left="0.5em"),
                    on_click=PromptsState.copy_to_clipboard_and_show_feedback(prompt.content, phase_key, index),
                    size="2",
                    color_scheme="blue",
                ),
                width="100%",
                margin_top="1em",
                align_items="center",
            ),
            align_items="stretch",
            width="100%",
        ),
        width="100%",
        style={"border": "1px solid #3B82F6", "border_radius": "var(--radius-3)"},
    )


# --- CAMBIO FINAL AQUÍ ---
# 2. REEMPLAZAMOS @rx.page POR @require_login
@require_login
def prompts_page() -> rx.Component:
    """Define el contenido de la página de prompts."""
    # ... (el contenido de la función prompts_page no cambia)
    content = rx.container(
        rx.vstack(
            rx.heading("Metodología de Prompts para Análisis Constitucional con IA", size="7", align="center", margin_top="1em", margin_bottom="1em"),
            rx.text(
                (
                    "Un prompt es una instrucción escrita que se le da a una inteligencia artificial "
                    "para que genere una respuesta útil. Es como formular una pregunta bien "
                    "enfocada para obtener un análisis o información precisa."
                ),
                align="center", size="3", color_scheme="gray", margin_bottom="1em",
            ),
            rx.text(
                "Utiliza, edita y copia estos prompts para tus análisis de leyes y proyectos de ley.",
                align="center", size="3", color_scheme="gray", margin_bottom="2em",
            ),
            rx.foreach(
                PromptsState.prompt_phases,
                lambda item_tuple: rx.vstack(
                    rx.heading(item_tuple[0], size="6", margin_top="1.5em", margin_bottom="1em"),
                    rx.foreach(
                        item_tuple[1],
                        lambda prompt, index: render_prompt_card(prompt, item_tuple[0], index),
                    ),
                    rx.divider(margin_y="2em", color_scheme="blue"),
                    width="100%", spacing="4", align_items="center",
                ),
            ),
            width="100%", spacing="4", align_items="center",
        ),
        padding_x="2em",
        padding_y="1em",
        max_width="1000px",
        margin="auto",
        width="100%",
    )
    return main_layout(content)