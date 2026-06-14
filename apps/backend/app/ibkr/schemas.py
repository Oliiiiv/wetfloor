"""Pydantic models for IBKR-related API responses."""
from __future__ import annotations

from datetime import datetime

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


# --- Portfolio snapshot (Smart Homepage feed) ------------------------------


class Holding(BaseModel):
    """A single portfolio holding with valuation metrics.

    Optional fields (`market_price`, `market_value`, `unrealized_pnl`,
    `allocation_pct`) may be `None` when IBKR's portfolio cache hasn't
    populated them yet (typically right after connect, or for instruments
    without an active market data subscription).
    """

    symbol: str
    sec_type: str
    exchange: str | None = None
    currency: str
    quantity: float
    avg_cost: float
    market_price: float | None = None
    market_value: float | None = None
    unrealized_pnl: float | None = None
    unrealized_pnl_pct: float | None = None  # relative to cost basis
    realized_pnl: float | None = None
    allocation_pct: float | None = None  # 0.0 - 1.0 of gross position value


class PortfolioSnapshot(BaseModel):
    """Composite portfolio view powering the Smart Homepage (PLAN.md §5.2.1)."""

    as_of: datetime
    base_currency: str
    account: str | None = None
    net_liquidation: float | None = None
    total_market_value: float | None = None
    total_unrealized_pnl: float | None = None
    holdings: list[Holding]
