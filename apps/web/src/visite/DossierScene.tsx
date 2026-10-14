"use client";

// Visit, time 1: the map becomes the dossier (brief « à distance », 4.1). The publication on ivory paper with its
// source and its date, a published fact kept apart from our reading (simap's general terms, ch. 5); then (one gesture)
// what it lets one consider (an estimate, to confirm), what remains to verify, and the question to open the call. In
// German, no call sentence is presented as ready until a German speaker has read it: the published fact, in its
// original language, and the mention of the review (§ 9).
import { motion } from "motion/react";
import { ArrowUpRight } from "lucide-react";
import { CorrectionNote } from "@/futur/CorrectionNote";
import { fmtDate } from "@/lib/dates";
import { swissAmount } from "@/lib/amount";
import { T } from "@/presentation/motion";
import { COPY } from "@/presentation/copy";
import { SimapLine } from "@/presentation/Frame";
import { PButton } from "@/presentation/ui";
import { VISIT_COPY } from "./copy";
import type { VisitDossier } from "./dossier";
import type { VisitAction } from "./state";
import { HAUT_VALAIS } from "./valais";
import type { Proposer } from "./proposer";
import { QuiProposer } from "./QuiProposer";
import type { GuidedFacts } from "./moments";
import { FaitsConcordants } from "./NouveauxMoments";

const appear = (k = 0) => ({ initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, transition: { ...T.medium, delay: k * 0.12 } });

export function DossierScene({ d, lang, example, reveal, dispatch, hautValais, who, facts, factSources }: {
  d: VisitDossier; lang: "fr" | "de"; example: boolean; reveal: number; dispatch: (a: VisitAction) => void;
  hautValais: VisitDossier | null; // the example of the Upper Valais, when another dossier is open
  who: Proposer | null; // « Qui proposer ? », beside the reason to call (suite 2, § 4)
  facts: GuidedFacts["dossiers"][string] | null; // the published facts that go the same way (§ 3.2), guided dossiers only
  factSources: GuidedFacts["sources"];
}) {
  const t = VISIT_COPY[lang].dossier;
  const p = d.publication;
  return (
    <div className="v-dossier" data-testid="dossier" data-company={d.id}>
      <div className="v-dossier-head">
        <h2 className="d-company">
          {d.nom}
          <span className="block">
            {d.ville} · {t.real}{d.guide ? ` · ${t.toValidate}` : ""}
            {example ? <span className="d-caps v-example"> · {VISIT_COPY[lang].example}</span> : null}
          </span>
        </h2>
        <button className="v-link d-small" onClick={() => dispatch({ type: "temps", temps: 1 })}>{t.backToMap}</button>
      </div>
      <div className="v-dossier-grid">
        {/* what simap published, on paper, with its mention (never taken for an official publication); our count and
            our reading stay off the paper */}
        <div className="v-published">
        <article className="d-paper v-paper" data-testid="publication" data-lumiere="papier">
          <span className="px-tag px-onglet" aria-hidden>{t.publicationTab.replace("{date}", fmtDate(p.date))}</span>
          {lang === "fr" && d.id === HAUT_VALAIS.entreprise ? <p className="d-small v-original" data-testid="original-de">{t.originalDe}</p> : null}
          <header className="d-paper-head">
            <span>{t.award} · {t.published.replace("{date}", fmtDate(p.date))}</span>
            <span>simap.ch</span>
          </header>
          <p className="d-paper-title">« {p.titre} »</p>
          {p.adjudicateur ? <p className="d-paper-meta">{t.by.replace("{who}", p.adjudicateur)}</p> : null}
          {p.montant ? <p className="d-paper-meta">{t.amount.replace("{chf}", swissAmount(p.montant))}</p> : null}
          <PButton variant="paper" onClick={() => dispatch({ type: "openSource", url: p.url })}>{t.source} <ArrowUpRight aria-hidden /></PButton>
          <CorrectionNote url={p.url} lang={lang} />
          <p className="d-paper-mention" data-testid="paper-mention"><SimapLine t={COPY[lang]} lang={lang} /></p>
        </article>
        {facts ? <FaitsConcordants f={facts} sources={factSources} paperUrl={p.url} lang={lang}
          onSource={(url) => dispatch({ type: "openSource", url })} /> : null}
        </div>
        <div className="v-reading" data-testid="reading">
          {facts ? null : <p className="d-small d-muted" data-testid="count">{t.count.replace("{n}", String(d.n52))}</p>}
          {who ? <QuiProposer who={who} lang={lang} story /> : null}
          {reveal >= 1 ? (
            <>
              {d.envisager ? (
                <motion.section {...appear(0)}>
                  <h3 className="d-small d-muted">{t.envisager}</h3>
                  <p className="d-lead">{d.envisager[lang]}</p>
                  <p className="d-small d-muted">{t.estimate}</p>
                </motion.section>
              ) : null}
              <motion.section {...appear(1)}>
                <h3 className="d-small d-muted">{t.verify}</h3>
                <ul className="v-list">{d.verifier[lang].map((v) => <li key={v}>{v}</li>)}</ul>
              </motion.section>
              <motion.section {...appear(2)} data-testid="question" data-revealed data-lumiere="question">
                <h3 className="d-small d-muted">{t.question}</h3>
                {lang === "fr" ? (
                  <>
                    <p className="d-lead v-question">« {d.question.fr} »</p>
                    <p className="d-small d-muted">{t.grounded}</p>
                  </>
                ) : (
                  <>
                    <p className="d-small" data-testid="question-review">{t.reviewDe}</p>
                    <p className="d-lead v-question">« {p.titre} » · {fmtDate(p.date)}</p>
                  </>
                )}
              </motion.section>
            </>
          ) : (
            <PButton variant="action" onClick={() => dispatch({ type: "reveal", n: 1 })}>{t.read}</PButton>
          )}
        </div>
      </div>
      {/* « Le Valais entier » (brief of 07.10.2026, § 3.5): the list reads French and German publications */}
      <p className="d-small v-valais" data-testid="valais">
        <span className="px-marque">{t.valais}</span>
        {hautValais ? (
          <> {t.valaisExample.replace("{name}", hautValais.nom).replace("{ville}", hautValais.ville ?? "")}{" "}
            <button className="v-link" onClick={() => { dispatch({ type: "commune", bfs: HAUT_VALAIS.commune }); dispatch({ type: "company", id: HAUT_VALAIS.entreprise }); }}>
              {t.valaisOpen}
            </button>
          </>
        ) : null}
      </p>
    </div>
  );
}
