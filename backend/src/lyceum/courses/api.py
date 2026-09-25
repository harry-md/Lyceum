from typing import Annotated

from fastapi import APIRouter, Query

from lyceum.courses.deps import CourseServiceDep
from lyceum.courses.schemas import CourseFilter, CourseFilterRequest, CourseListResponse
from lyceum.shared.schemas import Page

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.get("", response_model=Page[CourseListResponse])
async def get_all_courses(
    request: Annotated[CourseFilterRequest, Query()],
    service: CourseServiceDep,
) -> Page[CourseListResponse]:
    filters = CourseFilter(**request.model_dump(exclude={"page", "page_size"}))

    return await service.get_courses(
        filters,
        request.page,
        request.page_size,
    )
