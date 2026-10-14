import { describe, expect, it } from "vitest";
import claims from "@/data/demo/claims.json";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { YEARS_SOURCES } from "./Avenir";
import { APERTUS, PORTE, VISIT_COPY } from "./copy";

// The future in three steps (suite 2, § 7) and « Iris demain » (suite 3, § 3): the sources of the years ahead are those
// of CLAIMS.md; Iris is a possible future, never a function that exists; Proxsis never says it has those contracts.
describe("l'avenir en trois étapes", () => {
  const registry = claims as Record<string, { source?: string; limite?: string; donnees?: string }>;
  it("cite les chantiers à venir avec la source de leur ligne CLAIMS, lue chez un tiers", () => {
    for (const s of YEARS_SOURCES) {
      const line = registry[s.claims];
      expect(line, s.claims).toBeDefined();
      expect(line.donnees).toBe("SOURCE PUBLIQUE");
      expect(JSON.stringify(line)).toContain(s.url);
      expect(JSON.stringify(line)).toContain(s.label.split(", ")[1]);
    }
  });
  for (const lang of ["fr", "de"] as const) {
    const t = VISIT_COPY[lang].avenir;
    it(`${lang} : trois étapes, chacune dit ce qu'il gagne, ce qu'il donne et quand il peut s'arrêter`, () => {
      expect(t.steps).toHaveLength(2);
      for (const st of t.steps) for (const k of ["gain", "give", "stop"] as const) expect(st[k].length).toBeGreaterThan(5);
      expect(t.third.items.length).toBeGreaterThanOrEqual(3);
    });
    it(`${lang} : Iris demain reste un avenir possible, avec ses garde-fous, sans le mot à éviter`, () => {
      expect(t.iris.tomorrow).toMatch(lang === "fr" ? /pourrait/ : /könnte/);
      expect(t.iris.guards).toHaveLength(5);
      const all = [t.title, t.lead, t.iris.title, t.iris.today, t.iris.tomorrow, t.iris.apertus, t.iris.silence, ...t.iris.guards,
        t.iris.future, t.third.lead, t.years.text, t.years.phrase];
      expect(all.flatMap((x) => forbiddenTerms(x, lang))).toEqual([]);
      // never said to be in Proxsis's data
      expect(t.years.text + t.years.phrase).not.toMatch(lang === "fr" ? /nos données|Proxsis/ : /unseren Daten|Proxsis/);
    });
    it(`${lang} : l'étape 3 dit le passage sur Apertus (suite 8, § 6), sans nommer d'autre fournisseur`, () => {
      const plain = (x: string) => x.replace(/\u00a0/g, " ");
      expect(t.third.items.map(plain)).toContain(APERTUS[lang]);
      expect(JSON.stringify(t)).not.toMatch(/OpenAI|Anthropic/);
    });
  }
});

