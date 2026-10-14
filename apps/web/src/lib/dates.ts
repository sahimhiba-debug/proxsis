// Dates written the Swiss way, straight from ISO strings (no Date object, so no time zone: « 2026-10-05 » is always
// the 5th). No dependency: the presentation's client components use it without the dictionaries.

/** « 05.10.2026 » ; « — » when there is no date. */
export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const [y, m, d] = iso.slice(0, 10).split("-");
  return `${d}.${m}.${y}`;
}

/** « 05.10 » (day and month, for axes and short lists). */
export function fmtDayMonth(iso: string): string {
  return `${iso.slice(8, 10)}.${iso.slice(5, 7)}`;
}
