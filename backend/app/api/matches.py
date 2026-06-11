from fastapi import APIRouter

from app.schemas.match import (
    JobMatchRequest,
    JobMatchResult,
)
from app.services.job_matcher import calculate_job_match


router = APIRouter(
    prefix="/api/matches",
    tags=["Job Match"],
)


@router.post(
    "/analyze",
    response_model=JobMatchResult,
)
def analyze_match(
    request: JobMatchRequest,
) -> JobMatchResult:
    return calculate_job_match(
        profile=request.profile,
        job=request.job,
    )