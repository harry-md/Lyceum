from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.db.repository import BaseRepository
from lyceum.users.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=User)

    async def find_by_username_or_email(self, username: str, email: str) -> User | None:
        return await self._session.scalar(
            select(User).where(or_(User.username == username, User.email == email))
        )
