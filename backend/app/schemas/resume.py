from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    degree: str = ""
    specialization: str = ""
    institution: str = ""
    location: str = ""
    start_year: str = ""
    end_year: str = ""
    score: str = ""


class ExperienceItem(BaseModel):
    role: str = ""
    organization: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    link: str = ""


class CertificationItem(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""
    credential_link: str = ""


class CandidateProfile(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""

    linkedin: str = ""
    github: str = ""
    portfolio: str = ""

    professional_summary: str = ""

    technical_skills: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    spoken_languages: list[str] = Field(default_factory=list)

    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    certifications: list[CertificationItem] = Field(default_factory=list)

    achievements: list[str] = Field(default_factory=list)
    courses: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)


class ResumeParseRequest(BaseModel):
    text: str = Field(
        min_length=30,
        max_length=50000,
    )