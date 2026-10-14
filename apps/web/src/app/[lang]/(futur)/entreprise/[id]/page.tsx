import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { ViewTransition, type ReactNode } from "react";
import { CarnetPanel } from "@/futur/CarnetPanel";
import { companies, compliance, meta } from "@/lib/data";
import { fmtChfPublished, fmtDate, getDict, LANGS, type Lang } from "@/lib/i18n";
import { needSummary } from "@/lib/need";
import { AwardPaper } from "@/futur/AwardPaper";
import { BackLink } from "@/futur/BackLink";
import { Counter } from "@/futur/Counter";
import { daysBetween, isRecent, callLine, reasonAward, timelinePoints, usageName, WINDOW_DAYS } from "@/futur/display";
import { MicroTimeline } from "@/futur/MicroTimeline";
import { PulseDot } from "@/futur/PulseDot";
import { CorrectionNote } from "@/futur/CorrectionNote";

export const dynamicParams = false;

export function generateStaticParams() {
  return LANGS.flatMap((lang) => Object.keys(companies).map((id) => ({ lang, id })));
}

export async function generateMetadata({ params }: PageProps<"/[lang]/entreprise/[id]">) {
  const { id } = await params;
  return { title: companies[id]?.nom ?? "" };
}

// reasons shown elsewhere in the dossier: the 52-week count (head), the latest contract (paper), the need and the
// expected lots (« ce que ça laisse envisager »)
const SHOWN_ELSEWHERE = new Set(["marches_52s", "dernier_marche", "besoin", "besoin_en_cours", "lots_attendus"]);

function Block({ title, children, id }: { title: string; children: ReactNode; id: string }) {
  return (
    <section aria-labelledby={id} className="mt-12">
      <h2 id={id} className="fx-caps fx-muted mb-4">{title}</h2>
      {children}
    </section>
  );
}

