from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.job import JobAnalysis
from app.schemas.resume import CandidateProfile


ATSStatus = Literal["passed", "warning", "failed"]


class ATSCheckRequest(BaseModel):
    profile: CandidateProfile
    job: JobAnalysis

    resume_text: str = Field(
        default="",
        max_length=50000,
    )


class ATSCheckItem(BaseModel):
    name: str
    status: ATSStatus

    score: int = 0
    maximum_score: int = 0

    message: str = ""
    suggestions: list[str] = Field(default_factory=list)


class ATSCheckResult(BaseModel):
    ats_score: int = 0
    rating: str = ""

    passed_count: int = 0
    warning_count: int = 0
    failed_count: int = 0

    checks: list[ATSCheckItem] = Field(default_factory=list)

    present_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)

    strengths: list[str] = Field(default_factory=list)
    priority_improvements: list[str] = Field(default_factory=list)