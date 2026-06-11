from pydantic import BaseModel, Field


class JobAnalysisRequest(BaseModel):
    target_role: str = Field(
        default="",
        max_length=150,
    )

    job_description: str = Field(
        min_length=50,
        max_length=30000,
    )


class JobAnalysis(BaseModel):
    target_role: str = ""
    company_name: str = ""
    experience_level: str = ""
    employment_type: str = ""
    location: str = ""

    job_summary: str = ""

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    programming_languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    cloud_platforms: list[str] = Field(default_factory=list)

    knowledge_areas: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)

    education_requirements: list[str] = Field(default_factory=list)
    experience_requirements: list[str] = Field(default_factory=list)

    important_keywords: list[str] = Field(default_factory=list)