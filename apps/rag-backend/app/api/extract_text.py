from fastapi import APIRouter, File, UploadFile

from app.parsing.extract_text import extract_text

router = APIRouter(tags=["extract-text"])


@router.post("/extract-text")
async def extract_text_endpoint(file: UploadFile = File(...)) -> dict:
    file_bytes = await file.read()
    text, extraction_method = extract_text(file_bytes, file.filename or "file")
    return {"text": text, "extraction_method": extraction_method}
