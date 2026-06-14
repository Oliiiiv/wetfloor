"""
Application settings. Override via environment variables.

In docker-compose, these are injected via the `environment:` block on the
`backend` service. For local dev, copy `.env.example` to `apps/backend/.env`.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # IBKR Gateway connection (matches socat-exposed ports in our compose file)
    IB_GATEWAY_HOST: str = "ib-gateway"
    IB_GATEWAY_PORT: int = 4004
    IB_CLIENT_ID: int = 2

    # CORS — frontend runs on :3000 in dev and in docker
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
