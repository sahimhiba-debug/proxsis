import type { NeedRow } from "./types";

/** Peak weekly persons (low / high), first week and trades of an estimated need. */
export function needSummary(rows: NeedRow[]) {
  if (!rows?.length) return null;
  const weeks = new Map<string, { low: number; mid: number; high: number }>();
  for (const r of rows) {
    const w = weeks.get(r.semaine) ?? { low: 0, mid: 0, high: 0 };
    w.low += r.personnes_bas;
    w.mid += r.personnes_milieu;
    w.high += r.personnes_haut;
    weeks.set(r.semaine, w);
  }
  const values = [...weeks.values()];
  return {
    low: Math.max(...values.map((v) => v.low)),
    high: Math.max(...values.map((v) => v.high)),
    first: [...weeks.keys()].sort()[0],
    trades: [...new Set(rows.map((r) => r.metier))].sort(),
    weeks: [...weeks.entries()].sort(([a], [b]) => a.localeCompare(b)),
  };
}

