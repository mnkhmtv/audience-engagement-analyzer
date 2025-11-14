from __future__ import annotations

"""
Centralized settings for DB and auth. Uses python-dotenv to load backend/.env,
then constructs a typed config object without relying on pydantic-settings to
parse all env vars (to avoid extra-field validation issues in mixed envs).
"""

import os
from pathlib import Path
from typing import Any
from pydantic import BaseModel
from pydantic import PostgresDsn
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ACCESS_EXPIRE: int
    OWNER_EMAIL: str = "owner@example.com"
    OWNER_PASSWORD: str = "owner"
    ASYNC_DATABASE_URI: PostgresDsn | None = None


def _build_settings() -> Settings:
    def env(name: str, default: Any | None = None) -> Any:
        return os.environ.get(name, default)

    db_user = env("DATABASE_USER")
    db_pass = env("DATABASE_PASSWORD")
    db_host = env("DATABASE_HOST")
    db_port = int(env("DATABASE_PORT", 5432))
    db_name = env("DATABASE_NAME")

    async_uri = env("ASYNC_DATABASE_URI")
    if not async_uri and all([db_user, db_pass, db_host, db_port, db_name]):
        async_uri = str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                path=f"{db_name}",
            )
        )

    return Settings(
        DATABASE_USER=db_user,
        DATABASE_PASSWORD=db_pass,
        DATABASE_HOST=db_host,
        DATABASE_PORT=db_port,
        DATABASE_NAME=db_name,
        SECRET_KEY=env("SECRET_KEY", "change_me"),
        ALGORITHM=env("ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)),
        REFRESH_TOKEN_EXPIRE_MINUTES=int(env("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)),
        ACCESS_EXPIRE=int(env("ACCESS_EXPIRE", 30)),
        OWNER_EMAIL=env("OWNER_EMAIL", "owner@example.com"),
        OWNER_PASSWORD=env("OWNER_PASSWORD", "owner"),
        ASYNC_DATABASE_URI=async_uri,  # type: ignore[arg-type]
    )


settings = _build_settings()
