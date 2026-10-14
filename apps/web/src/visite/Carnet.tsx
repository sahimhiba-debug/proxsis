"use client";

// Visit, time 1: the director decides with the carnet (brief « à distance », 4.1 and § 6), with one vocabulary and no
// free text: « À appeler », « À vérifier », « Revoir le… » (a date), « Écarter » with a closed reason; then hands the
// lead to « Consultant bâtiment », a demonstration role, explicitly fictional. « Continuer » shows the consultant's view:
// beside the director's on a computer, full screen on a phone (no drawn phone). What he did not choose stays the
// prepared example, and says so. Nothing is ever sent by itself.
import { Check } from "lucide-react";
import { motion } from "motion/react";
import { useState } from "react";
import { longDay } from "@/futur/display";
import { CARNET_COPY, DECISIONS, MOTIFS, type CarnetDecision, type CarnetEntry } from "@/lib/carnet";
import { fmtDate } from "@/lib/dates";
import { T } from "@/presentation/motion";
import { PButton } from "@/presentation/ui";
import { consultantMonday, EXAMPLE_ENTRY } from "./consultant";
import { VISIT_COPY } from "./copy";
import type { VisitDossier } from "./dossier";
import type { Proposer } from "./proposer";
import { QuiProposer } from "./QuiProposer";
import type { VisitAction } from "./state";

export interface TenRow { id: string; nom: string; ville: string | null }

const nextDay = (iso: string, days: number) => new Date(Date.parse(`${iso}T00:00:00Z`) + days * 86_400_000).toISOString().slice(0, 10);

function ConsultantView({ ten, d, entry, monday, lang, who }: {
  ten: TenRow[]; d: VisitDossier; entry: CarnetEntry; monday: string; lang: "fr" | "de"; who: Proposer | null;
}) {
  const t = VISIT_COPY[lang].carnet;
  const c = CARNET_COPY[lang];
  const [open, setOpen] = useState(true); // on a phone: full screen, closed by the visitor
  const m = consultantMonday(ten.map((x) => x.id), d.id, entry, monday);
  const name = (id: string) => (id === d.id ? { nom: d.nom, ville: d.ville } : ten.find((x) => x.id === id) ?? { nom: id, ville: null });
  const row = (id: string, confided: boolean, rank: number) => (
    <li key={id} data-confided={confided || undefined} data-testid="consultant-row">
      <span className="d-num d-muted">{rank}</span>
      <span className="min-w-0">
        <span className="block">{name(id).nom}<span className="d-muted">{name(id).ville ? ` · ${name(id).ville}` : ""}</span></span>
        {confided ? (
          <span className="d-small block">
            <span className="d-copper">{t.confidedBy}</span>
            {lang === "fr" ? <span className="d-muted"> · « {d.question.fr} »</span> : <span className="d-muted"> · {t.factOnly.replace("{date}", fmtDate(d.publication.date))}</span>}
          </span>
        ) : null}
      </span>
    </li>
  );
  return (
    <motion.section className="v-consultant" data-open={open || undefined} data-testid="consultant" aria-labelledby="v-consultant-title" data-revealed
      initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} transition={T.medium}>
      <header className="v-consultant-head">
        <div>
          <h2 id="v-consultant-title" className="d-small d-muted">{t.consultant}</h2>
          <p className="d-caps">{c.role} · <span className="d-muted">{c.roleNote}</span></p>
          <p className="d-small d-muted">{longDay(monday, lang)}</p>
        </div>
        <button className="v-link d-small v-close" onClick={() => setOpen(false)}>{t.close}</button>
      </header>
      <h3 className="d-lead">{t.firstThree}</h3>
      <ol className="v-calls">{m.first.map((r, i) => row(r.id, r.confided, i + 1))}</ol>
      {m.later.map((l) => (
        <p key={l.id} className="d-small" data-testid="consultant-later"><span className="d-copper">{c.revoirOn.replace("{date}", fmtDate(l.date))}</span> · {name(l.id).nom}</p>
      ))}
      {m.setAside.length ? <p className="d-small d-muted" data-testid="consultant-set-aside">{t.setAside.replace("{name}", d.nom)}</p> : null}
      {/* « Qui proposer ? » (brief of 07.10.2026, § 3.1): three fictional temps, as the application proposes them */}
      {who && entry.decision !== "ecarter" ? <QuiProposer who={who} lang={lang} /> : null}
      <h3 className="d-small d-muted">{t.others}</h3>
      <ol className="v-calls v-others">{m.others.map((r, i) => row(r.id, r.confided, i + 4))}</ol>
      {/* on a phone, read to the end, the way back is there too (not only at the top) */}
      <button className="v-link d-small v-close" onClick={() => setOpen(false)}>{t.close}</button>
      <PButton variant="quiet" className="v-reopen" onClick={() => setOpen(true)}>{t.open}</PButton>
    </motion.section>
  );
}

