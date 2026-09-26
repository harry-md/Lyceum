from typing import Final

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.courses.models import Course, CourseStatus
from lyceum.courses.schemas import CourseFilter, CourseOrderBy

_SORT_COLUMNS: Final[dict] = {
    CourseOrderBy.AVG_RATING: Course.avg_rating,
    CourseOrderBy.RATING_COUNT: Course.rating_count,
    CourseOrderBy.ENROLLMENT_COUNT: Course.enrollment_count,
    CourseOrderBy.PUBLISHED_AT: Course.published_at,
}


def _build_filters(filters: CourseFilter) -> list:
    res = []
    keyword = (filters.keyword or "").strip()
    if keyword:
        res.append(
            or_(
                Course.title.icontains(keyword, autoescape=True),
                Course.instructor_name.icontains(keyword, autoescape=True),
            )
        )
    if filters.instructor_id:
        res.append(Course.instructor_id == filters.instructor_id)
    if filters.level:
        res.append(Course.level == filters.level)
    if filters.from_price is not None:
        res.append(Course.price >= filters.from_price)
    if filters.to_price is not None:
        res.append(Course.price <= filters.to_price)
    if filters.from_rating is not None:
        res.append(Course.avg_rating >= filters.from_rating)
    if filters.to_rating is not None:
        res.append(Course.avg_rating <= filters.to_rating)
    if filters.from_duration_mins is not None:
        res.append(Course.total_duration_mins >= filters.from_duration_mins)
    if filters.to_duration_mins is not None:
        res.append(Course.total_duration_mins <= filters.to_duration_mins)

    res.append(Course.status == CourseStatus.PUBLISHED)
    return res


async def find_with_filters(
    filters: CourseFilter,
    offset: int,
    limit: int,
    session: AsyncSession,
) -> list[Course]:
    """
    Return a list of courses with applied filters.
    Need to use with count_courses_with_filters method.
    """

    list_filters = _build_filters(filters=filters)

    stm = select(Course).where(*list_filters).offset(offset).limit(limit)

    if filters.order_by:
        col = _SORT_COLUMNS[filters.order_by]
        stm = stm.order_by(
            col.desc().nulls_last(),
            Course.id.desc(),
        )
    else:
        stm = stm.order_by(Course.id.desc())

    result = await session.scalars(statement=stm)
    return list(result.all())


async def count_with_filters(filters: CourseFilter, session: AsyncSession) -> int:
    """
    Return the number of courses with filters.
    """

    list_filters = _build_filters(filters=filters)

    count_stm = select(func.count(Course.id)).where(*list_filters)
    return await session.scalar(count_stm) or 0


async def find_by_slug(slug: str, session: AsyncSession) -> Course | None:
    return await session.scalar(select(Course).where(Course.slug == slug))


async def find_by_slug_for_update(slug: str, session: AsyncSession) -> Course | None:
    stm = select(Course).where(Course.slug == slug).with_for_update()
    return await session.scalar(stm)
