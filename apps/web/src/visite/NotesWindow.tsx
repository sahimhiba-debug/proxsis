"use client";

import "@/presentation/direction.css";
import "./visite.css";
import "./identite.css";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { setPref } from "@/presentation/prefs";
import { PButton } from "@/presentation/ui";
import { useStoredString } from "@/lib/useStored";
import { GUIDE_COPY } from "./guide";
import { PREF_GUIDE } from "./GuideMascotte";
import { VISIT_COPY } from "./copy";
import { NOTE_ROWS, VISIT_NOTES } from "./notes";
import { VISIT_STEPS } from "./state";
import { useVisit } from "./useVisit";

// Presenter mode (brief « à distance », § 4): the same visit, in a separate window of the same browser, with what to say
// and do; moving here moves the shared screen, and the other way round (one visit kept on the device).
export function VisitNotes({ lang }: { lang: "fr" | "de" }) {
  const [s, dispatch] = useVisit();
  const t = VISIT_COPY[lang];
  const rows = NOTE_ROWS[lang];
  const step = VISIT_STEPS[s.step];
  const note = VISIT_NOTES[lang][step.id];
  const next = VISIT_STEPS[s.step + 1];
  const guideOn = useStoredString(PREF_GUIDE, "on") !== "off"; // the same setting as the shared screen (same device)
  return (
    <div className="dir" lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <header className="d-head">
        <h1 className="d-label">{rows.title} · {step.temps < 6 ? t.nav.of.replace("{n}", String(step.temps)) : t.temps[6]} · {t.temps[step.temps]}</h1>
        <p className="d-small d-muted">{VISIT_STEPS[s.step].gestures ? `${Math.min(s.reveal, step.gestures)} / ${step.gestures}` : ""}</p>
        <button type="button" className="d-tool" onClick={() => setPref(PREF_GUIDE, guideOn ? "off" : "on")} data-testid="notes-guide-toggle">
          {guideOn ? GUIDE_COPY[lang].hide : GUIDE_COPY[lang].show}
        </button>
      </header>
      <main className="d-main" tabIndex={0} aria-label={rows.title}>
        <p className="d-sub" data-testid="notes-narration">{t.narration[step.id]}</p>
        <dl className="mt-6 grid gap-4">
          {(["say", "gesture", "proof", "fallback"] as const).map((k) => (
            <div key={k} className="border-t border-[var(--trait)] pt-2">
              <dt className="d-caps d-muted">{rows[k]}</dt>
              <dd className={k === "say" ? "d-quote mt-1" : "d-lead mt-1"}>{note[k]}</dd>
            </div>
          ))}
        </dl>
        {next ? <p className="d-small d-muted mt-6">{rows.next} : {t.narration[next.id]}</p> : null}
      </main>
      <footer className="d-foot">
        <nav className="d-nav" aria-label={t.nav.move}>
          <PButton variant="nav" onClick={() => dispatch({ type: "prev" })}><ArrowLeft className="back" aria-hidden /> {t.nav.prev}</PButton>
          <span />
          <PButton variant="nav" className="justify-self-end" onClick={() => dispatch({ type: "next" })}>{t.nav.next} <ArrowRight className="fwd" aria-hidden /></PButton>
        </nav>
      </footer>
    </div>
  );
}
