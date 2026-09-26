from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.core.config import get_settings
from lyceum.core.security import create_access_token, hash_password
from lyceum.users.models import User, UserRole

pytestmark = pytest.mark.asyncio

URL = "/api/v1/users/me"
PASSWORD = "test-password-123"


@pytest_asyncio.fixture
async def existing_user(session: AsyncSession) -> User:
    user = User(
        username="current_user_test",
        email="current_user_test@example.com",
        first_name="Harry",
        last_name="Nguyen",
        dob=date(2000, 1, 1),
        password=hash_password(PASSWORD),
        role=UserRole.STUDENT,
    )

    async with session.begin():
        session.add(user)

    return user


def valid_payload(user: User) -> dict:
    now = datetime.now(UTC)
    return {
        "sub": str(user.id),
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }


def encode_token(
    payload: dict,
    *,
    wrong_secret: bool = False,
) -> str:
    settings = get_settings()
    secret = settings.jwt_secret_key.get_secret_value()

    if wrong_secret:
        secret += "-wrong-secret"

    return jwt.encode(
        payload,
        key=secret,
        algorithm=settings.jwt_algorithm,
    )


def assert_user_response(body: dict, user: User) -> None:
    # Kiểm tra chính xác các field public, tránh lộ password
    # hoặc vô tình thêm field nội bộ vào response.
    assert set(body) == {
        "id",
        "username",
        "first_name",
        "last_name",
        "dob",
        "email",
        "role",
        "created_at",
        "updated_at",
    }

    assert body["id"] == str(user.id)
    assert body["username"] == user.username
    assert body["first_name"] == user.first_name
    assert body["last_name"] == user.last_name
    assert body["dob"] == user.dob.isoformat()
    assert body["email"] == user.email
    assert body["role"] == user.role.value

    assert datetime.fromisoformat(body["created_at"]) == user.created_at
    assert datetime.fromisoformat(body["updated_at"]) == user.updated_at


async def test_get_current_user_with_valid_cookie(
    client: AsyncClient,
    existing_user: User,
) -> None:
    token = create_access_token(existing_user.id, get_settings())
    client.cookies.set("access_token", token)

    response = await client.get(URL)

    assert response.status_code == 200
    assert_user_response(response.json(), existing_user)


async def test_login_then_get_current_user(
    client: AsyncClient,
    existing_user: User,
) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "identifier": existing_user.username,
            "password": PASSWORD,
        },
    )

    assert login_response.status_code == 200
    assert login_response.cookies.get("access_token") is not None

    # AsyncClient tự lưu cookie nhận từ login và gửi sang /me.
    response = await client.get(URL)

    assert response.status_code == 200
    assert_user_response(response.json(), existing_user)


async def test_get_current_user_without_cookie(
    client: AsyncClient,
) -> None:
    response = await client.get(URL)

    assert response.status_code == 401
    assert response.json() == {"msg": "Thiếu access token"}


async def test_get_current_user_with_empty_cookie(
    client: AsyncClient,
) -> None:
    client.cookies.set("access_token", "")

    response = await client.get(URL)

    assert response.status_code == 401
    assert response.json() == {"msg": "Thiếu access token"}


async def test_bearer_header_does_not_replace_cookie(
    client: AsyncClient,
    existing_user: User,
) -> None:
    token = create_access_token(existing_user.id, get_settings())

    response = await client.get(
        URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    # Endpoint hiện tại chỉ đọc token từ cookie.
    assert response.status_code == 401
    assert response.json() == {"msg": "Thiếu access token"}


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        "abc.def.ghi",
    ],
)
async def test_get_current_user_with_malformed_token(
    client: AsyncClient,
    token: str,
) -> None:
    client.cookies.set("access_token", token)

    response = await client.get(URL)

    assert response.status_code == 401
    assert response.json() == {"msg": "Lỗi khi decode token"}


async def test_get_current_user_with_wrong_signature(
    client: AsyncClient,
    existing_user: User,
) -> None:
    token = encode_token(
        valid_payload(existing_user),
        wrong_secret=True,
    )
    client.cookies.set("access_token", token)

    response = await client.get(URL)

    assert response.status_code == 401
    assert response.json() == {"msg": "Lỗi khi decode token"}


@pytest.mark.parametrize(
    ("overrides", "removed_claim"),
    [
        pytest.param(
            {"exp": 0},
            None,
            id="expired-token",
        ),
        pytest.param(
            {},
            "exp",
            id="missing-exp",
        ),
        pytest.param(
            {},
            "sub",
            id="missing-sub",
        ),
        pytest.param(
            {"sub": "not-a-uuid"},
            None,
            id="sub-is-not-uuid",
        ),
        pytest.param(
            {"sub": ""},
            None,
            id="empty-sub",
        ),
        pytest.param(
            {"sub": 123},
            None,
            id="sub-is-not-string",
        ),
        pytest.param(
            {"exp": "not-a-timestamp"},
            None,
            id="invalid-exp",
        ),
    ],
)
async def test_get_current_user_with_invalid_claims(
    client: AsyncClient,
    existing_user: User,
    overrides: dict,
    removed_claim: str | None,
) -> None:
    payload = valid_payload(existing_user)
    payload.update(overrides)

    if removed_claim is not None:
        payload.pop(removed_claim)

    client.cookies.set("access_token", encode_token(payload))

    response = await client.get(URL)

    assert response.status_code == 401
    assert response.json() == {"msg": "Lỗi khi decode token"}


async def test_get_current_user_when_user_does_not_exist(
    client: AsyncClient,
) -> None:
    token = create_access_token(uuid4(), get_settings())
    client.cookies.set("access_token", token)

    response = await client.get(URL)

    # Hành vi hiện tại: InvalidCredentialsError được map thành 400.
    assert response.status_code == 400
    assert response.json() == {
        "msg": "Sai username/email hoặc mật khẩu",
    }


async def test_get_current_user_uses_identity_from_token(
    client: AsyncClient,
    session: AsyncSession,
    existing_user: User,
) -> None:
    another_user = User(
        username="another_current_user",
        email="another_current_user@example.com",
        first_name="Linh",
        last_name="Tran",
        dob=date(2001, 2, 3),
        password=existing_user.password,
        role=UserRole.INSTRUCTOR,
    )

    async with session.begin():
        session.add(another_user)

    token = create_access_token(another_user.id, get_settings())
    client.cookies.set("access_token", token)

    response = await client.get(URL)

    assert response.status_code == 200
    assert_user_response(response.json(), another_user)


async def test_get_current_user_reads_profile_from_database(
    client: AsyncClient,
    existing_user: User,
) -> None:
    payload = valid_payload(existing_user)
    payload.update(
        {
            "role": "admin",
            "email": "fake@example.com",
            "first_name": "Fake",
        }
    )
    client.cookies.set("access_token", encode_token(payload))

    response = await client.get(URL)

    # Các claim bổ sung không được ghi đè thông tin user trong DB.
    assert response.status_code == 200
    assert_user_response(response.json(), existing_user)
