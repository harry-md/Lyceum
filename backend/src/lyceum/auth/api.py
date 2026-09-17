from fastapi import APIRouter, status

from lyceum.auth.deps import AuthServiceDep
from lyceum.auth.schemas import RegisterRequest, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(request: RegisterRequest, user_service: AuthServiceDep):
    return await user_service.register(request)
