import "@/presentation/direction.css";
import "./visite.css";
import "./identite.css";
import Link from "next/link";
import { COPY } from "@/presentation/copy";
import { SimapLine } from "@/presentation/Frame";
import type { MondaysData } from "@/presentation/mondayData";
import { fmtDate } from "@/lib/dates";
import { Logo } from "@/lib/Logo";
import { Plus } from "@/lib/Plus";
import { VISIT_COPY } from "./copy";
import { PAGES_COPY } from "./pages";
import { visitPath } from "./paths";
import { PrintButton } from "./PrintButton";
import { VisitAddress } from "./VisitAddress";

// « Pour votre direction » (brief of 07.10.2026, suite 2, § 8): a page to pass on to the group, sober, printable (saved
// as PDF by the browser), reached by a discreet link from the conclusion. The sentence to remember; the problem in two
// lines; the proof over the Mondays of the measure (figures from lundis.json, CLAIMS PRES-DATE-1); the trial without
// risk; the future in three steps (those of the door, suite 9, § 8); the group's goals in its own words, with their
// sources, the group never named (CLAIMS EXT-GROUPE-*, EXT-FLEXSIS-MOTS); the door « Demain, si Flexsis le souhaite », a
// possible future, with its guardrails (suite 3, § 3; suite 9, § 8). No person's name.
export function PourDirection({ lang, mondays }: { lang: "fr" | "de"; mondays: MondaysData }) {
  const t = PAGES_COPY[lang].direction;
  const v = VISIT_COPY[lang];
  const brand = COPY[lang].dir;
  const m = mondays.mesure;
  const fill = (x: string) => x.replace("{n}", String(m.semaines)).replace("{from}", fmtDate(m.premiere)).replace("{to}", fmtDate(m.derniere))
    .replace("{rule}", m.affiche.regle[lang]).replace("{random}", m.affiche.hasard[lang]);
  const plus = PAGES_COPY[lang].plus;
  return (
    <div className="dir d-print" lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <main className="d-print-main v-info v-direction" data-testid="pour-direction">
        <header className="d-brand-block">
          <p className="d-brand"><Logo title={brand.name} /></p>
          <p className="d-small d-muted">{brand.signature}</p>
          <p className="d-proto">{brand.prototype}</p>
        </header>
        <h1 className="d-sub mt-[0.5em]">{t.title}</h1>
        <section className="v-direction-retenir" aria-label={t.retenir}>
          <p className="d-lead" data-testid="direction-retenir">{PAGES_COPY[lang].accueil.retenir}</p>
        </section>
        {/* on a phone (suite 9, § 10): one idea per section, the rest under « En savoir plus »; on a computer and on paper,
            the page as before */}
        <section>
          <h2>{t.probleme.h}</h2>
          <Plus label={plus} about={t.probleme.h}>
            {t.probleme.p.map((x, i) => <p key={x} className={i ? "px-plus-detail" : undefined}>{x}</p>)}
          </Plus>
        </section>
        <section data-testid="direction-preuve">
          <h2>{t.preuve.h}</h2>
          <p className="px-bref" data-testid="direction-preuve-bref">{fill(t.preuve.bref)}</p>
          <Plus label={plus} about={t.preuve.h}>
            <p className="px-plus-detail">{fill(t.preuve.p)}</p>
            <p>{t.preuve.limit}</p>
            <p className="d-small d-muted px-plus-detail">
              <Link className="v-link" href={`/${lang}/mesures/#PRES-DATE-1`}>{t.preuve.claims}</Link>
            </p>
          </Plus>
        </section>
        <section>
          <h2>{t.essai.h}</h2>
          <p>{t.essai.p}</p>
        </section>
        <section data-testid="direction-avenir">
          <h2>{t.avenir.h}</h2>
          <Plus label={plus} about={t.avenir.h}>
            <ol className="v-direction-steps">
              {t.avenir.steps.map((x) => <li key={x.court}>{x.court} <span className="px-plus-detail">{x.detail}</span></li>)}
            </ol>
          </Plus>
          <p className="d-print-tools"><Link className="d-tool inline-flex min-h-[44px] items-center" href={visitPath(lang, "feuille-de-route")} data-testid="direction-feuille">{PAGES_COPY[lang].feuille.link}</Link></p>
        </section>
        <section data-testid="direction-buts">
          <h2>{t.buts.h}</h2>
          <p className="d-small d-muted">{t.buts.note}</p>
          <Plus label={plus} about={t.buts.h}>
            <dl className="v-direction-buts">
              {t.buts.items.map((x) => (
                <div key={x.claims} data-claims={x.claims}>
                  <dt><span className="v-direction-quote">{x.quote}</span><span className="d-small d-muted block">{x.source}</span></dt>
                  <dd className="px-plus-detail">{x.how}</dd>
                </div>
              ))}
            </dl>
          </Plus>
        </section>
        {/* the door (suite 9, § 8): Hiba's texts, then the passage on Apertus and the five guardrails; a possible future */}
        <section data-testid="direction-iris">
          <h2>{t.iris.h}</h2>
          {t.iris.p.map((x) => <p key={x}>{x}</p>)}
          <Plus label={plus} about={t.iris.guardsTitle}>
            {/* on a phone, the first guardrail stays in view (fresh review, 13.10): the others under « En savoir plus » */}
            <p className="px-bref" data-testid="garde-fou-bref">{t.iris.guards[0]}</p>
            <p className="px-plus-detail">{t.iris.apertus}</p>
            <h3 className="px-plus-detail v-direction-h3">{t.iris.guardsTitle}</h3>
            <ul className="v-direction-guards px-plus-detail" data-testid="direction-garde-fous">{t.iris.guards.map((x) => <li key={x}>{x}</li>)}</ul>
          </Plus>
          <p className="d-small d-muted" data-testid="direction-futur">{t.iris.future}</p>
        </section>
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
