"use client";

// Visit, time 5 « Une décision » (brief « à distance », 4.5 and § 11): the pilot in one sentence (the narration), then
// « Nous continuerons si… »: he picks an indicator and proposes a threshold, with a prepared example (the days of his
// threshold at time 4). A proposal to formalise, not a contract. The pilot's frame in a few lines: one main comparison,
// companies drawn by lot in each agency, the simple rule selects, no wait for the 12-month history, orders followed
// beyond six weeks, an exploratory result if the volume is low, everything fixed before the start.
import { useState } from "react";
import { parseAmount } from "@/lib/seuil";
import { PButton } from "@/presentation/ui";
import { VISIT_COPY } from "./copy";
import { EXAMPLE_THRESHOLD, INDICATORS, MAX, pilotSentence, type Indicator } from "./pilot";
import type { PilotChoice, VisitAction } from "./state";

export function PiloteScene({ lang, value, example, dispatch }: {
  lang: "fr" | "de"; value: PilotChoice | null; example: PilotChoice; dispatch: (a: VisitAction) => void;
}) {
  const t = VISIT_COPY[lang].pilote;
  const p = value ?? example;
  const ind = (INDICATORS as readonly string[]).includes(p.indicator) ? (p.indicator as Indicator) : "journees";
  const set = (next: PilotChoice) => dispatch({ type: "pilot", value: next });
  const [draft, setDraft] = useState<string | null>(null); // what is being typed, until it is a valid whole number
  return (
    <div className="v-pilote" data-testid="pilote">
      <section className="v-condition" aria-labelledby="v-condition">
        <h2 id="v-condition" className="d-sub">{t.lead}</h2>
        <div className="d-options v-indicators" role="group" aria-label={t.choose}>
          {INDICATORS.map((k) => (
            <PButton key={k} variant="option" aria-pressed={ind === k}
              onClick={() => set({ indicator: k, threshold: k === ind ? p.threshold : k === "journees" ? example.threshold : EXAMPLE_THRESHOLD[k] })}>
              <span>{t.indicators[k].label}</span>
            </PButton>
          ))}
        </div>
        <label className="d-field v-threshold">
          <span>{t.indicators[ind].thresholdLabel}{value ? null : <span className="d-caps v-example"> · {VISIT_COPY[lang].example}</span>}</span>
          <input inputMode="numeric" value={draft ?? String(p.threshold)} data-testid="pilot-threshold"
            aria-invalid={draft !== null && parseAmount(draft, MAX[ind], true) === null ? true : undefined}
            onChange={(e) => {
              setDraft(e.target.value);
              const v = parseAmount(e.target.value, MAX[ind], true);
              if (v !== null) set({ indicator: ind, threshold: v });
            }}
            onBlur={() => setDraft(null)} />
        </label>
        <p className="d-lead v-sentence" data-testid="pilot-sentence" aria-live="polite">{pilotSentence(p, lang)}</p>
        <p className="d-small d-muted">{t.formalize}</p>
      </section>
      <section className="v-frame" aria-labelledby="v-frame">
        <h2 id="v-frame" className="d-small d-muted">{t.frameTitle}</h2>
        <ul className="v-list">{t.frame.map((line) => <li key={line} className="d-small">{line}</li>)}</ul>
      </section>
    </div>
  );
}
