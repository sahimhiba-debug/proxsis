"use client";

import "@/presentation/direction.css";
import "./visite.css";
import "./identite.css";
import Link from "next/link";
import { COPY } from "@/presentation/copy";
import { SimapLine } from "@/presentation/Frame";
import { PButton } from "@/presentation/ui";
import { VISIT_COPY } from "./copy";
import { visitPath } from "./paths";
import { summaryRows, type SummaryInputs } from "./summary";
import { useVisit } from "./useVisit";
import { PAGES_COPY } from "./pages";
import { VisitAddress } from "./VisitAddress";
import { Logo } from "@/lib/Logo";
import { Plus } from "@/lib/Plus";

// « Télécharger ma synthèse » (brief « à distance », § 5): one A4 page made in his browser, with no server and no added
// library: the visit's choices read on this device, what he did not change marked « exemple préparé », the three next
// steps and the mentions; « Enregistrer en PDF » opens the browser's print dialog (save as PDF), in French or German.
export function SyntheseVisite({ inputs }: { inputs: Omit<SummaryInputs, "s"> }) {
  const lang = inputs.lang;
  const t = VISIT_COPY[lang];
  const brand = COPY[lang].dir;
  const [s] = useVisit();
  const rows = summaryRows({ ...inputs, s });
  const allExample = rows.every((r) => r.example); // nothing of his own yet: one « exemple préparé », not one per line
  return (
    <div className="dir d-print" lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <main className="d-print-main v-synthese" data-testid="synthese">
        <header className="d-brand-block">
          <p className="d-brand"><Logo title={brand.name} /></p>
          <p className="d-small d-muted">{brand.signature}</p>
          <p className="d-proto">{brand.prototype}</p>
        </header>
        <h1 className="d-sub mt-[0.8em]">{t.narration.conclusion}</h1>
        {allExample ? <p className="d-caps v-example" data-testid="synthese-all-example">{t.example}</p> : null}
        <dl className="v-recap">
          {rows.map((r) => (
            <div key={r.key} data-example={r.example || undefined}>
              <dt className="d-small d-muted">{r.label}{r.example && !allExample ? ` · ${t.example}` : ""}</dt>
              <dd>{r.value}</dd>
            </div>
          ))}
        </dl>
        {/* on a phone (suite 9, § 10): his choices first; the three steps under « En savoir plus » (on paper, as before) */}
        <section data-testid="synthese-etapes">
          <h2 className="d-lead">{t.conclusion.next.title}</h2>
          <p className="px-bref">{t.avenir.lead}</p>
          <Plus label={PAGES_COPY[lang].plus} about={t.conclusion.next.title}>
            <ol className="v-list px-plus-detail">{t.conclusion.next.steps.map((step) => <li key={step}>{step}</li>)}</ol>
          </Plus>
        </section>
        <p className="d-small">{brand.promise}</p>
        <div className="d-small d-muted grid gap-1">
          <p>{t.mentions.general}{t.mentions.review ? ` · ${t.mentions.review}` : ""}</p>
          <p><SimapLine t={COPY[lang]} lang={lang} /></p>
          <p>{t.privacy.sent} {t.privacy.kept}</p>
        </div>
        {/* printed, the page leads back to the visit (the address as he opened it) */}
        <VisitAddress lang={lang} label={PAGES_COPY[lang].unePage.address} />
        <div className="d-print-tools">
          <PButton variant="action" onClick={() => window.print()}>{t.synthese.save}</PButton>
          <Link className="d-tool inline-flex min-h-[44px] items-center" href={visitPath(lang)}>{t.synthese.back}</Link>
        </div>
        <p className="d-small d-muted d-print-tools">{t.synthese.how}</p>
      </main>
    </div>
  );
}
