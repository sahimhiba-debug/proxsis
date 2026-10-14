"use client";

import { useSyncExternalStore } from "react";

// Browser storage read through useSyncExternalStore: the server (and the first render) sees ``fallback``; the
// client re-renders with the stored value; writes call ``notifyStored()`` so every reader updates.
const listeners = new Set<() => void>();

export function notifyStored(): void {
  for (const l of listeners) l();
}

function subscribe(cb: () => void): () => void {
  listeners.add(cb);
  window.addEventListener("storage", cb);
  return () => {
    listeners.delete(cb);
    window.removeEventListener("storage", cb);
  };
}

// Storage refused (site data blocked, some private modes): what was written is kept in memory for this visit, so every
// choice still works until the page is closed (brief « à distance », § 8). A later successful write clears it.
const memory = new Map<string, string>();

export function readStored(key: string): string | null {
  if (memory.has(key)) return memory.get(key) ?? null;
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function writeStored(key: string, value: string): void {
  try {
    window.localStorage.setItem(key, value);
    memory.delete(key);
  } catch {
    memory.set(key, value);
  }
  notifyStored();
}

export function useStoredString(key: string, fallback: string): string {
  return useSyncExternalStore(subscribe, () => readStored(key) ?? fallback, () => fallback);
}
