import Link from "next/link";

import { HoldingCard } from "@/components/HoldingCard";
import { StatsStrip } from "@/components/StatsStrip";
import { fetchPortfolioSnapshot, type PortfolioSnapshot } from "@/lib/api";
import {
  fmtMoney,
  fmtPct,
  fmtQty,
  fmtSignedMoney,
  pnlColorClass,
} from "@/lib/format";

// IBKR data changes constantly — opt out of every cache layer.
export const dynamic = "force-dynamic";

const TOP_HOLDINGS_COUNT = 5;

export default async function DashboardPage() {
  let snapshot: PortfolioSnapshot | null = null;
  let error: string | null = null;

  try {
    snapshot = await fetchPortfolioSnapshot();
  } catch (err) {
    error = err instanceof Error ? err.message : String(err);
  }

  const topHoldings = snapshot?.holdings.slice(0, TOP_HOLDINGS_COUNT) ?? [];
  const remainingHoldings = snapshot?.holdings.slice(TOP_HOLDINGS_COUNT) ?? [];

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="max-w-6xl mx-auto space-y-10">
        <header className="flex items-baseline justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-sm text-neutral-500 mt-1">
              {snapshot
                ? `Snapshot at ${new Date(snapshot.as_of).toLocaleTimeString()}`
                : "Loading live data from your IBKR account."}
            </p>
          </div>
          <Link
            href="/"
            className="text-sm text-neutral-500 hover:text-neutral-900"
          >
            ← Home
          </Link>
        </header>

        {error && (
          <section className="rounded-md border border-red-200 bg-red-50 p-5">
            <div className="font-medium text-red-900 mb-2">
              Could not reach the backend.
            </div>
            <pre className="text-xs text-red-800 whitespace-pre-wrap font-mono">
              {error}
            </pre>
            <p className="text-xs text-red-700 mt-3">
              Check that <code className="font-mono">backend</code> and{" "}
              <code className="font-mono">ib-gateway</code> are running:{" "}
              <code className="font-mono">./scripts/compose.sh ps</code>.
            </p>
          </section>
        )}

        {snapshot && (
          <>
            {/* Smart Statistics Strip */}
            <StatsStrip snapshot={snapshot} />

            {/* Top Holdings Spotlight */}
            {topHoldings.length > 0 ? (
              <section>
                <div className="flex items-baseline justify-between mb-4">
                  <h2 className="text-lg font-semibold">Top holdings</h2>
                  <span className="text-xs text-neutral-500">
                    by market value
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {topHoldings.map((holding, idx) => (
                    <HoldingCard
                      key={`${holding.symbol}-${holding.sec_type}`}
                      holding={holding}
                      rank={idx + 1}
                    />
                  ))}
                </div>
              </section>
            ) : (
              <section className="rounded-md border border-neutral-200 px-5 py-8 text-center text-neutral-500 text-sm">
                No holdings yet. Place a trade in IBKR to see data here.
              </section>
            )}

            {/* All Positions table — the rest after top N */}
            {remainingHoldings.length > 0 && (
              <section>
                <div className="flex items-baseline justify-between mb-4">
                  <h2 className="text-lg font-semibold">
                    Other positions{" "}
                    <span className="text-neutral-400 font-normal">
                      ({remainingHoldings.length})
                    </span>
                  </h2>
                </div>
                <div className="overflow-x-auto rounded-md border border-neutral-200">
                  <table className="w-full text-sm">
                    <thead className="bg-neutral-50 text-neutral-500 text-xs uppercase tracking-wide">
                      <tr>
                        <th className="text-left font-medium px-4 py-2">
                          Symbol
                        </th>
                        <th className="text-left font-medium px-4 py-2">
                          Type
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Qty
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Price
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Value
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Unrealized P&L
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Alloc
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {remainingHoldings.map((pos) => (
                        <tr
                          key={`${pos.symbol}-${pos.sec_type}`}
                          className="border-t border-neutral-100"
                        >
                          <td className="px-4 py-2 font-mono">{pos.symbol}</td>
                          <td className="px-4 py-2 text-neutral-500">
                            {pos.sec_type}
                          </td>
                          <td className="px-4 py-2 text-right font-mono">
                            {fmtQty(pos.quantity)}
                          </td>
                          <td className="px-4 py-2 text-right font-mono">
                            {fmtMoney(pos.market_price)}
                          </td>
                          <td className="px-4 py-2 text-right font-mono">
                            {fmtMoney(pos.market_value)}{" "}
                            <span className="text-neutral-400">
                              {pos.currency}
                            </span>
                          </td>
                          <td
                            className={`px-4 py-2 text-right font-mono ${pnlColorClass(pos.unrealized_pnl)}`}
                          >
                            {fmtSignedMoney(pos.unrealized_pnl)}
                          </td>
                          <td className="px-4 py-2 text-right font-mono text-neutral-500">
                            {fmtPct(pos.allocation_pct)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </main>
  );
}
