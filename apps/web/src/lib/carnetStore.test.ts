import { describe, expect, it } from "vitest";
import { carnet, lastNote, parseBook, trialExport, type CarnetBook } from "./carnetStore";

const T1 = "2026-10-05T09:00:00.000Z";
const T2 = "2026-10-05T10:00:00.000Z";

describe("le carnet de l'application : sur l'appareil, sans texte libre", () => {
  it("décider, changer d'avis, effacer", () => {
    let b: CarnetBook = {};
    b = carnet.decide(b, "a", { decision: "appeler", confie: true });
    expect(b.a.decision).toEqual({ decision: "appeler", confie: true });
    b = carnet.decide(b, "a", { decision: "ecarter", motif: "client" });
    expect(b.a.decision).toEqual({ decision: "ecarter", motif: "client" });
    b = carnet.decide(b, "a", null);
    expect(b.a.decision).toBeUndefined();
  });

  it("les suites d'appel sont datées ; un rappel garde sa date ; la dernière fait foi", () => {
    let b = carnet.note({}, "a", "pasJoint", T1);
    b = carnet.note(b, "a", "rappel", T2, "2026-10-12");
    expect(b.a.suites).toEqual([{ outcome: "pasJoint", le: T1 }, { outcome: "rappel", le: T2, rappel: "2026-10-12" }]);
    expect(lastNote(b.a)?.outcome).toBe("rappel");
    expect(carnet.note(b, "a", "nimporte" as never, T2)).toBe(b); // an unknown outcome is not kept
  });

  it("une suite touchée deux fois le même jour n'en fait qu'une ; la dernière se retire ; la date du rappel se règle après", () => {
    let b = carnet.note({}, "a", "pasJoint", "2026-10-12T08:10:00.000Z");
    b = carnet.note(b, "a", "pasJoint", "2026-10-12T08:11:00.000Z"); // a second touch, not a second call
    expect(b.a.suites).toEqual([{ outcome: "pasJoint", le: "2026-10-12T08:11:00.000Z" }]);
    b = carnet.note(b, "a", "pasJoint", "2026-10-13T08:00:00.000Z"); // another day: another call
    expect(b.a.suites).toHaveLength(2);
    b = carnet.note(b, "a", "rappel", "2026-10-13T09:00:00.000Z", "2026-10-19");
    b = carnet.retime(b, "a", "2026-10-21");
    expect(lastNote(b.a)).toEqual({ outcome: "rappel", le: "2026-10-13T09:00:00.000Z", rappel: "2026-10-21" });
    expect(carnet.retime(b, "a", "pas une date")).toBe(b);
    b = carnet.undo(b, "a");
    expect(b.a.suites.map((n) => n.outcome)).toEqual(["pasJoint", "pasJoint"]);
    expect(carnet.retime(b, "a", "2026-10-22")).toBe(b); // the last one is no longer a call back
    expect(carnet.undo({}, "z")).toEqual({});
  });

  it("aucun champ libre ne survit au stockage ; un carnet abîmé repart proprement", () => {
    const raw = JSON.stringify({ a: { decision: { decision: "appeler", note: "Jean Exemple" }, suites: [{ outcome: "besoin", le: T1, texte: "x" }] },
      b: { decision: { decision: "?" } }, c: "abîmé" });
    expect(parseBook(raw)).toEqual({ a: { decision: { decision: "appeler" }, suites: [{ outcome: "besoin", le: T1 }] } });
    expect(parseBook("{pas du json")).toEqual({});
  });

  it("l'export de la semaine témoin : des identifiants et des choix, aucun nom", () => {
    let b = carnet.decide({}, "ent-1", { decision: "appeler" });
    b = carnet.note(b, "ent-1", "etape", T1);
    b = carnet.prepare(b, "ent-1", 12);
    b = carnet.note(b, "ent-2", "pasJoint", T2);
    const x = trialExport(b, "2026-10-05", "M1", ["ent-1", "ent-2", "ent-3"]);
    expect(x.entreprises.map((e) => [e.entreprise_id, e.conversation_utile, e.temps_preparation_min])).toEqual([
      ["ent-1", true, 12], ["ent-2", false, null], ["ent-3", null, null]]);
    expect(JSON.stringify(x)).not.toMatch(/"nom"|Jean/);
  });
});
