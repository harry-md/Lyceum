from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic_settings import SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from lyceum.core.config import Settings, get_settings


class TestSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_prefix="TEST_",
        extra="ignore",
    )

    cookie_secure: bool = False


@pytest.fixture(scope="session")
def app():
    test_settings = TestSettings()

    if make_url(test_settings.database_url).database != "lyceumdb_test":
        pytest.fail("Integration test chỉ được dùng DB lyceumdb_test")

    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("DATABASE_URL", test_settings.database_url)
        patch.setenv(
            "JWT_SECRET_KEY",
            test_settings.jwt_secret_key.get_secret_value(),
        )
        patch.setenv("JWT_EXPIRE", str(test_settings.jwt_expire))
        patch.setenv("COOKIE_SECURE", "false")

        get_settings.cache_clear()
        from lyceum.main import app as fastapi_app

        yield fastapi_app
        get_settings.cache_clear()


@pytest_asyncio.fixture
async def db_connection(app) -> AsyncGenerator[AsyncConnection]:
    from lyceum.db.session import engine

    if engine.url.database != "lyceumdb_test":
        pytest.fail("Engine đang không trỏ tới DB lyceumdb_test")

    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def session(db_connection: AsyncConnection) -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    ) as db_session:
        yield db_session


@pytest_asyncio.fixture
async def client(
    app: FastAPI, db_connection: AsyncConnection
) -> AsyncGenerator[AsyncClient, Any]:
    from lyceum.db.session import get_session

    async def override_get_session():
        async with AsyncSession(
            bind=db_connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        ) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as http_client:
            yield http_client
    finally:
        app.dependency_overrides.pop(get_session, None)
