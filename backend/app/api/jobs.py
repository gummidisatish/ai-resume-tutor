from fastapi import APIRouter, HTTPException

from app.schemas.job import (
    JobAnalysis,
    JobAnalysisRequest,
)
from app.services.job_analyzer import (
    JobAnalyzerError,
    analyze_job_description,
)

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
)


@router.post(
    "/analyze",
    response_model=JobAnalysis,
)
def analyze_job(
    request: JobAnalysisRequest,
) -> JobAnalysis:
    cleaned_description = request.job_description.strip()
    cleaned_role = request.target_role.strip()

    if len(cleaned_description) < 50:
        raise HTTPException(
            status_code=400,
            detail=(
                "The job description is too short. "
                "Please provide the complete description."
            ),
        )

    try:
        return analyze_job_description(
            job_description=cleaned_description,
            target_role=cleaned_role,
        )

    except JobAnalyzerError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error