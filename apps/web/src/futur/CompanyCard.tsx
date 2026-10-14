"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { ArrowRight } from "lucide-react";
import { ViewTransition, type ReactNode } from "react";
import { CARNET_COPY } from "@/lib/carnet";
import { CARNET_KEY, lastNote, parseBook } from "@/lib/carnetStore";
import { fmtDate } from "@/lib/dates";
import { Plus } from "@/lib/Plus";
import { useStoredString } from "@/lib/useStored";
import { MicroTimeline, type Point } from "./MicroTimeline";
import { SPRING } from "./motion";

export interface CardData {
  id: string;
  rank: string | null; // « 01 », or null for a newcomer
  commune: string;
  name: string; // usage name (display)
  legal: string; // full legal name (accessible name, dossier)
  why: string | null; // the export's reason, word for word (its first clause for the latest contract)
  phone: { text: string; review: boolean; lead?: string; title?: string } | null; // display.callLine: the sentence (FR) or the published fact (DE, under review)
  points: Point[];
  n52: number;
  consortium: string | null; // « Consortium : A, B » or « membres non nommés »; null for a single company
}

interface CardLabels {
  call: string; dossier: string; markets: string; market1: string; marketsAria: string; recent: string; newcomer: string;
  phone: string; phoneFact: string; phoneReview: string;
  recent1: string; recentN: string; rankReason: string; rankReason1: string; more: string;
}

const PressLink = motion.create(Link);
export const WEEK_KEY = "fx.week.path"; // the dossier's « back » returns to this list at the same scroll position

function rememberWeek() {
  try {
    window.sessionStorage.setItem(WEEK_KEY, window.location.pathname);
  } catch {
    // storage blocked: « back » simply opens the list
  }
}

/**
 * The card of a company. It is visible without JavaScript (the entrance is a CSS animation, removed when motion is
 * reduced); its surface and its title are the same objects as the dossier's head: the card opens and becomes it.
 */
export function CompanyCard({ c, i, lang, t, level = 2, featured = false, compact = false }: {
  c: CardData; i: number; lang: string; t: CardLabels; level?: 2 | 3; featured?: boolean;
  compact?: boolean; // on a phone (suite 9, § 10), the call sentence and the 52 weeks under « En savoir plus »
}) {
  const Title = level === 2 ? "h2" : "h3";
  const dossier = `/${lang}/entreprise/${c.id}/`;
  const recent = c.points.filter((p) => p.recent).length;
  return (
    <li data-testid="company-card" className={`fx-in flex ${featured ? "fx-featured" : ""}`} style={{ ["--i" as string]: i }}>
      <ViewTransition name={`co-${c.id}`} share="fx-morph" default="none">
        <div className="fx-card flex w-full flex-col p-5 sm:p-6">
          <ViewTransition name={`ti-${c.id}`} share="fx-morph" default="none">
            <div>
              <p className="fx-caps fx-copper">{c.rank ? `${c.rank} · ` : `${t.newcomer} · `}{c.commune}</p>
              <Title className={`fx-display mt-2 ${featured ? "text-[30px] sm:text-[38px]" : "text-[26px] sm:text-[30px]"}`}>
                <Link href={dossier} aria-label={c.legal} onClick={rememberWeek} data-demo={`ouvrir-${c.id}`}
                  className="inline-flex min-h-11 min-w-11 items-center outline-offset-4 hover:text-[var(--fx-copper)]">{c.name}</Link>
              </Title>
            </div>
          </ViewTransition>
          {c.consortium ? <p className="fx-caps fx-muted mt-1" data-testid="consortium">{c.consortium}</p> : null}
          {/* why this rank (the simple rule: the most contracts in 52 weeks), then how recent the last one is */}
          {c.rank ? (
            <p className="mt-2 text-[15px] leading-snug" data-testid="rank-reason">
              {(c.n52 === 1 ? t.rankReason1 : t.rankReason).replace("{n}", String(c.n52))}
            </p>
          ) : null}
          {c.why ? <p className="fx-muted mt-1 text-[15px] leading-snug">{c.why}</p> : null}
          <Detail on={compact} label={t.more} about={c.name}>
            {c.phone ? (
              <p className={`fx-phone mt-4${compact ? " px-plus-detail" : ""}`} data-testid="phone-line">
                <span className="fx-caps fx-muted block">{c.phone.review ? t.phoneFact : t.phone}</span>
                {c.phone.lead && c.phone.title ? (
                  <>
                    <span className="mt-1 block">{c.phone.lead}</span>
                    <q className="fx-citation" data-testid="phone-title">{c.phone.title}</q>
                  </>
                ) : <span className="mt-1 block">{c.phone.text}</span>}
                {c.phone.review ? <span className="fx-muted mt-1 block text-[13px]" data-testid="phone-review">{t.phoneReview}</span> : null}
              </p>
            ) : null}
            <div className={`mt-5 flex items-center gap-4${compact ? " px-plus-detail" : ""}`}>
              <div className="min-w-0 flex-1">
                <MicroTimeline points={c.points} label={t.marketsAria.replace("{n}", String(c.n52))} recentLabel={t.recent} />
              </div>
              <span className="fx-caps fx-muted shrink-0">
                {c.n52 === 1 ? t.market1 : t.markets.replace("{n}", String(c.n52))}
                {recent ? <span className="fx-copper"> · {recent === 1 ? t.recent1 : t.recentN.replace("{n}", String(recent))}</span> : null}
              </span>
            </div>
          </Detail>
          <CarnetLine id={c.id} lang={lang} />
          <div className="mt-auto flex items-center justify-between gap-3 pt-4">
            <PressLink href={`/${lang}/entreprise/${c.id}/appel/`} className="fx-call" whileTap={{ scale: 0.96 }} transition={SPRING}>
              {t.call} <ArrowRight aria-hidden className="size-4" strokeWidth={1.75} />
            </PressLink>
            <PressLink href={dossier} onClick={rememberWeek} className="fx-quiet" whileTap={{ scale: 0.96 }} transition={SPRING}>
              {t.dossier}
            </PressLink>
          </div>
        </div>
      </ViewTransition>
    </li>
  );
}

