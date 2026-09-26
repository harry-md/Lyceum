import logging
import re
import unicodedata
from uuid import UUID, uuid7

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.auth.schemas import UserResponse
from lyceum.core.cloudinary import (
    delete_image,
    upload_image,
)
from lyceum.core.config import Settings
from lyceum.courses.models import Course, CourseStatus
from lyceum.courses.queries import count_with_filters, find_with_filters
from lyceum.courses.schemas import (
    CourseCreateRequest,
    CourseCreateResponse,
    CourseFilter,
    CourseListResponse,
)
from lyceum.db.errors import violated_constraint
from lyceum.shared.exceptions import ConflictError
from lyceum.shared.schemas import Page

logger = logging.getLogger(__name__)


async def get_courses(
    filters: CourseFilter,
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> Page[CourseListResponse]:
    offset = (page - 1) * page_size

    courses = await find_with_filters(
        filters=filters,
        offset=offset,
        limit=page_size,
        session=session,
    )

    total = await count_with_filters(filters=filters, session=session)

    total_pages = (total + page_size - 1) // page_size

    return Page(
        items=courses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def _build_course_slug(title: str, course_id: UUID) -> str:
    normalized = unicodedata.normalize(
        "NFKD",
        title.casefold().replace("đ", "d"),
    )
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii")
    stem = re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")
    stem = stem or "course"

    # 222 + dấu "-" + 32 ký tự UUID = tối đa 255.
    return f"{stem[:222].rstrip('-')}-{course_id.hex}"


async def create_course(
    request: CourseCreateRequest,
    instructor: UserResponse,
    thumbnail_content: bytes,
    session: AsyncSession,
    settings: Settings,
) -> CourseCreateResponse:
    course_id = uuid7()
    public_id = course_id.hex
    uploaded = False
    commit_started = False

    try:
        instructor_name = f"{instructor.first_name} {instructor.last_name}"

        thumbnail_url = await upload_image(
            content=thumbnail_content,
            public_id=public_id,
            settings=settings,
        )
        uploaded = True

        course = Course(
            id=course_id,
            instructor_id=instructor.id,
            instructor_name=instructor_name,
            title=request.title,
            slug=_build_course_slug(request.title, course_id),
            short_description=request.short_description,
            description="\n".join(request.description),
            thumbnail=thumbnail_url,
            level=request.level,
            price=request.price,
            status=CourseStatus.DRAFT,
            rating_count=0,
            enrollment_count=0,
            total_duration_mins=0,
        )
        response = CourseCreateResponse.model_validate(course)

        async with session.begin():
            session.add(course)
            await session.flush()
            commit_started = True

        return response

    except IntegrityError as error:
        if uploaded:
            await delete_image(public_id=public_id, settings=settings)

        if violated_constraint(error) == "uq_courses_slug":
            raise ConflictError("Slug khóa học bị trùng, vui lòng thử lại") from error
        raise

    except Exception:
        if uploaded and not commit_started:
            await delete_image(public_id=public_id, settings=settings)
        elif uploaded:
            # Mất kết nối khi COMMIT có thể làm kết quả không rõ.
            # Giữ ảnh để tránh xóa thumbnail của course đã được lưu.
            logger.error(
                "Course commit outcome uncertain; course_id=%s public_id=%s",
                course_id,
                public_id,
            )
        raise
