import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.schemas.tutor import (
    TutorCoursePlan,
    TutorCourseRequest,
)

load_dotenv()


class TutorServiceError(Exception):
    """Raised when the AI tutor cannot create a course."""


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise TutorServiceError(
            "GEMINI_API_KEY is missing from backend/.env."
        )

    return genai.Client(api_key=api_key)


def get_model_names() -> list[str]:
    configured_model = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash-lite",
    )

    models = [
        configured_model,
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ]

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(models))


def build_course_prompt(
    request: TutorCourseRequest,
) -> str:
    return f"""
You are an expert technical course tutor.

Create a practical course plan for a student who needs to learn the
following missing job skill:

Skill: {request.skill}
Target job: {request.target_role or "Not specified"}
Current knowledge level: {request.knowledge_level}

Rules:
1. Teach the skill from the student's current level.
2. Focus on knowledge useful for the target job.
3. Use simple, clear module titles.
4. Create between 5 and 8 modules.
5. Arrange modules from fundamentals to practical application.
6. Each module must include topics and one practical task.
7. Include realistic estimated learning time.
8. Include a final project.
9. Include five technical interview questions.
10. Do not claim the student already knows the skill.
11. Return only structured data matching the requested schema.
"""


def generate_course_plan(
    request: TutorCourseRequest,
) -> TutorCoursePlan:
    client = get_gemini_client()
    prompt = build_course_prompt(request)

    last_error: Exception | None = None

    for model_name in get_model_names():
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=TutorCoursePlan,
                    ),
                )

                if response.parsed:
                    if isinstance(
                        response.parsed,
                        TutorCoursePlan,
                    ):
                        return response.parsed

                    return TutorCoursePlan.model_validate(
                        response.parsed
                    )

                if response.text:
                    return TutorCoursePlan.model_validate_json(
                        response.text
                    )

                raise TutorServiceError(
                    "The AI tutor returned an empty response."
                )

            except Exception as error:
                last_error = error
                message = str(error).lower()

                is_temporary = (
                    "503" in message
                    or "unavailable" in message
                    or "high demand" in message
                    or "429" in message
                    or "quota" in message
                )

                if is_temporary and attempt == 0:
                    time.sleep(2)
                    continue

                break

    message = str(last_error) if last_error else "Unknown error"

    if (
        "api key" in message.lower()
        or "401" in message
        or "403" in message
    ):
        raise TutorServiceError(
            "The Gemini API key is invalid or unauthorized."
        ) from last_error

    if "429" in message or "quota" in message.lower():
        raise TutorServiceError(
            "The free Gemini request limit has been reached."
        ) from last_error

    if (
        "503" in message
        or "unavailable" in message.lower()
        or "high demand" in message.lower()
    ):
        raise TutorServiceError(
            "The AI tutor is temporarily busy. Please retry."
        ) from last_error

    raise TutorServiceError(
        f"The AI tutor could not create the course: {message}"
    ) from last_error