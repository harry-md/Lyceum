from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.chapters.models import Chapter


async def get_max_order(course_id: UUID, session: AsyncSession) -> int:
    stm = select(func.coalesce(func.max(Chapter.order), 0)).where(
        Chapter.course_id == course_id
    )
    result = await session.scalar(stm)
    return int(result) if result is not None else 10_000
