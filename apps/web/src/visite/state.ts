// The visit in five times (brief « à distance », § 4): one state for the whole visit (the director's screen, the
// presenter's notes window), pure transitions, no timer, kept on the device only. Every choice is optional: what the
// director did not set stays the prepared example, and says so. The language is not in the state: switching FR ↔ DE
// keeps the step and every choice.

import { parseEntry, type CarnetEntry } from "@/lib/carnet";
import type { SeuilInput } from "@/lib/seuil";

export type StepId = "carte" | "dossier" | "carnet" | "suivant" | "date" | "seuil" | "pilote" | "conclusion";
export type Temps = 1 | 2 | 3 | 4 | 5 | 6; // 6: the conclusion

export interface VisitStep {
  id: StepId;
  temps: Temps;
  gestures: number; // what « Continuer » reveals inside the step before moving on
}

export const VISIT_STEPS: VisitStep[] = [
  { id: "carte", temps: 1, gestures: 0 },
  { id: "dossier", temps: 1, gestures: 1 },
  { id: "carnet", temps: 1, gestures: 1 },
  { id: "suivant", temps: 2, gestures: 1 },
  { id: "date", temps: 3, gestures: 2 },
  { id: "seuil", temps: 4, gestures: 0 },
  { id: "pilote", temps: 5, gestures: 0 },
  { id: "conclusion", temps: 6, gestures: 0 },
];
export const TEMPS: Temps[] = [1, 2, 3, 4, 5, 6];
export const firstOf = (t: Temps) => VISIT_STEPS.findIndex((s) => s.temps === t);

export interface PilotChoice {
  indicator: string;
  threshold: number;
}

export interface VisitState {
  version: 1;
  step: number;
  reveal: number;
  commune: string | null; // official number of the touched commune; null: the prepared example
  agence: string | null; // the chosen Flexsis agency (suite 2, § 3); null: the prepared example, Martigny
  company: string | null; // the opened company; null: the prepared example
  carnet: Record<string, CarnetEntry>; // his decisions; a company without one keeps the prepared example
  monday: string | null; // « Choisissez une date »; null: the prepared example
  seuil: SeuilInput | null; // his assumptions for the threshold (4.4); null: the example values
  half: boolean; // « Deux fois moins »
  pilot: PilotChoice | null; // « Nous continuerons si… »; null: the prepared example
  source: string | null; // a published source open above the scene
}

export type VisitAction =
  | { type: "next" }
  | { type: "prev" }
  | { type: "goto"; step: number }
  | { type: "temps"; temps: Temps }
  | { type: "reveal"; n: number }
  | { type: "commune"; bfs: string | null }
  | { type: "agence"; id: string | null }
  | { type: "company"; id: string | null }
  | { type: "decide"; company: string; entry: CarnetEntry | null }
  | { type: "monday"; value: string | null }
  | { type: "seuil"; value: SeuilInput | null }
  | { type: "half"; value: boolean }
  | { type: "pilot"; value: PilotChoice | null }
  | { type: "openSource"; url: string }
  | { type: "closeSource" }
  | { type: "reset" };

/** Where the visit is kept on this device (memory only when the browser refuses storage, e.g. private browsing). */
export const VISIT_KEY = "proxsis.visite.v1";
export const ALL = 99;
const ISO_DAY = /^\d{4}-\d{2}-\d{2}$/;

export function initialVisit(): VisitState {
  return { version: 1, step: 0, reveal: 0, commune: null, agence: null, company: null, carnet: {}, monday: null, seuil: null,
    half: false, pilot: null, source: null };
}

const clamp = (n: number) => Math.max(0, Math.min(VISIT_STEPS.length - 1, n));

