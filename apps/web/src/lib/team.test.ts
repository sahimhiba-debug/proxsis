import { describe, expect, it } from "vitest";
import team from "@/data/equipe/equipe.json";
import { teamMissing, type Team } from "./team";

// « Qui sommes-nous » (suite 6 of Hiba, § 5): no empty slot is ever displayed, and none goes to production
describe("« Qui sommes-nous » n'affiche aucun emplacement vide", () => {
  it("chaque emplacement vide est nommé ; sans contact, il n'y en a pas : la page n'en montre simplement pas", () => {
    expect(teamMissing({ membres: [{ nom: "A", role: null }], contact: null })).toEqual(["membre 1 : rôle"]);
    expect(teamMissing({ membres: [{ nom: "A", role: "B" }], contact: null })).toEqual([]);
    expect(teamMissing({ membres: [{ nom: "A", role: "B" }], contact: "c@d.ch" })).toEqual([]);
    expect(teamMissing({ membres: [], contact: null })).toEqual(["membres"]);
  });

  it("aujourd'hui, la page n'a aucun emplacement vide : un seul membre, celui que Hiba a donné, et pas de contact", () => {
    expect(teamMissing(team as Team)).toEqual([]);
    expect(team.membres).toHaveLength(1);
    expect(team.contact).toBeNull();
  });
});
