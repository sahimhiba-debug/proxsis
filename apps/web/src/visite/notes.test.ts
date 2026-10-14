import { describe, expect, it } from "vitest";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { allStrings } from "@/test/strings";
import { VISIT_NOTES } from "./notes";
import { VISIT_STEPS } from "./state";

describe("mode présentateur : une note par étape, FR et DE", () => {
  it("chaque étape a ses quatre lignes dans les deux langues, sans terme à éviter", () => {
    for (const lang of ["fr", "de"] as const) {
      for (const step of VISIT_STEPS) {
        const n = VISIT_NOTES[lang][step.id];
        for (const k of ["say", "gesture", "proof", "fallback"] as const) expect(n[k], `${lang} ${step.id} ${k}`).toBeTruthy();
      }
      expect(allStrings(VISIT_NOTES[lang]).flatMap((s) => forbiddenTerms(s, lang))).toEqual([]);
    }
  });

  it("aucune phrase sur le nom dans les notes (§ 2)", () => {
    for (const lang of ["fr", "de"] as const) {
      expect(allStrings(VISIT_NOTES[lang]).filter((s) => /\b(?:le nom|nom de travail|der Name|Arbeitsname)\b/i.test(s))).toEqual([]);
    }
  });

  // suite 8, § 3: three reasons, never « un iris orange »; the mandatory answers of the brief (06.10.2026, § 7), word for
  // word, in natural language
  it("pourquoi « Iris » : trois raisons ; les réponses obligatoires du § 7, mot pour mot", () => {
    const fr = allStrings(VISIT_NOTES.fr).map((s) => s.replace(/\u00a0/g, " ")).join(" ");
    expect(fr).toContain("dans les légendes grecques, Iris est la messagère des dieux (CLAIMS EXT-IRIS-MESSAGERE)");
    expect(fr).toContain("Iris met les points sur les i");
    expect(fr).toContain("« Iris » se dit pareil en français, en allemand et en anglais");
    expect(fr).toContain("« Moi, je prépare. Vous, vous décidez. »");
    expect(fr).toContain("Sur ce premier examen des marchés publics, notre sélection n'a pas fait mieux qu'une règle simple. Nous gardons donc cette règle comme référence. Ce que nous vous proposons de tester, c'est l'utilité d'une information vérifiable dans le travail de vos consultants : aide-t-elle à préparer les bons appels, et à quel coût ? Le pilote doit nous permettre de le mesurer.");
    expect(fr).toContain("« Parce que nous pouvons vous montrer le travail que le consultant pourrait faire avec ces informations, puis le comparer à sa pratique actuelle. Nous n'avons pas encore démontré le gain chez vous. Si le pilote n'en montre pas suffisamment, nous aurons une raison claire de nous arrêter. »");
    expect(fr).toContain("731 entreprises");
    for (const lang of ["fr", "de"] as const) expect(allStrings(VISIT_NOTES[lang]).join(" ")).not.toMatch(/iris orange|orangen Iris|\b729\b/i);
    expect(allStrings(VISIT_NOTES.de).join(" ")).toContain("die Botin der Götter");
  });
});
