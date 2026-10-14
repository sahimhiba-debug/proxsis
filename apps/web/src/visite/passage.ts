"use client";

// The scenes and their passages (brief of 07.10.2026, § 2.3; IDENTITE.md, « Fonds, scènes et raccords »): white
// dominant, black #121212 for three moments only (the director decides in the carnet, the next Monday, the big question
// of « Une date »). To enter one of them going forward, one orange diagonal band crosses the image in 0.9 s and covers it
// entirely at the instant the scene changes: the step changes under it, half-way. Three times at most in a walk, never
// during reading. Without motion (the visitor's setting or « Sans mouvement »), the step changes at once and the colours
// fade in a short time instead.
import { useCallback, useEffect, useRef, useState } from "react";
import { reduce, VISIT_STEPS, type StepId, type VisitAction, type VisitState } from "./state";

export const SOMBRES: ReadonlySet<StepId> = new Set<StepId>(["carnet", "suivant", "date"]);
export const HALF_BAND_MS = 450;

export function sceneOf(step: number): "sombre" | "claire" {
  return SOMBRES.has(VISIT_STEPS[step]?.id) ? "sombre" : "claire";
}

/** Whether this action, from this state, enters one of the three dark moments going forward (the band crosses then). */
export function entersDarkMoment(s: VisitState, a: VisitAction): boolean {
  const to = reduce(s, a).step;
  return to > s.step && SOMBRES.has(VISIT_STEPS[to].id);
}

/** Moves through the visit; when a move enters a dark moment with motion, the band covers first (bande: its key). */
export function usePassage(s: VisitState, dispatch: (a: VisitAction) => void, motion: boolean) {
  const [bande, setBande] = useState(0);
  const pending = useRef<{ a: VisitAction; timer: number } | null>(null);
  useEffect(() => () => { if (pending.current) window.clearTimeout(pending.current.timer); }, []);
  const go = useCallback((a: VisitAction) => {
    // a second move while the band crosses: the first one lands at once, then this one, without a band
    if (pending.current) {
      const p = pending.current;
      window.clearTimeout(p.timer);
      pending.current = null;
      dispatch(p.a);
      dispatch(a);
      return;
    }
    const still = !motion || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!still && entersDarkMoment(s, a)) {
      setBande((k) => k + 1);
      const timer = window.setTimeout(() => { pending.current = null; dispatch(a); }, HALF_BAND_MS);
      pending.current = { a, timer };
      return;
    }
    dispatch(a);
  }, [s, dispatch, motion]);
  return { go, bande };
}
