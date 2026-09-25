from typing import Annotated

from fastapi import Depends

from lyceum.courses.repository import CourseRepository
from lyceum.courses.service import CourseService
from lyceum.db.deps import SessionDep


def get_course_repository(session: SessionDep) -> CourseRepository:
    return CourseRepository(session)


CourseRepositoryDep = Annotated[CourseRepository, Depends(get_course_repository)]


def get_course_service(
    session: SessionDep, course_repository: CourseRepositoryDep
) -> CourseService:
    return CourseService(session, course_repository)


CourseServiceDep = Annotated[CourseService, Depends(get_course_service)]
