"use client";

import "./direction.css";
// the same order everywhere (direction, visit, identity): in production Next groups the sheets, and a page that
// loaded the identity without the visit sheet put visite.css after it, which undid identity rules of equal weight
import "@/visite/visite.css";
import "@/visite/identite.css";
import Link from "next/link";
import { COPY, type PLang } from "./copy";
import { COPY_C } from "./copy_c";
import { SimapLine } from "./Frame";
import { ALL, type Action } from "./state";
import { StoryScene } from "./Stories";
import type { StoriesData } from "./storyData";
import { Logo } from "@/lib/Logo";

// The proof dossier (Hiba, 07.10.2026): the three dated stories that opened act 4, kept in reserve out of the guided
// path, shown complete (every stop); each source opens on simap.ch. Opened from « Choisissez une date » or the notes.
export function ProofDossier({ lang, stories }: { lang: PLang; stories: StoriesData }) {
  const t = COPY[lang];
  const y = COPY_C[lang].dir.preuves;
  // no session here: a source opens in a new tab instead of the stage's paper sheet
  const act = (a: Action) => {
    if (a.type === "openSource") window.open(a.url, "_blank", "noopener,noreferrer");
  };
  return (
    <div className="dir d-print" lang={lang === "de" ? "de-CH" : "fr-CH"}>
      <main className="d-print-main d-proofs">
        <header className="d-brand-block">
          <p className="d-brand"><Logo title={t.dir.name} /></p>
          <p className="d-small d-muted">{t.dir.signature}</p>
          <p className="d-proto">{t.dir.prototype}</p>
        </header>
        <h1 className="d-sub mt-[1em]">{y.title}</h1>
        <p className="d-lead max-w-[44em]">{y.lead}</p>
        <p className="d-small d-muted max-w-[44em]">{stories.regle[lang]}</p>
        {stories.histoires.map((story, k) => (
          <section key={story.id} className="d-proof" aria-label={t.steps[`histoire${k + 1}`]}>
            <StoryScene story={story} index={k} total={stories.histoires.length} lang={lang} t={t} reveal={ALL} dispatch={act} />
          </section>
        ))}
        <p className="d-small d-muted"><SimapLine t={t} lang={lang} /></p>
        <div className="d-print-tools">
          <Link className="d-tool inline-flex min-h-[44px] items-center" href={`/${lang}/presentation/`}>{y.back}</Link>
        </div>
      </main>
    </div>
  );
}
