import { dictionaries, LANGS, type Dict } from "@/i18n/dictionaries";

export type Lang = (typeof LANGS)[number];
export { LANGS };

export function isLang(x: string): x is Lang {
  return (LANGS as readonly string[]).includes(x);
}

export function getDict(lang: string): Dict {
  return dictionaries[isLang(lang) ? lang : "fr"];
}

/** Replace {name} placeholders. */
export function fmt(s: string, vars: Record<string, string | number | null | undefined> = {}): string {
  return s.replace(/\{(\w+)\}/g, (_, k: string) => (vars[k] === undefined || vars[k] === null ? "—" : String(vars[k])));
}

const LOCALE: Record<Lang, string> = { fr: "fr-CH", de: "de-CH" };

export function fmtNum(n: number | null | undefined, lang: Lang, digits = 0): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return new Intl.NumberFormat(LOCALE[lang], { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
}

export { fmtDate } from "./dates";

import { swissAmount as swissAmountOf } from "./amount";

export function fmtChfPublished(n: number | null | undefined): string {
  return n === null || n === undefined ? "—" : `CHF ${swissAmountOf(n)}`;
}

/** A moment on this device, written the Swiss way: « 07.10.2026 à 01:42 » / « 07.10.2026 um 01:42 » (no seconds, no AM/PM). */
export function fmtStamp(iso: string, lang: Lang): string {
  const d = new Date(iso);
  const p = (n: number) => String(n).padStart(2, "0");
  return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()} ${lang === "fr" ? "à" : "um"} ${p(d.getHours())}:${p(d.getMinutes())}`;
}
