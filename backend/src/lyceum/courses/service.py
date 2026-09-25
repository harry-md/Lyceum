from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.courses.repository import CourseRepository
from lyceum.courses.schemas import CourseFilter, CourseListResponse
from lyceum.shared.schemas import Page


class CourseService:
    def __init__(self, session: AsyncSession, course_repository: CourseRepository):
        self._session = session
        self._course_repository = course_repository

    async def get_courses(
        self,
        filters: CourseFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> Page[CourseListResponse]:
        offset = (page - 1) * page_size

        courses = await self._course_repository.find_with_filters(
            filters=filters,
            offset=offset,
            limit=page_size,
        )

        total = await self._course_repository.count_with_filters(filters=filters)

        total_pages = (total + page_size - 1) // page_size

        return Page(
            items=courses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
