import base64
import io

import fitz
from docx import Document
from mistralai.client import Mistral

from app.core.config import get_settings

settings = get_settings()


def _extract_pdf_text_layer(file_bytes: bytes) -> tuple[str, int]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    try:
        pages = [page.get_text() for page in doc]
    finally:
        doc.close()
    return "\n\n".join(pages), len(pages)


def _extract_pdf_via_mistral_ocr(file_bytes: bytes) -> str:
    client = Mistral(api_key=settings.mistral_api_key)
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    response = client.ocr.process(
        model=settings.mistral_ocr_model_id,
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}",
        },
    )
    return "\n\n".join(page.markdown for page in response.pages)


def _extract_pdf(file_bytes: bytes) -> tuple[str, str]:
    text, page_count = _extract_pdf_text_layer(file_bytes)
    chars_per_page = len(text) / page_count if page_count else 0
    if chars_per_page >= settings.ocr_min_chars_per_page:
        return text, "pymupdf"
    return _extract_pdf_via_mistral_ocr(file_bytes), "mistral_ocr"


def _extract_docx(file_bytes: bytes) -> tuple[str, str]:
    doc = Document(io.BytesIO(file_bytes))
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return text, "python-docx"


def extract_text(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """Returns (extracted_text, extraction_method)."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension == "pdf":
        return _extract_pdf(file_bytes)
    if extension == "docx":
        return _extract_docx(file_bytes)
    raise ValueError(f"Unsupported resume file type: .{extension}")
