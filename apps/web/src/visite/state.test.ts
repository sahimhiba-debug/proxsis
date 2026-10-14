import { describe, expect, it } from "vitest";
import { ALL, firstOf, initialVisit, parseVisit, reduce, VISIT_STEPS, type VisitAction, type VisitState } from "./state";

const go = (s: VisitState, ...actions: VisitAction[]) => actions.reduce(reduce, s);

describe("visite : état", () => {
  it("cinq temps puis la conclusion, chaque temps a au moins une étape", () => {
    expect([...new Set(VISIT_STEPS.map((s) => s.temps))]).toEqual([1, 2, 3, 4, 5, 6]);
    expect(VISIT_STEPS.at(-1)?.id).toBe("conclusion");
  });

  it("« Continuer » révèle les gestes d'une étape puis avance ; « Retour » revient, l'étape précédente complète", () => {
    const date = firstOf(3);
    let s = go(initialVisit(), { type: "goto", step: date });
    s = go(s, { type: "next" }, { type: "next" });
    expect([s.step, s.reveal]).toEqual([date, 2]);
    s = reduce(s, { type: "next" });
    expect([s.step, s.reveal]).toEqual([date + 1, 0]);
    s = reduce(s, { type: "prev" });
    expect([s.step, s.reveal]).toEqual([date, ALL]);
    s = reduce(s, { type: "prev" });
    expect([s.step, s.reveal]).toEqual([date, 1]);
  });

  it("sauter un temps, aller à la conclusion, ne jamais sortir des bornes", () => {
    expect(VISIT_STEPS[reduce(initialVisit(), { type: "temps", temps: 4 }).step].id).toBe("seuil");
    const end = reduce(initialVisit(), { type: "temps", temps: 6 });
    expect(VISIT_STEPS[end.step].id).toBe("conclusion");
    expect(reduce(end, { type: "next" })).toEqual(end);
    expect(reduce(initialVisit(), { type: "prev" }).step).toBe(0);
  });

  it("le carnet ne garde que des choix valides, sans texte libre", () => {
    let s = reduce(initialVisit(), { type: "decide", company: "a", entry: { decision: "ecarter", motif: "client" } });
    expect(s.carnet.a).toEqual({ decision: "ecarter", motif: "client" });
    s = reduce(s, { type: "decide", company: "b", entry: { decision: "revoir", revoir: "pas une date" } });
    expect(s.carnet.b).toBeUndefined();
    s = reduce(s, { type: "decide", company: "c", entry: { decision: "appeler", confie: true, note: "Jean" } as never });
    expect(s.carnet.c).toEqual({ decision: "appeler", confie: true });
    expect(reduce(s, { type: "decide", company: "a", entry: null }).carnet.a).toBeUndefined();
  });

  it("une nouvelle date cache de nouveau ce qui vient après elle", () => {
    const s = go(initialVisit(), { type: "goto", step: firstOf(3) }, { type: "next" }, { type: "monday", value: "2025-11-03" });
    expect([s.monday, s.reveal]).toEqual(["2025-11-03", 0]);
  });

  it("reprendre plus tard au même endroit ; une séance abîmée repart proprement", () => {
    const s = go(initialVisit(), { type: "temps", temps: 4 }, { type: "half", value: true },
      { type: "pilot", value: { indicator: "utiles", threshold: 3 } });
    expect(parseVisit(JSON.stringify(s))).toEqual(s);
    expect(parseVisit("{pas du json")).toEqual(initialVisit());
    expect(parseVisit(JSON.stringify({ ...s, step: 999, carnet: { x: { decision: "?" } }, pilot: { indicator: 3 } })))
      .toEqual({ ...s, step: VISIT_STEPS.length - 1, carnet: {}, pilot: null });
    expect(reduce(s, { type: "reset" })).toEqual(initialVisit());
  });
});
