from typing import Annotated

from fastapi import Depends

from lyceum.auth.service import AuthService
from lyceum.core.deps import SettingsDep
from lyceum.users.deps import SessionDep, UserRepositoryDep


def get_auth_service(
    session: SessionDep, user_repository: UserRepositoryDep, settings: SettingsDep
) -> AuthService:
    return AuthService(
        session=session,
        user_repository=user_repository,
        settings=settings,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
