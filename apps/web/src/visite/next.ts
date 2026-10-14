// Visit, time 2 « Le lundi suivant » (brief « à distance », 4.2 and § 6): the following Monday keeps the decisions of
// the first one. Pure: the ranking of the following Monday by the same rule (lundi_suivant.json), the carnet. A lead
// set aside does not come back; a lead to look at again comes back on its date (or keeps waiting for it); a kept lead
// comes back with its next action; the next company of the ranking takes each freed place. Nothing here is a call
// result: a lead handed over never turns by itself into a successful call or a mission.
import type { CarnetEntry } from "@/lib/carnet";

export interface NextData {
  schema: 1;
  premier: string; // the first Monday (the frozen list)
  lundi: string; // the following Monday
  fin_des_donnees: string;
  regle: string;
  classement: { id: string; nom: string; ville: string | null; rang: number }[];
  nouvelles_publications: string[]; // published between the two Mondays in our data
}

export type NextKind = "recall" | "kept" | "new" | "ranked";

export interface NextRow {
  id: string;
  kind: NextKind; // « recall »: its date has come; « kept »: back with its next action; « new »: not in the first list
  entry?: CarnetEntry;
}

export interface NextMonday {
  calls: NextRow[]; // the ten of the following Monday
  waiting: { id: string; date: string }[]; // to look at again later than the following Monday
  setAside: string[]; // never back
}

/** The prepared examples of time 2, for the companies on which the director has not decided: a lead set aside
 *  (reason « autre »: nothing is said about the real company) and a lead to look at again on the following Monday. */
export function exampleCarnet(next: string): Record<string, CarnetEntry> {
  return {
    "ent-734d5f7d45": { decision: "ecarter", motif: "autre" }, // Bitz travaux publics SA
    "ent-266673a5c4": { decision: "revoir", revoir: next }, // MELLY CONSTRUCTIONS SA
  };
}

export function nextMonday(data: NextData, firstTen: string[], carnet: Record<string, CarnetEntry>): NextMonday {
  const setAside = Object.keys(carnet).filter((id) => carnet[id].decision === "ecarter").sort();
  const waiting = Object.entries(carnet).filter(([, e]) => e.decision === "revoir" && e.revoir && e.revoir > data.lundi)
    .map(([id, e]) => ({ id, date: e.revoir as string })).sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
  const recalls = Object.entries(carnet).filter(([, e]) => e.decision === "revoir" && e.revoir && e.revoir <= data.lundi)
    .map(([id]) => id);
  const kept = Object.entries(carnet).filter(([, e]) => e.decision === "appeler" || e.decision === "verifier").map(([id]) => id);
  const rank = (id: string) => data.classement.find((c) => c.id === id)?.rang ?? Number.MAX_SAFE_INTEGER;
  const byRank = (a: string, b: string) => rank(a) - rank(b) || a.localeCompare(b);
  const placed = new Set([...setAside, ...waiting.map((w) => w.id)]);
  const calls: NextRow[] = [];
  for (const id of recalls.sort(byRank)) calls.push({ id, kind: "recall", entry: carnet[id] });
  for (const id of kept.sort(byRank)) calls.push({ id, kind: "kept", entry: carnet[id] });
  for (const r of calls) placed.add(r.id);
  for (const c of data.classement) {
    if (calls.length >= 10) break;
    if (placed.has(c.id)) continue;
    calls.push({ id: c.id, kind: firstTen.includes(c.id) ? "ranked" : "new" });
    placed.add(c.id);
  }
  return { calls: calls.slice(0, 10), waiting, setAside };
}
