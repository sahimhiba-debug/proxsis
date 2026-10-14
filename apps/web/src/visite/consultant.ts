// Visit, time 1: what the consultant's Monday shows after the director's decision (brief « à distance », 4.1 and § 6).
// Pure: the ten of the list in their order, the company the director decided on, his carnet entry. A lead handed to
// the consultant comes first; a lead set aside never goes to the consultant; a lead to look at again later waits for its
// date instead of taking a call; the next companies of the ranking keep their order. Nothing is ever sent by itself.
import type { CarnetEntry } from "@/lib/carnet";
import { AGENCE_EXEMPLE } from "./agences";

export interface ConsultantRow {
  id: string;
  confided: boolean; // handed by the director
}

export interface ConsultantMonday {
  first: ConsultantRow[]; // « Vos trois premiers appels »
  others: ConsultantRow[]; // the seven others, same ranking
  later: { id: string; date: string }[]; // to look at again, on their date
  setAside: string[]; // never shown to the consultant
}

/** The prepared example when the director has not decided: « À appeler », handed to the consultant. */
export const EXAMPLE_ENTRY: CarnetEntry = { decision: "appeler", confie: true };

export function consultantMonday(ten: string[], opened: string, entry: CarnetEntry, monday: string): ConsultantMonday {
  const ranked = ten.filter((id) => id !== opened);
  const handed = entry.confie === true && entry.decision !== "ecarter";
  if (entry.decision === "ecarter") {
    return { first: rows(ranked.slice(0, 3)), others: rows(ranked.slice(3, 10)), later: [], setAside: [opened] };
  }
  if (entry.decision === "revoir" && entry.revoir && entry.revoir > monday) {
    return { first: rows(ranked.slice(0, 3)), others: rows(ranked.slice(3, 10)), later: [{ id: opened, date: entry.revoir }],
      setAside: [] };
  }
  const order = handed ? [opened, ...ranked] : ten.includes(opened) ? ten : ranked;
  const all = order.slice(0, 10).map((id) => ({ id, confided: handed && id === opened }));
  return { first: all.slice(0, 3), others: all.slice(3), later: [], setAside: [] };
}

const rows = (ids: string[]) => ids.map((id) => ({ id, confided: false }));

/** One list in the visit and in the application (Q17, Hiba, 13.10.2026; B7): the ten of the Monday in the order of the
 *  agency's week in « Ma semaine » (Martigny, the agency of the example, when none is chosen); the list as it stands
 *  if the application has no week for that agency. */
export function inAgencyOrder<T extends { id: string }>(ten: T[], around: Record<string, string[]>, agence: string | null | undefined): T[] {
  const order = around[agence ?? AGENCE_EXEMPLE] ?? around[AGENCE_EXEMPLE] ?? [];
  const byId = new Map(ten.map((r) => [r.id, r]));
  const rows = order.map((id) => byId.get(id)).filter((r): r is T => r !== undefined);
  return rows.length === ten.length ? rows : ten;
}
