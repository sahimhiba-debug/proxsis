import { describe, expect, it } from "vitest";
import agences from "@/data/demo/agences.json";
import curated from "@/data/presentation/dossiers.json";
import listes from "@/data/demo/listes.json";
import territoire from "@/data/presentation/territoire.json";
import { AGENCE_EXEMPLE } from "./agences";
import { consultantMonday, EXAMPLE_ENTRY, inAgencyOrder } from "./consultant";

const TEN = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
const MONDAY = "2026-10-05";

describe("visite : la vue du consultant après la décision", () => {
  it("une piste confiée passe en tête ; les suivantes gardent leur ordre ; jamais plus de dix", () => {
    const m = consultantMonday(TEN, "x", EXAMPLE_ENTRY, MONDAY);
    expect(m.first).toEqual([{ id: "x", confided: true }, { id: "a", confided: false }, { id: "b", confided: false }]);
    expect(m.others.map((r) => r.id)).toEqual(["c", "d", "e", "f", "g", "h", "i"]);
    expect(consultantMonday(TEN, "e", EXAMPLE_ENTRY, MONDAY).first.map((r) => r.id)).toEqual(["e", "a", "b"]);
  });

  it("une piste écartée ne part jamais chez le consultant, la suivante prend sa place", () => {
    const m = consultantMonday(TEN, "b", { decision: "ecarter", motif: "client" }, MONDAY);
    expect([...m.first, ...m.others].map((r) => r.id)).toEqual(["a", "c", "d", "e", "f", "g", "h", "i", "j"]);
    expect(m.setAside).toEqual(["b"]);
  });

  it("« Revoir le… » attend sa date ; une piste non confiée garde sa place, sans marque", () => {
    const later = consultantMonday(TEN, "c", { decision: "revoir", revoir: "2026-10-12", confie: true }, MONDAY);
    expect(later.later).toEqual([{ id: "c", date: "2026-10-12" }]);
    expect([...later.first, ...later.others].map((r) => r.id)).not.toContain("c");
    const kept = consultantMonday(TEN, "c", { decision: "verifier" }, MONDAY);
    expect(kept.first.map((r) => r.id)).toEqual(["a", "b", "c"]);
    expect(kept.first.some((r) => r.confided)).toBe(false);
  });
});

// Q17 (Hiba, 13.10.2026) : « le même ordre des trois premiers appels partout ». La visite montre la semaine du consultant
// de l'agence (Martigny par défaut) dans l'ordre de l'application (« Ma semaine »), avec la piste confiée en tête.
describe("une seule liste : la visite et « Ma semaine » ont les mêmes trois premiers appels", () => {
  const parAgence = (listes as unknown as { batiment: { par_agence: Record<string, { entreprises: string[] }> } }).batiment.par_agence;
  const around = Object.fromEntries(Object.entries(parAgence).map(([a, p]) => [a, p.entreprises]));
  const ten = curated.dix.map((id) => ({ id }));
  const exemple = (territoire as unknown as { exemple: { entreprise: string } }).exemple.entreprise;
  for (const [agence, a] of Object.entries(agences as unknown as Record<string, { consultants: { code: string; specialite: string }[] }>)) {
    it(`${agence} : les trois premiers appels de la visite sont ceux de « Ma semaine » (${a.consultants.find((c) => c.specialite === "batiment")?.code})`, () => {
      const rows = inAgencyOrder(ten, around, agence);
      expect(rows.map((r) => r.id).sort()).toEqual([...curated.dix].sort());
      const visite = consultantMonday(rows.map((r) => r.id), exemple, EXAMPLE_ENTRY, MONDAY).first.map((r) => r.id);
      const app = parAgence[agence].entreprises;
      // the handed lead first, then the application's order without it
      expect(visite).toEqual([exemple, ...app.filter((id) => id !== exemple)].slice(0, 3));
      if (app.indexOf(exemple) < 3) expect([...visite].sort()).toEqual(app.slice(0, 3).sort());
    });
  }
  it("sans agence choisie : Martigny, l'agence de l'exemple", () => {
    expect(inAgencyOrder(ten, around, null).map((r) => r.id)).toEqual(parAgence[AGENCE_EXEMPLE].entreprises);
  });
});
