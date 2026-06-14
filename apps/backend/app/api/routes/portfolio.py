"""
Portfolio snapshot endpoint — powers the Smart Homepage (PLAN.md §5.2.1).

This is the single source of truth for the dashboard's first paint. It pulls
the IBKR portfolio cache (populated by ib_async during connectAsync) and
augments it with account summary metrics, allocation %, and an unrealized
P&L percentage relative to cost basis.

`ib.portfolio()` is a pure cache getter — safe to call from FastAPI's async
context. Account summary requires the async variant (see route below).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from ...ibkr.schemas import Holding, PortfolioSnapshot

logger = logging.getLogger(__name__)

router = APIRouter()


def _safe_div(num: float | None, den: float | None) -> float | None:
    """Defensive division: returns None if inputs are missing or denominator is 0."""
    if num is None or den is None or den == 0:
        return None
    return num / den


@router.get("/snapshot", response_model=PortfolioSnapshot)
async def portfolio_snapshot(request: Request) -> PortfolioSnapshot:
    ibkr = request.app.state.ibkr
    try:
        ib = await ibkr.get_client()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to obtain IBKR client")
        raise HTTPException(
            status_code=503,
            detail=f"IBKR Gateway unavailable: {exc}",
        ) from exc

    # --- Account-level metrics (drives Stats Strip) ---
    # accountSummary is RPC-backed in async mode, so we await it. The values
    # are strings in IBKR's API; we cast carefully.
    summary = await ib.accountSummaryAsync()
    account_id: str | None = None
    base_currency: str = "USD"
    net_liquidation: float | None = None

    for item in summary:
        if account_id is None and item.account:
            account_id = item.account
        if item.tag == "NetLiquidation":
            net_liquidation = _try_float(item.value)
            if item.currency:
                base_currency = item.currency

    # --- Per-holding portfolio items (pure cache; no RPC) ---
    portfolio_items = ib.portfolio()

    # Compute total market value across all holdings for allocation % math.
    # We use absolute value to keep short positions sensible.
    total_abs_value = sum(
        abs(item.marketValue or 0.0) for item in portfolio_items
    ) or None

    holdings: list[Holding] = []
    total_unrealized = 0.0
    saw_unrealized = False

    for item in portfolio_items:
        contract = item.contract
        market_price = item.marketPrice if item.marketPrice is not None else None
        market_value = item.marketValue if item.marketValue is not None else None
        unrealized = item.unrealizedPNL if item.unrealizedPNL is not None else None
        realized = item.realizedPNL if item.realizedPNL is not None else None
        avg_cost = float(item.averageCost or 0.0)
        qty = float(item.position or 0.0)

        # P&L % relative to cost basis (qty * avg_cost).
        cost_basis = qty * avg_cost if qty and avg_cost else None
        pnl_pct = _safe_div(unrealized, cost_basis) if cost_basis else None

        allocation = (
            _safe_div(abs(market_value), total_abs_value)
            if market_value is not None
            else None
        )

        if unrealized is not None:
            total_unrealized += unrealized
            saw_unrealized = True

        holdings.append(
            Holding(
                symbol=contract.symbol,
                sec_type=contract.secType,
                exchange=(contract.primaryExchange or contract.exchange or None) or None,
                currency=contract.currency,
                quantity=qty,
                avg_cost=avg_cost,
                market_price=market_price,
                market_value=market_value,
                unrealized_pnl=unrealized,
                unrealized_pnl_pct=pnl_pct,
                realized_pnl=realized,
                allocation_pct=allocation,
            )
        )

    # Sort holdings by market value desc — frontend can take top-N from here.
    holdings.sort(
        key=lambda h: abs(h.market_value) if h.market_value is not None else 0.0,
        reverse=True,
    )

    return PortfolioSnapshot(
        as_of=datetime.now(timezone.utc),
        base_currency=base_currency,
        account=account_id,
        net_liquidation=net_liquidation,
        total_market_value=total_abs_value,
        total_unrealized_pnl=total_unrealized if saw_unrealized else None,
        holdings=holdings,
    )


def _try_float(value: str) -> float | None:
    """Permissive float parse. IBKR account summary values are strings."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
