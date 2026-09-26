from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.chapters.models import Chapter
from lyceum.chapters.queries import get_max_order
from lyceum.chapters.schemas import (
    ChapterCreateRequest,
    ChapterResponse,
)
from lyceum.courses.queries import find_by_slug_for_update
from lyceum.db.errors import violated_constraint
from lyceum.shared.exceptions import (
    ConflictError,
    ForbiddenError,
    ResourceNotFoundError,
)

CHAPTER_ORDER_STEP = 10_000
MAX_CHAPTER_ORDER = 2_147_483_647  # max value for int4 in pg


async def create_chapter(
    slug: str,
    request: ChapterCreateRequest,
    instructor_id: UUID,
    session: AsyncSession,
) -> ChapterResponse:
    try:
        course = await find_by_slug_for_update(slug, session=session)

        if course is None:
            raise ResourceNotFoundError("Không tìm thấy khóa học")

        if course.instructor_id != instructor_id:
            raise ForbiddenError("Bạn không có quyền thêm chương vào khóa học này")

        max_order = await get_max_order(course.id, session=session)
        next_order = max_order + CHAPTER_ORDER_STEP

        if next_order > MAX_CHAPTER_ORDER:
            raise ConflictError(
                "Thứ tự chương vượt giới hạn; cần sắp xếp lại trước khi thêm"
            )

        chapter = Chapter(
            course_id=course.id,
            title=request.title,
            order=next_order,
        )
        session.add(chapter)
        await session.flush()

        response = ChapterResponse.model_validate(chapter)
        await session.commit()
        return response

    except IntegrityError as error:
        await session.rollback()

        if violated_constraint(error) == "uq_chapters_course_order":
            raise ConflictError("Thứ tự chương bị trùng, vui lòng thử lại") from error
        raise

    except Exception:
        await session.rollback()
        raise
