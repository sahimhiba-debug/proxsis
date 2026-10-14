"use client";

import { useState } from "react";

/** Copies a prepared text; says « Copié » for a moment, and says so when the browser refuses (the text stays selectable). */
export function CopyButton({ text, label, done, failed, className = "rounded-md border px-2 py-1 text-xs font-medium hover:bg-muted" }: {
  text: string; label: string; done: string; failed: string; className?: string;
}) {
  const [state, setState] = useState<"idle" | "done" | "failed">("idle");
  return (
    <>
      <button
        type="button"
        className={className}
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(text);
            setState("done");
            setTimeout(() => setState("idle"), 1500);
          } catch {
            setState("failed");
          }
        }}
      >
        {state === "done" ? done : state === "failed" ? failed : label}
      </button>
      <span className="sr-only" role="status" aria-live="polite">{state === "done" ? done : state === "failed" ? failed : ""}</span>
    </>
  );
}
