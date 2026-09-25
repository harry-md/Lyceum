from fastapi import APIRouter, Response, status

from lyceum.auth.deps import AuthServiceDep
from lyceum.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from lyceum.core.deps import SettingsDep

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest, auth_service: AuthServiceDep
) -> UserResponse:
    return await auth_service.register(request)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    response: Response,
    request: LoginRequest,
    auth_service: AuthServiceDep,
    settings: SettingsDep,
) -> dict[str, str]:
    token = await auth_service.login(request)
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
