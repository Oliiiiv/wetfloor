import type { Holding } from "@/lib/api";
import {
  fmtMoney,
  fmtPct,
  fmtQty,
  fmtSignedMoney,
  pnlColorClass,
} from "@/lib/format";

interface HoldingCardProps {
  holding: Holding;
  rank?: number;
}

/**
 * Top Holdings Spotlight card. v1 is a quiet, scannable layout: symbol +
 * essentials at the top, P&L on the right, allocation bar at the bottom.
 *
 * v2 will add a mini K-line chart (TradingView Lightweight Charts) and the
 * day-change indicator once we proxy IBKR historical bars.
 */
export function HoldingCard({ holding, rank }: HoldingCardProps) {
  const allocationPct = holding.allocation_pct ?? 0;

  return (
    <article className="rounded-md border border-neutral-200 p-4 flex flex-col gap-3 hover:border-neutral-300 transition-colors">
      {/* Header: symbol + sec type + optional rank */}
      <header className="flex items-baseline justify-between gap-2">
        <div className="flex items-baseline gap-2">
          <span className="text-lg font-semibold font-mono tracking-tight">
            {holding.symbol}
          </span>
          <span className="text-xs text-neutral-500">{holding.sec_type}</span>
          {holding.exchange && (
            <span className="text-xs text-neutral-400">{holding.exchange}</span>
          )}
        </div>
        {rank !== undefined && (
          <span className="text-xs text-neutral-400 tabular-nums">
            #{rank}
          </span>
        )}
      </header>

      {/* Body: price + qty + market value, P&L on the right */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-xs text-neutral-500">Quantity</div>
          <div className="font-mono">{fmtQty(holding.quantity)}</div>
          <div className="text-xs text-neutral-500 mt-2">Avg cost</div>
          <div className="font-mono text-sm">
            {fmtMoney(holding.avg_cost)}{" "}
            <span className="text-neutral-400">{holding.currency}</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-neutral-500">Market price</div>
          <div className="font-mono">
            {holding.market_price !== null
              ? fmtMoney(holding.market_price)
              : "—"}
          </div>
          <div className="text-xs text-neutral-500 mt-2">Market value</div>
          <div className="font-mono text-sm">
            {fmtMoney(holding.market_value)}{" "}
            <span className="text-neutral-400">{holding.currency}</span>
          </div>
        </div>
      </div>

      {/* Unrealized P&L */}
      <div className="flex items-baseline justify-between border-t border-neutral-100 pt-3">
        <span className="text-xs text-neutral-500">Unrealized P&L</span>
        <div className="text-right">
          <span
            className={`font-mono font-medium ${pnlColorClass(
              holding.unrealized_pnl
            )}`}
          >
            {fmtSignedMoney(holding.unrealized_pnl)}
          </span>
          {holding.unrealized_pnl_pct !== null && (
            <span
              className={`ml-2 text-sm ${pnlColorClass(holding.unrealized_pnl_pct)}`}
            >
              {fmtPct(holding.unrealized_pnl_pct, 2, true)}
            </span>
          )}
        </div>
      </div>

      {/* Allocation bar */}
      <div>
        <div className="flex items-baseline justify-between text-xs text-neutral-500 mb-1.5">
          <span>Allocation</span>
          <span className="font-mono">{fmtPct(holding.allocation_pct)}</span>
        </div>
        <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-brand rounded-full"
            style={{ width: `${Math.min(allocationPct * 100, 100)}%` }}
          />
        </div>
      </div>
    </article>
  );
}
