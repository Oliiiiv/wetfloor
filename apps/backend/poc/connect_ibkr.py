"""
Phase 0 De-risk Script: IBKR Paper Account Connection
=====================================================

Goal: Verify that we can connect to an IBKR paper account from inside Docker
      and pull basic account data.

Run via:
    docker compose up backend-poc

Expected output:
    - Account summary (Net Liquidation, Cash Balance, Buying Power)
    - Position list (may be empty if you haven't traded in the paper account yet)
"""
from __future__ import annotations

import os
import sys
import time

from ib_async import IB


def main() -> int:
    host = os.getenv("IB_GATEWAY_HOST", "ib-gateway")
    port = int(os.getenv("IB_GATEWAY_PORT", "4002"))
    client_id = int(os.getenv("IB_CLIENT_ID", "1"))

    print()
    print("=" * 70)
    print("  CautiousWetfloor — Phase 0 De-risk: IBKR Paper Connection")
    print("=" * 70)
    print(f"Connecting to IB Gateway at {host}:{port} (clientId={client_id})...")
    print()

    ib = IB()

    # IB Gateway can take 30-60s to be fully ready, even after the port
    # opens. Retry with backoff.
    max_retries = 12
    for attempt in range(1, max_retries + 1):
        try:
            ib.connect(host, port, clientId=client_id, timeout=10)
            print(f"[OK] Connected on attempt {attempt}")
            print()
            break
        except Exception as exc:  # noqa: BLE001
            if attempt == max_retries:
                print(f"[FAIL] Could not connect after {max_retries} attempts: {exc}")
                print()
                print("Troubleshooting:")
                print("  1. Check that IB Gateway container is running:")
                print("       docker compose ps")
                print("  2. Check IB Gateway logs:")
                print("       docker compose logs ib-gateway")
                print("  3. Verify your IBKR credentials in .env are correct")
                print("  4. Make sure API access is enabled in your IBKR account:")
                print("       Account Management -> Settings -> API -> Settings")
                return 1
            print(f"  attempt {attempt}: {exc}. Retrying in 5s...")
            time.sleep(5)

    try:
        # -----------------------------------------------------------------
        # Account summary
        # -----------------------------------------------------------------
        print("Account Summary")
        print("-" * 70)
        summary = ib.accountSummary()
        keys_of_interest = {
            "NetLiquidation": "Net Liquidation Value",
            "TotalCashValue": "Total Cash Value",
            "BuyingPower": "Buying Power",
            "AvailableFunds": "Available Funds",
            "GrossPositionValue": "Gross Position Value",
        }
        for item in summary:
            if item.tag in keys_of_interest:
                label = keys_of_interest[item.tag]
                print(f"  {label:<28s} {item.value:>18s}  {item.currency}")
        print()

        # -----------------------------------------------------------------
        # Positions
        # -----------------------------------------------------------------
        print("Positions")
        print("-" * 70)
        positions = ib.positions()
        if not positions:
            print("  (No positions — buy something in your paper account to see data here)")
        else:
            print(f"  {'Symbol':<12s} {'Qty':>10s} {'Avg Cost':>14s} {'Currency':>10s}")
            for pos in positions:
                symbol = pos.contract.symbol
                qty = float(pos.position)
                avg_cost = float(pos.avgCost)
                currency = pos.contract.currency
                print(f"  {symbol:<12s} {qty:>10.2f} {avg_cost:>14.2f} {currency:>10s}")
        print()

        # -----------------------------------------------------------------
        # Success
        # -----------------------------------------------------------------
        print("=" * 70)
        print("  [PASS] De-risk Task 1 — IBKR connection works inside Docker!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  - Update docs/DERISK_LOG.md with your findings")
        print("  - Mark Task 1 complete; move on to Task 2 (FinBERT local inference)")
        print()
        return 0

    finally:
        ib.disconnect()


if __name__ == "__main__":
    sys.exit(main())