/** The call sentence and the 52 weeks of a card: as they are, or folded on a phone under « En savoir plus » (Plus). */
function Detail({ on, label, about, children }: { on: boolean; label: string; about: string; children: ReactNode }) {
  return on ? <Plus label={label} about={about}>{children}</Plus> : <>{children}</>;
}

/** What the carnet holds for this company (decision, last return from the field), kept on this device: dashed, apart. */
function CarnetLine({ id, lang }: { id: string; lang: string }) {
  const t = CARNET_COPY[lang === "de" ? "de" : "fr"];
  const r = parseBook(useStoredString(CARNET_KEY, "{}"))[id];
  const e = r?.decision;
  const last = lastNote(r);
  if (!e && !last) return null;
  const decision = e ? (e.decision === "revoir" && e.revoir ? t.revoirOn.replace("{date}", fmtDate(e.revoir))
    : e.decision === "ecarter" ? `${t.decisions.ecarter} · ${t.motifs[e.motif ?? "autre"]}` : t.decisions[e.decision]) : null;
  const suite = last ? (last.outcome === "rappel" && last.rappel ? t.rappelOn.replace("{date}", fmtDate(last.rappel)) : t.outcomes[last.outcome]) : null;
  return (
    <p className="fx-field-notes mt-4 text-[14px]" data-testid="carnet-line">
      <span className="fx-caps fx-muted">{t.panel}</span> {[decision, suite].filter(Boolean).join(" · ")}
    </p>
  );
}

/** The list: the cards enter one after the other (CSS, from the first paint); the first one leads. */
export function CardList({ cards, lang, t, label, level = 2, lead = false, compact = false }: {
  cards: CardData[]; lang: string; t: CardLabels; label: string; level?: 2 | 3; lead?: boolean; compact?: boolean;
}) {
  return (
    <ol className="fx-cards space-y-4" aria-label={label}>
      {cards.map((c, i) => <CompanyCard key={c.id} c={c} i={i} lang={lang} t={t} level={level} featured={lead && i === 0} compact={compact} />)}
    </ol>
  );
}
