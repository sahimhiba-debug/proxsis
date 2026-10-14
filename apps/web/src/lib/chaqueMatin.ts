// Suite 10 (Hiba, 13.10.2026): « Chaque matin » and the map of the sources. One place for her sentences, word for word
// in French, used by the application, the visit and the A4 page; the German is a proposal **to review** (Hiba does not
// read German; the German pages say so in their footer). The numbers of the sources come from their file
// (src/data/sources/carte.json, written by `proxsis carte-sources` from data/catalogue.csv and refused there when it
// differs from CLAIMS SOURCES-1), never from the text. « Depuis hier » shows facts, never a score: no new figure.
import carte from "@/data/sources/carte.json";
import type { LiveContract, LiveCorrection, LiveFile, LiveMode } from "./types";

type L = "fr" | "de";

/** Where the Monday is spoken of (the visit, the A4 page, the application); not in the film. */
export const MORNING: Record<L, string> = {
  fr: "Chaque matin, Iris lit les marchés publics attribués. Le lundi, elle pose les dix points.",
  de: "Jeden Morgen liest Iris die vergebenen öffentlichen Aufträge. Am Montag setzt sie die zehn Punkte.", // à relire
};
/** The section of the application (« Cette semaine, en direct de simap » until 13.10.2026). */
export const SECTION_TITLE: Record<L, string> = {
  fr: "Chaque matin, en direct de simap",
  de: "Jeden Morgen, direkt von simap", // à relire
};
/** A day without a new contract. */
export const NOTHING_NEW: Record<L, string> = {
  fr: "Rien de nouveau depuis hier. Iris veille.",
  de: "Seit gestern nichts Neues. Iris wacht.", // à relire
};
/** A laureate that is already in the list of the week (the Monday list does not change during the week). */
export const IN_YOUR_LIST: Record<L, string> = {
  fr: "dans votre liste",
  de: "in Ihrer Liste", // à relire
};
/** The rule, under the numbers of the sources. */
export const RULE: Record<L, string> = {
  fr: "Proxsis ne lit que ce qu'il a le droit de lire, et ne promet que ce qu'il a mesuré.",
  de: "Proxsis liest nur, was es lesen darf, und verspricht nur, was es gemessen hat.", // à relire
};
const SOURCES_LINE: Record<L, string> = {
  fr: "{n} sources étudiées : {service} en service, {requests} couvertes par une demande d'accès envoyée, {excluded} écartées. Les autres : conditions à vérifier, ou rien d'utile pour la liste.",
  de: "{n} Quellen geprüft: {service} in Betrieb, {requests} mit versandtem Zugangsgesuch, {excluded} ausgeschlossen. Die übrigen: Bedingungen offen oder ohne Nutzen für die Liste.", // à relire
};

/** src/data/sources/carte.json (python/src/proxsis/source_map.py). */
export interface SourceMap {
  schema: 1; claims: string; catalogue: string; etudiees: number;
  en_service: { nombre: number; lignes: string[] };
  demandes: { nombre: number; liste: { cle: string; lignes: string[]; fichier: string; statut: string; mois: string }[] };
  ecartees: { nombre: number; familles: Record<string, string[]> };
  autres: { nombre: number; conditions_a_verifier: number; sans_usage_pour_la_liste: number };
}
export const SOURCE_MAP = carte as SourceMap;

/** « 68 sources étudiées : 2 en service, … » with the numbers of the catalogue. */
export function sourcesLine(lang: L, c: SourceMap = SOURCE_MAP): string {
  return SOURCES_LINE[lang].replace("{n}", String(c.etudiees)).replace("{service}", String(c.en_service.nombre))
    .replace("{requests}", String(c.demandes.nombre)).replace("{excluded}", String(c.ecartees.nombre));
}

export type MorningItem = Omit<LiveContract, "laureats"> & { laureats: { nom: string; id: string; inList: boolean }[] };
export type MorningView =
  | { state: "attente" }
  | { state: "nouveau" | "rien"; mode: LiveMode; periode: { du: string; au: string }; lu: string; total: number;
      items: MorningItem[]; corrections: LiveCorrection[] };

/** What the section shows from its file: nothing yet (waiting for the morning job), something new, or nothing new
 *  (a day without a new contract). ``list``: the identifiers of the companies of the list of the week. */
export function morningView(file: LiveFile, list: ReadonlySet<string>): MorningView {
  if (file.etat !== "a_jour" || !file.mode || !file.periode || !file.mis_a_jour_le) return { state: "attente" };
  const items = file.marches.map((c) => ({ ...c, laureats: c.laureats.map((w) => ({ ...w, inList: list.has(w.id) })) }));
  return { state: items.length ? "nouveau" : "rien", mode: file.mode, periode: file.periode, lu: file.mis_a_jour_le,
    total: file.total, items, corrections: file.rectifications ?? [] };
}
