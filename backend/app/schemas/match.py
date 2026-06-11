from pydantic import BaseModel, Field

from app.schemas.job import JobAnalysis
from app.schemas.resume import CandidateProfile


class SkillMatchItem(BaseModel):
    skill: str
    evidence: list[str] = Field(default_factory=list)


class JobMatchRequest(BaseModel):
    profile: CandidateProfile
    job: JobAnalysis


class JobMatchResult(BaseModel):
    target_role: str = ""
    match_percentage: int = 0

    required_skill_count: int = 0
    preferred_skill_count: int = 0

    matched_count: int = 0
    partial_count: int = 0
    missing_count: int = 0

    matching_skills: list[SkillMatchItem] = Field(
        default_factory=list
    )

    partially_evidenced_skills: list[SkillMatchItem] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    matched_preferred_skills: list[str] = Field(
        default_factory=list
    )

    missing_preferred_skills: list[str] = Field(
        default_factory=list
    )

    strengths: list[str] = Field(
        default_factory=list
    )

    next_steps: list[str] = Field(
        default_factory=list
    )