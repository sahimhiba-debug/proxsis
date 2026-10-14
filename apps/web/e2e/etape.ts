import type { Page } from "@playwright/test";
import { ALL, initialVisit, VISIT_KEY, VISIT_STEPS, type VisitState } from "../src/visite/state";

/** The steps of the presentation (the visit in five times), read from the visit itself (src/visite/state.ts). */
export const STEP_IDS = VISIT_STEPS.map((s) => s.id);

/** What a step needs to show everything: « Choisissez une date » is opened at the least favourable Monday (4 out of
 *  10) instead of the prepared example; the date field itself is gone through by visite.spec.ts. */
const STEP_STATE: Partial<Record<string, Partial<VisitState>>> = { date: { monday: "2025-11-03" } };

/** Opens the current page's presentation at a step, everything revealed, by storing the visit exactly as the visit
 *  stores it (a new version of the state is followed here without any change). */
export async function openStep(page: Page, step: number, reload: Parameters<Page["reload"]>[0] = {}): Promise<void> {
  const session = JSON.stringify({ ...initialVisit(), ...STEP_STATE[STEP_IDS[step]], step, reveal: ALL });
  await page.evaluate(([key, value]) => localStorage.setItem(key, value), [VISIT_KEY, session] as const);
  await page.reload(reload);
}
