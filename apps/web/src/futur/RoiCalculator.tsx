"use client";

import { useState } from "react";
import { groupDigits } from "@/lib/digits";
import { parseAmount, SEUIL_COPY, SEUIL_EXAMPLE, SEUIL_FIELDS, seuil, WEEKS_MAX, type SeuilField, type SeuilInput } from "@/lib/seuil";

/**
 * « Retour sur investissement » is the threshold of the visit (brief « à distance », 4.4), with the same calculation,
 * the same texts and the same example values (src/lib/seuil.ts): the number of additional billed days that covers the
 * cost over a period, then the result according to the assumptions; « Deux fois moins » halves the days, not the cost;
 * a loss stays on screen; the time saved stays apart. Nothing here is measured; the start values are examples.
 */
export function RoiCalculator({ lang, tags }: { lang: "fr" | "de"; tags: { hypothesis: string; example: string } }) {
  const t = SEUIL_COPY[lang];
  const [x, setX] = useState<SeuilInput>(SEUIL_EXAMPLE);
  const [half, setHalf] = useState(false);
  const [drafts, setDrafts] = useState<Partial<Record<SeuilField, string>>>({});
  const r = seuil(x, half);
  const nf = (n: number) => groupDigits(n, 0, lang === "de" ? "de-CH" : "fr-CH");
  const fields: { key: SeuilField; max: number; whole?: boolean }[] = [{ key: "weeks", max: WEEKS_MAX, whole: true }, ...SEUIL_FIELDS];
  const invalid = fields.some((f) => drafts[f.key] !== undefined && parseAmount(drafts[f.key]!, f.max, f.whole) === null);
  const n = r.breakEvenDays;
  const main = n === null ? t.noMargin : n === 0 ? t.resultNone : n === 1 ? t.resultOne : t.result.replace("{n}", nf(n));
  const sign = r.net < 0 ? t.loss : r.net === 0 ? t.zero : t.gain;
  const changed = fields.some((f) => x[f.key] !== SEUIL_EXAMPLE[f.key]) || half;
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)] lg:items-start">
      <section className="fx-card p-5 sm:p-6" aria-labelledby="fx-roi-in">
        <h2 id="fx-roi-in" className="fx-caps fx-muted flex flex-wrap items-center gap-3">
          {t.period.replace("{weeks}", nf(x.weeks))} <span className="fx-tag" data-kind="hypothese">{tags.hypothesis}</span>
        </h2>
        <p className="fx-muted mt-2 text-[13px]">{t.examples}</p>
        <div className="mt-4 grid gap-4">
          {fields.map((f) => {
            const bad = drafts[f.key] !== undefined && parseAmount(drafts[f.key]!, f.max, f.whole) === null;
            const copy = f.key === "weeks" ? { label: t.periodLabel, hint: "" } : t.fields[f.key as Exclude<SeuilField, "weeks">];
            return (
              <label key={f.key} className="block">
                <span className="block text-[15px] leading-snug">
                  {copy.label}{x[f.key] === SEUIL_EXAMPLE[f.key] ? <span className="fx-muted"> · {t.example}</span> : null}
                </span>
                {copy.hint ? <span className="fx-muted block text-[13px] leading-snug">{copy.hint}</span> : null}
                <input inputMode={f.whole ? "numeric" : "decimal"} value={drafts[f.key] ?? nf(x[f.key])} aria-invalid={bad}
                  onChange={(e) => {
                    const raw = e.target.value;
                    setDrafts((d) => ({ ...d, [f.key]: raw }));
                    const v = parseAmount(raw, f.max, f.whole);
                    if (v !== null && !(f.key === "weeks" && v < 1)) setX((old) => ({ ...old, [f.key]: v }));
                  }}
                  onBlur={() => setDrafts((d) => ({ ...d, [f.key]: undefined }))}
                  className="fx-input mt-1" data-testid={`roi-${f.key}`} />
              </label>
            );
          })}
        </div>
        <p className="mt-3 text-[14px]" role="status" aria-live="polite">{invalid ? t.invalid : ""}</p>
      </section>

      <section className="fx-raised p-5 sm:p-6" aria-labelledby="fx-roi-out">
        <h2 id="fx-roi-out" className="fx-display text-[26px] leading-tight sm:text-[32px]" data-testid="roi-main" aria-live="polite">{main}</h2>
        <p className="fx-muted mt-2 text-[14px]">
          {t.period.replace("{weeks}", nf(x.weeks))}{n ? ` · ${t.perWeek.replace("{n}", nf(Math.ceil(n / x.weeks)))}` : ""}
        </p>
        <p className="mt-2 text-[15px]">{t.costLine.replace("{cost}", nf(r.cost)).replace("{service}", nf(x.serviceCost)).replace("{team}", nf(r.teamCost))}</p>
        <div className="mt-5 border-t border-[var(--fx-line)] pt-4">
          <p className="fx-caps fx-muted">{t.according}</p>
          <p className="mt-2 flex flex-wrap items-baseline gap-x-3" aria-live="polite">
            <span className="fx-display fx-num text-[36px] leading-none" data-testid="roi-net" data-negative={r.negative}>
              {t.net.replace("{net}", nf(r.net)).replace("{weeks}", nf(x.weeks))}
            </span>
            <span className="text-[16px]">· {sign}</span>
          </p>
          {r.negative ? <p className="mt-2 text-[15px]">{t.lossStays}</p> : null}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button type="button" className="fx-choice" aria-pressed={half} onClick={() => setHalf((h) => !h)}>{half ? t.halfOff : t.half}</button>
            {half ? <span className="fx-muted text-[14px]">{t.halfOn}</span> : null}
          </div>
          <p className="fx-muted mt-4 text-[14px]">{t.saved.replace("{h}", nf(x.savedHours))}</p>
        </div>
        <p className="fx-muted mt-4 text-[13px] leading-relaxed">{t.rules}</p>
        {changed ? (
          <button type="button" className="fx-quiet mt-2" onClick={() => { setDrafts({}); setX(SEUIL_EXAMPLE); setHalf(false); }}>{t.reset}</button>
        ) : null}
      </section>
    </div>
  );
}
