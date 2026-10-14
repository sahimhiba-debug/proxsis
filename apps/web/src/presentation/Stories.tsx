"use client";

// Act 4, « Revenir à ce qui était connu »: three stories replayed at a past Monday, three stops each (what was known,
// the reason to call with those pieces only, what happened next with a named interval), then the first examination,
// unfavourable result first. Everything shown comes from histoires.json; the copy only frames it.
import { motion } from "motion/react";
import { ArrowUpRight } from "lucide-react";
import { fmtDate } from "@/lib/dates";
import type { PLang, PresentationCopy } from "./copy";
import { COPY_C } from "./copy_c";
import { DUR, T } from "./motion";
import type { Action } from "./state";
import type { Story, StoryInterval, StoryPiece } from "./storyData";
import { Em, PButton } from "./ui";

/** A text without its last sentence when that sentence is `tail` (shown apart); the words are otherwise unchanged. */
function withoutTrailing(text: string, tail: string): string {
  return text.trimEnd().endsWith(tail) ? text.trimEnd().slice(0, -tail.length).trimEnd() : text;
}
const appear = (delay = 0) => ({ initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 }, transition: { ...T.medium, delay } });

function Piece({ p, same, lang, t, dispatch }: {
  p: StoryPiece; same: boolean; lang: PLang; t: PresentationCopy; dispatch: (a: Action) => void;
}) {
  const h = COPY_C[lang].dir.histoire;
  return (
    <li className="d-story-piece">
      <p className="d-caps d-muted flex flex-wrap items-baseline justify-between gap-x-[1em]">
        <span>
          {p.type === "adjudication" ? t.dir.stories.award : t.dir.stories.tender} · {h.published.replace("{date}", fmtDate(p.date))}
          {p.type === "appel_offres" && p.ouvert_a_T ? ` · ${t.dir.stories.open}` : ""}
        </span>
        <PButton variant="quiet" className="d-source-link" onClick={() => dispatch({ type: "openSource", url: p.url })}>
          {t.dir.stories.source} <ArrowUpRight aria-hidden />
        </PButton>
      </p>
      {/* the award of a tender just shown: same object, same authority, not repeated */}
      {same ? null : (
        <p className="mt-[0.15em]">{p.objet?.[lang] ?? `« ${p.titre} »`}{p.adjudicateur ? <span className="d-muted"> · {p.adjudicateur}</span> : null}</p>
      )}
    </li>
  );
}

/** A named interval; `hero`: the one that tells the story (what came next), in large figures; the others stay quiet. */
function Interval({ i, lang, t, hero = false }: { i: StoryInterval; lang: PLang; t: PresentationCopy; hero?: boolean }) {
  return (
    <li className="d-interval" data-hero={hero || undefined}>
      <span className="d-num">{i.jours}</span>
      <span className="d-small">
        {(i.jours === 1 ? t.dir.stories.day1 : t.dir.stories.days)} {i.nom[lang]}
        <span className="d-muted"> ({fmtDate(i.debut)} → {fmtDate(i.fin)})</span>
      </span>
    </li>
  );
}

