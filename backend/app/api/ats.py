from fastapi import APIRouter

from app.schemas.ats import (
    ATSCheckRequest,
    ATSCheckResult,
)
from app.services.ats_checker import run_ats_check


router = APIRouter(
    prefix="/api/ats",
    tags=["ATS Checker"],
)


@router.post(
    "/check",
    response_model=ATSCheckResult,
)
def check_resume_ats(
    request: ATSCheckRequest,
) -> ATSCheckResult:
    return run_ats_check(
        profile=request.profile,
        job=request.job,
        resume_text=request.resume_text,
    )