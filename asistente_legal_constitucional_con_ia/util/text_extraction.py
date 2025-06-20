import io
import os
import tempfile
import logging
from typing import Optional
import docx
import fitz
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

logging.basicConfig(level=logging.INFO)


def extract_text_from_bytes(
    file_bytes: bytes, filename: str, progress_callback=None
) -> Optional[str]:
    """
    Extracts text from a file given as bytes (PDF, DOCX, TXT).
    For PDF, it attempts direct extraction and falls back to OCR.
    If progress_callback is provided, it is called with (current_page, total_pages).
    """
    try:
        if filename.lower().endswith(".pdf"):
            logging.info(
                f"Processing PDF '{filename}' with PyMuPDF."
            )
            text = ""
            with fitz.open(
                stream=file_bytes, filetype="pdf"
            ) as doc:
                for page in doc:
                    text += page.get_text()
            if len(text.strip()) < 100:
                logging.warning(
                    f"Minimal text from '{filename}'. Trying OCR."
                )
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name
                try:
                    images = convert_from_path(
                        tmp_path, dpi=200
                    )
                    ocr_text = ""
                    total_pages = len(images)
                    for i, image in enumerate(images):
                        logging.info(
                            f"OCR on page {i + 1}/{total_pages} of '{filename}'."
                        )
                        if progress_callback:
                            progress_callback(i + 1, total_pages)
                        ocr_text += (
                            pytesseract.image_to_string(
                                image, lang="spa+eng"
                            )
                            + "\n"
                        )
                    text = ocr_text
                finally:
                    os.remove(tmp_path)
            return text.strip()
        elif filename.lower().endswith(".docx"):
            logging.info(f"Processing DOCX '{filename}'.")
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join(
                [para.text for para in doc.paragraphs]
            ).strip()
        elif filename.lower().endswith(".txt"):
            logging.info(f"Processing TXT '{filename}'.")
            return file_bytes.decode(
                "utf-8", errors="ignore"
            ).strip()
        else:
            logging.error(
                f"Unsupported file format: {filename}"
            )
            return None
    except Exception as e:
        logging.error(
            f"Error processing file '{filename}': {e}",
            exc_info=True,
        )
        return None
