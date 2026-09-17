from typing import Annotated

from fastapi import Depends

from lyceum.db.deps import SessionDep
from lyceum.users.repository import UserRepository


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
