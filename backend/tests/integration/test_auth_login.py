from datetime import date

import jwt
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.core.config import get_settings
from lyceum.core.security import hash_password
from lyceum.users.models import User, UserRole


@pytest_asyncio.fixture
async def existing_user(session: AsyncSession) -> User:
    user = User(
        username="user1",
        email="user1@gmail.com",
        first_name="AAA",
        last_name="BBB",
        dob=date(2000, 1, 1),
        password=hash_password("1"),
        role=UserRole.STUDENT,
    )

    async with session.begin():
        session.add(user)

    return user


@pytest.mark.asyncio
async def test_login(
    client: AsyncClient,
    existing_user: User,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "identifier": "user1",
            "password": "1",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"msg": "Đăng nhập thành công"}

    token = response.cookies.get("access_token")
    assert token is not None
    assert "httponly" in response.headers["set-cookie"].lower()

    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(existing_user.id)


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient,
    existing_user: User,
) -> None:
    response = await client.post(
        url="/api/v1/auth/login",
        json={
            "identifier": "user1",
            "password": "2",
        },
    )

    assert response.status_code == 400
    assert response.cookies.get("access_token") is None
