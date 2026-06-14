"""
FastAPI application entry point.

The IBKR client is held on `app.state.ibkr` as a lazily-connected singleton.
Routes call `await request.app.state.ibkr.get_client()` to acquire a connected
`ib_async.IB` instance.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import account, health, portfolio
from .config import settings
from .ibkr.client import IBKRClient

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Construct the IBKR client at startup; disconnect at shutdown.

    We don't eagerly connect: IB Gateway may not be ready yet when the
    backend starts. The first request that needs IBKR triggers the connect
    with the client's own retry loop.
    """
    ibkr = IBKRClient(
        host=settings.IB_GATEWAY_HOST,
        port=settings.IB_GATEWAY_PORT,
        client_id=settings.IB_CLIENT_ID,
    )
    app.state.ibkr = ibkr
    logger.info(
        "IBKR client configured (host=%s port=%d clientId=%d). "
        "Will connect lazily on first request.",
        settings.IB_GATEWAY_HOST,
        settings.IB_GATEWAY_PORT,
        settings.IB_CLIENT_ID,
    )

    yield

    await ibkr.disconnect()
    logger.info("IBKR client disconnected.")


app = FastAPI(
    title="Wetfloor Backend",
    description="Self-hosted IBKR dashboard backend.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(account.router, prefix="/api/account", tags=["account"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
