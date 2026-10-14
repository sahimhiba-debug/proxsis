import "@/presentation/direction.css";
import "./visite.css";
import "./identite.css";
import Link from "next/link";
import { COPY } from "@/presentation/copy";
import { SimapLine } from "@/presentation/Frame";
import type { MondaysData } from "@/presentation/mondayData";
import { PORTE, VISIT_COPY } from "./copy";
import { sourcesAnswer } from "./guide";
import { PAGES_COPY } from "./pages";
import { visitPath } from "./paths";
import type { VisitDossier } from "./dossier";
import { PrintButton } from "./PrintButton";
import { VisitAddress } from "./VisitAddress";
import { fmtDate } from "@/lib/dates";
import { Logo } from "@/lib/Logo";
import { IrisPetite } from "@/iris/IrisPetite";

// « Proxsis en une page » (brief « à distance », § 3 and § 5): the general summary, distinct from the director's own;
// one A4 page in French or German, saved as PDF by the browser. The figures come from the data (lundis.json, CLAIMS
// REEL-SPEC-BAT), never from the text. The door (suite 9, § 8) closes it in a short block, before the promise.
export function UnePage({ lang, mondays, example }: { lang: "fr" | "de"; mondays: MondaysData; example: VisitDossier }) {
  const t = PAGES_COPY[lang].unePage;
  const v = VISIT_COPY[lang];
  const d = v.dossier;
  const brand = COPY[lang].dir;
  const fill = (s: string) => s.replace("{n}", String(mondays.mesure.semaines)).replace("{rule}", mondays.mesure.affiche.regle[lang])
    .replace("{random}", mondays.mesure.affiche.hasard[lang]);
  return (
    <div className="dir d-print" lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <main className="d-print-main v-info v-une" data-testid="une-page">
        <header className="d-brand-block">
          <p className="d-brand"><Logo title={brand.name} /></p>
          <p className="d-small d-muted">{brand.signature}</p>
          <p className="d-proto">{brand.prototype}</p>
        </header>
        <h1 className="d-sub mt-[0.6em]">{t.title}</h1>
        {/* Iris, petite et immobile (l'impression ne bouge pas), tournée vers ce qu'elle dit */}
        <div className="v-une-iris" data-testid="une-iris">
          <IrisPetite hauteur={58} humeur="contente" regard={[2, 1]} immobile label={t.iris.name} />
          <p><span className="block">{t.iris.says}</span><span className="d-small d-muted">{t.iris.motto}</span></p>
        </div>
        {[t.what, t.measure, t.proposal].map((sec, i) => (
          <section key={sec.h} className="v-tech">
            <h2 className="d-lead">{sec.h}</h2>
            {sec.p.map((x) => <p key={x}>{fill(x)}</p>)}
            {/* suite 10, § 3: one line, the numbers of the catalogue and the rule (the same as under Iris's answer) */}
            {i === 1 ? <p className="d-small" data-testid="une-sources">{sourcesAnswer(lang)}</p> : null}
            {/* after « what Proxsis does », the prepared example of the visit: a real company, its published award, the
                question (in German, the fact only, until a German speaker has read the sentence) */}
            {i === 0 ? (
              <div className="v-une-example" data-testid="une-example">
                <p className="d-small d-muted">{t.example} · {example.nom}{example.ville ? `, ${example.ville}` : ""}</p>
                <div className="d-paper v-une-paper">
                  <p className="d-paper-head"><span>{d.award} · {d.published.replace("{date}", fmtDate(example.publication.date))}</span><span>simap.ch</span></p>
                  <p className="d-paper-title">{lang === "fr" ? `« ${example.publication.titre} »` : `«${example.publication.titre}»`}</p>
                </div>
                {lang === "fr" ? (
                  <p><span className="d-small d-muted block">{d.question}</span>« {example.question.fr} »</p>
                ) : (
                  <p className="d-small d-muted">{d.reviewDe}</p>
                )}
              </div>
            ) : null}
          </section>
        ))}
        {/* the door (suite 9, § 8), a short block: two sentences, then its three steps on one line */}
        <section className="v-tech v-une-porte" data-testid="une-porte">
          <h2 className="d-lead">{t.porte.h}</h2>
          <p>{t.porte.p}</p>
          <p className="d-small v-une-etapes" data-testid="une-etapes">
            {PORTE[lang].etapes.map((x, i) => <span key={x}>{i ? " · " : ""}{i + 1}. {x}</span>)}
          </p>
        </section>
        <p className="d-small">{brand.promise}</p>
        <div className="d-small d-muted grid gap-1">
          <p>{v.mentions.general}{v.mentions.review ? ` · ${v.mentions.review}` : ""}</p>
          <p><SimapLine t={COPY[lang]} lang={lang} /></p>
        </div>
        <VisitAddress lang={lang} label={t.address} />
        <div className="d-print-tools">
          <PrintButton label={t.save} />
          <Link className="d-tool inline-flex min-h-[44px] items-center" href={visitPath(lang)}>{t.visit}</Link>
        </div>
      </main>
    </div>
  );
}