export function reduce(s: VisitState, a: VisitAction): VisitState {
  const gestures = VISIT_STEPS[s.step].gestures;
  switch (a.type) {
    case "next":
      if (Math.min(s.reveal, gestures) < gestures) return { ...s, reveal: Math.min(s.reveal, gestures) + 1, source: null };
      return s.step === VISIT_STEPS.length - 1 ? s : { ...s, step: s.step + 1, reveal: 0, source: null };
    case "prev":
      if (Math.min(s.reveal, gestures) > 0) return { ...s, reveal: Math.min(s.reveal, gestures) - 1, source: null };
      return s.step === 0 ? { ...s, reveal: 0 } : { ...s, step: s.step - 1, reveal: ALL, source: null };
    case "goto":
      return { ...s, step: clamp(a.step), reveal: 0, source: null };
    case "temps":
      return { ...s, step: clamp(firstOf(a.temps)), reveal: 0, source: null };
    case "reveal":
      return { ...s, reveal: Math.max(0, Math.min(ALL, a.n)) };
    case "commune":
      return { ...s, commune: a.bfs };
    case "agence":
      return { ...s, agence: a.id };
    case "company":
      return { ...s, company: a.id };
    case "decide": {
      const carnet = { ...s.carnet };
      const entry = a.entry ? parseEntry(a.entry) : null;
      if (entry) carnet[a.company] = entry;
      else delete carnet[a.company];
      return { ...s, carnet };
    }
    case "monday":
      // a new date hides again what came after it: the list first, then « Continuer » reveals
      return { ...s, monday: a.value && ISO_DAY.test(a.value) ? a.value : null, reveal: 0 };
    case "seuil":
      return { ...s, seuil: a.value ? parseSeuil(a.value) : null };
    case "half":
      return { ...s, half: a.value };
    case "pilot":
      return { ...s, pilot: a.value ? parsePilot(a.value) : null };
    case "openSource":
      return { ...s, source: a.url };
    case "closeSource":
      return { ...s, source: null };
    case "reset":
      return initialVisit();
  }
}

const SEUIL_KEYS = ["weeks", "marginPerDay", "serviceCost", "teamHours", "hourCost", "days", "savedHours"] as const;
const number = (x: unknown) => typeof x === "number" && Number.isFinite(x) && x >= 0 && x <= 10_000_000;

function parseSeuil(x: unknown): SeuilInput | null {
  if (!x || typeof x !== "object") return null;
  const o = x as Record<string, unknown>;
  return SEUIL_KEYS.every((k) => number(o[k])) && (o.weeks as number) >= 1 && (o.weeks as number) <= 52
    ? (Object.fromEntries(SEUIL_KEYS.map((k) => [k, o[k]])) as unknown as SeuilInput) : null;
}

function parsePilot(x: unknown): PilotChoice | null {
  if (!x || typeof x !== "object") return null;
  const o = x as Record<string, unknown>;
  return typeof o.indicator === "string" && o.indicator.length <= 40 && number(o.threshold)
    ? { indicator: o.indicator, threshold: o.threshold as number } : null;
}

/** Restores a saved visit field by field: anything unreadable starts afresh, a damaged field falls back to its initial
 *  value instead of breaking a screen. */
export function parseVisit(raw: string | null): VisitState {
  try {
    const v = JSON.parse(raw ?? "null") as Record<string, unknown> | null;
    if (v && typeof v === "object" && v.version === 1 && typeof v.step === "number") {
      const carnet = Object.entries((v.carnet && typeof v.carnet === "object" ? v.carnet : {}) as Record<string, unknown>)
        .flatMap(([id, e]) => {
          const entry = parseEntry(e);
          return entry ? [[id, entry] as const] : [];
        });
      const text = (x: unknown) => (typeof x === "string" ? x : null);
      return {
        ...initialVisit(),
        step: clamp(v.step),
        reveal: typeof v.reveal === "number" ? Math.max(0, Math.min(ALL, v.reveal)) : 0,
        commune: typeof v.commune === "string" && /^\d+$/.test(v.commune) ? v.commune : null,
        agence: typeof v.agence === "string" && /^[a-z]+$/.test(v.agence) ? v.agence : null,
        company: text(v.company),
        carnet: Object.fromEntries(carnet),
        monday: typeof v.monday === "string" && ISO_DAY.test(v.monday) ? v.monday : null,
        seuil: parseSeuil(v.seuil),
        half: v.half === true,
        pilot: parsePilot(v.pilot),
        source: text(v.source),
      };
    }
  } catch {
    // unreadable storage: a fresh visit
  }
  return initialVisit();
}
