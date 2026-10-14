// Visit, time 5: the indicators of « Nous continuerons si… », the prepared example and the sentence (pure, shared by
// the scene, the conclusion, the printable summary and the e-mail).
import { groupDigits } from "@/lib/digits";
import { VISIT_COPY } from "./copy";
import type { PilotChoice } from "./state";

export const INDICATORS = ["journees", "utiles", "commandes"] as const;
export type Indicator = (typeof INDICATORS)[number];
export const MAX: Record<Indicator, number> = { journees: 100_000, utiles: 10, commandes: 10_000 };
// prepared thresholds of the other indicators (examples, marked as such; « journees » takes the days of time 4)
export const EXAMPLE_THRESHOLD: Record<Exclude<Indicator, "journees">, number> = { utiles: 3, commandes: 2 };

/** The prepared example: the additional billed days of his threshold (time 4). */
export const examplePilot = (days: number | null): PilotChoice => ({ indicator: "journees", threshold: days ?? 0 });

export function pilotSentence(p: PilotChoice, lang: "fr" | "de"): string {
  const t = VISIT_COPY[lang].pilote;
  const ind = (INDICATORS as readonly string[]).includes(p.indicator) ? (p.indicator as Indicator) : "journees";
  return t.sentence.replace("{criterion}", t.indicators[ind].criterion.replace("{n}", groupDigits(p.threshold, 0, lang === "de" ? "de-CH" : "fr-CH")));
}
