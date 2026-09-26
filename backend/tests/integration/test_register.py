from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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
async def test_register_success(client: AsyncClient, existing_user: User) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "first_name": "Test",
            "last_name": "User",
            "email": "user2@gmail.com",
            "password": "1",
            "dob": "2000-01-01",
        },
    )
    res = response.json()

    assert response.status_code == 201
    assert "id" in res
    assert "password" not in res
    assert res["username"] == "user2"
    assert res["first_name"] == "Test"
    assert res["last_name"] == "User"
    assert res["email"] == "user2@gmail.com"
    assert res["dob"] == "2000-01-01"


@pytest.mark.asyncio
async def test_register_same_username(client: AsyncClient, existing_user: User) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user1",
            "first_name": "Test",
            "last_name": "User",
            "email": "user2@gmail.com",
            "password": "1",
            "dob": "2000-01-01",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"msg": "Username đã tồn tại"}


@pytest.mark.asyncio
async def test_register_same_email(client: AsyncClient, existing_user: User) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "first_name": "Test",
            "last_name": "User",
            "email": "user1@gmail.com",
            "password": "1",
            "dob": "2000-01-01",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"msg": "Email đã tồn tại"}


@pytest.mark.asyncio
async def test_register_missing_username(
    client: AsyncClient, existing_user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": None,
            "first_name": "Test",
            "last_name": "User",
            "email": "user2@gmail.com",
            "password": "1",
            "dob": "2000-01-01",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_first_name(
    client: AsyncClient, existing_user: User
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "first_name": None,
            "last_name": "User",
            "email": "user2@gmail.com",
            "password": "1",
            "dob": "2000-01-01",
        },
    )

    assert response.status_code == 422
