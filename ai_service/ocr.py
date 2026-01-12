import io
import pdfplumber
from PIL import Image
import pytesseract
import pytesseract
from .config import ai_settings

if ai_settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = ai_settings.TESSERACT_CMD

def extract_text_from_file(raw_bytes: bytes, filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_text_from_pdf(raw_bytes)
    elif lower.endswith((".png", ".jpg", ".jpeg")):
        return _extract_text_from_image(raw_bytes)
    else:
        raise ValueError("Unsupported file type")

def _extract_text_from_pdf(raw_bytes: bytes) -> str:
    text_chunks: list[str] = []
    with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)

def _extract_text_from_image(raw_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(raw_bytes))
    return pytesseract.image_to_string(image)

