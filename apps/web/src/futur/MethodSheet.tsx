"use client";

import Link from "next/link";
import { X } from "lucide-react";
import { useRef } from "react";

/** « Comment cette liste est faite » : plain words in a sheet that rises from the bottom (native <dialog>: focus, Esc). */
export function MethodSheet({ label, title, body, measureHref, measureLabel, sources, mention, close }: {
  label: string; title: string; body: string[]; measureHref: string | null; measureLabel: string; sources: string;
  mention: string; close: string;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  return (
    <>
      <button type="button" className="fx-link inline-flex min-h-11 items-center text-[15px]" onClick={() => ref.current?.showModal()}
        aria-haspopup="dialog">
        {label}
      </button>
      <dialog ref={ref} className="fx-sheet" aria-labelledby="fx-how-title" onClick={(e) => { if (e.target === ref.current) ref.current?.close(); }}>
        <div className="max-h-[85dvh] overflow-y-auto px-6 pb-10 pt-3">
          <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-[var(--fx-line-strong)]" aria-hidden />
          <div className="flex items-start justify-between gap-4">
            <h2 id="fx-how-title" className="fx-display text-[26px]">{title}</h2>
            <button type="button" className="fx-tool shrink-0 !px-0" onClick={() => ref.current?.close()} aria-label={close} autoFocus>
              <X aria-hidden className="size-4" strokeWidth={1.5} />
            </button>
          </div>
          <div className="mt-4 space-y-3 text-[16px] leading-relaxed">
            {body.map((p) => <p key={p}>{p}</p>)}
          </div>
          {measureHref ? (
            <p className="mt-5"><Link className="fx-link" href={measureHref}>{measureLabel}</Link></p>
          ) : null}
          <p className="fx-muted mt-5 text-[14px]">{sources}</p>
          <p className="fx-muted mt-2 text-[13px]">{mention}</p>
        </div>
      </dialog>
    </>
  );
}
