from typing import Literal

from pydantic import BaseModel, Field


KnowledgeLevel = Literal[
    "beginner",
    "basic",
    "diagnostic",
]


class TutorCourseRequest(BaseModel):
    skill: str = Field(
        min_length=1,
        max_length=100,
    )

    target_role: str = Field(
        default="",
        max_length=150,
    )

    knowledge_level: KnowledgeLevel = "beginner"


class TutorModule(BaseModel):
    module_number: int
    title: str
    objective: str

    topics: list[str] = Field(default_factory=list)

    practice_task: str = ""

    estimated_minutes: int = Field(
        default=30,
        ge=10,
        le=180,
    )


class TutorCoursePlan(BaseModel):
    skill: str
    target_role: str = ""
    knowledge_level: KnowledgeLevel

    course_title: str
    course_description: str

    prerequisites: list[str] = Field(default_factory=list)
    learning_outcomes: list[str] = Field(default_factory=list)

    modules: list[TutorModule] = Field(default_factory=list)

    final_project: str = ""

    interview_questions: list[str] = Field(
        default_factory=list
    )