/**
 * Number / currency / percent formatters tuned for a financial dashboard.
 *
 * Conventions:
 *   - Money: localized with grouping separators, fixed decimal places, currency code on the side
 *   - Percentages: x.x% style (we pass 0.18 for 18%)
 *   - Diffs: explicit "+" sign for gains
 */

export function fmtMoney(
  value: number | null | undefined,
  currency = "USD",
  fractionDigits = 2,
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  return value.toLocaleString(undefined, {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
}

export function fmtSignedMoney(
  value: number | null | undefined,
  fractionDigits = 2,
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return (
    sign +
    value.toLocaleString(undefined, {
      minimumFractionDigits: fractionDigits,
      maximumFractionDigits: fractionDigits,
    })
  );
}

export function fmtPct(
  value: number | null | undefined,
  fractionDigits = 2,
  signed = false,
): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  const pct = value * 100;
  const sign = signed && pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(fractionDigits)}%`;
}

export function fmtQty(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  // Whole-share holdings most common; format with grouping but no forced decimals.
  return value.toLocaleString(undefined, {
    maximumFractionDigits: 6,
  });
}

/** Tailwind color class for a P&L value (green / red / neutral). */
export function pnlColorClass(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "text-neutral-500";
  }
  if (value > 0) return "text-emerald-600";
  if (value < 0) return "text-rose-600";
  return "text-neutral-500";
}
