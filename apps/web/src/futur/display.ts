// Display helpers of the « futurisme suisse » screens. Pure functions: they choose what to show and how, they never
// create a fact. The full legal name, the reasons and the dates come unchanged from the demo export.
import { fmtDate } from "@/lib/dates";
import { frenchSpaces } from "@/lib/typo";
import type { Company, Reason, Source } from "@/lib/types";

const LEGAL_FORM = /\b(SA|AG|S\.A\.|Sàrl|SARL|Sarl|GmbH|S\.à\s?r\.l\.|Ltd)\b/;
// a description before the comma (« Société de Travaux Publics, Joseph Carron SA »), not a list of names
// (« Entreprise Manenti, Farquet et Cie SA »); \b would ignore « é »
const GENERIC = /^(société|entreprise|bureau|atelier|groupe)\s+(de|d'|d’|des|du)\s/i;
const BRANCH = /\s*,?\s*succursale de .+$/i;

/** The title of a company, for display only: its legal name without the description before the comma (« Société de
 *  Travaux Publics, Joseph Carron SA » → « Joseph Carron SA »), without a description after it once the legal form is
 *  there (« Theler AG, Bauunternehmung » → « Theler AG ») and without a branch. The legal form stays: without it, a
 *  company reads like a person (Q17, Hiba, 13.10.2026). */
export function usageName(legal: string): string {
  const parts = legal.replace(BRANCH, "").split(",").map((s) => s.trim()).filter(Boolean);
  let keep = parts;
  if (parts.length > 1 && GENERIC.test(parts[0])) keep = parts.slice(1);
  else if (parts.length > 1 && LEGAL_FORM.test(parts[0])) keep = parts.slice(0, 1);
  let name = keep.join(", ").replace(/\s{2,}/g, " ").trim();
  if (name.length < 2) return legal;
  // ALL CAPITALS (« MELLY CONSTRUCTIONS SA », « ABI-NETTOYAGES Sàrl ») reads like shouting at this size: title case,
  // words kept; the legal form is left as it is written
  const core = name.split(" ").filter((w) => !LEGAL_FORM.test(w)).join(" ");
  if (core === core.toUpperCase() && /[A-ZÀ-Ý]{3}/.test(core)) {
    // initials, acronyms and legal forms stay as they are (« JM ROSSA SA » → « JM Rossa SA »)
    name = name.split(" ").map((w) => (w.length <= 3 || LEGAL_FORM.test(w) ? w : w.toLowerCase()
      .replace(/(^|[-'’])(\p{L})/gu, (_, sep: string, ch: string) => sep + ch.toUpperCase()))).join(" ");
  }
  return name;
}

const DAY = 86_400_000;
/** Whole days from one ISO date to another (noon to noon: no daylight-saving edge). */
export const daysBetween = (from: string, to: string) =>
  Math.round((Date.parse(`${to}T12:00:00Z`) - Date.parse(`${from}T12:00:00Z`)) / DAY);
/** The 52 weeks counted by `n_52s` (python: call_list, awards of the last 364 days). */
export const WINDOW_DAYS = 52 * 7;
/** A signal younger than this carries the copper pulse (DESIGN.md). */
const RECENT_DAYS = 14;

/** One point per public contract of the company's main specialty in the 52 weeks before `asOf` (same count as `n_52s`). */
export function timelinePoints(c: Company, asOf: string): { date: string; x: number; recent: boolean; titre: string }[] {
  return c.chronologie
    .filter((s) => s.specialite === c.specialite_principale)
    .map((s) => ({ s, age: daysBetween(s.date, asOf) }))
    .filter(({ age }) => age >= 0 && age < WINDOW_DAYS)
    .map(({ s, age }) => ({ date: s.date, x: 1 - age / WINDOW_DAYS, recent: age < RECENT_DAYS, titre: s.titre }))
    .sort((a, b) => a.x - b.x);
}

/** A signal of less than RECENT_DAYS (the copper pulse). */
export function isRecent(date: string, asOf: string): boolean {
  const age = daysBetween(date, asOf);
  return age >= 0 && age < RECENT_DAYS;
}

const NOW_ORDER = ["rythme_double", "nouveau_venu", "dernier_marche", "permis_entreprise"];

/** « Pourquoi maintenant » : the most time-bound reason already written by the export, word for word. */
export function whyNow(reasons: Reason[], skip: string[] = []): Reason | null {
  for (const code of NOW_ORDER.filter((c) => !skip.includes(c))) {
    const r = reasons.find((x) => x.code === code);
    if (r) return r;
  }
  return reasons[0] ?? null;
}

/**
 * The sentence shown on a card: the reason's short form when the export gives one (the latest contract: « Dernier
 * marché il y a 54 jours », the title and the authority being on the dossier's paper), else the reason word for word.
 */
export function shortWhy(r: Reason | null, lang: "fr" | "de"): string | null {
  if (!r) return null;
  return r.court?.[lang] ?? r[lang];
}

/**
 * The award that is the reason to call (the « annonce » of the dossier, the sentence to say on the phone, fact 1 of the
 * call guide): the latest contract in the company's main specialty, as the list's reason says (« Dernier marché il y a
 * … »); the latest contract of any specialty only when the export gives none.
 */
export function reasonAward(c: Company): Source | null {
  return c.sources[0] ?? [...c.chronologie].sort((a, b) => b.date.localeCompare(a.date))[0] ?? null;
}

/** « Lundi 5 octobre » / « Montag, 5. Oktober » from an ISO date (Swiss time zone, no clock involved). */
export function longDay(iso: string, lang: "fr" | "de"): string {
  const d = new Date(`${iso}T12:00:00Z`);
  const s = new Intl.DateTimeFormat(lang === "fr" ? "fr-CH" : "de-CH", {
    weekday: "long", day: "numeric", month: "long", timeZone: "Europe/Zurich",
  }).format(d);
  // the day and its month stay on one line (« Montag, 5. / Oktober » would leave the number alone)
  return (s.charAt(0).toUpperCase() + s.slice(1)).replace(/(\d+\.?) (?=\p{L})/u, "$1\u00a0");
}

/**
 * French typography for display: the space before « : ; ? ! » and inside « … » becomes a no-break space, so the
 * sign never starts a line. Only spaces change (the words and the signs stay exactly those of the export); German
 * text is left as it is.
 */
export { frenchSpaces } from "@/lib/typo";

/** dd.mm.yyyy from an ISO date. */

/**
 * The sentence the consultant can say on the phone (Hiba, 07.10.2026; questionnaire of 07.10.2026, B8): a simple
 * sentence with the date of the notice on simap, then the title of the award that is the reason to call, exact and
 * whole, as a quotation (a consultant does not read a raw simap title as his own words, and it cannot be rewritten
 * without changing what simap published). Nothing is added: no estimate, no reading of the title, no figure. The
 * awarding authority stays on the dossier's paper.
 */
export function phoneParts(c: Company, lang: "fr" | "de"): { lead: string; title: string } | null {
  const last = reasonAward(c);
  if (!last) return null;
  return {
    lead: lang === "fr" ? `J'ai vu sur simap que vous avez remporté un marché publié le ${fmtDate(last.date)} :`
      : `Ich habe auf simap gesehen, dass Sie einen Auftrag gewonnen haben, publiziert am ${fmtDate(last.date)}:`,
    title: last.titre.trim(),
  };
}

/** The same, in one line: the sentence, then the title between quotation marks. */
export function phoneLine(c: Company, lang: "fr" | "de"): string | null {
  const p = phoneParts(c, lang);
  if (!p) return null;
  return lang === "fr" ? frenchSpaces(`${p.lead} « ${p.title} »`, "fr") : `${p.lead} «${p.title}»`;
}

/**
 * What the card or the dossier shows to start the call (brief « à distance », § 9): in French, the sentence to say
 * (`phoneLine`); in German, until a German speaker has read the call sentences, no German sentence is shown as ready:
 * the published fact in its original words and its date, with the mention that the German wording is being reviewed.
 */
export function callLine(c: Company, lang: "fr" | "de"): { text: string; review: boolean; lead?: string; title?: string } | null {
  if (lang === "fr") {
    const fr = phoneLine(c, "fr");
    const parts = phoneParts(c, "fr");
    return fr && parts ? { text: fr, review: false, lead: frenchSpaces(parts.lead, "fr"), title: parts.title } : null;
  }
  const last = reasonAward(c);
  return last ? { text: `«${last.titre.trim()}», ${fmtDate(last.date)}`, review: true } : null;
}

/** A fictional temp named in the page's language from its demo number (« cand-161 » → « Intérimaire 161 »). */
export function workerName(candidateId: string, template: string): string {
  return template.replace("{n}", candidateId.replace(/^cand-/, ""));
}

/**
 * A consortium (brief « à distance », § 6): its members when the published name separates them (« Consortium
 * PraderLosinger – Implenia » → two), an empty list when it does not name them (« Consortium Galerie du Fregnoley »),
 * null when the name is not a consortium's. Nothing is guessed beyond the published words.
 */
export function consortiumMembers(name: string): string[] | null {
  const m = name.match(/^\s*(?:consortium|arge|arbeitsgemeinschaft|groupement)\b(?:\s+(?:de la|des entreprises du|des|du|de))?\s*(.*)$/i);
  if (!m) return null;
  const LEGAL = /\b(?:SA|AG|Sàrl|SARL|GmbH|SNC|KG)\b\.?$/i;
  // « – », « - » and « / » separate members; « + » and « & » only when every side is a firm (« Bächler + Güttinger AG »
  // is one firm, « Michel Démolition SA & Bernard Torrent SA » two)
  const parts = m[1].split(/\s+[-–]\s+|\s*[–/]\s*/).flatMap((x) => {
    const sides = x.split(/\s+[+&]\s+/).map((y) => y.trim());
    return sides.length > 1 && sides.every((y) => LEGAL.test(y)) ? sides : [x.trim()];
  }).filter((x) => x.length > 1);
  return parts.length >= 2 ? parts : [];
}
