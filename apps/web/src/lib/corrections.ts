// The corrections that simap published after our frozen data, for a notice those data show (brief « à distance », § 7;
// AGB API simap ch. 5 al. 2: corrections are passed on). Written every working day with « Chaque matin, en direct de simap »
// (python/src/proxsis/live_week.py, corrections.json), only when every check passes; the frozen data and CLAIMS never
// change: the notice stays as it was, and a line next to it says that it was corrected and that simap is authoritative.
import corrections from "@/data/direct/corrections.json";
import { fmtDate } from "./dates";
import { frenchSpaces } from "./typo";
import type { CorrectionKind, CorrectionsFile } from "./types";

const data = corrections as CorrectionsFile;
const PROJECT = /\/project-detail\/([0-9a-f-]{36})$/;

export const CORRECTION_COPY = {
  fr: {
    kind: { correction: "rectifiée", revocation: "révoquée", abandonment: "interrompue" } satisfies Record<CorrectionKind, string>,
    note: "Cette publication a été {kind} sur simap le {date} ; la version officielle fait foi.",
    open: "Voir sur simap.ch",
  },
  de: {
    kind: { correction: "berichtigt", revocation: "widerrufen", abandonment: "abgebrochen" } satisfies Record<CorrectionKind, string>,
    note: "Diese Publikation wurde am {date} auf simap {kind}; massgebend ist die offizielle Fassung.",
    open: "Auf simap.ch ansehen",
  },
} as const;

/** The corrections published for the project of a simap page (« …/project-detail/<id> », any language), oldest first. */
export function correctionsFor(url: string | null | undefined, file: CorrectionsFile = data) {
  const id = url ? PROJECT.exec(url)?.[1] : undefined;
  return id ? file.avis.filter((n) => n.projet === id) : [];
}

/** The sentence shown next to a corrected notice. */
export function correctionSentence(kind: CorrectionKind, date: string, lang: "fr" | "de"): string {
  const t = CORRECTION_COPY[lang];
  return frenchSpaces(t.note.replace("{kind}", t.kind[kind]).replace("{date}", fmtDate(date)), lang);
}
