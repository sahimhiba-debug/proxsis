import { describe, expect, it } from "vitest";
import { allStrings } from "@/test/strings";
import { COPY } from "./copy";
import { forbiddenTerms, FORBIDDEN } from "./vocabulary";

describe("vocabulaire montré au directeur", () => {
  it("détecte les mots entiers et leurs variantes, sans faux positif", () => {
    expect(forbiddenTerms("Notre modèle prédit", "fr")).toEqual(["modèle"]);
    expect(forbiddenTerms("une API ouverte et des APIs", "fr")).toEqual(["API", "APIs"]);
    expect(forbiddenTerms("le backtest et les backtests", "fr")).toEqual(["backtest", "backtests"]);
    expect(forbiddenTerms("Modèle de contrat", "fr")).toEqual(["Modèle"]);
    expect(forbiddenTerms("rapidement, capitale, apiculteur, précisément", "fr")).toEqual([]);
    expect(forbiddenTerms("Das Modell und die KI", "de")).toEqual(["Modell", "KI"]);
    expect(forbiddenTerms("Kirche, Kiosk, modellieren", "de")).toEqual([]);
  });

  it("aucun texte de la présentation (écran et notes, FR et DE) n'emploie un terme à éviter", () => {
    for (const lang of ["fr", "de"] as const) {
      const hits = allStrings(COPY[lang]).flatMap((s) => forbiddenTerms(s, lang).map((t) => `${t} ← « ${s.slice(0, 60)} »`));
      expect(hits).toEqual([]);
    }
    expect(FORBIDDEN.fr.length).toBeGreaterThan(10);
  });
});
