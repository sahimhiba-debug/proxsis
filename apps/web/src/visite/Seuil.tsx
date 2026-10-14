"use client";

// Visit, time 4 « Un seuil » (brief « à distance », 4.4): the main result first, « Il suffit de N journées
// supplémentaires facturées pour couvrir le coût », over a period shown and editable; below it, the result according to
// the assumptions, « Deux fois moins », a loss that stays visible, the time saved kept apart. Every start value is an
// example and says so; one can go on without typing anything. Illustration: a fictional mission ends on Friday, a
// possible follow-up in dots, « À confirmer ». The same calculation as « Retour sur investissement » (src/lib/seuil.ts).
import { useState } from "react";
import { groupDigits } from "@/lib/digits";
import { parseAmount, SEUIL_COPY, SEUIL_EXAMPLE, SEUIL_FIELDS, seuil, WEEKS_MAX, type SeuilField, type SeuilInput } from "@/lib/seuil";
import { PButton } from "@/presentation/ui";
import type { VisitAction } from "./state";

function Calendar({ lang }: { lang: "fr" | "de" }) {
  const t = SEUIL_COPY[lang].calendar;
  return (
    <figure className="v-calendar" aria-label={t.title}>
      <figcaption className="d-small d-muted">{t.title}</figcaption>
      {/* two weeks side by side on a computer, one under the other on a phone (positions in visite.css) */}
      <div className="v-calendar-grid">
        {[0, 1].flatMap((w) => t.days.map((d, i) => (
          <span key={`${w}-${d}`} className="v-cal-day d-small d-muted" data-week={w} style={{ ["--day" as string]: i + 1 }}>{d}</span>
        )))}
        <span className="v-cal-mission d-small">{t.ends}</span>
        <span className="v-cal-free d-small d-muted">{t.free}</span>
        <span className="v-cal-next d-small">{t.next} · <b>{t.toConfirm}</b></span>
      </div>
    </figure>
  );
}

export function SeuilScene({ lang, value, half, dispatch }: {
  lang: "fr" | "de"; value: SeuilInput | null; half: boolean; dispatch: (a: VisitAction) => void;
}) {
  const t = SEUIL_COPY[lang];
  const x = value ?? SEUIL_EXAMPLE;
  const r = seuil(x, half);
  const [drafts, setDrafts] = useState<Partial<Record<SeuilField, string>>>({});
  const nf = (n: number) => groupDigits(n, 0, lang === "de" ? "de-CH" : "fr-CH");
  const fields: { key: SeuilField; max: number; whole?: boolean }[] = [{ key: "weeks", max: WEEKS_MAX, whole: true }, ...SEUIL_FIELDS];
  const bad = fields.some((f) => drafts[f.key] !== undefined && parseAmount(drafts[f.key]!, f.max, f.whole) === null);
  const set = (k: SeuilField, raw: string, max: number, whole?: boolean) => {
    setDrafts((d) => ({ ...d, [k]: raw }));
    const v = parseAmount(raw, max, whole);
    if (v !== null && !(k === "weeks" && v < 1)) dispatch({ type: "seuil", value: { ...x, [k]: v } });
  };
  const n = r.breakEvenDays;
  const main = n === null ? t.noMargin : n === 0 ? t.resultNone : n === 1 ? t.resultOne : t.result.replace("{n}", nf(n));
  const sign = r.net < 0 ? t.loss : r.net === 0 ? t.zero : t.gain;
  return (
    <div className="v-seuil" data-testid="seuil">
      <section className="v-seuil-result" aria-live="polite">
        <p className="v-seuil-main" data-testid="seuil-main" data-lumiere="seuil">{main}</p>
        <p className="d-small d-muted">
          {t.period.replace("{weeks}", nf(x.weeks))}
          {n ? ` · ${t.perWeek.replace("{n}", nf(Math.ceil(n / x.weeks)))}` : ""}
        </p>
        <p className="d-small">{t.costLine.replace("{cost}", nf(r.cost)).replace("{service}", nf(x.serviceCost)).replace("{team}", nf(r.teamCost))}</p>
        <div className="v-seuil-net">
          <p className="d-small d-muted">{t.according}</p>
          <p className="d-lead" data-testid="seuil-net" data-negative={r.negative}>
            {t.net.replace("{net}", nf(r.net)).replace("{weeks}", nf(x.weeks))} · {sign}
          </p>
          {r.negative ? <p className="d-small">{t.lossStays}</p> : null}
          <PButton variant="option" aria-pressed={half} onClick={() => dispatch({ type: "half", value: !half })} className="v-half">
            {half ? t.halfOff : t.half}
          </PButton>
          {half ? <p className="d-small d-muted">{t.halfOn}</p> : null}
          <p className="d-small d-muted">{t.saved.replace("{h}", nf(x.savedHours))}</p>
        </div>
        <p className="d-small d-muted">{t.rules}</p>
      </section>
      <section className="v-seuil-inputs" aria-label={t.according}>
        <p className="d-small d-muted">{t.examples}</p>
        {fields.map((f) => {
          const label = f.key === "weeks" ? t.periodLabel : t.fields[f.key as Exclude<SeuilField, "weeks">].label;
          const hint = f.key === "weeks" ? "" : t.fields[f.key as Exclude<SeuilField, "weeks">].hint;
          const invalid = drafts[f.key] !== undefined && parseAmount(drafts[f.key]!, f.max, f.whole) === null;
          return (
            <label key={f.key} className="d-field v-seuil-field">
              <span>
                {label}{x[f.key] === SEUIL_EXAMPLE[f.key] ? <span className="d-caps v-example"> · {t.example}</span> : null}
                {hint ? <span className="block d-muted">{hint}</span> : null}
              </span>
              <input inputMode={f.whole ? "numeric" : "decimal"} value={drafts[f.key] ?? nf(x[f.key])} aria-invalid={invalid || undefined}
                data-testid={`seuil-${f.key}`} onChange={(e) => set(f.key, e.target.value, f.max, f.whole)}
                onBlur={() => setDrafts((d) => ({ ...d, [f.key]: undefined }))} />
            </label>
          );
        })}
        <p className="d-small" role="status">{bad ? t.invalid : ""}</p>
        {value || half ? (
          <PButton variant="quiet" onClick={() => { setDrafts({}); dispatch({ type: "seuil", value: null }); dispatch({ type: "half", value: false }); }}>
            {t.reset}
          </PButton>
        ) : null}
      </section>
      <Calendar lang={lang} />
    </div>
  );
}
