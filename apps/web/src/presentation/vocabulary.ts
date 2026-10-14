// « Un lundi, pas un radar » (Hiba, 07.10.2026): Proxsis is the consultant's Monday, not an alert radar. The visible
// interface says « liste de la semaine », « raison d'appeler », « fait vérifiable », « décision »; never the words below
// (German compounds included: « Kontextsignale »). Quoted sources are not interface text and are not checked.
export const NOT_A_RADAR: Record<"fr" | "de", string[]> = {
  fr: ["radars?", "alertes?", "alerter", "signal", "signaux", "signal(?:er|é|ée|és|ées|ement|ements)", "niveaux?"],
  de: ["\\p{L}*[Rr]adar\\p{L}*", "\\p{L}*[Aa]larm\\p{L}*", "\\p{L}*[Ss]ignal\\p{L}*", "Niveaus?"],
};

// Words the director should not hear or read (brief § 14): internal jargon, FR and DE. Whole words and their useful
// variants only (« API » but not « rapidement », « KI » but not « Kirche »). Applies to screens, buttons, notes,
// objections and documents for the director — not to code, technical docs or quoted sources.
export const FORBIDDEN: Record<"fr" | "de", string[]> = {
  fr: ["backtests?", "mod[èe]les?", "APIs?", "scraping", "extractions?", "parsing", "IA", "pipelines?", "backend",
    "bases? de données", "kappa", "précision", "datasets?", "algorithmes?", "machine learning", "apprentissage automatique",
    ...NOT_A_RADAR.fr],
  de: ["Backtests?", "Modell(?:e|en|s)?", "APIs?", "Scraping", "Extraktion(?:en)?", "Parsing", "KI", "Pipelines?",
    "Backend", "Datenbank(?:en)?", "Kappa", "Präzision", "Datens[äa]tz(?:e|en)?", "Algorithm(?:us|en)", "maschinelles Lernen",
    ...NOT_A_RADAR.de],
};

export function forbiddenTerms(text: string, lang: "fr" | "de"): string[] {
  const out: string[] = [];
  for (const pattern of FORBIDDEN[lang]) {
    const sensitive = /^[A-Z]{2,}/.test(pattern) ? "g" : "gi"; // « IA », « KI », « API » only as acronyms
    const rx = new RegExp(`(?<![\\p{L}\\p{N}])(?:${pattern})(?![\\p{L}\\p{N}])`, `${sensitive}u`);
    for (const m of text.matchAll(rx)) out.push(m[0]);
  }
  return out;
}
