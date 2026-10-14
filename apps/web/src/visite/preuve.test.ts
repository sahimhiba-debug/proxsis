import { describe, expect, it } from "vitest";
import lundis from "@/data/presentation/lundis.json";
import type { MondaysData } from "@/presentation/mondayData";
import { reponse } from "./guide";
import { PAGES_COPY } from "./pages";

const data = lundis as unknown as MondaysData;

// Retour de Hiba du 13.10.2026 : quelqu'un qui voit la preuve pour la première fois doit comprendre d'où viennent les
// chiffres. Partout où elle est dite (page pour votre direction, page A4, réponse du guide), on dit d'abord que la
// liste a été mise à l'épreuve du passé : des lundis rejoués avec seulement ce qui était publié ce jour-là, puis ce
// qui a suivi dans les 8 semaines. Un marché remporté est une raison d'appeler, jamais la preuve d'un besoin de personnel.
describe("la preuve : d'où viennent les chiffres", () => {
  const textes = (lang: "fr" | "de") => {
    const t = PAGES_COPY[lang];
    return { direction: t.direction.preuve.p, bref: t.direction.preuve.bref, a4: t.unePage.measure.p[0], guide: reponse("marche", lang, data) };
  };

  it("fr : chaque endroit dit que la liste a été mise à l'épreuve du passé, avec ce qui était publié ce jour-là", () => {
    const t = textes("fr");
    for (const [ou, s] of Object.entries(t)) {
      expect(s, ou).toMatch(ou === "bref" ? /^Testée sur \{n\} lundis passés/ : /mise à l'épreuve du passé|mis la liste à l'épreuve du passé/);
      expect(s, ou).toMatch(/8 semaines/);
      expect(s, ou).toMatch(/hasard/);
    }
    for (const ou of ["direction", "a4", "guide"] as const) expect(t[ou], ou).toContain("ce qui était publié ce jour-là");
  });

  it("de : la même chose, à relire (an der Vergangenheit geprüft, nur mit dem, was an jenem Tag publiziert war)", () => {
    const t = textes("de");
    for (const [ou, s] of Object.entries(t)) {
      expect(s, ou).toMatch(ou === "bref" ? /^Getestet an \{n\} vergangenen Montagen/ : /an der Vergangenheit geprüft/);
      expect(s, ou).toMatch(/8 Wochen/);
    }
    for (const ou of ["direction", "a4", "guide"] as const) expect(t[ou], ou).toContain("was an jenem Tag publiziert war");
  });

  it("jamais plus qu'une raison d'appeler : ni besoin de personnel, ni commande promise", () => {
    for (const lang of ["fr", "de"] as const) {
      for (const [ou, s] of Object.entries(textes(lang))) {
        expect(s, `${lang} ${ou}`).not.toMatch(/besoin|Bedarf|garanti/i);
        expect(s, `${lang} ${ou}`).not.toMatch(/(?<!pas une |keine )(commande|Bestellung)/);
      }
    }
  });
});
