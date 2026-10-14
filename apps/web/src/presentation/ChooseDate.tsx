"use client";

// Act 4, « Choisissez une date » (Hiba, 07.10.2026): the director picks a past date, brought back to its Monday; the
// ten companies the unchanged simple rule would have proposed that day, computed from publications published before it
// only (lundis.json, CLAIMS PRES-DATE-1); then (one gesture) what each obtained in the 8 following weeks, good and bad
// alike; then (one gesture) every Monday of the measure, ten companies at random and the closing sentence.
import { motion } from "motion/react";
import { ArrowUpRight } from "lucide-react";
import Link from "next/link";
import { useState, type FormEvent, type ReactNode } from "react";
import { fmtDate } from "@/lib/dates";
import type { PLang } from "./copy";
import { COPY_C } from "./copy_c";
import { pickMonday, type Monday, type MondayCompany, type MondaysData } from "./mondayData";
import { DUR, T } from "./motion";
import { PButton } from "./ui";

const fill = (text: string, values: Record<string, string | number>) =>
  text.replace(/\{(\w+)\}/g, (m, k: string) => (k in values ? String(values[k]) : m));
/** The same, with some values as elements (a figure set off inside its unchanged sentence). */
const fillNodes = (text: string, values: Record<string, ReactNode>): ReactNode[] =>
  text.split(/(\{\w+\})/).map((part, i) => {
    const k = /^\{(\w+)\}$/.exec(part)?.[1];
    return k && k in values ? <span key={i}>{values[k]}</span> : part;
  });
const appear = (delay = 0) => ({ initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, transition: { ...T.medium, delay } });

function Outcome({ c, h, lang, onSource }: { c: MondayCompany; h: number; lang: PLang; onSource: (url: string) => void }) {
  const y = COPY_C[lang].dir.date;
  const n = c.nouveau_marche;
  if (!n) return <span>— {fill(y.none, { h })}</span>;
  const text = n.nombre > 2 ? fill(y.wonMore, { date: fmtDate(n.date), n: n.nombre - 1 })
    : n.nombre === 2 ? fill(y.wonMoreOne, { date: fmtDate(n.date) }) : fill(y.won, { date: fmtDate(n.date) });
  return (
    <PButton variant="quiet" className="d-source-link d-date-won" title={n.titre ?? undefined}
      onClick={() => onSource(n.url)}>
      {text} <ArrowUpRight aria-hidden />
    </PButton>
  );
}

/** The first test the confession is about (CLAIMS REEL-T0, histoires.json): another scope than the measure shown. */
export interface FirstTest { semaines: number; regle: Record<PLang, string>; m0: Record<PLang, string> }

/** `monday`: his date (null: the prepared example); `head`: what sits above the title (the presentation's act line);
 *  `firstTest`: the scope of the confession, shown under it; `titleAs`: h2 where the page already has its h1 (the visit);
 *  `afterResult`: what follows the result over every Monday, before the confession (the visit: « celles qui accélèrent »);
 *  `morning`: what sits under the ten, for the Monday shown (the visit: « Chaque matin » of that Monday, suite 10, § 2). */
