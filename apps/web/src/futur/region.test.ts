import { describe, expect, it } from "vitest";
import agences from "@/data/demo/agences.json";
import entreprises from "@/data/demo/entreprises.json";
import listes from "@/data/demo/listes.json";
import type { Company } from "@/lib/types";
import { communesIn, labelSide, places, project, regionView } from "./region";

const companies = entreprises as unknown as Record<string, Company>;
type Part = { entreprises: string[]; surprises: string[] };
const lists = listes as unknown as Record<string, { par_agence: Record<string, Part> }>;

describe("futurisme : la carte de la région ne place rien au hasard", () => {
  it("chaque entreprise de la semaine est sur sa commune, l'agence et les points restent dans le cadre 4:3", () => {
    for (const a of Object.values(agences)) {
      for (const c of a.consultants) {
        const part = lists[c.specialite]?.par_agence[a.id];
        if (!part) continue;
        const week = [...new Set([...part.entreprises, ...part.surprises])].map((id) => companies[id]);
        const ps = places(week.map((x) => ({ ville: x.ville, lat: x.lat, lon: x.lon, recent: false })));
        // one place per commune of the week, as many companies as on the page
        expect(ps.map((p) => p.ville).sort()).toEqual([...new Set(week.map((x) => x.ville))].sort());
        expect(ps.reduce((n, p) => n + p.n, 0)).toBe(week.length);
        const home = project(a.lat, a.lon);
        const v = regionView([home, ...ps]);
        expect(v.w / v.h).toBeCloseTo(4 / 3, 6);
        for (const p of [home, ...ps]) {
          expect(p.x).toBeGreaterThan(v.x);
          expect(p.x).toBeLessThan(v.x + v.w);
          expect(p.y).toBeGreaterThan(v.y);
          expect(p.y).toBeLessThan(v.y + v.h);
        }
        expect(communesIn(v).length).toBeGreaterThan(0);
      }
    }
  });

  it("une commune est en cuivre seulement si l'une de ses entreprises a un marché de moins de 14 jours", () => {
    const ps = places([
      { ville: "A", lat: 46.1, lon: 7.0, recent: false },
      { ville: "A", lat: 46.1, lon: 7.0, recent: true },
      { ville: "B", lat: 46.2, lon: 7.1, recent: false },
    ]);
    expect(ps.find((p) => p.ville === "A")).toMatchObject({ n: 2, recent: 1 });
    expect(ps.find((p) => p.ville === "B")).toMatchObject({ n: 1, recent: 0 });
    expect(ps.at(-1)?.ville).toBe("A"); // drawn last, above the others
  });
});

describe("une étiquette se pose du côté libre", () => {
  it("à droite s'il y a la place, à gauche contre le bord droit, jamais sur un autre point", () => {
    expect(labelSide({ x: 100, y: 100 }, "Sion", [], 600, 450)).toBe("right");
    expect(labelSide({ x: 580, y: 100 }, "Sion", [], 600, 450)).toBe("left");
    // a dot just to the right: the label goes elsewhere
    expect(labelSide({ x: 100, y: 100 }, "Martigny", [{ x: 130, y: 100 }], 600, 450)).not.toBe("right");
  });
});
