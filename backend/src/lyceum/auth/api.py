from fastapi import APIRouter, Response, status

import lyceum.auth.service as auth_service
from lyceum.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from lyceum.core.deps import SettingsDep
from lyceum.db.deps import SessionDep

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: SessionDep,
) -> UserResponse:
    return await auth_service.register(request, session)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    response: Response,
    request: LoginRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> dict[str, str]:
    token = await auth_service.login(
        request=request, session=session, settings=settings
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        max_age=settings.jwt_expire * 60,
        path="/",
    )
    return {"msg": "Đăng nhập thành công"}
