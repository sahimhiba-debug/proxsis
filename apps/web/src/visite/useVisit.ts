"use client";

import { useCallback, useMemo, useSyncExternalStore } from "react";
import { initialVisit, parseVisit, reduce, VISIT_KEY, type VisitAction, type VisitState } from "./state";

// One visit per device, shared by the visit and the presenter's notes window (same browser): stored on this device only,
// synchronised through BroadcastChannel; in memory when the browser refuses storage (private browsing): the visit still
// works for this visit. Nothing leaves the device.
const CHANNEL = "proxsis-visite";
const listeners = new Set<() => void>();
let memory: string | null = null;

function read(): string | null {
  try {
    return window.localStorage.getItem(VISIT_KEY) ?? memory;
  } catch {
    return memory;
  }
}

function subscribe(cb: () => void): () => void {
  listeners.add(cb);
  const ch = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(CHANNEL) : null;
  if (ch) ch.onmessage = () => cb();
  window.addEventListener("storage", cb);
  return () => {
    listeners.delete(cb);
    ch?.close();
    window.removeEventListener("storage", cb);
  };
}

function write(next: VisitState): void {
  const raw = JSON.stringify(next);
  memory = raw;
  try {
    window.localStorage.setItem(VISIT_KEY, raw);
  } catch {
    // storage refused: kept in memory
  }
  for (const l of listeners) l();
  if (typeof BroadcastChannel !== "undefined") {
    const ch = new BroadcastChannel(CHANNEL);
    ch.postMessage("update");
    ch.close();
  }
}

// The step saved before this page opened, and whether the visitor has moved since: « Vous reprenez là où vous vous
// étiez arrêté » shows only on the step the visit reopened on, until the first move.
let openedOn: number | null = null;
let moved = false;
const openedStep = () => (openedOn ??= parseVisit(read()).step);
const noSubscription = () => () => {};

export function useVisit(): [VisitState, (a: VisitAction) => void] {
  const raw = useSyncExternalStore(subscribe, read, () => null);
  const state = useMemo(() => (raw ? parseVisit(raw) : initialVisit()), [raw]);
  const dispatch = useCallback((a: VisitAction) => {
    const before = parseVisit(read());
    const next = reduce(before, a);
    if (next.step !== before.step) moved = true;
    write(next);
  }, []);
  return [state, dispatch];
}

/** True while the visit shows the step it reopened on (a step saved earlier, not the first one). */
export function useResumed(step: number): boolean {
  return useSyncExternalStore(noSubscription, () => !moved && openedStep() > 0 && step === openedStep(), () => false);
}
