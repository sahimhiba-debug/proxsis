"use client";

// The conclusion « Votre premier lundi » (brief « à distance », § 5): his choices, what he did not change marked
// « exemple préparé »; « Préparer un e-mail » (subject and text for the team, no attachment, no figure in francs unless
// he ticks « inclure mes hypothèses », « Copier le texte » when no mail client opens); « Si la solution vous intéresse », the
// future in three steps (Avenir); and, apart, what happens to what he typed (§ 8).
import Link from "next/link";
import { useState } from "react";
import { PButton } from "@/presentation/ui";
import { VISIT_COPY } from "./copy";
import { PAGES_COPY } from "./pages";
import { visitPath } from "./paths";
import { emailText, type SummaryRow } from "./summary";
import { Fort } from "./Fort";
import { Avenir } from "./Avenir";

export function ConclusionScene({ rows, lang }: { rows: SummaryRow[]; lang: "fr" | "de" }) {
  const t = VISIT_COPY[lang].conclusion;
  const v = VISIT_COPY[lang];
  const p = PAGES_COPY[lang];
  const [withHypotheses, setWithHypotheses] = useState(false);
  const [copied, setCopied] = useState(false);
  const mail = emailText(rows, lang, withHypotheses);
  const href = `mailto:?subject=${encodeURIComponent(mail.subject)}&body=${encodeURIComponent(mail.body)}`;
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(`${mail.subject}\n\n${mail.body}`);
      setCopied(true);
    } catch {
      setCopied(false); // the text stays shown below, to select by hand
    }
  };
  // nothing of his own yet: one « exemple préparé » for the whole summary, not one per line
  const allExample = rows.every((r) => r.example);
  return (
    <div className="v-conclusion" data-testid="conclusion">
      <div className="v-recap-block">
        {allExample ? <p className="d-caps v-example" data-testid="recap-all-example">{v.example}</p> : null}
        <dl className="v-recap">
          {rows.map((r) => (
            <div key={r.key} data-testid={`recap-${r.key}`} data-example={r.example || undefined}>
              <dt className="d-small d-muted">{r.label}{r.example && !allExample ? <span className="d-caps v-example"> · {v.example}</span> : null}</dt>
              <dd>{r.value}</dd>
            </div>
          ))}
        </dl>
      </div>
      <section className="v-share" aria-labelledby="v-share">
        <h2 id="v-share" className="sr-only">{t.email.button}</h2>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <Link className="d-action" href={visitPath(lang, "synthese")} target="_blank" data-testid="pdf-link">{t.pdf}</Link>
          {/* one copper action per screen: the summary; the e-mail is the second way to keep it */}
          <a className="v-link" href={href} data-testid="email-link">{t.email.button}</a>
          <PButton variant="quiet" onClick={copy}>{t.email.copy}</PButton>
          {copied ? <span className="d-small" role="status">{t.email.copied}</span> : null}
        </div>
        <label className="v-check d-small">
          <input type="checkbox" checked={withHypotheses} onChange={(e) => setWithHypotheses(e.target.checked)} />
          <span>{t.email.include}</span>
        </label>
        <details className="d-small d-muted">
          <summary>{t.email.show}</summary>
          <pre className="v-mail" data-testid="email-text">{`${mail.subject}\n\n${mail.body}`}</pre>
        </details>
      </section>
      <section className="v-yours" aria-labelledby="v-yours" data-testid="with-your-figures">
        <h2 id="v-yours" className="d-sub"><Fort text={t.yours.title} strong={t.yours.strong} /></h2>
        <p className="d-lead">{t.yours.text}</p>
      </section>
      <Avenir lang={lang} id="v-avenir-conclusion" />
      <nav className="v-more" aria-label={p.links.questions}>
        <Link className="v-link" href={visitPath(lang, "questions")}>{p.links.questions}</Link>
        <Link className="v-link" href={visitPath(lang, "equipe")}>{p.links.equipe}</Link>
        <Link className="v-link" href={visitPath(lang, "technique")}>{p.links.technique}</Link>
        <Link className="v-link" href={visitPath(lang, "direction")} data-testid="direction-link">{p.direction.link}</Link>
        <Link className="v-link" href={visitPath(lang, "feuille-de-route")} data-testid="feuille-link">{p.feuille.link}</Link>
        <Link className="v-link" href={`/${lang}/application/`}>{p.links.app}</Link>
      </nav>
      <section className="d-small d-muted v-privacy" data-testid="privacy-end">
        <p>{v.privacy.sent}</p>
        <p>{v.privacy.kept}</p>
        <p>{v.privacy.share}</p>
      </section>
    </div>
  );
}
