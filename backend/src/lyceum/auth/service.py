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
from lyceum.users.models import User, UserRole
from lyceum.users.repository import UserRepository


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        settings: Settings,
    ):
        self._session = session
        self._user_repo = user_repository
        self._settings = settings

    async def register(self, request: RegisterRequest) -> UserResponse:
        username = request.username.casefold()
        email = request.email.casefold()

        try:
            async with self._session.begin():
                existing_user = await self._user_repo.find_by_username_or_email(
                    username=username, email=email
                )
                if existing_user:
                    if existing_user.username == username:
                        raise AccountAlreadyExistsError("username")
                    raise AccountAlreadyExistsError("email")

                user = User(
                    username=username,
                    email=email,
                    first_name=request.first_name,
                    last_name=request.last_name,
                    dob=request.dob,
                    password=hash_password(request.password.get_secret_value()),
                    role=UserRole.STUDENT,
                )

                self._user_repo.add(user)
        except IntegrityError as err:
            raise AccountAlreadyExistsError() from err
        return UserResponse.model_validate(user)

    async def login(self, request: LoginRequest) -> str:
        user = await self._user_repo.find_by_username_or_email(
            username=request.identifier, email=request.identifier
        )

        if not user or not verify_password(
            request.password.get_secret_value(), user.password
        ):
            raise InvalidCredentialsError("Sai username/email hoặc mật khẩu")

        return create_access_token(user_id=user.id, settings=self._settings)
