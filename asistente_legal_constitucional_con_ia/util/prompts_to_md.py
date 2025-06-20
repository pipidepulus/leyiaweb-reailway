import os
import re
from ..util.text_extraction import extract_text_from_bytes


def extract_prompts_to_markdown(docx_path: str, md_path: str):
    """
    Extrae contenido de un archivo DOCX y lo formatea en Markdown.
    La introducción va bajo "# Introducción".
    Cada "Fase X: ..." o "X.Y Prompt (...):" se convierte en un "## Título" en Markdown,
    representando un bloque de prompt individual en la UI.
    """
    with open(docx_path, "rb") as f:
        text = extract_text_from_bytes(f.read(), os.path.basename(docx_path))
    if not text:
        return False

    lines = text.splitlines()
    output_md_lines = []

    # Regex para identificar inicios de bloques que serán H2 (prompts individuales para la UI)
    # Incluye "Fase X:" y "X.Y Prompt (...):" o "Prompt X:"
    block_start_regex = re.compile(
        r"^\s*(Fase \d+[:\s].*|(\d+\.\d+|\d+)\s*Prompt\s*\(?[^)]*\)?[:\s]|Prompt\s*\d*[:\s])",
        re.IGNORECASE
    )

    intro_lines = []
    current_block_content = []
    intro_ended = False

    for line in lines:
        stripped_line = line.strip()
        if not intro_ended and block_start_regex.match(stripped_line):
            intro_ended = True
            # Guardar la introducción acumulada
            if intro_lines:
                output_md_lines.append("# Introducción\\n")
                output_md_lines.append("\\n".join(intro_lines).strip() + "\\n")
            # Iniciar el primer bloque de prompt/fase
            current_block_content = [line]
        elif intro_ended:
            if block_start_regex.match(stripped_line):
                # Guardar el bloque anterior
                if current_block_content:
                    title = current_block_content[0].strip()
                    content = "\\n".join(current_block_content[1:]).strip()
                    output_md_lines.append(f"## {title}\\n")
                    if content:
                        output_md_lines.append(content + "\\n")
                current_block_content = [line]  # Iniciar nuevo bloque
            elif current_block_content:  # Si ya estamos en un bloque, añadir línea
                current_block_content.append(line)
            # else: ignorar líneas vacías entre bloques si no se ha iniciado uno
        else:  # Acumular líneas de introducción
            intro_lines.append(line)

    # Guardar el último bloque de prompt/fase
    if current_block_content:
        title = current_block_content[0].strip()
        content = "\\n".join(current_block_content[1:]).strip()
        output_md_lines.append(f"## {title}\\n")
        if content:
            output_md_lines.append(content + "\\n")
    elif not intro_ended and intro_lines:  # Caso: todo el doc es introducción
        output_md_lines.append("# Introducción\\n")
        output_md_lines.append("\\n".join(intro_lines).strip() + "\\n")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\\n".join(output_md_lines))
    return True