/** One story, three stops revealed by the presenter (arrow key) or by the scene's action. */
export function StoryScene({ story, index, total, lang, t, reveal, dispatch }: {
  story: Story; index: number; total: number; lang: PLang; t: PresentationCopy; reveal: number; dispatch: (a: Action) => void;
}) {
  const h = COPY_C[lang].dir.histoire;
  const stop = Math.min(reveal, 2);
  const known = story.intervalles.filter((x) => x.arret === "connu");
  const after = story.intervalles.filter((x) => x.arret === "ensuite");
  const limit = story.type === "limite";
  const ctx = story.arrets.connu.contexte?.texte[lang];
  return (
    <div className="d-scene d-dense" data-testid="story">
      {/* the story's place in the act and its company, on the act's line: the stops get the height of the screen */}
      <div className="d-scene-head">
        <p className="d-label">04 — {t.acts[4]}</p>
        <p className="d-small d-muted text-right">
          {h.kicker.replace("{n}", String(index + 1)).replace("{total}", String(total))}
          {limit ? <span className="d-copper"> · {h.limit}</span> : null}
          {" — "}<span className="text-[var(--texte)]">{story.entreprise.nom}</span> · {story.entreprise.ville} · {story.region[lang]}
        </p>
      </div>
      {/* the act's statement, the same anchor for the three stories */}
      <h1 className="d-sub d-story-title"><Em text={h.statement} /></h1>
      {/* the stops are titled by their headings, not named regions: three stories on one page (the proof dossier) would
          repeat the same region names */}
      <div className="d-story-grid">
        <section>
          <h2 id={`${story.id}-stop-1`} className="d-caps">{h.stops.known.replace("{date}", fmtDate(story.date_T))}</h2>
          <ol className="mt-[0.3em]">
            {story.arrets.connu.pieces.map((p, k, all) => (
              <Piece key={`${p.numero}-${p.date}`} p={p} lang={lang} t={t} dispatch={dispatch}
                same={k > 0 && JSON.stringify(all[k - 1].objet) === JSON.stringify(p.objet)} />
            ))}
          </ol>
          {ctx ? <p className="d-small d-muted mt-[0.6em]">{ctx}</p> : null}
          {known.filter((i) => !i.prevu).length ? (
            <ul className="mt-[0.5em]">{known.filter((i) => !i.prevu).map((i, k) => <Interval key={`${i.code}-${k}`} i={i} lang={lang} t={t} />)}</ul>
          ) : null}
          {/* planned works (dates written in a tender, never observed) stay in the data and the review sheets, not on
              the projected slide (design critique, round 2) */}
        </section>
        <div className="d-story-right">
        <section>
          <h2 id={`${story.id}-stop-2`} className="d-caps">{h.stops.signal}</h2>
          {stop >= 1 ? (
            <motion.p className="mt-[0.5em]" {...appear()}>{story.arrets.signalement.texte[lang]}</motion.p>
          ) : (
            <PButton variant="action" className="mt-[0.6em]" onClick={() => dispatch({ type: "reveal", n: 1 })}>{h.actions.signal}</PButton>
          )}
        </section>
        <section>
          <h2 id={`${story.id}-stop-3`} className="d-caps">{h.stops.after}</h2>
          {stop >= 2 ? (
            <motion.div {...appear()}>
              {/* the need sentence ends the data's text: it is shown once, on its own line, in bold */}
              <p className="mt-[0.5em]">{withoutTrailing(story.arrets.ensuite.texte[lang], story.besoin_personnel[lang])}</p>
              {/* the interval that tells the story, in large figures; the others are in the text above */}
              {after.length ? <ul className="mt-[0.6em]"><Interval i={after[0]} lang={lang} t={t} hero /></ul> : null}
              {story.arrets.ensuite.autres_traces?.publications.length ? (
                <p className="d-small d-muted mt-[0.6em]">
                  {story.arrets.ensuite.autres_traces.source[lang]}{lang === "de" ? ": " : "\u00a0: "}{story.arrets.ensuite.autres_traces.publications
                    .map((b) => `${fmtDate(b.date)} (${b.commune})`).join(", ")}
                </p>
              ) : null}
              {limit ? (
                <motion.div className="mt-[0.5em]" {...appear(DUR.medium)}>
                  <p>{h.question}</p>
                  <p className="d-muted">{h.noAnswer}</p>
                </motion.div>
              ) : null}
              <motion.p className="mt-[0.4em] font-semibold" {...appear(DUR.long)}>{story.besoin_personnel[lang]}</motion.p>
            </motion.div>
          ) : stop >= 1 ? (
            <PButton variant="action" className="mt-[0.6em]" onClick={() => dispatch({ type: "reveal", n: 2 })}>{h.actions.after}</PButton>
          ) : null}
        </section>
        </div>
      </div>
    </div>
  );
}
