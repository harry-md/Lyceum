from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.params import Cookie

from lyceum.auth.exceptions import InvalidCredentialsError, MissingAccessTokenError
from lyceum.auth.schemas import UserResponse
from lyceum.core.deps import SettingsDep
from lyceum.db.deps import SessionDep
from lyceum.users.repository import UserRepository


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


async def get_current_user(
    user_repository: UserRepositoryDep,
    settings: SettingsDep,
    access_token: Annotated[str | None, Cookie()] = None,
) -> UserResponse:
    if not access_token:
        raise MissingAccessTokenError("Thiếu access token")

    try:
        payload = jwt.decode(
            jwt=access_token,
            key=settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
        user_id = UUID(payload["sub"])
    except Exception as ex:
        raise MissingAccessTokenError("Lỗi khi decode token") from ex

    user = await user_repository.find_by_id(user_id)
    if not user:
        raise InvalidCredentialsError("Sai username/email hoặc mật khẩu")

    return UserResponse.model_validate(user)


CurrentUserDep = Annotated[UserResponse, Depends(get_current_user)]
