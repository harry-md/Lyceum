from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.params import Cookie

from lyceum.auth.exceptions import InvalidCredentialsError, MissingAccessTokenError
from lyceum.auth.schemas import UserResponse
from lyceum.core.deps import SettingsDep
from lyceum.db.deps import SessionDep
from lyceum.shared.exceptions import ForbiddenError
from lyceum.users.models import User
from lyceum.users.queries import find_instructor_by_id


def get_token_user_id(
    settings: SettingsDep,
    access_token: Annotated[str | None, Cookie()] = None,
) -> UUID:
    if not access_token:
        raise MissingAccessTokenError("Thiếu access token")

    try:
        payload = jwt.decode(
            jwt=access_token,
            key=settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )

        subject = payload["sub"]
        if not isinstance(subject, str):
            raise ValueError("JWT sub phải là chuỗi")  # noqa: TRY004

        return UUID(subject)

    except (jwt.InvalidTokenError, ValueError) as error:
        raise MissingAccessTokenError("Lỗi khi decode token") from error


TokenUserIdDep = Annotated[UUID, Depends(get_token_user_id)]


async def get_current_user(
    user_id: TokenUserIdDep,
    session: SessionDep,
) -> UserResponse:
    user: User | None = await session.get(User, user_id)

    if not user:
        raise InvalidCredentialsError("Sai username/email hoặc mật khẩu")

    return UserResponse.model_validate(user)


async def get_current_instructor(
    user_id: TokenUserIdDep,
    session: SessionDep,
) -> UserResponse:
    async with session.begin():
        instructor = await find_instructor_by_id(user_id=user_id, session=session)

        if not instructor:
            raise ForbiddenError(
                "Tài khoản không có quyền giảng viên hoặc chưa có hồ sơ giảng viên"
            )
        response = UserResponse.model_validate(instructor)

    return response


CurrentInstructorDep = Annotated[
    UserResponse,
    Depends(get_current_instructor),
]


CurrentUserDep = Annotated[UserResponse, Depends(get_current_user)]
