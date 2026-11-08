/** Thin-space grouped litres, e.g. "12 400". */
export function formatLitres(litres: number, fractionDigits = 0): string {
  const fixed = litres.toFixed(fractionDigits);
  const [whole, frac] = fixed.split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, "\u2009");
  return frac !== undefined ? `${grouped}.${frac}` : grouped;
}

/** Days of stock left, one decimal when under 10. */
export function formatDaysLeft(days: number): string {
  if (!Number.isFinite(days) || days < 0) return "—";
  if (days >= 10) return `${Math.round(days)} days left`;
  return `${days.toFixed(1)} days left`;
}
