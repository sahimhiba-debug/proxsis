import { describe, expect, it } from "vitest";
import { homeFor, parseRole } from "./RoleSwitcher";

describe("rôle gardé sur l'appareil", () => {
  it("relit le rôle choisi", () => {
    expect(parseRole(JSON.stringify({ role: "directeur", consultant: "M2", agence: "sion" })))
      .toEqual({ role: "directeur", consultant: "M2", agence: "sion" });
  });

  it("un stockage vide, illisible ou abîmé redonne le rôle par défaut, champ par champ, sans planter", () => {
    const fallback = { role: "consultant", consultant: "M1", agence: "martigny" };
    expect(parseRole(null)).toEqual(fallback);
    expect(parseRole("{pas du json")).toEqual(fallback);
    expect(parseRole("null")).toEqual(fallback);
    expect(parseRole(JSON.stringify({ role: "pdg", consultant: 5, agence: "sion" }))).toEqual({ ...fallback, agence: "sion" });
  });

  it("un code qui n'en est pas un ne fabrique jamais une adresse", () => {
    const r = parseRole(JSON.stringify({ role: "consultant", consultant: "../../conformite" }));
    expect(homeFor("fr", r)).toBe("/fr/semaine/M1/");
  });
});
