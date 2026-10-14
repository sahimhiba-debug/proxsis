import { describe, expect, it } from "vitest";
import claims from "@/data/demo/claims.json";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { APERTUS, PORTE } from "./copy";
import { PAGES_COPY } from "./pages";

// « Pour votre direction » (suite 2, § 8): the group's words are those of their CLAIMS lines, quoted as read, with the
// date of the article and of the reading; the group is never named, nor any person; no word to avoid.
describe("la page pour votre direction", () => {
  const registry = claims as Record<string, Record<string, string>>;
  const clean = (x: string) => x.replace(/[«»"  ]/g, " ").replace(/\s+/g, " ").trim();
  for (const lang of ["fr", "de"] as const) {
    const t = PAGES_COPY[lang].direction;
    it(`${lang} : chaque but est cité tel que sa ligne de CLAIMS le lit, avec ses dates`, () => {
      expect(t.buts.items.map((x) => x.claims)).toEqual(["EXT-GROUPE-PARTS", "EXT-GROUPE-DELAI", "EXT-GROUPE-TECH", "EXT-FLEXSIS-MOTS"]);
      for (const x of t.buts.items) {
        const line = registry[x.claims];
        expect(line, x.claims).toBeDefined();
        expect(line.donnees).toBe("SOURCE PUBLIQUE");
        const all = clean(Object.values(line).join(" "));
        // the quoted words are in the line (« améliorer » introduces the quote, it is the line's own word)
        expect(all.toLowerCase()).toContain(clean(x.quote).replace(/^améliorer /, "").toLowerCase());
        for (const d of x.source.match(/\d{2}\.\d{2}\.\d{4}/g) ?? []) expect(all).toContain(d);
      }
    });
    it(`${lang} : ni le nom du groupe, ni celui d'une personne, ni un mot à éviter`, () => {
      const text = JSON.stringify(t);
      expect(text).not.toMatch(/interiman|tobien|https?:\/\//i);
      const strings = [t.title, t.link, ...t.probleme.p, t.preuve.p, t.preuve.bref, t.preuve.limit, t.essai.p, t.avenir.h,
        ...t.avenir.steps.flatMap((x) => [x.court, x.detail]), t.buts.h, t.buts.note, ...t.buts.items.map((x) => x.how), t.iris.h,
        ...t.iris.p, t.iris.apertus, t.iris.guardsTitle, ...t.iris.guards, t.iris.future];
      expect(strings.flatMap((s) => forbiddenTerms(s, lang))).toEqual([]);
      expect(t.iris.future).toMatch(lang === "fr" ? /Rien de cela n'existe aujourd'hui/ : /Nichts davon existiert heute/);
      // suite 8, § 6: the passage on Apertus, word for word; no other provider named
      expect(t.iris.apertus.replace(/\u00a0/g, " ")).toBe(APERTUS[lang]);
      expect(JSON.stringify(t.iris)).not.toMatch(/OpenAI|Anthropic/);
    });
    // suite 9, § 8: the door, word for word (SUITE-9-VISITE.md, § 1): its title, its three sentences, its five guardrails;
    // « L'avenir en trois étapes » are its three steps, each with what it means (shown, on a phone, under « En savoir plus »)
    it(`${lang} : la porte, ses garde-fous et l'avenir en trois étapes, mot pour mot`, () => {
      const plain = (x: string) => x.replace(/\u00a0/g, " ");
      const p = PORTE[lang];
      expect(plain(t.iris.h)).toBe(p.titre);
      expect(t.iris.p.map(plain)).toEqual(p.texte);
      expect(t.iris.guards.map(plain)).toEqual(p.gardeFous);
      expect(plain(t.avenir.h)).toBe(lang === "fr" ? "L'avenir en trois étapes" : "Die Zukunft in drei Schritten");
      expect(t.avenir.steps.map((x) => plain(x.court))).toEqual(p.etapes);
      for (const x of t.avenir.steps) expect(x.detail.length).toBeGreaterThan(20);
      expect(JSON.stringify(t)).not.toMatch(lang === "fr" ? /\bIA\b/ : /\bKI\b/);
    });
    // suite 9, § 10: on a phone, the proof in one short sentence; the same figures, filled from the same data (PRES-DATE-1)
    it(`${lang} : la preuve en bref garde les mêmes chiffres que la preuve entière`, () => {
      for (const k of ["{n}", "{rule}", "{random}"]) expect(t.preuve.bref).toContain(k);
      expect(t.preuve.bref.length).toBeLessThan(t.preuve.p.length * 0.75);
    });
  }
});
