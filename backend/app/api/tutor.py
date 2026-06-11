from fastapi import APIRouter, HTTPException

from app.schemas.tutor import (
    TutorCoursePlan,
    TutorCourseRequest,
)
from app.services.tutor_service import (
    TutorServiceError,
    generate_course_plan,
)


router = APIRouter(
    prefix="/api/tutor",
    tags=["AI Tutor"],
)


@router.post(
    "/course-plan",
    response_model=TutorCoursePlan,
)
def create_course_plan(
    request: TutorCourseRequest,
) -> TutorCoursePlan:
    try:
        return generate_course_plan(request)

    except TutorServiceError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error