"""Liveness + readiness endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict:
    """Return service liveness and the current IBKR connection state.

    Does NOT attempt to connect to IBKR. Use `/api/account/summary` (or any
    real endpoint) to force a connection.
    """
    ibkr = request.app.state.ibkr
    return {
        "status": "ok",
        "ibkr_connected": ibkr.is_connected,
    }
