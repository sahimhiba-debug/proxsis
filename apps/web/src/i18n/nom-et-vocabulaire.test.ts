import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { COPY } from "@/presentation/copy";
import { COPY_C } from "@/presentation/copy_c";
import { forbiddenTerms, NOT_A_RADAR } from "@/presentation/vocabulary";
import { allStrings } from "@/test/strings";
import { dictionaries } from "./dictionaries";

// The product is called Proxsis (Hiba, 07.10.2026): the old name never shows, in French or in German, in the texts of
// the application, of the presentation, or in the data the screens display. And it is a Monday, not a radar.
const DATA = join(__dirname, "../data");
const dataFiles = (dir: string): string[] => readdirSync(dir).flatMap((f) => {
  const p = join(dir, f);
  return statSync(p).isDirectory() ? dataFiles(p) : f.endsWith(".json") ? [p] : [];
});
// not shown on any page: « commande » (the command that redoes a measure, kept for engineers in CLAIMS.md), and the
// internal codes and identifiers of the data
const HIDDEN_KEYS = new Set(["commande", "code", "id"]);
// « Chaque matin, en direct de simap » (suite 10, § 2) and its frozen mornings: what simap published, quoted unchanged
// on screen (« titre », the laureates, the authority, the commune: AGB API ch. 5 al. 2) is not our text — a title such as
// « signalisation routière » must never stop the morning publication, whose job runs these tests
const SIMAP_QUOTES = new Set(["titre", "nom", "adjudicateur", "commune"]);
const simapSection = (p: string) => /[/\\]direct[/\\]matin\.json$|[/\\]presentation[/\\]matins\.json$/.test(p);
const shownData = dataFiles(DATA).flatMap((p) => allStrings(JSON.parse(readFileSync(p, "utf-8")),
  (k) => HIDDEN_KEYS.has(k) || (simapSection(p) && SIMAP_QUOTES.has(k))));
// quoted sources (titles of public contracts, publications) are not interface text: « … » and «…» are left out
const unquoted = (s: string) => s.replace(/«[^»]*»/g, "«»");
const NAME = /flex[\s-]?radar/i; // the former name, in any spelling
const radarWords = (s: string, lang: "fr" | "de") => forbiddenTerms(s, lang).filter((w) =>
  NOT_A_RADAR[lang].some((p) => new RegExp(`^(?:${p})$`, "iu").test(w)));

describe("le nom : Proxsis, jamais l'ancien", () => {
  it("aucun texte de l'application ni de la présentation (FR et DE) ne porte l'ancien nom", () => {
    for (const lang of ["fr", "de"] as const) {
      const texts = [...allStrings(dictionaries[lang]), ...allStrings(COPY[lang]), ...allStrings(COPY_C[lang])];
      expect(texts.filter((s) => NAME.test(s))).toEqual([]);
      expect(dictionaries[lang].app.name).toBe("Proxsis");
    }
  });

  it("aucune donnée affichée par les écrans ne porte l'ancien nom", () => {
    expect(shownData.length).toBeGreaterThan(1000);
    expect(shownData.filter((s) => NAME.test(s)).map((s) => s.slice(0, 80))).toEqual([]);
  });
});

describe("un lundi, pas un radar : ni radar, ni alerte, ni signal, ni niveau dans l'interface", () => {
  it("détecte les mots et leurs variantes, mots composés allemands compris", () => {
    expect(radarWords("Les signaux de la semaine, le radar, une alerte, le niveau", "fr")).toEqual(["radar", "alerte", "signaux", "niveau"]);
    expect(radarWords("le signalement et ce qui est signalé", "fr")).toEqual(["signalement", "signalé"]);
    expect(radarWords("Die Signale, Kontextsignale, der Radar, ein Alarm", "de")).toEqual(["Radar", "Alarm", "Signale", "Kontextsignale"]);
    expect(radarWords("la liste de la semaine, la raison d'appeler, un fait vérifiable, la décision", "fr")).toEqual([]);
  });

  it("aucun texte d'interface (application et présentation, FR et DE) n'emploie ces mots", () => {
    for (const lang of ["fr", "de"] as const) {
      const texts = [...allStrings(dictionaries[lang]), ...allStrings(COPY[lang]), ...allStrings(COPY_C[lang])];
      expect(texts.flatMap((s) => radarWords(s, lang).map((w) => `${w} ← ${s.slice(0, 70)}`))).toEqual([]);
    }
  });

  it("les textes que nous écrivons dans les données affichées non plus (hors citations des sources)", () => {
    const hits = shownData.flatMap((s) => (["fr", "de"] as const).flatMap((lang) => radarWords(unquoted(s), lang)));
    expect(hits).toEqual([]);
  });
});