// The dossier, futurisme suisse: the head of the card that opened (same object, ViewTransition), then the three
// blocks (what the announcement says, what it suggests, what remains to check) and the dated contracts on paper.
export default async function CompanyPage({ params }: PageProps<"/[lang]/entreprise/[id]">) {
  const { lang: l, id } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const c = companies[id];
  if (!c) notFound();
  const need = needSummary(c.besoin);
  const subject = (compliance[id] ?? []).filter((x) => x.soumis).length;
  const phase = (p: string | null) => (p ? (t.company.phase as Record<string, string>)[p] ?? p : "—");
  const spec = t.specialty[c.specialite_principale as keyof typeof t.specialty] ?? c.specialite_principale;
  const last = reasonAward(c);
  const phone = callLine(c, lang);
  const facts = c.raisons.filter((r) => !SHOWN_ELSEWHERE.has(r.code));
  const weak = c.specialites[c.specialite_principale]?.faiblesses ?? [];
  const chrono = [...c.chronologie].sort((a, b) => b.date.localeCompare(a.date));
  // the 52 weeks that the head counts (the main specialty in full, the others quieter), then the older ones folded
  const within = chrono.filter((s) => daysBetween(s.date, meta.semaine) < WINDOW_DAYS);
  const older = chrono.filter((s) => daysBetween(s.date, meta.semaine) >= WINDOW_DAYS);
  const contract = (s: (typeof chrono)[number]) => (
    <li key={`${s.url_simap}-${s.date}`} className="relative" data-other={s.specialite !== c.specialite_principale}>
      <PulseDot recent={isRecent(s.date, meta.semaine)} label={t.fx.recent} />
      <p className="fx-mono fx-muted mb-2 text-[12px]">
        {fmtDate(s.date)}{s.phase ? ` · ${phase(s.phase)}` : ""}{s.specialite !== c.specialite_principale ? ` · ${t.fx.otherSpec}` : ""}
      </p>
      <div className="fx-paper p-4">
        <p className="fx-paper-title text-[16px]">
          <a href={s.url_simap} target="_blank" rel="noopener noreferrer">{s.titre}</a>
        </p>
        <p className="mt-2 text-[13px] text-[var(--fx-ink-muted)]">
          {t.company.authority}{t.label.colon} {s.adjudicateur ?? "—"}
          {s.montant_chf ? <span className="fx-num"> · {fmtChfPublished(s.montant_chf)}</span> : null}
        </p>
        <CorrectionNote url={s.url_simap} lang={lang} className="mt-2" />
      </div>
    </li>
  );
  return (
    <article className="fx-col fx-dossier pt-2">
      <div className="fx-dossier-head">
      <BackLink lang={lang} label={t.semaine.title} />

      <ViewTransition name={`co-${id}`} share="fx-morph" default="none">
        <header className="fx-raised mt-3 p-6 sm:p-8">
          <ViewTransition name={`ti-${id}`} share="fx-morph" default="none">
            <div>
              <p className="fx-caps fx-copper">{c.ville} · {c.canton}</p>
              <h1 className="fx-display mt-2 text-[36px] sm:text-[48px]">{usageName(c.nom)}</h1>
            </div>
          </ViewTransition>
          <p className="fx-muted mt-2 text-[14px]"><span className="sr-only">{t.fx.legal} : </span>{c.nom} · {spec}</p>
          {phone ? (
            <p className="fx-phone mt-5" data-testid="phone-line">
              <span className="fx-caps fx-muted block">{phone.review ? t.fx.phoneFact : t.fx.phone}</span>
              {phone.lead && phone.title ? (
                <>
                  <span className="mt-1 block">{phone.lead}</span>
                  <q className="fx-citation" data-testid="phone-title">{phone.title}</q>
                </>
              ) : <span className="mt-1 block">{phone.text}</span>}
              {phone.review ? <span className="fx-muted mt-1 block text-[13px]">{t.fx.phoneReview}</span> : null}
            </p>
          ) : null}
          <div className="mt-7 flex items-end gap-4">
            <Counter value={c.n_52s} className="fx-display text-[52px] leading-none" />
            <p className="fx-muted pb-1 text-[14px] leading-snug">{t.fx.figure}</p>
          </div>
          <div className="mt-4">
            <MicroTimeline points={timelinePoints(c, meta.semaine)} label={t.fx.marketsAria.replace("{n}", String(c.n_52s))}
              recentLabel={t.fx.recent} />
            <p className="fx-caps fx-muted mt-1 flex justify-between" aria-hidden><span>{t.fx.axisPast}</span><span>{t.fx.axisNow}</span></p>
          </div>
          <div className="mt-7 flex flex-wrap items-center gap-x-5 gap-y-2">
            <Link href={`/${lang}/entreprise/${id}/appel/`} className="fx-action" data-demo="preparer-appel">
              {t.semaine.call} <ArrowRight aria-hidden className="size-4" strokeWidth={1.75} />
            </Link>
            <Link href={`/${lang}/entreprise/${id}/candidats/`} className="fx-quiet">{t.company.candidates}</Link>
          </div>
        </header>
      </ViewTransition>
      </div>

      <div className="fx-dossier-body">
      {/* the call's outcome, where the consultant comes back after calling (not at the end of the evidence): under the
          head on a phone, at the top of the evidence on a wide screen, so that the head always fits in view */}
      <div className="mt-4 lg:mt-[44px]">
        <CarnetPanel entreprise={id} monday={meta.semaine} lang={lang} />
      </div>

      <Block title={t.fx.says} id="fx-says">
        {last ? <AwardPaper award={last} t={t} lang={lang} /> : null}
        {facts.length ? (
          <>
            <h3 className="fx-muted mb-1 mt-6 text-[13px]">{t.fx.otherFacts}</h3>
            <ul className="border-t border-[var(--fx-line)]">
              {facts.map((r) => <li key={r.code} className="border-b border-[var(--fx-line)] py-3 text-[15px] leading-snug">{r[lang]}</li>)}
            </ul>
          </>
        ) : null}
      </Block>

      <Block title={t.fx.suggests} id="fx-suggests">
        {need ? (
          <div className="fx-card p-5">
            <p className="text-[13px] text-[var(--fx-muted)]">{t.company.needTrades}</p>
            <p className="mt-1 text-[17px]">{need.trades.map((x) => meta.metiers[x]?.[lang] ?? x).join(", ")}</p>
            <p className="fx-mono mt-3 text-[13px] text-[var(--fx-muted)]">
              {t.company.needPeriod}
            </p>
            <p className="mt-3 text-[14px]"><Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/mesures/#BESOIN-1`}>{t.fx.howMeasure}</Link></p>
          </div>
        ) : (
          <p className="fx-muted text-[15px]">{t.fx.noNeed}</p>
        )}
        {c.lots_attendus.length ? (
          <div className="mt-4">
            <h3 className="fx-muted mb-1 text-[13px]">{t.company.expected}</h3>
            <ul className="border-t border-[var(--fx-line)]">
              {c.lots_attendus.map((x) => (
                <li key={`${x.phase}-${x.date_p10}`} className="flex items-baseline justify-between gap-4 border-b border-[var(--fx-line)] py-3 text-[15px]">
                  <span>{phase(x.phase)}</span>
                  <span className="fx-mono fx-muted text-[13px]">{fmtDate(x.date_p10)} – {fmtDate(x.date_p90)}</span>
                </li>
              ))}
            </ul>
            <p className="fx-muted mt-2 text-[13px]">{t.company.expectedNote} <Link className="fx-link" href={`/${lang}/mesures/#PHAS-2`}>{t.fx.howMeasure}</Link></p>
          </div>
        ) : null}
      </Block>

      <Block title={t.fx.verify} id="fx-verify">
        <ul className="border-t border-[var(--fx-line)]">
          {t.fx.questions.map((q) => <li key={q} className="border-b border-[var(--fx-line)] py-3 text-[15px]">{q}</li>)}
        </ul>
        {subject ? (
          <p className="mt-4 text-[15px]">
            <Link className="fx-link" href={`/${lang}/conformite/#${id}`}>{subject === 1 ? t.fx.compliance1 : t.fx.compliance.replace("{n}", String(subject))}</Link>
          </p>
        ) : null}
        {weak.length ? (
          <p className="fx-muted mt-4 text-[13px]">
            {t.fx.limits}{t.label.colon} {weak.map((w) => t.fx.weak[w] ?? w).join(" ; ")}
          </p>
        ) : null}
      </Block>

      <Block title={t.fx.timeline} id="fx-timeline">
        <ol className="fx-tl space-y-4" data-testid="timeline">
          {within.map(contract)}
        </ol>
        {older.length ? (
          <details className="mt-2">
            <summary className="fx-tl-mark fx-caps fx-muted pl-7"><span>{t.fx.since52} · {t.fx.older.replace("{n}", String(older.length))}</span></summary>
            <ol className="fx-tl mt-4 space-y-4">{older.map(contract)}</ol>
          </details>
        ) : null}
      </Block>

      </div>
    </article>
  );
}
