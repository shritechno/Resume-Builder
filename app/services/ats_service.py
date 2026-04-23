from __future__ import annotations

from io import BytesIO

from docx import Document
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


async def extract_resume_text(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf") and not filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if filename.endswith(".pdf"):
        text = _extract_pdf_text(raw)
    else:
        text = _extract_docx_text(raw)

    cleaned = " ".join(text.split())
    if len(cleaned) < 80:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough resume text. Please upload a clearer PDF or DOCX file.",
        )
    return cleaned


def _extract_pdf_text(raw: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(raw))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(exc)}") from exc


def _extract_docx_text(raw: bytes) -> str:
    try:
        document = Document(BytesIO(raw))
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read DOCX: {str(exc)}") from exc
