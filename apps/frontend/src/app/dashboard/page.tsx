import Link from "next/link";

import { fetchAccountSummary, type AccountSummary } from "@/lib/api";

// The IBKR data changes on every request — opt out of any caching.
export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let summary: AccountSummary | null = null;
  let error: string | null = null;

  try {
    summary = await fetchAccountSummary();
  } catch (err) {
    error = err instanceof Error ? err.message : String(err);
  }

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="max-w-5xl mx-auto space-y-10">
        <header className="flex items-baseline justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-sm text-neutral-500 mt-1">
              Live data from your IBKR paper account.
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

        {summary && (
          <>
            <section>
              <h2 className="text-lg font-semibold mb-4">Account summary</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {summary.items.map((item) => (
                  <div
                    key={item.tag}
                    className="rounded-md border border-neutral-200 p-4"
                  >
                    <div className="text-xs uppercase tracking-wide text-neutral-500">
                      {item.label}
                    </div>
                    <div className="mt-2 text-xl font-mono">
                      {item.value}{" "}
                      <span className="text-sm text-neutral-500">
                        {item.currency}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-lg font-semibold mb-4">
                Positions{" "}
                <span className="text-neutral-400 font-normal">
                  ({summary.positions.length})
                </span>
              </h2>
              {summary.positions.length === 0 ? (
                <p className="text-sm text-neutral-500 italic">
                  No positions yet. Place a paper trade in IBKR to see data
                  here.
                </p>
              ) : (
                <div className="overflow-x-auto rounded-md border border-neutral-200">
                  <table className="w-full text-sm">
                    <thead className="bg-neutral-50 text-neutral-500">
                      <tr>
                        <th className="text-left font-medium px-4 py-2">
                          Symbol
                        </th>
                        <th className="text-left font-medium px-4 py-2">
                          Type
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Quantity
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Avg cost
                        </th>
                        <th className="text-right font-medium px-4 py-2">
                          Currency
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.positions.map((pos) => (
                        <tr
                          key={`${pos.symbol}-${pos.sec_type ?? ""}`}
                          className="border-t border-neutral-100"
                        >
                          <td className="px-4 py-2 font-mono">{pos.symbol}</td>
                          <td className="px-4 py-2 text-neutral-500">
                            {pos.sec_type ?? "—"}
                          </td>
                          <td className="px-4 py-2 text-right font-mono">
                            {pos.quantity.toLocaleString()}
                          </td>
                          <td className="px-4 py-2 text-right font-mono">
                            {pos.avg_cost.toFixed(2)}
                          </td>
                          <td className="px-4 py-2 text-right text-neutral-500">
                            {pos.currency}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
