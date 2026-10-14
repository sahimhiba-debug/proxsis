// The application's carnet (brief « à distance », § 6): per company of the Monday list, the decision (the same
// vocabulary as the visit, src/lib/carnet.ts) and what followed each call, dated, and in the trial week the preparation
// time. Kept on this device only (never sent: not a CRM, never a client record); no free text, so no name of a person.
// The trial export is one file, with company ids and choices only: it never goes into the repository or the site.
import { OUTCOMES, parseEntry, USEFUL, type CarnetEntry, type Outcome } from "./carnet";
import { readStored, writeStored } from "./useStored";

export const CARNET_KEY = "proxsis.carnet.v1";
export const TRIAL_KEY = "proxsis.essai"; // « on » during the trial week (semaine témoin)

export interface FieldNote {
  outcome: Outcome;
  rappel?: string; // « rappel convenu le… »: AAAA-MM-JJ
  le: string; // when it was noted (ISO), shown dated: a return from the field, never a published fact
}

export interface CarnetRecord {
  decision?: CarnetEntry;
  suites: FieldNote[];
  preparationMinutes?: number;
}

export type CarnetBook = Record<string, CarnetRecord>;

const ISO_DAY = /^\d{4}-\d{2}-\d{2}$/;

function parseNote(x: unknown): FieldNote | null {
  if (!x || typeof x !== "object") return null;
  const o = x as Record<string, unknown>;
  if (!OUTCOMES.includes(o.outcome as Outcome) || typeof o.le !== "string" || Number.isNaN(Date.parse(o.le))) return null;
  const note: FieldNote = { outcome: o.outcome as Outcome, le: o.le };
  if (o.outcome === "rappel" && typeof o.rappel === "string" && ISO_DAY.test(o.rappel)) note.rappel = o.rappel;
  return note;
}

/** A stored carnet, entry by entry: anything unknown is dropped, an unreadable store gives an empty carnet. */
export function parseBook(raw: string | null): CarnetBook {
  try {
    const v: unknown = JSON.parse(raw || "{}");
    if (!v || typeof v !== "object" || Array.isArray(v)) return {};
    return Object.fromEntries(Object.entries(v as Record<string, unknown>).flatMap(([id, r]) => {
      if (!r || typeof r !== "object") return [];
      const o = r as Record<string, unknown>;
      const decision = parseEntry(o.decision) ?? undefined;
      const suites = Array.isArray(o.suites) ? o.suites.map(parseNote).filter((n): n is FieldNote => n !== null) : [];
      const minutes = typeof o.preparationMinutes === "number" && o.preparationMinutes >= 0 && o.preparationMinutes <= 600
        ? Math.round(o.preparationMinutes) : undefined;
      return decision || suites.length || minutes !== undefined
        ? [[id, { ...(decision ? { decision } : {}), suites, ...(minutes !== undefined ? { preparationMinutes: minutes } : {}) }]] : [];
    }));
  } catch {
    return {};
  }
}

// storage refused (site data blocked): readStored and writeStored keep the carnet in memory for this visit, and the
// panels, which read through useStoredString, see the same value
export function readBook(): CarnetBook {
  return parseBook(readStored(CARNET_KEY));
}

function writeBook(book: CarnetBook): void {
  writeStored(CARNET_KEY, JSON.stringify(book));
}

const record = (book: CarnetBook, id: string): CarnetRecord => book[id] ?? { suites: [] };

/** Pure transitions, tested; the components write their result. */
export const carnet = {
  decide(book: CarnetBook, id: string, entry: CarnetEntry | null): CarnetBook {
    const r = { ...record(book, id) };
    const parsed = entry ? parseEntry(entry) : null;
    if (parsed) r.decision = parsed;
    else delete r.decision;
    return { ...book, [id]: r };
  },
  /** A call's outcome, dated. The same outcome touched again the same day replaces the last one (a second touch is not
   *  a second call): the trial export counts calls, not touches. */
  note(book: CarnetBook, id: string, outcome: Outcome, le: string, rappel?: string): CarnetBook {
    const n = parseNote({ outcome, le, rappel });
    if (!n) return book;
    const r = record(book, id);
    const last = lastNote(r);
    const again = last && last.outcome === n.outcome && last.le.slice(0, 10) === n.le.slice(0, 10);
    const suites = again ? r.suites.map((x) => (x === last ? n : x)) : [...r.suites, n];
    return { ...book, [id]: { ...r, suites } };
  },
  /** Takes back the last outcome noted (a wrong touch is corrected, not kept). */
  undo(book: CarnetBook, id: string): CarnetBook {
    const r = book[id];
    const last = lastNote(r);
    if (!r || !last) return book;
    return { ...book, [id]: { ...r, suites: r.suites.filter((x) => x !== last) } };
  },
  /** The date of the last « rappel convenu le… », set after choosing it. */
  retime(book: CarnetBook, id: string, rappel: string): CarnetBook {
    const r = book[id];
    const last = lastNote(r);
    if (!r || !last || last.outcome !== "rappel" || !ISO_DAY.test(rappel)) return book;
    return { ...book, [id]: { ...r, suites: r.suites.map((x) => (x === last ? { ...x, rappel } : x)) } };
  },
  prepare(book: CarnetBook, id: string, minutes: number | null): CarnetBook {
    const r = { ...record(book, id) };
    if (minutes === null || !Number.isFinite(minutes) || minutes < 0 || minutes > 600) delete r.preparationMinutes;
    else r.preparationMinutes = Math.round(minutes);
    return { ...book, [id]: r };
  },
};

export function saveBook(next: CarnetBook): void {
  writeBook(next);
}

/** The last outcome of a company, if any (the latest noted). */
export const lastNote = (r: CarnetRecord | undefined): FieldNote | null =>
  r && r.suites.length ? [...r.suites].sort((a, b) => a.le.localeCompare(b.le)).at(-1)! : null;

/** The trial file: one line per company of the week, ids and choices only, no name of a person or of a company. */
export function trialExport(book: CarnetBook, week: string, consultant: string, ranked: string[]) {
  return {
    fichier: "Proxsis, semaine témoin — export du carnet (ne pas verser dans le dépôt ni sur le site)",
    semaine: week,
    consultant, // the demo role's code (« M1 »), never a name
    definition_conversation_utile: "rappel convenu à une date, besoin confirmé, ou prochaine étape acceptée",
    entreprises: ranked.map((id, i) => {
      const r = book[id];
      const last = lastNote(r);
      return {
        rang: i + 1, entreprise_id: id,
        decision: r?.decision?.decision ?? null, motif: r?.decision?.motif ?? null, revoir: r?.decision?.revoir ?? null,
        confiee: r?.decision?.confie ?? false,
        suites: (r?.suites ?? []).map((n) => ({ suite: n.outcome, rappel: n.rappel ?? null, notee_le: n.le })),
        conversation_utile: last ? USEFUL.includes(last.outcome) : null,
        temps_preparation_min: r?.preparationMinutes ?? null,
      };
    }),
  };
}
