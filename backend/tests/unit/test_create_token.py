from uuid import uuid7

import jwt
import pytest
from pydantic import SecretStr

from lyceum.core.config import Settings
from lyceum.core.security import create_access_token


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://test:test@localhost/lyceum_test",
        jwt_secret_key=SecretStr(
            "035ddede5e87696d973f54648a36a3c26d9e4888df9d88690c974aaf0008af57"
        ),
        jwt_expire=30,
        jwt_algorithm="HS256",
        cookie_secure=False,
    )


def test_create_access_token(settings: Settings) -> None:
    user_id = uuid7()
    token = create_access_token(user_id, settings)

    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == str(user_id)
    assert "iat" in payload
    assert "exp" in payload
