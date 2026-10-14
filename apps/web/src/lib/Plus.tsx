"use client";

import "./plus.css";
import { useId, useState, type ReactNode } from "react";

/**
 * « En savoir plus » (« Mehr erfahren »), suite 9, § 10: on a phone, a dense screen keeps one idea in view; the detail
 * (the elements marked `px-plus-detail` inside, and those only) stays folded until a touch opens it. On a tablet, on a
 * computer and on paper the detail is shown as before and the button is not there (plus.css). Nothing leaves the page:
 * the figures, the sources and the mentions of the detail stay in it. A real button (aria-expanded, aria-controls), at
 * least 44 × 44 px; `about` names what it opens for a screen reader when the same label is repeated on a page.
 */
export function Plus({ label, about, children }: { label: string; about?: string; children: ReactNode }) {
  const id = useId();
  const [open, setOpen] = useState(false);
  return (
    <div className="px-plus" data-ouvert={open ? "" : undefined}>
      <div id={id} className="px-plus-zone">{children}</div>
      <button type="button" className="px-plus-btn" aria-expanded={open} aria-controls={id} data-testid="plus"
        onClick={() => setOpen((o) => !o)}>
        <span className="px-plus-label">{label}</span>{about ? <span className="sr-only"> · {about}</span> : null}
      </button>
    </div>
  );
}
