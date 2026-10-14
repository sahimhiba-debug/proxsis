import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import contours from "@/data/presentation/communes_vs.json";
import curated from "@/data/presentation/dossiers.json";
import territoire from "@/data/presentation/territoire.json";
import { AGENCE_EXEMPLE, AGENCES, autour, centre } from "./agences";

const claims = readFileSync(join(__dirname, "../../../../CLAIMS.md"), "utf8");
const line = claims.split("\n").find((l) => l.startsWith("| EXT-FLEXSIS-AGENCES-VS |")) ?? "";
const centres = Object.fromEntries(contours.communes.map((c) => [String(c.bfs), centre(c.d)]));
const companies = territoire.entreprises as Record<string, { nom: string; commune_siege: number }>;

describe("« Votre lundi à Martigny, Sion, Monthey » (suite 2, § 3)", () => {
  it("les trois agences : leurs adresses publiques, telles que CLAIMS les cite, à leur commune", () => {
    expect(line).toContain("SOURCE PUBLIQUE");
    for (const a of AGENCES) {
      expect(line).toContain(a.adresse);
      expect(contours.communes.find((c) => String(c.bfs) === a.bfs)?.nom).toBe(a.nom);
    }
    expect(AGENCE_EXEMPLE).toBe("martigny");
  });

  it("autour de Martigny, l'exemple préparé : l'entreprise du dossier guidé de Saxon d'abord", () => {
    const week = curated.dix.filter((id) => id in companies);
    const around = autour(week, (id) => String(companies[id].commune_siege), centres, AGENCES[0], (id) => companies[id].nom);
    expect(around[0]).toBe(territoire.exemple.entreprise);
    expect(new Set(around).size).toBe(around.length);
  });
});

// One list in the visit and in the application (questionnaire of Hiba, 07.10.2026, B7): around each agency, the visit
// shows the week of that agency's consultant in the application, in the same order: the ten of the frozen list.
describe("une seule liste dans la visite et dans l'application", () => {
  it("chaque agence du Valais a, en Bâtiment, les dix de la visite, la plus proche d'abord", async () => {
    const { default: listes } = await import("@/data/demo/listes.json");
    const { default: dossiers } = await import("@/data/presentation/dossiers.json");
    const parts = (listes as unknown as { batiment: { par_agence: Record<string, { entreprises: string[] }> } }).batiment.par_agence;
    for (const a of AGENCES) {
      expect([...parts[a.id].entreprises].sort(), a.id).toEqual([...dossiers.dix].sort());
    }
    expect(parts.martigny.entreprises[0]).toBe("ent-1ef761b229"); // Carron (Saxon), the guided dossier, first for Martigny
  });
});
