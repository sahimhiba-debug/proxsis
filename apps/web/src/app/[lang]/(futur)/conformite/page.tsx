import Link from "next/link";
import { CopyButton } from "@/components/CopyButton";
import { companies, compliance, meta } from "@/lib/data";
import { getDict, type Lang } from "@/lib/i18n";
import type { ComplianceCheck } from "@/lib/types";
import { ComplianceCountdown } from "@/futur/ComplianceCountdown";
import { usageName } from "@/futur/display";
import { StatusRing } from "@/futur/StatusRing";

export async function generateMetadata({ params }: PageProps<"/[lang]/conformite">) {
  const { lang } = await params;
  return { title: getDict(lang).compliance.title };
}

// « Conformité », futurisme suisse: for every trade a followed company will probably need, is the post subject to the
// 2026 reporting obligation? A status ring per post (copper: working days of restriction left), the free-publication
// date, the announcement text ready to copy. Companies with a subject post first; the dossier links here by anchor.
export default async function CompliancePage({ params }: PageProps<"/[lang]/conformite">) {
  const { lang: l } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const c = t.compliance;
  const f = t.fx.conf;
  const rows = Object.entries(compliance).filter(([id]) => companies[id])
    .sort(([a], [b]) => usageName(companies[a].nom).localeCompare(usageName(companies[b].nom), lang));
  const withSubject = rows.filter(([, checks]) => checks.some((x) => x.soumis));
  const without = rows.filter(([, checks]) => !checks.some((x) => x.soumis));
  const all = rows.flatMap(([, checks]) => checks);
  const nSubject = all.filter((x) => x.soumis).length;
  const nNot = all.filter((x) => x.soumis === false).length;
  const status = (x: ComplianceCheck) => (x.soumis === null ? c.unknown : x.soumis ? c.subject : c.notSubject)
    + (x.exception_code ? ` — ${c.exception[x.exception_code]}` : "");

  // the post: trade, status in words, and the legal basis (CH-ISCO-19 code and its official title) in small print
  const post = (x: ComplianceCheck) => (
    <>
      <p className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[16px]">
        {x.metier_libelle[lang]} <span className="fx-tag" data-kind="estimation">{f.estimated}</span>
      </p>
      <p data-testid="subject" className={`mt-0.5 text-[14px] ${x.soumis ? "" : "fx-muted"}`}>{status(x)}</p>
      <p className="fx-muted mt-1 text-[12px] leading-snug">
        <span className="fx-mono">{x.genre ?? "—"}</span> · {lang === "fr" ? x.libelle_fr : x.libelle_de}{x.correspondance === "probable" ? "" : ` · ${f.toConfirm}`}
      </p>
    </>
  );

  const company = ([id, checks]: [string, ComplianceCheck[]]) => (
    <section key={id} id={id} className="fx-card scroll-mt-24 p-5 sm:p-6" data-testid="compliance-company" aria-labelledby={`fx-conf-${id}`}>
      <h3 id={`fx-conf-${id}`} className="flex flex-wrap items-baseline justify-between gap-x-4">
        <Link className="fx-link inline-flex min-h-11 items-center text-[20px]" href={`/${lang}/entreprise/${id}/`}>{usageName(companies[id].nom)}</Link>
        <span className="fx-caps fx-muted">{companies[id].ville}</span>
      </h3>
      <ul className="mt-2">
        {checks.map((x) => (
          <li key={x.metier} className="border-t border-[var(--fx-line)] py-4">
            {x.soumis ? (
              <>
                <ComplianceCountdown start={meta.semaine} today={meta.semaine} holidays={meta.jours_feries_valais}
                  labels={{ online: f.online, onlineLong: c.online, freeFrom: c.freeFrom, left1: f.left1, leftN: f.leftN, over: c.over,
                    asOf: f.asOf }}>
                  {post(x)}
                </ComplianceCountdown>
                <details className="mt-2 pl-12">
                  <summary className="fx-quiet">{c.ad}</summary>
                  <div className="fx-paper mt-2 p-4">
                    <div className="flex justify-end">
                      <CopyButton text={x.annonce[lang]} label={t.label.copy} done={t.label.copied} failed={t.label.copyFailed} className="fx-paper-button" />
                    </div>
                    <pre className="mt-2 whitespace-pre-wrap font-[inherit] text-[14px] leading-relaxed">{x.annonce[lang]}</pre>
                  </div>
                </details>
              </>
            ) : (
              <div className="flex items-start gap-4">
                <StatusRing status={x.soumis === null ? "unknown" : "not-subject"} />
                <div className="min-w-0 flex-1">{post(x)}</div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );

  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{c.title}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{f.title}</span>
      </h1>
      <p className="fx-muted mt-4 max-w-[62ch] text-[16px] leading-relaxed">{f.lead}</p>
      <p className="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-[14px]">
        <span className="inline-flex items-center gap-2"><StatusRing status="subject" left={5} />{f.subjectN.replace("{n}", String(nSubject))}
          <span className="fx-muted">({f.legend})</span></span>
        <span className="inline-flex items-center gap-2"><StatusRing status="not-subject" />{f.notSubjectN.replace("{n}", String(nNot))}</span>
      </p>

      <section className="fx-card mt-8 p-5 sm:p-6" aria-labelledby="fx-conf-rules">
        <h2 id="fx-conf-rules" className="fx-caps fx-muted">{f.rules}</h2>
        <p className="mt-3 max-w-[64ch] text-[15px] leading-relaxed">{c.rules}</p>
        <p className="fx-muted mt-2 max-w-[64ch] text-[14px] leading-relaxed">{f.genre} {c.orp} {c.holidays}</p>
        <p className="fx-muted mt-2 max-w-[64ch] text-[13px] leading-relaxed">{c.claimScope}</p>
        <p className="mt-1 text-[14px]"><Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/mesures/#CONF-1`}>{t.fx.howMeasure}</Link></p>
      </section>

      <section className="mt-12" aria-labelledby="fx-conf-subject">
        <h2 id="fx-conf-subject" className="fx-caps fx-muted mb-4">{f.withSubject.replace("{n}", String(withSubject.length))}</h2>
        <div className="fx-conf-grid">{withSubject.map(company)}</div>
      </section>
      {without.length ? (
        <details className="mt-12">
          <summary className="fx-caps fx-muted flex min-h-11 items-center">{f.without.replace("{n}", String(without.length))}</summary>
          <div className="fx-conf-grid mt-4">{without.map(company)}</div>
        </details>
      ) : null}
      <p className="fx-muted mt-10 text-[12px]">{c.sources}</p>
    </div>
  );
}