export function CarnetScene({ d, ten, monday, lang, own, reveal, dispatch, who }: {
  d: VisitDossier; ten: TenRow[]; monday: string; lang: "fr" | "de"; own: CarnetEntry | undefined; reveal: number;
  dispatch: (a: VisitAction) => void; who: Proposer | null;
}) {
  const t = VISIT_COPY[lang].carnet;
  const c = CARNET_COPY[lang];
  const entry = own ?? EXAMPLE_ENTRY;
  const set = (e: CarnetEntry) => dispatch({ type: "decide", company: d.id, entry: e });
  const choose = (decision: CarnetDecision) => set({
    decision,
    ...(decision === "revoir" ? { revoir: entry.revoir ?? nextDay(monday, 7) } : {}),
    ...(decision === "ecarter" ? { motif: entry.motif ?? "autre" } : { confie: entry.confie }),
  });
  const handed = entry.confie === true && entry.decision !== "ecarter";
  return (
    <div className="v-carnet" data-testid="carnet" data-reveal={reveal}>
      <section className="v-desk" aria-labelledby="v-you">
        <h2 id="v-you" className="d-small d-muted">
          {t.you}{own ? null : <span className="d-caps v-example"> · {VISIT_COPY[lang].example}</span>}
        </h2>
        {/* the company card: kept (to call, to check, to see again), it gets the orange edge and the small diagonal */}
        <div className={`px-etiquette px-carte${entry.decision !== "ecarter" ? " px-choisi" : ""}`} data-testid="carnet-card">
          <p className="d-company">{d.nom}<span className="block">{d.ville} · {t.published.replace("{date}", fmtDate(d.publication.date))}</span></p>
          <span className="px-statut" data-or={entry.decision !== "ecarter" || undefined} aria-hidden>
            {entry.decision === "revoir" && entry.revoir ? c.revoirOn.replace("{date}", fmtDate(entry.revoir)) : c.decisions[entry.decision]}
          </span>
        </div>
        <div className="d-options v-decisions" role="group" aria-label={t.decide}>
          {DECISIONS.map((k) => (
            <PButton key={k} variant="option" aria-pressed={entry.decision === k} onClick={() => choose(k)} data-testid={`decide-${k}`}>
              <span>{k === "revoir" && entry.decision === "revoir" && entry.revoir ? c.revoirOn.replace("{date}", fmtDate(entry.revoir)) : c.decisions[k]}</span>
            </PButton>
          ))}
        </div>
        {entry.decision === "revoir" ? (
          <label className="d-field v-date-field">
            <span>{c.dateLabel}</span>
            <input type="date" value={entry.revoir} min={nextDay(monday, 1)}
              onChange={(e) => e.target.value && set({ ...entry, revoir: e.target.value })} />
          </label>
        ) : null}
        {entry.decision === "ecarter" ? (
          <div className="v-motifs" role="group" aria-label={c.motifLabel}>
            <p className="d-small d-muted">{c.motifLabel}</p>
            {MOTIFS.map((m) => (
              <PButton key={m} variant="option" aria-pressed={entry.motif === m} onClick={() => set({ ...entry, motif: m })}>{c.motifs[m]}</PButton>
            ))}
          </div>
        ) : (
          // once handed over, the action turns into a choice made (outlined, ticked): the same look as a chosen option
          <PButton variant="action" className="v-confide" aria-pressed={handed} onClick={() => set({ ...entry, confie: !handed })} data-testid="confide">
            {handed ? <Check aria-hidden /> : null}{(handed ? c.confided : c.confide).replace("{role}", c.role)}
          </PButton>
        )}
        {/* the fictional role is said once: here before the consultant's view, then in that view's head */}
        <p className="d-small d-muted">{reveal >= 1 ? c.noFreeText : `${c.roleNote} · ${c.noFreeText}`}</p>
        <p className="d-small">{t.noAuto}</p>
      </section>
      {reveal >= 1 ? (
        <ConsultantView key={`${d.id}-${reveal}`} ten={ten} d={d} entry={entry} monday={monday} lang={lang} who={who} />
      ) : (
        <div className="v-consultant-wait d-small d-muted">{t.wait}</div>
      )}
    </div>
  );
}
