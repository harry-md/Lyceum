from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.courses.models import Course, CourseStatus
from lyceum.courses.schemas import CourseFilter, CourseOrderBy
from lyceum.db.repository import BaseRepository


class CourseRepository(BaseRepository[Course]):
    _SORT_COLUMNS = {
        CourseOrderBy.AVG_RATING: Course.avg_rating,
        CourseOrderBy.RATING_COUNT: Course.rating_count,
        CourseOrderBy.ENROLLMENT_COUNT: Course.enrollment_count,
        CourseOrderBy.PUBLISHED_AT: Course.published_at,
    }

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Course)

    def _build_filters(
        self,
        *,
        filters: CourseFilter,
    ) -> list:
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

    """
        Return a list of courses with applied filters.
        Need to use with count_courses_with_filters method.
    """

    async def find_with_filters(
        self,
        filters: CourseFilter,
        offset: int,
        limit: int,
    ) -> list[Course]:
        list_filters = self._build_filters(filters=filters)

        stm = select(Course).where(*list_filters).offset(offset).limit(limit)

        if filters.order_by:
            col = self._SORT_COLUMNS[filters.order_by]
            stm = stm.order_by(
                col.desc().nulls_last(),
                Course.id.desc(),
            )
        else:
            stm = stm.order_by(Course.id.desc())

        result = await self._session.scalars(statement=stm)
        return list(result.all())

    """
        Return the number of courses with filters.
    """

    async def count_with_filters(
        self,
        filters: CourseFilter,
    ) -> int:
        list_filters = self._build_filters(filters=filters)

        count_stm = select(func.count(Course.id)).where(*list_filters)
        return await self._session.scalar(count_stm) or 0
