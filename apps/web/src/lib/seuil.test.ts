import { describe, expect, it } from "vitest";
import { parseAmount, SEUIL_COPY, SEUIL_EXAMPLE, seuil } from "./seuil";

/** The words, with the no-break spaces of French typography made ordinary. */
const plain = (x: string) => x.replace(/\u00a0/g, " ");

describe("le seuil : un seul calcul, quatre règles", () => {
  it("le nombre de journées qui couvre le coût, sur la période", () => {
    const r = seuil(SEUIL_EXAMPLE);
    expect(r.cost).toBe(3600 + 12 * 60);
    expect(r.breakEvenDays).toBe(44); // 4 320 / 100 = 43,2 → 44 journées
    expect(44 * SEUIL_EXAMPLE.marginPerDay).toBeGreaterThanOrEqual(r.cost);
    expect(43 * SEUIL_EXAMPLE.marginPerDay).toBeLessThan(r.cost);
    expect(seuil({ ...SEUIL_EXAMPLE, marginPerDay: 0 }).breakEvenDays).toBeNull();
    expect(seuil({ ...SEUIL_EXAMPLE, marginPerDay: 4320, serviceCost: 3600 }).breakEvenDays).toBe(1);
  });

  it("on compte la marge, pas le chiffre d'affaires : chaque journée rapporte sa marge, rien d'autre", () => {
    const one = seuil({ ...SEUIL_EXAMPLE, days: 1 }).net;
    const two = seuil({ ...SEUIL_EXAMPLE, days: 2 }).net;
    expect(two - one).toBe(SEUIL_EXAMPLE.marginPerDay);
  });

  it("une journée sans mission est un manque à gagner, pas un coût salarial : le coût ne dépend que du service et du temps des équipes", () => {
    for (const days of [0, 10, 100]) expect(seuil({ ...SEUIL_EXAMPLE, days }).cost).toBe(4320);
    expect(seuil({ ...SEUIL_EXAMPLE, days: 0 }).net).toBe(-4320); // no day: the cost, no salary added
  });

  it("aucune journée n'est comptée deux fois : une seule quantité de journées, une seule marge", () => {
    const r = seuil(SEUIL_EXAMPLE);
    expect(r.gains).toBe(SEUIL_EXAMPLE.days * SEUIL_EXAMPLE.marginPerDay);
  });

  it("le temps gagné reste à part tant que sa valeur n'est pas définie", () => {
    expect(seuil({ ...SEUIL_EXAMPLE, savedHours: 0 })).toEqual(seuil({ ...SEUIL_EXAMPLE, savedHours: 500 }));
  });

  it("« Deux fois moins » divise les journées, pas le coût ; la perte reste une perte", () => {
    const r = seuil(SEUIL_EXAMPLE, true);
    expect([r.gains, r.cost, r.net, r.negative]).toEqual([3000, 4320, -1320, true]);
    expect(seuil(SEUIL_EXAMPLE).net).toBe(1680);
    expect(r.breakEvenDays).toBe(seuil(SEUIL_EXAMPLE).breakEvenDays);
  });

  it("une saisie hors limite n'est pas prise en compte", () => {
    expect(parseAmount("1'200,5", 10_000)).toBe(1200.5);
    expect(parseAmount("2,5", 100, true)).toBeNull();
    expect(parseAmount("-3", 100)).toBeNull();
    expect(parseAmount("", 100)).toBeNull();
  });

  it("les textes du brief, mot pour mot, et les mêmes clés en allemand", () => {
    expect(plain(SEUIL_COPY.fr.question)).toBe("Combien de journées supplémentaires facturées faut-il pour couvrir le coût ?");
    expect(plain(SEUIL_COPY.fr.result)).toBe("Il suffit de {n} journées supplémentaires facturées pour couvrir le coût.");
    expect(plain(SEUIL_COPY.fr.half)).toBe("Deux fois moins");
    expect(Object.keys(SEUIL_COPY.de).sort()).toEqual(Object.keys(SEUIL_COPY.fr).sort());
  });
});
