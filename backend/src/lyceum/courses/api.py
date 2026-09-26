from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from pydantic import Json

from lyceum.core.deps import SettingsDep
from lyceum.courses.schemas import (
    CourseCreateRequest,
    CourseCreateResponse,
    CourseFilter,
    CourseFilterRequest,
    CourseListResponse,
)
from lyceum.courses.service import create_course, get_courses
from lyceum.db.deps import SessionDep
from lyceum.shared.schemas import Page
from lyceum.users.deps import CurrentInstructorDep

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


MAX_THUMBNAIL_BYTES = 5 * 1024 * 1024
ALLOWED_THUMBNAIL_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


@router.get("", response_model=Page[CourseListResponse])
async def list_courses(
    request: Annotated[CourseFilterRequest, Query()], session: SessionDep
) -> Page[CourseListResponse]:
    filters = CourseFilter(**request.model_dump(exclude={"page", "page_size"}))

    return await get_courses(
        filters=filters,
        session=session,
        page=request.page,
        page_size=request.page_size,
    )


@router.post(
    "",
    response_model=CourseCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    data: Annotated[Json[CourseCreateRequest], Form()],
    thumbnail: Annotated[UploadFile, File()],
    instructor: CurrentInstructorDep,
    session: SessionDep,
    settings: SettingsDep,
) -> CourseCreateResponse:
    try:
        if thumbnail.content_type not in ALLOWED_THUMBNAIL_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Chỉ chấp nhận định dạng ảnh",
            )

        content = await thumbnail.read(MAX_THUMBNAIL_BYTES + 1)

        if not content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Ảnh không được rỗng",
            )

        if len(content) > MAX_THUMBNAIL_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Ảnh không được vượt quá 5 MB",
            )

        return await create_course(
            request=data,
            instructor=instructor,
            thumbnail_content=content,
            session=session,
            settings=settings,
        )

    finally:
        await thumbnail.close()
