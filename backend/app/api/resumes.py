from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.resume import CandidateProfile, ResumeParseRequest
from app.services.ai_resume_parser import (
    AIResumeParserError,
    parse_resume_with_ai,
)
from app.services.document_parser import (
    DocumentExtractionError,
    extract_document_text,
)

# Router must be created before using @router.post(...)
router = APIRouter(
    prefix="/api/resumes",
    tags=["Resumes"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
}


def validate_resume_file(
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
) -> None:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file type is invalid.",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The résumé must be smaller than 5 MB.",
        )


@router.post("/extract")
async def extract_resume(
    resume: UploadFile = File(...),
) -> dict:
    filename = resume.filename or "resume"
    file_bytes = await resume.read()
    await resume.close()

    validate_resume_file(
        filename=filename,
        content_type=resume.content_type,
        file_bytes=file_bytes,
    )

    try:
        extracted_text, document_type = extract_document_text(
            filename=filename,
            file_bytes=file_bytes,
        )

    except DocumentExtractionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if not extracted_text:
        raise HTTPException(
            status_code=422,
            detail=(
                "No readable text was found. "
                "The résumé may be scanned or image-based."
            ),
        )

    return {
        "success": True,
        "filename": filename,
        "document_type": document_type,
        "character_count": len(extracted_text),
        "word_count": len(extracted_text.split()),
        "text": extracted_text,
    }


@router.post(
    "/parse",
    response_model=CandidateProfile,
)
def parse_resume(
    request: ResumeParseRequest,
) -> CandidateProfile:
    cleaned_text = request.text.strip()

    if len(cleaned_text) < 30:
        raise HTTPException(
            status_code=400,
            detail="The résumé text is too short to analyse.",
        )

    try:
        return parse_resume_with_ai(cleaned_text)

    except AIResumeParserError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error


@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
) -> dict:
    filename = resume.filename or "resume"
    file_bytes = await resume.read()
    await resume.close()

    validate_resume_file(
        filename=filename,
        content_type=resume.content_type,
        file_bytes=file_bytes,
    )

    try:
        extracted_text, document_type = extract_document_text(
            filename=filename,
            file_bytes=file_bytes,
        )

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text was found. "
                    "The résumé may be scanned or image-based."
                ),
            )

        candidate_profile = parse_resume_with_ai(extracted_text)

        return {
            "success": True,
            "filename": filename,
             "document_type": document_type,
             "word_count": len(extracted_text.split()),
            "character_count": len(extracted_text),
            "resume_text": extracted_text,
            "profile": candidate_profile.model_dump(),
        }
    except DocumentExtractionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except AIResumeParserError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error