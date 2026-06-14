"""Account summary endpoint — the first real vertical slice."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...ibkr.schemas import AccountSummary, AccountValueItem, PositionItem

logger = logging.getLogger(__name__)

router = APIRouter()

# Account summary fields surfaced to the dashboard. IBKR returns many more
# (Cushion, ExcessLiquidity, OptionMarketValue, ...) — we filter to the
# headline numbers a retail user cares about.
_HEADLINE_TAGS: dict[str, str] = {
    "NetLiquidation": "Net Liquidation Value",
    "TotalCashValue": "Total Cash Value",
    "BuyingPower": "Buying Power",
    "AvailableFunds": "Available Funds",
    "GrossPositionValue": "Gross Position Value",
}


@router.get("/summary", response_model=AccountSummary)
async def account_summary(request: Request) -> AccountSummary:
    ibkr = request.app.state.ibkr
    try:
        ib = await ibkr.get_client()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to obtain IBKR client")
        raise HTTPException(
            status_code=503,
            detail=f"IBKR Gateway unavailable: {exc}",
        ) from exc

    # NOTE: inside FastAPI we MUST use the *Async variants of ib_async methods.
    # The sync methods (e.g. ib.accountSummary()) internally call
    # loop.run_until_complete(...) which throws RuntimeError when invoked from
    # within an already-running event loop.
    raw_summary = await ib.accountSummaryAsync()
    items = [
        AccountValueItem(
            tag=item.tag,
            label=_HEADLINE_TAGS[item.tag],
            value=item.value,
            currency=item.currency,
        )
        for item in raw_summary
        if item.tag in _HEADLINE_TAGS
    ]

    # ib.positions() is a pure cache getter (no RPC, no _run), so it's safe to
    # call sync. Positions are auto-subscribed during connectAsync().
    raw_positions = ib.positions()
    positions = [
        PositionItem(
            symbol=pos.contract.symbol,
            quantity=float(pos.position),
            avg_cost=float(pos.avgCost),
            currency=pos.contract.currency,
            exchange=getattr(pos.contract, "exchange", None) or None,
            sec_type=getattr(pos.contract, "secType", None) or None,
        )
        for pos in raw_positions
    ]

    return AccountSummary(items=items, positions=positions)
