import io
import logging
from typing import Optional

import docx
import fitz

logging.basicConfig(level=logging.INFO)


def extract_text_from_bytes(file_bytes: bytes, filename: str, progress_callback=None, skip_ocr: bool = True) -> Optional[str]:
    """Extrae texto de PDF, DOCX o TXT.

    OCR deshabilitado: si un PDF tiene poco texto (<100 chars) se devuelve lo encontrado
    sin intentar reconocimiento de imágenes.
    """
    try:
        if filename.lower().endswith(".pdf"):
            logging.info(f"Processing PDF '{filename}' with PyMuPDF (OCR deshabilitado).")
            text = []
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text.append(page.get_text())
            joined = "".join(text).strip()
            # Si es muy poco, devolver tal cual (el llamador decidirá si rechaza el PDF)
            return joined
        elif filename.lower().endswith(".docx"):
            logging.info(f"Processing DOCX '{filename}'.")
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([para.text for para in doc.paragraphs]).strip()
        elif filename.lower().endswith(".txt"):
            logging.info(f"Processing TXT '{filename}'.")
            return file_bytes.decode("utf-8", errors="ignore").strip()
        else:
            logging.error(f"Unsupported file format: {filename}")
            return None
    except Exception as e:
        logging.error(
            f"Error processing file '{filename}': {e}",
            exc_info=True,
        )
        return None
