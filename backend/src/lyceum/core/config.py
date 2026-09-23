from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Lyceum"
    database_url: str

    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_expire: int
    cookie_secure: bool

    frontend_origin: str = "http://localhost:3000"
    sql_echo: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
