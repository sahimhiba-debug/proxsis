import { describe, expect, it } from "vitest";
import curated from "@/data/presentation/dossiers.json";
import suivant from "@/data/presentation/lundi_suivant.json";
import { exampleCarnet, nextMonday, type NextData } from "./next";

const DATA = suivant as unknown as NextData;
const TEN = curated.dix;

describe("visite : le lundi suivant retrouve les décisions", () => {
  it("le fichier : le lundi suivant, la même règle, rien d'inventé après la fin des données", () => {
    expect(DATA.premier).toBe(curated.rejeu);
    expect(Date.parse(DATA.lundi) - Date.parse(DATA.premier)).toBe(7 * 86_400_000);
    expect(DATA.classement.length).toBe(15);
    expect(DATA.fin_des_donnees < DATA.premier && DATA.nouvelles_publications.length === 0).toBe(true);
  });

  it("sans décision, la liste du lundi suivant est le classement de la règle", () => {
    const m = nextMonday(DATA, TEN, {});
    expect(m.calls.map((r) => r.id)).toEqual(DATA.classement.slice(0, 10).map((c) => c.id));
  });

  it("l'écartée ne revient pas, le rappel tombe à sa date, la piste gardée revient, la suivante prend la place libérée", () => {
    const carnet = { ...exampleCarnet(DATA.lundi), "ent-1ef761b229": { decision: "appeler" as const, confie: true },
      "ent-0ff073ea76": { decision: "revoir" as const, revoir: "2026-10-26" } };
    const m = nextMonday(DATA, TEN, carnet);
    const ids = m.calls.map((r) => r.id);
    expect(ids).not.toContain("ent-734d5f7d45"); // set aside
    expect(m.setAside).toEqual(["ent-734d5f7d45"]);
    expect(m.calls[0]).toEqual({ id: "ent-266673a5c4", kind: "recall", entry: { decision: "revoir", revoir: DATA.lundi } });
    expect(m.calls[1]).toMatchObject({ id: "ent-1ef761b229", kind: "kept" });
    expect(m.waiting).toEqual([{ id: "ent-0ff073ea76", date: "2026-10-26" }]);
    expect(ids).not.toContain("ent-0ff073ea76");
    expect(ids.length).toBe(10);
    const entered = m.calls.filter((r) => r.kind === "new").map((r) => r.id);
    expect(entered.length).toBeGreaterThan(0); // the freed places, taken by the next of the ranking
    expect(entered.every((id) => !TEN.includes(id))).toBe(true);
  });
});
