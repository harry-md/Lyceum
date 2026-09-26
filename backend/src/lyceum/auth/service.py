from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.auth.exceptions import AccountAlreadyExistsError, InvalidCredentialsError
from lyceum.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from lyceum.core.config import Settings
from lyceum.core.security import create_access_token, hash_password, verify_password
from lyceum.shared.exceptions import ConflictError
from lyceum.users.models import User, UserRole


async def register(request: RegisterRequest, session: AsyncSession) -> UserResponse:
    username = request.username
    email = request.email

    try:
        async with session.begin():
            existing_user: User | None = await session.scalar(
                select(User).where(or_(User.username == username, User.email == email))
            )

            if existing_user:
                if existing_user.username == username:
                    raise AccountAlreadyExistsError("Username")
                raise AccountAlreadyExistsError("Email")

            user = User(
                username=username,
                email=email,
                first_name=request.first_name,
                last_name=request.last_name,
                dob=request.dob,
                password=hash_password(request.password.get_secret_value()),
                role=UserRole.STUDENT,
            )

            session.add(user)
    except IntegrityError as err:
        raise ConflictError("Có lỗi khi đăng ký tài khoản") from err
    return UserResponse.model_validate(user)


async def login(
    request: LoginRequest, session: AsyncSession, settings: Settings
) -> str:
    user: User | None = await session.scalar(
        select(User).where(
            or_(
                User.username == request.identifier,
                User.email == request.identifier,
            )
        )
    )

    if not user or not verify_password(
        request.password.get_secret_value(), user.password
    ):
        raise InvalidCredentialsError("Sai username/email hoặc mật khẩu")

    return create_access_token(user_id=user.id, settings=settings)
