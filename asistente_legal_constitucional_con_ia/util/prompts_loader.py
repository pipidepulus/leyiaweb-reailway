import os
from ..util.text_extraction import extract_text_from_bytes

def extract_prompts_from_docx(docx_path: str):
    """
    Extrae los prompts y la introducción de un archivo DOCX.
    Retorna (intro, [prompts])
    """
    with open(docx_path, "rb") as f:
        text = extract_text_from_bytes(f.read(), os.path.basename(docx_path))
    if not text:
        return "", []
    # Separar introducción y prompts (asume prompts separados por líneas vacías o numerados)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    intro = []
    prompts = []
    current = []
    for line in lines:
        if (line.lower().startswith("prompt") or line[:2].isdigit()):
            if current:
                prompts.append(" ".join(current).strip())
                current = []
            current.append(line)
        else:
            if not prompts:
                intro.append(line)
            else:
                current.append(line)
    if current:
        prompts.append(" ".join(current).strip())
    return " ".join(intro), prompts
