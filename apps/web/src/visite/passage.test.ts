import { describe, expect, it } from "vitest";
import { entersDarkMoment, sceneOf, SOMBRES } from "./passage";
import { initialVisit, VISIT_STEPS, type VisitState } from "./state";

const at = (id: string, reveal = 99): VisitState => ({ ...initialVisit(), step: VISIT_STEPS.findIndex((s) => s.id === id), reveal });

describe("les scènes et leurs passages (brief du 07.10.2026, § 2.3)", () => {
  it("trois moments sombres seulement : le carnet, le lundi suivant, la grande question de « Une date »", () => {
    expect([...SOMBRES].sort()).toEqual(["carnet", "date", "suivant"]);
    expect(VISIT_STEPS.map((s, i) => sceneOf(i))).toEqual(VISIT_STEPS.map((s) => (SOMBRES.has(s.id) ? "sombre" : "claire")));
  });

  it("la bande passe en entrant dans un moment sombre en avançant, trois fois au plus sur tout le parcours", () => {
    expect(entersDarkMoment(at("dossier"), { type: "next" })).toBe(true);
    expect(entersDarkMoment(at("carnet"), { type: "next" })).toBe(true);
    expect(entersDarkMoment(at("suivant"), { type: "next" })).toBe(true);
    expect(entersDarkMoment(at("date"), { type: "next" })).toBe(false);
    // a gesture inside a step, going back, or straight to the conclusion: no band
    expect(entersDarkMoment(at("dossier", 0), { type: "next" })).toBe(false);
    expect(entersDarkMoment(at("seuil", 0), { type: "prev" })).toBe(false);
    expect(entersDarkMoment(at("carte"), { type: "temps", temps: 6 })).toBe(false);
    let s: VisitState = { ...initialVisit() };
    let bands = 0;
    for (let i = 0; i < 40 && s.step < VISIT_STEPS.length - 1; i++) {
      if (entersDarkMoment(s, { type: "next" })) bands++;
      s = { ...s, ...(s.reveal < VISIT_STEPS[s.step].gestures ? { reveal: s.reveal + 1 } : { step: s.step + 1, reveal: 0 }) };
    }
    expect(bands).toBe(3);
  });
});