export function DateScene({ data, lang, monday: his, reveal, head, firstTest, titleAs: Title = "h1", afterResult, morning, onMonday, onReveal, onSource }: {
  data: MondaysData; lang: PLang; monday: string | null; reveal: number; head?: ReactNode; firstTest?: FirstTest; titleAs?: "h1" | "h2";
  afterResult?: ReactNode; morning?: (monday: Monday) => ReactNode;
  onMonday: (iso: string) => void; onReveal: (n: number) => void; onSource: (url: string) => void;
}) {
  const y = COPY_C[lang].dir.date;
  const r = data.regle;
  const w = Math.round(r.historique_jours / 7);
  const h = Math.round(r.horizon_jours / 7);
  // his date, or the prepared example (2 March 2026): the visit never waits for a date to be typed
  const chosen = his ? data.lundis.find((m) => m.lundi === his && m.choisissable) : undefined;
  const monday = chosen ?? data.lundis.find((m) => m.lundi === data.choix.exemple)!;
  const [typed, setTyped] = useState(monday.lundi);
  const [problem, setProblem] = useState<string | null>(null);
  const [snapped, setSnapped] = useState(false);
  const bounds = { first: fmtDate(data.choix.premier), last: fmtDate(data.choix.dernier), w, h };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const picked = pickMonday(data, typed);
    if (!picked) setProblem(y.invalid);
    else if ("outside" in picked) setProblem(fill(picked.outside === "avant" ? y.tooEarly : y.tooLate, bounds));
    else {
      setProblem(null);
      setSnapped(picked.monday.lundi !== typed);
      setTyped(picked.monday.lundi);
      onMonday(picked.monday.lundi);
    }
  };

  return (
    <div className="d-scene d-dense" data-testid="date-monday" data-monday={monday.lundi}>
      {head}
      <div className="d-date-head">
        <Title className="d-sub">
          {fill(y.title, { date: fmtDate(monday.lundi) })}
          {chosen ? null : <span className="d-caps d-muted d-date-example"> · {y.example}</span>}
        </Title>
        {/* the bounds guide the calendar; a date outside them is explained here, not refused silently by the browser */}
        <form className="d-date-form" onSubmit={submit} noValidate>
          <label className="d-field">
            <span>{y.choose}</span>
            <input type="date" value={typed} min={data.choix.premier} max={data.choix.dernier} required
              aria-invalid={problem ? true : undefined} aria-describedby="d-date-range"
              onChange={(e) => { setTyped(e.target.value); setProblem(null); }} />
          </label>
          <PButton variant="quiet" type="submit">{y.show}</PButton>
        </form>
      </div>
      {problem ? <p className="d-small d-copper" role="alert" data-testid="date-problem">{problem}</p> : null}
      {/* on a short screen, the rule (read at the first gestures) leaves its room to the closing sentence */}
      <p className="d-small d-muted d-date-rule" data-later={reveal >= 2 || undefined}>
        {snapped ? <>{y.snapped} </> : null}{fill(y.rule, { k: r.k, w })}{" "}
        <span id="d-date-range">{fill(y.range, bounds)}</span>
      </p>
      <ol className="d-date-list">
        {monday.dix.map((c) => (
          <li key={c.id} data-testid="date-company" data-won={reveal >= 1 ? Boolean(c.nouveau_marche) : undefined}>
            <span className="d-num d-muted">{c.rang}</span>
            <span className="min-w-0">
              <span className="block">{c.nom}{c.ville ? <span className="d-muted"> · {c.ville}</span> : null}</span>
              {/* what was known on the Monday, then (one gesture) what came in the 8 weeks, on the same line */}
              <span className="d-date-line d-small">
                <span className="d-muted">
                  {fill(y.awards, { n: c.marches_52s, w })}
                  {c.autre_inscription_de ? <> · {fill(y.branch, { n: c.autre_inscription_de })}</> : null}
                </span>
                {reveal >= 1 ? (
                  <motion.span className={c.nouveau_marche ? "" : "d-muted"} {...appear()}><Outcome c={c} h={h} lang={lang} onSource={onSource} /></motion.span>
                ) : null}
              </span>
            </span>
          </li>
        ))}
      </ol>
      {morning ? morning(monday) : null}
      {reveal >= 1 ? (
        <div className="d-date-result">
          <motion.p className="d-lead" data-testid="date-count" data-revealed data-lumiere="compte" {...appear(DUR.medium)}>
            {fill(y.count, { n: monday.obtenu, k: r.k, h })}
          </motion.p>
          {reveal >= 2 ? (
            <motion.p className="d-small d-date-all" data-testid="date-all" data-lumiere="mesure" {...appear()}>
              {/* the strongest evidence of the visit, set off inside its sentence (the words do not change) */}
              {fillNodes(y.mean, { n: data.mesure.semaines, from: fmtDate(data.mesure.premiere), to: fmtDate(data.mesure.derniere),
                p: <strong className="d-date-figure">{data.mesure.affiche.regle[lang]}</strong> })}{" "}
              {fillNodes(y.random, { k: r.k, p: <strong className="d-date-figure d-date-figure-low">{data.mesure.affiche.hasard[lang]}</strong> })}{" "}
              <Link className="d-muted underline underline-offset-4" href={`/${lang}/presentation/preuves/`} target="_blank">{y.proofs}</Link>
            </motion.p>
          ) : (
            <PButton variant="quiet" onClick={() => onReveal(2)}>{y.all}</PButton>
          )}
        </div>
      ) : (
        <PButton variant="action" onClick={() => onReveal(1)}>{fill(y.ask, { h })}</PButton>
      )}
      {reveal >= 2 && afterResult ? <motion.div {...appear(DUR.medium)}>{afterResult}</motion.div> : null}
      {/* the confession of the first test, word for word, then what a new contract is not */}
      {reveal >= 2 ? (
        <div className="d-date-end" data-revealed>
          <motion.p className="d-lead" data-testid="date-aveu" {...appear(DUR.medium)}>{y.aveu}</motion.p>
          {firstTest ? (
            <motion.p className="d-small d-muted d-date-scope" data-testid="date-aveu-scope" {...appear(DUR.medium)}>
              {fill(y.aveuScope, { weeks: firstTest.semaines, rule: firstTest.regle[lang], m0: firstTest.m0[lang] })}
            </motion.p>
          ) : null}
          <motion.p className="d-lead d-date-closing" {...appear(DUR.long)}>{y.closing}</motion.p>
        </div>
      ) : null}
    </div>
  );
}
