"use client";

// Visit, time 2 « Le lundi suivant » (brief « à distance », 4.2): « vous ne recommencez pas à zéro ». On the left, the
// decisions of the first Monday (his, or the prepared examples, marked as such), each one can be changed; on the right
// (one gesture), the following Monday by the same rule: a lead set aside does not come back, a lead to look at again
// comes back on its date, a kept lead comes back with its next action, the next of the ranking takes a freed place,
// and the new publications are added (none is invented after the end of the demonstration's data).
import { motion } from "motion/react";
import { CARNET_COPY, type CarnetEntry } from "@/lib/carnet";
import { fmtDate } from "@/lib/dates";
import { longDay } from "@/futur/display";
import { T } from "@/presentation/motion";
import type { TenRow } from "./Carnet";
import { VISIT_COPY } from "./copy";
import { nextMonday, type NextData } from "./next";
import type { VisitAction } from "./state";

const plusDays = (iso: string, days: number) => new Date(Date.parse(`${iso}T00:00:00Z`) + days * 86_400_000).toISOString().slice(0, 10);

/** The value of the compact choice of a row: a decision, or « revoir » with its date. */
const key = (e: CarnetEntry | undefined) => (e ? (e.decision === "revoir" ? `revoir:${e.revoir}` : e.decision) : "");

export function SuivantScene({ data, rows, names, carnet, examples, lang, reveal, dispatch }: {
  data: NextData; rows: TenRow[]; names: Record<string, string>; carnet: Record<string, CarnetEntry>;
  examples: Set<string>; lang: "fr" | "de"; reveal: number; dispatch: (a: VisitAction) => void;
}) {
  const t = VISIT_COPY[lang].suivant;
  const c = CARNET_COPY[lang];
  const m = nextMonday(data, rows.map((r) => r.id), carnet);
  const name = (id: string) => names[id] ?? data.classement.find((x) => x.id === id)?.nom ?? id;
  const options: [string, string][] = [
    ["appeler", c.decisions.appeler], ["verifier", c.decisions.verifier],
    [`revoir:${data.lundi}`, c.revoirOn.replace("{date}", fmtDate(data.lundi))],
    [`revoir:${plusDays(data.lundi, 14)}`, c.revoirOn.replace("{date}", fmtDate(plusDays(data.lundi, 14)))],
    ["ecarter", c.decisions.ecarter],
  ];
  const choose = (id: string, value: string) => {
    const entry: CarnetEntry | null = value.startsWith("revoir:") ? { decision: "revoir", revoir: value.slice(7) }
      : value === "ecarter" ? { decision: "ecarter", motif: carnet[id]?.motif ?? "autre" }
      : value === "appeler" || value === "verifier" ? { decision: value, confie: carnet[id]?.confie } : null;
    dispatch({ type: "decide", company: id, entry });
  };
  const decided = [...rows.map((r) => r.id), ...Object.keys(carnet).filter((id) => !rows.some((r) => r.id === id))];
  // the light goes from « Revoir le… » on the first Monday to « À revoir aujourd'hui » on the next one (no line)
  const revoirId = decided.find((id) => carnet[id]?.decision === "revoir");
  return (
    <div className="v-suivant" data-testid="suivant">
      <section className="v-week" aria-labelledby="v-first">
        <h2 id="v-first" className="d-small d-muted">{t.first.replace("{date}", longDay(data.premier, lang))}</h2>
        <ol className="v-firsts">
          {decided.map((id) => (
            <li key={id} data-testid="first-row" data-lumiere={id === revoirId ? "revoir" : undefined}>
              <span className="v-nom">{name(id)}</span>
              <span className="v-choice-cell">
                <label className="v-choice d-small">
                  <span className="sr-only">{t.change.replace("{name}", name(id))}</span>
                  <select value={key(carnet[id])} onChange={(e) => choose(id, e.target.value)}>
                    {carnet[id] ? null : <option value="">{t.none}</option>}
                    {/* a date chosen at time 1 stays a choice of its own */}
                    {carnet[id]?.decision === "revoir" && !options.some(([v]) => v === key(carnet[id]))
                      ? <option value={key(carnet[id])}>{c.revoirOn.replace("{date}", fmtDate(carnet[id].revoir ?? ""))}</option> : null}
                    {options.map(([v, label]) => <option key={v} value={v}>{label}</option>)}
                  </select>
                </label>
                {examples.has(id) ? <span className="d-caps v-example">{VISIT_COPY[lang].example}</span> : null}
              </span>
            </li>
          ))}
        </ol>
      </section>
      {reveal >= 1 ? (
        <motion.section className="v-week v-next" aria-labelledby="v-next" data-testid="next-monday" initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }} transition={T.medium}>
          <h2 id="v-next" className="d-lead"><span className="d-copper">{t.next.replace("{date}", longDay(data.lundi, lang))}</span></h2>
          <ol className="v-calls">
            {m.calls.map((r, i) => (
              <li key={r.id} data-kind={r.kind} data-testid="next-row"
                data-lumiere={r.kind === "recall" && r.id === m.calls.find((x) => x.kind === "recall")?.id ? "rappel" : undefined}>
                {r.kind === "recall" && r.entry?.revoir ? (
                  <span className="px-tag px-onglet" data-or aria-hidden>{c.revoirOn.replace("{date}", fmtDate(r.entry.revoir))}</span>
                ) : null}
                <span className="d-num d-muted">{i + 1}</span>
                <span className="v-next-line">
                  <span className="v-nom">{name(r.id)}</span>
                  {r.kind === "recall" ? <span className="px-statut" data-or>{t.recall}</span> : null}
                  {r.kind === "kept" && r.entry ? <span className="px-statut" data-or>{t.kept.replace("{decision}", c.decisions[r.entry.decision])}</span> : null}
                  {r.kind === "new" ? <span className="px-statut">{t.newIn}</span> : null}
                </span>
              </li>
            ))}
          </ol>
          {m.waiting.map((w) => <p key={w.id} className="d-small">{t.waiting.replace("{name}", name(w.id)).replace("{date}", fmtDate(w.date))}</p>)}
          {m.setAside.map((id) => <p key={id} className="d-small d-muted" data-testid="next-set-aside">{t.setAside.replace("{name}", name(id))}</p>)}
          <p className="d-small d-muted">
            {data.nouvelles_publications.length
              ? t.publications.replace("{date}", fmtDate(data.premier)).replace("{n}", String(data.nouvelles_publications.length))
              : t.noPublications.replace("{date}", fmtDate(data.premier)).replace("{end}", fmtDate(data.fin_des_donnees))}
          </p>
          <p className="d-small d-muted">{t.noResult}</p>
        </motion.section>
      ) : (
        <div className="v-consultant-wait d-small d-muted">{t.wait}</div>
      )}
      {reveal >= 1 ? <motion.p className="d-lead v-closing" data-revealed {...{ initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { ...T.medium, delay: 0.4 } }}>{t.closing}</motion.p> : null}
    </div>
  );
}
