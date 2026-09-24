from fastapi import APIRouter

from lyceum.auth.schemas import UserResponse
from lyceum.users.deps import CurrentUserDep

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUserDep):
    return current_user
