import "@/presentation/direction.css";
import "./visite.css";
import "./identite.css";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { fmtDate } from "@/lib/dates";
import { COPY } from "@/presentation/copy";
import { SimapLine } from "@/presentation/Frame";
import { VISIT_COPY } from "./copy";
import type { VisitDossier } from "./dossier";
import { PAGES_COPY } from "./pages";
import { visitPath } from "./paths";
import { LogoIris } from "@/iris/LogoIris";
import { Fort } from "./Fort";

// The first screen of proxsis.vercel.app (brief « à distance », § 3): the title and the subtitle, beside them a real
// view of the product (one company, its dated publication, the call question), « Voir Proxsis en 11 minutes » to start
// the visit, « Lire la synthèse (1 page) », the language and the prototype mention. A server page with no data beyond
// the one dossier it shows: under 1 MB transferred (e2e/accueil.spec.ts). The logo is the moment of the first screen:
// Iris puts the dot on the « i » (suite 8, § 4), once per visit; without motion, the full logo.
export function Accueil({ lang, d }: { lang: "fr" | "de"; d: VisitDossier }) {
  const t = PAGES_COPY[lang].accueil;
  const v = VISIT_COPY[lang];
  const brand = COPY[lang].dir;
  const other = lang === "fr" ? "de" : "fr";
  const p = d.publication;
  return (
    <div className="dir d-print v-accueil" lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <header className="d-head">
        <div className="d-brand-block">
          {/* le point du « i » (suite 8, § 4) : une seule fois par visite ; toucher le logo rejoue le toc */}
          <p className="d-brand v-accueil-logo"><LogoIris title={brand.name} replay={v.nav.replay} /></p>
          <p className="d-proto">{brand.prototype}</p>
        </div>
        <div className="d-head-right">
          <Link className="d-tool" href={`/${other}/`} hrefLang={other}>{v.nav.language}</Link>
        </div>
      </header>
      <main className="v-accueil-main">
        <div className="v-accueil-text">
          <h1 className="d-statement v-miroir"><Fort text={t.title} strong={t.titleStrong} /></h1>
          <p className="d-lead v-retenir" data-testid="retenir">{t.retenir}</p>
          <p className="d-lead">{t.subtitle}</p>
          <div className="v-accueil-actions">
            <Link className="d-action" href={visitPath(lang)} data-testid="start">{t.start} <ArrowRight aria-hidden /></Link>
            <Link className="v-link" href={`${visitPath(lang)}#questions`} data-testid="questions-link">{v.questions.title}</Link>
            <Link className="v-link" href={`/${lang}/une-page/`}>{t.summary}</Link>
          </div>
        </div>
        <section className="v-accueil-preview" aria-label={t.preview}>
          <p className="d-small d-muted">{t.preview}</p>
          <p className="d-company">{d.nom}<span className="block">{d.ville}</span></p>
          <article className="d-paper v-paper">
            <header className="d-paper-head">
              <span>{v.dossier.award} · {v.dossier.published.replace("{date}", fmtDate(p.date))}</span>
              <span>simap.ch</span>
            </header>
            <p className="d-paper-title">« {p.titre} »</p>
          </article>
          <div>
            <p className="d-small d-muted">{t.question}</p>
            {lang === "fr" ? <p className="d-lead v-question">« {d.question.fr} »</p>
              : <p className="d-small">{v.dossier.reviewDe}</p>}
          </div>
        </section>
      </main>
      <footer className="d-foot">
        <p className="d-small d-muted">{v.mentions.general}{v.mentions.review ? ` · ${v.mentions.review}` : ""} · <SimapLine t={COPY[lang]} lang={lang} /></p>
      </footer>
    </div>
  );
}
