import type { PortfolioSnapshot } from "@/lib/api";
import { fmtMoney, fmtSignedMoney, pnlColorClass } from "@/lib/format";

interface StatsStripProps {
  snapshot: PortfolioSnapshot;
}

/**
 * Smart Statistics Strip — the top horizontal band on the dashboard.
 * v1 surfaces account-level metrics derived purely from IBKR data.
 * v2 will add today's P&L, daily contributors, and sentiment temperature
 * once we wire in historical bars and FinBERT.
 */
export function StatsStrip({ snapshot }: StatsStripProps) {
  const holdingsCount = snapshot.holdings.length;

  return (
    <section
      aria-label="Account statistics"
      className="grid grid-cols-2 sm:grid-cols-4 gap-3"
    >
      <StatTile
        label="Net liquidation"
        value={fmtMoney(snapshot.net_liquidation, snapshot.base_currency)}
        unit={snapshot.base_currency}
      />
      <StatTile
        label="Total unrealized P&L"
        value={fmtSignedMoney(snapshot.total_unrealized_pnl)}
        unit={snapshot.base_currency}
        valueClassName={pnlColorClass(snapshot.total_unrealized_pnl)}
      />
      <StatTile
        label="Holdings"
        value={holdingsCount.toString()}
        unit={holdingsCount === 1 ? "position" : "positions"}
      />
      <StatTile
        label="Account"
        value={snapshot.account ?? "—"}
      />
    </section>
  );
}

function StatTile({
  label,
  value,
  unit,
  valueClassName,
}: {
  label: string;
  value: string;
  unit?: string;
  valueClassName?: string;
}) {
  return (
    <div className="rounded-md border border-neutral-200 px-4 py-3">
      <div className="text-xs uppercase tracking-wide text-neutral-500">
        {label}
      </div>
      <div className="mt-1 flex items-baseline gap-1.5">
        <span className={`text-lg font-mono font-medium ${valueClassName ?? ""}`}>
          {value}
        </span>
        {unit && (
          <span className="text-xs text-neutral-400 font-normal">{unit}</span>
        )}
      </div>
    </div>
  );
}
