"""Pydantic models for IBKR-related API responses."""
from __future__ import annotations

from pydantic import BaseModel


class AccountValueItem(BaseModel):
    """One line of the IBKR account summary, e.g. NetLiquidation."""

    tag: str
    label: str
    value: str
    currency: str


class PositionItem(BaseModel):
    symbol: str
    quantity: float
    avg_cost: float
    currency: str
    exchange: str | None = None
    sec_type: str | None = None


class AccountSummary(BaseModel):
    """Composite response: account-level metrics + per-symbol positions."""

    items: list[AccountValueItem]
    positions: list[PositionItem]