// Suite 9, § 8 (working notes): « la porte », Hiba's texts word for word, in the step « Demain,
// peut-être » of the visit: the agent that reads the publications every morning, Apertus adapted to the data on their
// servers or at a Swiss host, the five guardrails with it, the third step, and the sentence of the silence, in the future
// (Q04). All in the future or the conditional; « intelligence artificielle » in full, never the acronym.
describe("la porte (suite 9, § 8)", () => {
  const plain = (x: string) => x.replace(/\u00a0/g, " ");
  it("les textes de la consigne, mot pour mot (FR ; DE à relire)", () => {
    expect(PORTE.fr).toEqual({
      titre: "Demain, si Flexsis le souhaite",
      texte: [
        "Aujourd'hui, la liste vient de règles claires, mesurées sur des lundis passés.",
        "Demain, Iris pourrait s'installer chez Flexsis : une assistante pour chaque consultant, et un agent qui lit les publications chaque matin et propose les appels.",
        "Avec Apertus, l'intelligence artificielle suisse et ouverte, adaptée à vos données : missions, réussites, compétences des consultants. Sur vos serveurs ou chez un hébergeur suisse. Vos données ne sortiraient jamais.",
      ],
      etapes: [
        "Une semaine d'essai avec deux consultants volontaires.",
        "Six semaines dans deux agences.",
        "Si les résultats sont là : Iris installée chez Flexsis, avec Apertus adapté à ses données, chez elle.",
      ],
      gardeFous: [
        "Iris proposera, le consultant décidera, toujours.",
        "Chaque consultant verra ce qu'Iris garde, et pourra le corriger ou l'effacer.",
        "Iris ne classera ni ne surveillera jamais les consultants.",
        "Les données de Flexsis resteront sous son contrôle, en Suisse, avec son accord écrit.",
        "Chaque nouvelle capacité sera mesurée avant d'être ouverte.",
      ],
      silence: "Et si une source se tait, je vous le dirai.",
    });
    expect(PORTE.de).toEqual({
      titre: "Morgen, wenn Flexsis es wünscht",
      texte: [
        "Heute stammt die Liste aus klaren Regeln, gemessen an vergangenen Montagen.",
        "Morgen könnte Iris bei Flexsis einziehen: eine Assistentin für jede Beraterin und jeden Berater, und ein Agent, der jeden Morgen die Publikationen liest und die Anrufe vorschlägt.",
        "Mit Apertus, der offenen Schweizer künstlichen Intelligenz, angepasst an Ihre Daten: Einsätze, Erfolge, Kompetenzen der Beraterinnen und Berater. Auf Ihren Servern oder bei einem Schweizer Hoster. Ihre Daten würden das Haus nie verlassen.",
      ],
      etapes: [
        "Eine Testwoche mit zwei freiwilligen Beraterinnen oder Beratern.",
        "Sechs Wochen in zwei Filialen.",
        "Wenn die Ergebnisse stimmen: Iris bei Flexsis eingerichtet, mit Apertus, angepasst an ihre Daten, bei ihr im Haus.",
      ],
      gardeFous: [
        "Iris wird vorschlagen, die Beraterin oder der Berater wird entscheiden, immer.",
        "Alle werden sehen, was Iris speichert, und es korrigieren oder löschen können.",
        "Iris wird die Beraterinnen und Berater nie bewerten oder überwachen.",
        "Die Daten von Flexsis werden unter ihrer Kontrolle bleiben, in der Schweiz, mit ihrer schriftlichen Zustimmung.",
        "Jede neue Fähigkeit wird gemessen werden, bevor sie freigeschaltet wird.",
      ],
      silence: "Und wenn eine Quelle verstummt, werde ich es Ihnen sagen.",
    });
  });
  for (const lang of ["fr", "de"] as const) {
    const t = VISIT_COPY[lang].avenir;
    const p = PORTE[lang];
    it(`${lang} : « Demain, peut-être » dit la porte, ses garde-fous et le silence au futur ; l'étape 3 la nomme`, () => {
      expect(plain(t.iris.title)).toBe(p.titre);
      expect([t.iris.today, t.iris.tomorrow, t.iris.apertus].map(plain)).toEqual(p.texte);
      expect(t.iris.guards.map(plain)).toEqual(p.gardeFous);
      expect(plain(t.iris.silence)).toBe(p.silence);
      expect(plain(t.third.lead)).toBe(p.etapes[2]);
      // the passage on Apertus stays where it was, word for word (suite 8, § 6)
      expect(t.third.items.map(plain)).toContain(APERTUS[lang]);
    });
    it(`${lang} : tout au futur ou au conditionnel, jamais le sigle`, () => {
      const door = [p.titre, ...p.texte, ...p.etapes, ...p.gardeFous, p.silence];
      expect(door.join(" ")).not.toMatch(lang === "fr" ? /\bIA\b/ : /\bKI\b/);
      expect(p.texte[1]).toMatch(lang === "fr" ? /pourrait/ : /könnte/);
      expect(p.texte[2]).toMatch(lang === "fr" ? /sortiraient/ : /würden/);
      expect(p.silence).toMatch(lang === "fr" ? /dirai\.$/ : /werde ich/);
      expect(door.flatMap((x) => forbiddenTerms(x, lang))).toEqual([]);
    });
  }
});

