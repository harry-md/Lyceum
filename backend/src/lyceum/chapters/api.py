from fastapi import APIRouter

from lyceum.chapters.schemas import (
    ChapterCreateRequest,
    ChapterResponse,
)
from lyceum.chapters.service import create_chapter
from lyceum.db.deps import SessionDep
from lyceum.users.deps import CurrentInstructorDep

router = APIRouter(
    prefix="/api/v1/courses",
    tags=["chapters"],
)


@router.post(
    "/{slug}/chapters",
    response_model=ChapterResponse,
    status_code=201,
)
async def create(
    slug: str,
    request: ChapterCreateRequest,
    instructor: CurrentInstructorDep,
    session: SessionDep,
) -> ChapterResponse:
    return await create_chapter(
        slug=slug,
        request=request,
        instructor_id=instructor.id,
        session=session,
    )
