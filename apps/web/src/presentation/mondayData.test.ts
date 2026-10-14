import { describe, expect, it } from "vitest";
import claims from "@/data/demo/claims.json";
import histoires from "@/data/presentation/histoires.json";
import lundis from "@/data/presentation/lundis.json";
import { firstTest } from "@/visite/firstTest";
import { mondayOf, pickMonday, type MondaysData } from "./mondayData";

const data = lundis as unknown as MondaysData; // checked against its schema in src/lib/schema.test.ts

describe("acte 4 : « Choisissez une date »", () => {
  it("toute date est ramenée au lundi de sa semaine", () => {
    expect(mondayOf("2025-11-09")).toBe("2025-11-03"); // a Sunday
    expect(mondayOf("2025-11-03")).toBe("2025-11-03");
    expect(mondayOf("2026-01-01")).toBe("2025-12-29");
  });

  it("seules les dates avec 52 semaines avant et 8 semaines complètes après sont proposées ; les autres sont dites", () => {
    expect(pickMonday(data, "2025-07-14")).toEqual({ outside: "avant" }); // in the measure, but 51 weeks of data before
    expect(pickMonday(data, "2026-08-10")).toEqual({ outside: "apres" });
    expect(pickMonday(data, "pas une date")).toBeNull();
    const first = pickMonday(data, data.choix.premier);
    expect(first && "monday" in first && first.monday.lundi).toBe("2025-07-21");
    // the prepared example of the visit: Monday 2 March 2026, a Monday that can be chosen
    const example = pickMonday(data, data.choix.exemple);
    expect(example && "monday" in example && example.monday.lundi).toBe("2026-03-02");
  });

  it("les nombres écrits en toutes lettres dans le texte suivent les données (« deux premiers », « vingt entreprises »)", () => {
    // « Les deux premiers ne sont pas proposés au choix » (copy_c.ts, dir.date.mean)
    expect(data.mesure.semaines - data.choix.nombre).toBe(2);
    expect(data.lundis.filter((m) => !m.choisissable).map((m) => m.lundi)).toEqual(["2025-07-07", "2025-07-14"]);
    // the scope of the confession: « vingt entreprises par semaine » in Suisse romande (copy_c.ts, dir.date.aveuScope)
    expect(histoires.mesure.claims).toBe("REEL-T0");
    expect(histoires.mesure.definition.fr).toContain("Sur 20 entreprises proposées chaque semaine");
    expect(histoires.mesure.perimetre.texte.fr).toContain("Suisse romande");
    expect(firstTest()).toEqual({ semaines: 44, regle: { fr: "55,0 %", de: "55,0 %" }, m0: { fr: "52,7 %", de: "52,7 %" } });
  });

  it("un lundi défavorable s'affiche tel quel", () => {
    const worst = Math.min(...data.lundis.map((m) => m.obtenu));
    const picked = pickMonday(data, "2025-11-05"); // a Wednesday of the worst week
    expect(picked && "monday" in picked && [picked.monday.lundi, picked.monday.obtenu]).toEqual(["2025-11-03", worst]);
    expect(worst).toBe(4);
  });

  it("chaque liste suit la règle simple : le plus de marchés en 52 semaines d'abord, dix entreprises", () => {
    for (const m of data.lundis) {
      expect(m.dix.map((c) => c.rang)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
      const n = m.dix.map((c) => c.marches_52s);
      expect(n).toEqual([...n].sort((a, b) => b - a));
      for (const c of m.dix) expect(c.dernier_marche < m.lundi).toBe(true); // only what was published before
    }
  });

  it("la moyenne et le hasard affichés sont ceux du registre (REEL-SPEC-BAT), recalculés depuis les lundis", () => {
    const mean = data.lundis.reduce((a, m) => a + m.obtenu, 0) / (10 * data.lundis.length);
    expect(mean).toBeCloseTo(data.mesure.regle, 12);
    const line = (claims as Record<string, { valeur: string }>)["REEL-SPEC-BAT"].valeur;
    expect(line).toContain(`fréquence 52 sem. ${data.mesure.affiche.regle.fr}`);
    expect(line).toContain(`hasard ${data.mesure.affiche.hasard.fr}`);
    expect((claims as Record<string, unknown>)["PRES-DATE-1"]).toBeTruthy();
  });
});
