import "@/presentation/direction.css";
import "./visite.css";
import "./identite.css";
import Link from "next/link";
import type { ReactNode } from "react";
import team from "@/data/equipe/equipe.json";
import { COPY } from "@/presentation/copy";
import type { Team } from "@/lib/team";
import { PAGES_COPY } from "./pages";
import { visitPath } from "./paths";
import { Logo } from "@/lib/Logo";
import { Plus } from "@/lib/Plus";

// The discreet pages of the conclusion (brief « à distance », § 5 and § 11): « Vos questions », « Qui sommes-nous »,
// « Pour vos équipes techniques ». The same paper-free direction as the printable summary, readable on any device.
function Shell({ lang, title, children }: { lang: "fr" | "de"; title: string; children: ReactNode }) {
  const brand = COPY[lang].dir;
  const t = PAGES_COPY[lang];
  return (
    <div className="dir d-print" lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <main className="d-print-main v-info">
        <header className="d-brand-block">
          <p className="d-brand"><Logo title={brand.name} /></p>
          <p className="d-small d-muted">{brand.signature}</p>
          <p className="d-proto">{brand.prototype}</p>
        </header>
        <h1 className="d-sub mt-[0.8em]">{title}</h1>
        {children}
        <p><Link className="d-tool inline-flex min-h-[44px] items-center" href={visitPath(lang)}>{t.back}</Link></p>
      </main>
    </div>
  );
}

// On a phone (suite 9, § 10), each answer in short sentences first, the whole answer of the brief under « En savoir
// plus »; on a computer, the whole answer, as before.
export function QuestionsPage({ lang }: { lang: "fr" | "de" }) {
  const t = PAGES_COPY[lang].questions;
  return (
    <Shell lang={lang} title={t.title}>
      <dl className="v-qa">
        {t.items.map((x) => (
          <div key={x.q} data-testid="question-item">
            <dt className="d-lead">« {x.q} »</dt>
            <dd>
              <p className="px-bref" data-testid="question-bref">{x.bref}</p>
              <Plus label={PAGES_COPY[lang].plus} about={x.q}><p className="px-plus-detail" data-testid="question-answer">{x.a}</p></Plus>
            </dd>
          </div>
        ))}
      </dl>
    </Shell>
  );
}

export function TeamPage({ lang }: { lang: "fr" | "de" }) {
  const t = PAGES_COPY[lang].equipe;
  const data = team as Team;
  // only what Hiba gave, as she wrote it (suite 6, § 5): no empty slot, and the contact only when there is one
  return (
    <Shell lang={lang} title={t.title}>
      {data.membres.map((m, i) => (
        <p key={i} className="d-lead" data-testid="team-member">{[m.nom, m.role].filter(Boolean).join(", ")}</p>
      ))}
      {data.contact ? <p data-testid="team-contact"><span className="d-small d-muted">{t.contact} : </span>{data.contact}</p> : null}
    </Shell>
  );
}

export function TechniquePage({ lang }: { lang: "fr" | "de" }) {
  const t = PAGES_COPY[lang].technique;
  return (
    <Shell lang={lang} title={t.title}>
      {t.sections.map((s) => (
        <section key={s.h} className="v-tech">
          <h2 className="d-lead">{s.h}</h2>
          {s.p.map((p) => <p key={p}>{p}</p>)}
        </section>
      ))}
      <p><Link className="v-link" href={`/${lang}/mesures/`}>{t.measures}</Link></p>
    </Shell>
  );
}

// The roadmap (Hiba, 14.10.2026): today, five steps without any duration, and the rule that opens each step.
export function RoadmapPage({ lang }: { lang: "fr" | "de" }) {
  const t = PAGES_COPY[lang].feuille;
  return (
    <Shell lang={lang} title={t.title}>
      <section className="v-tech" data-testid="feuille-aujourdhui">
        <h2 className="d-lead">{t.today.h}</h2>
        <p>{t.today.p}</p>
        <p><Link className="v-link" href={`/${lang}/mesures/`}>{t.today.measures}</Link></p>
      </section>
      {t.steps.map((s) => (
        <section key={s.h} className="v-tech" data-testid="feuille-etape">
          <h2 className="d-lead">{s.h}</h2>
          {s.p ? <p>{s.p}</p> : null}
        </section>
      ))}
      <section className="v-tech" data-testid="feuille-regle">
        <h2 className="d-lead">{t.rule.h}</h2>
        <p>{t.rule.p}</p>
      </section>
    </Shell>
  );
}
