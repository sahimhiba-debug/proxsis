import { describe, expect, it } from "vitest";
import { forbiddenTerms } from "../vocabulary";
import { MENTIONS, PHONE_COPY } from "./copy";
import { SCRIPT } from "./script";

function strings(v: unknown, at = ""): [string, string][] {
  if (typeof v === "string") return [[at, v]];
  if (v && typeof v === "object") return Object.entries(v).flatMap(([k, x]) => strings(x, at ? `${at}.${k}` : k));
  return [];
}

const keys = (v: unknown) => strings(v).map(([k]) => k).sort();

describe("les textes de la démo du téléphone", () => {
  it("existent en français et en allemand, avec les mêmes entrées", () => {
    expect(keys(PHONE_COPY.de)).toEqual(keys(PHONE_COPY.fr));
    expect(keys(MENTIONS.de)).toEqual(keys(MENTIONS.fr));
  });

  it("chaque étape du script a son titre, sa phrase et sa mention dans les deux langues", () => {
    for (const lang of ["fr", "de"] as const) {
      for (const s of SCRIPT) {
        const step = PHONE_COPY[lang].steps[s.id];
        expect(step.label.length).toBeGreaterThan(2);
        expect(step.caption.length).toBeGreaterThan(10);
        expect(step.mention.length).toBeGreaterThan(0);
      }
    }
  });

  it("les mentions sont posées au niveau de l'information, avec les libellés convenus", () => {
    for (const lang of ["fr", "de"] as const) {
      const allowed = Object.values(MENTIONS[lang]);
      for (const s of SCRIPT) {
        for (const m of PHONE_COPY[lang].steps[s.id].mention) expect(allowed).toContain(m);
      }
    }
    expect(MENTIONS.fr.real).toBe("Entreprise réelle");
    expect(MENTIONS.de.illustrative).toBe("Beispielsituation");
  });

  it("ne contiennent aucun mot interdit pour le directeur (vocabulary.ts)", () => {
    for (const lang of ["fr", "de"] as const) {
      const found = strings(PHONE_COPY[lang]).flatMap(([k, v]) => forbiddenTerms(v, lang).map((w) => `${k}: ${w}`));
      expect(found).toEqual([]);
    }
  });

  it("n'avancent aucun chiffre : seulement la date du lundi rejoué et l'heure de la barre d'état", () => {
    const allowed = [/5 octobre 2026/g, /5\. Oktober 2026/g, /^\d{1,2}:\d{2}$/g, /\{[a-z]+\}/g];
    for (const lang of ["fr", "de"] as const) {
      for (const [k, v] of strings(PHONE_COPY[lang])) {
        const rest = allowed.reduce((s, rx) => s.replace(rx, ""), v);
        expect(rest, `${lang} ${k}`).not.toMatch(/\d/);
      }
    }
  });

  it("l'allemand suit l'usage suisse (ss, jamais ß)", () => {
    expect(strings(PHONE_COPY.de).filter(([, v]) => v.includes("ß"))).toEqual([]);
  });
});
