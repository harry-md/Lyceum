from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.users.models import Instructor, User, UserRole


async def find_instructor_by_id(user_id: UUID, session: AsyncSession) -> User | None:
    stm = (
        select(User)
        .join(Instructor, Instructor.user_id == User.id)
        .where(
            User.id == user_id,
            User.role == UserRole.INSTRUCTOR,
        )
    )
    return await session.scalar(stm)
