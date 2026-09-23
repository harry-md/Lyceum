import datetime
from datetime import UTC, timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from lyceum.core.config import Settings

password_hasher = PasswordHash.recommended()

DUMMY_PASSWORD_HASH = password_hasher.hash(password="dummy-password")


def hash_password(password: str) -> str:
    return password_hasher.hash(password=password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password=password, hash=hashed_password)


def create_access_token(user_id: UUID, settings: Settings) -> str:
    now = datetime.datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.jwt_expire)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload=payload,
        key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
