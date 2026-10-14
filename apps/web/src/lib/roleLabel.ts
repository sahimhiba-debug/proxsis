import type { Dict } from "@/i18n/dictionaries";

/** Readable demo role of a fictional consultant (« Consultant·e bâtiment », « Berater·in Bau »), never its code. */
export function consultantLabel(t: Dict, lang: string, specialite: string): string {
  const spec = t.specialty[specialite as keyof typeof t.specialty] ?? specialite;
  // French writes the specialty in lower case after the role; German keeps its capital (a noun)
  return t.fx.roleConsultant.replace("{spec}", lang === "fr" ? spec.charAt(0).toLowerCase() + spec.slice(1) : spec);
}
