/**
 * Backend API client.
 *
 * Server-side rendering (which is where `/dashboard` fetches happen) runs
 * inside the Next.js container, so the backend is reachable via the docker
 * network hostname `backend`. For local dev with `npm run dev`, set
 * BACKEND_URL=http://localhost:8000 in `.env.local`.
 */
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export interface AccountValueItem {
  tag: string;
  label: string;
  value: string;
  currency: string;
}

export interface PositionItem {
  symbol: string;
  quantity: number;
  avg_cost: number;
  currency: string;
  exchange: string | null;
  sec_type: string | null;
}

export interface AccountSummary {
  items: AccountValueItem[];
  positions: PositionItem[];
}

export async function fetchAccountSummary(): Promise<AccountSummary> {
  const res = await fetch(`${BACKEND_URL}/api/account/summary`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(
      `Backend returned ${res.status} ${res.statusText}: ${body || "(empty)"}`
    );
  }
  return res.json();
}

export interface HealthResponse {
  status: string;
  ibkr_connected: boolean;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BACKEND_URL}/health`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`);
  }
  return res.json();
}

// --- Portfolio snapshot (Smart Homepage) -------------------------------

export interface Holding {
  symbol: string;
  sec_type: string;
  exchange: string | null;
  currency: string;
  quantity: number;
  avg_cost: number;
  market_price: number | null;
  market_value: number | null;
  unrealized_pnl: number | null;
  unrealized_pnl_pct: number | null;
  realized_pnl: number | null;
  allocation_pct: number | null;
}

export interface PortfolioSnapshot {
  as_of: string;
  base_currency: string;
  account: string | null;
  net_liquidation: number | null;
  total_market_value: number | null;
  total_unrealized_pnl: number | null;
  holdings: Holding[];
}

export async function fetchPortfolioSnapshot(): Promise<PortfolioSnapshot> {
  const res = await fetch(`${BACKEND_URL}/api/portfolio/snapshot`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(
      `Backend returned ${res.status} ${res.statusText}: ${body || "(empty)"}`
    );
  }
  return res.json();
}
