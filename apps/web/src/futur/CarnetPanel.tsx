"use client";

import { useMemo } from "react";
import { CARNET_COPY, DECISIONS, MOTIFS, OUTCOMES, USEFUL, type CarnetDecision, type Outcome } from "@/lib/carnet";
import { CARNET_KEY, carnet, lastNote, parseBook, readBook, saveBook, TRIAL_KEY } from "@/lib/carnetStore";
import { fmtDate } from "@/lib/dates";
import { fmtStamp, type Lang } from "@/lib/i18n";
import { useStoredString, writeStored } from "@/lib/useStored";

const plusDays = (iso: string, days: number) => new Date(Date.parse(`${iso}T00:00:00Z`) + days * 86_400_000).toISOString().slice(0, 10);

/**
 * The carnet of one company (brief « à distance », § 6), where the consultant comes back after calling: the decision on
 * the Monday list (one vocabulary with the visit; « Écarter » with a closed reason, « Revoir le… » with a date), then
 * what followed the call, each one dated and kept apart from the published facts, and in the trial week the preparation
 * time. No free text; kept on this device only.
 */
export function CarnetPanel({ entreprise, monday, lang }: { entreprise: string; monday: string; lang: Lang }) {
  const t = CARNET_COPY[lang];
  const raw = useStoredString(CARNET_KEY, "{}");
  const trial = useStoredString(TRIAL_KEY, "off") === "on";
  const r = useMemo(() => parseBook(raw)[entreprise], [raw, entreprise]);
  const e = r?.decision;
  const last = lastNote(r);
  const decide = (decision: CarnetDecision) => saveBook(carnet.decide(readBook(), entreprise, {
    decision,
    ...(decision === "revoir" ? { revoir: e?.revoir ?? plusDays(monday, 7) } : {}),
    ...(decision === "ecarter" ? { motif: e?.motif ?? "autre" } : { confie: e?.confie }),
  }));
  // a call back is noted a week later by default; its date is set just after, on the same line
  const note = (outcome: Outcome) =>
    saveBook(carnet.note(readBook(), entreprise, outcome, new Date().toISOString(), outcome === "rappel" ? plusDays(monday, 7) : undefined));
  return (
    <section aria-labelledby={`cn-${entreprise}`} data-testid="carnet-panel" className="fx-card p-5 sm:p-6">
      <h2 id={`cn-${entreprise}`} className="fx-caps fx-muted">{t.panel}</h2>
      <p className="mt-3 text-[15px]">{t.decisionTitle}</p>
      <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label={t.decisionTitle}>
        {DECISIONS.map((k) => (
          <button key={k} type="button" className="fx-choice" aria-pressed={e?.decision === k} onClick={() => decide(k)}
            data-testid={`carnet-${k}`}>
            {k === "revoir" && e?.decision === "revoir" && e.revoir ? t.revoirOn.replace("{date}", fmtDate(e.revoir)) : t.decisions[k]}
          </button>
        ))}
      </div>
      {e?.decision === "revoir" ? (
        <label className="mt-3 block text-[14px]">
          <span className="fx-muted block">{t.dateLabel}</span>
          <input type="date" className="fx-input mt-1" value={e.revoir} min={plusDays(monday, 1)}
            onChange={(ev) => ev.target.value && saveBook(carnet.decide(readBook(), entreprise, { ...e, revoir: ev.target.value }))} />
        </label>
      ) : null}
      {e?.decision === "ecarter" ? (
        <div className="mt-3 flex flex-wrap items-center gap-2" role="group" aria-label={t.motifLabel}>
          <span className="fx-muted text-[14px]">{t.motifLabel}</span>
          {MOTIFS.map((m) => (
            <button key={m} type="button" className="fx-choice" aria-pressed={e.motif === m}
              onClick={() => saveBook(carnet.decide(readBook(), entreprise, { ...e, motif: m }))}>{t.motifs[m]}</button>
          ))}
        </div>
      ) : null}

      <p className="mt-5 text-[15px]">{t.afterCall}</p>
      <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label={t.afterCall}>
        {/* the last outcome shows as chosen; touching it again the same day does not count a second call */}
        {OUTCOMES.map((o) => (
          <button key={o} type="button" className="fx-choice" aria-pressed={last?.outcome === o} onClick={() => note(o)}
            data-testid={`suite-${o}`}>{t.outcomes[o]}</button>
        ))}
      </div>
      {last?.outcome === "rappel" ? (
        <label className="mt-3 block text-[14px]">
          <span className="fx-muted block">{t.rappelDate}</span>
          <input type="date" className="fx-input mt-1" value={last.rappel ?? plusDays(monday, 7)} min={plusDays(monday, 1)}
            data-testid="rappel-date"
            onChange={(ev) => ev.target.value && saveBook(carnet.retime(readBook(), entreprise, ev.target.value))} />
        </label>
      ) : null}
      {last ? (
        <button type="button" className="fx-tool fx-tool-plain mt-2" onClick={() => saveBook(carnet.undo(readBook(), entreprise))}
          data-testid="suite-undo">{t.undo}</button>
      ) : null}
      <p className="fx-muted mt-2 text-[13px]">{t.useful}</p>

      {trial ? (
        <label className="mt-4 block text-[14px]">
          <span className="block">{t.trial.prep}</span>
          <input inputMode="numeric" className="fx-input mt-1 w-28" data-testid="carnet-prep" defaultValue={r?.preparationMinutes ?? ""}
            onChange={(ev) => {
              const v = ev.target.value.trim() === "" ? null : Number(ev.target.value);
              if (v === null || (Number.isFinite(v) && v >= 0 && v <= 600)) saveBook(carnet.prepare(readBook(), entreprise, v));
            }} />
        </label>
      ) : null}

      {/* the returns from the field: dated, set apart from the published facts (a ruled box, never on paper) */}
      {r?.suites.length ? (
        <div className="fx-field-notes mt-5" data-testid="field-notes">
          <p className="fx-caps fx-muted">{t.fieldNotes}</p>
          <ul className="mt-2 space-y-1 text-[14px]">
            {[...r.suites].reverse().map((n) => (
              <li key={n.le + n.outcome}>
                <span className={USEFUL.includes(n.outcome) ? "" : "fx-muted"}>
                  {n.outcome === "rappel" && n.rappel ? t.rappelOn.replace("{date}", fmtDate(n.rappel)) : t.outcomes[n.outcome]}
                </span>
                <span className="fx-muted"> · {t.notedOn.replace("{date}", fmtStamp(n.le, lang))}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <p className="fx-muted mt-4 text-[13px]" role="status" aria-live="polite">{t.deviceOnly} {t.noFreeText}</p>
    </section>
  );
}

/**
 * The trial week (semaine témoin) on « Ma semaine »: switch the trial mode on, see how many companies are noted, and
 * export the carnet as one file (company ids and choices only), kept on the device, never in the repository or the site.
 */
export function TrialBar({ lang, week, consultant, ranked }: { lang: Lang; week: string; consultant: string; ranked: string[] }) {
  const t = CARNET_COPY[lang];
  const trial = useStoredString(TRIAL_KEY, "off") === "on";
  const book = parseBook(useStoredString(CARNET_KEY, "{}"));
  const noted = ranked.filter((id) => book[id]?.decision || book[id]?.suites.length).length;
  // storage refused: the trial mode is kept in memory for this visit
  const toggle = () => writeStored(TRIAL_KEY, trial ? "off" : "on");
  const download = async () => {
    const { trialExport } = await import("@/lib/carnetStore");
    const blob = new Blob([JSON.stringify(trialExport(readBook(), week, consultant, ranked), null, 1)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `proxsis-essai-${consultant}-${week}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <section className="mt-6 flex flex-wrap items-center gap-3" aria-label={t.trial.title} data-testid="trial-bar">
      <button type="button" className="fx-choice" aria-pressed={trial} onClick={toggle}>{trial ? t.trial.on : t.trial.off}</button>
      {trial ? (
        <>
          <span className="fx-muted text-[14px]">{t.trial.count.replace("{n}", String(noted))}</span>
          <button type="button" className="fx-tool fx-tool-plain" onClick={download} data-testid="trial-export">{t.trial.export}</button>
          <p className="fx-muted basis-full text-[13px]">{t.useful} {t.trial.exportNote}</p>
        </>
      ) : null}
    </section>
  );
}

/** The agency page: how many companies the carnet of this device holds, and the same one-file export (ids only). */
export function CarnetCount({ lang, week }: { lang: Lang; week: string }) {
  const t = CARNET_COPY[lang];
  const book = parseBook(useStoredString(CARNET_KEY, "{}"));
  const ids = Object.keys(book).sort();
  const download = async () => {
    const { trialExport } = await import("@/lib/carnetStore");
    const blob = new Blob([JSON.stringify(trialExport(readBook(), week, "agence", ids), null, 1)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `proxsis-carnet-${week}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <p className="text-sm" data-testid="carnet-count">
      {t.trial.count.replace("{n}", String(ids.length))}{" "}
      {ids.length ? <button type="button" onClick={download} className="fx-tool fx-tool-plain ml-2">{t.trial.export}</button> : null}
      <span className="block text-[13px]">{t.deviceOnly}</span>
    </p>
  );
}
