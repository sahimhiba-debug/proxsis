import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { companies, meta, proposals } from "@/lib/data";
import { fmt, fmtDate, fmtNum, getDict, LANGS, type Lang } from "@/lib/i18n";
import { usageName, workerName } from "@/futur/display";
import { KindTag } from "@/futur/KindTag";

export const dynamicParams = false;

export function generateStaticParams() {
  return LANGS.flatMap((lang) => Object.keys(companies).map((id) => ({ lang, id })));
}

export async function generateMetadata({ params }: PageProps<"/[lang]/entreprise/[id]/candidats">) {
  const { lang, id } = await params;
  return { title: `${getDict(lang).candidates.title} · ${companies[id]?.nom ?? ""}` };
}

// « Candidats proposés », futurisme suisse: for each estimated need of the company, the strict criteria in order (how
// many fictional temps remain after each), then the proposed temps, each with why, the CCT category and, when the post
// is subject to the reporting obligation, the date from which contact is allowed. Everything about people is fictional.
export default async function CandidatesPage({ params }: PageProps<"/[lang]/entreprise/[id]/candidats">) {
  const { lang: l, id } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const c = companies[id];
  if (!c) notFound();
  const k = t.candidates;
  const needs = proposals[id] ?? [];
  return (
    <article className="fx-col pb-8 pt-2">
      <Link href={`/${lang}/entreprise/${id}/`} className="fx-quiet -ml-1">
        <ArrowLeft aria-hidden className="size-4" strokeWidth={1.5} /> {usageName(c.nom)}
      </Link>
      <header className="mt-3">
        <p className="fx-caps fx-copper">{c.ville} · {c.canton}</p>
        <h1 className="fx-display mt-2 text-[36px] sm:text-[44px]">{k.title}</h1>
        <p className="mt-3 flex flex-wrap items-center gap-3 text-[15px]">
          <KindTag kind="fictif" t={t} /> <span className="fx-muted">{k.fictionalNote}</span>
        </p>
        <p className="mt-1 text-[14px]"><Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/mesures/#PROP-1`}>{t.fx.howMeasure}</Link></p>
      </header>
      {needs.length === 0 ? <p className="fx-muted mt-8 text-[15px]">{t.company.needNone}</p> : null}
      {needs.map((n) => {
        const steps: [string, number][] = [[k.funnelAll, n.entonnoir.tous], [k.funnelTrade, n.entonnoir.metier],
          [k.funnelCert, n.entonnoir.certificat], [k.funnelAvail, n.entonnoir.disponible], [k.funnelDistance, n.entonnoir.distance]];
        return (
          <section key={`${n.besoin.metier}-${n.besoin.debut}`} className="mt-12" data-testid="need-proposals"
            aria-labelledby={`fx-need-${n.besoin.metier}`}>
            <h2 id={`fx-need-${n.besoin.metier}`} className="fx-display text-[24px] sm:text-[28px]">
              {fmt(k.need, { metier: meta.metiers[n.besoin.metier]?.[lang] ?? n.besoin.metier, date: fmtDate(n.besoin.debut) })}
            </h2>
            <p className="mt-2"><KindTag kind="estimation" t={t} /></p>
            {/* the free-publication date of the export: counted from the list's Monday, the demonstration's « today » */}
            {n.annonce?.annonce_requise && n.annonce.publication_libre ? (
              <p className="fx-muted mt-2 text-[14px] leading-snug">
                {fmt(k.subjectNeed, { genre: n.annonce.genre ?? "—", day: fmtDate(meta.semaine), date: fmtDate(n.annonce.publication_libre) })}
              </p>
            ) : null}
            <div className="mt-5">
              <p className="fx-caps fx-muted flex flex-wrap items-center gap-3">{k.funnel} <KindTag kind="fictif" t={t} /></p>
              <ol className="fx-funnel mt-3" aria-label={k.funnel}>
                {steps.map(([label, value], i) => (
                  <li key={label} data-last={i === steps.length - 1}>
                    <span className="fx-mono text-[20px]">{value}</span>
                    <span className="fx-muted block text-[12px] leading-tight">{label}</span>
                  </li>
                ))}
              </ol>
            </div>
            {n.propositions.length === 0 ? <p className="fx-muted mt-5 text-[15px]">{k.none}</p> : null}
            <ul className="mt-6 grid gap-3 lg:grid-cols-2">
              {n.propositions.map((p) => (
                <li key={p.candidate_id} className="fx-card p-5" data-testid="candidate">
                  <p className="flex flex-wrap items-center justify-between gap-3">
                    <span className="text-[17px]">{workerName(p.candidate_id, t.fx.worker)}</span>
                    <KindTag kind="fictif" t={t} />
                  </p>
                  <p className="fx-muted mt-1 text-[13px] leading-snug">
                    {k.category}{t.label.colon} <span className="text-[var(--fx-ivory)]">{k.cat[p.categorie_cct]}</span> ·{" "}
                    {p.salaire_minimum_cct_ls_heure !== null
                      ? fmt(k.wage, { n: fmtNum(p.salaire_minimum_cct_ls_heure, lang, 2) })
                      : fmt(k.cctApplicable, { cct: lang === "fr" ? p.cct_applicable : p.cct_applicable_de })}
                  </p>
                  {n.annonce?.annonce_requise && !p.contact_des ? (
                    <p className="mt-2 text-[14px]" data-testid="contact-date">{k.orpRegistered}</p>
                  ) : null}
                  <p className="fx-caps fx-muted mt-4">{k.reasons}</p>
                  <ul className="mt-1 border-t border-[var(--fx-line)]">
                    {(lang === "fr" ? p.raisons_fr : p.raisons_de).map((r) => (
                      <li key={r} className="border-b border-[var(--fx-line)] py-2 text-[14px] leading-snug">{r}</li>
                    ))}
                  </ul>
                  <p className="fx-muted mt-3 text-[13px]">
                    {k.permit}{t.label.colon} {p.permis_travail} · {k.languages}{t.label.colon} {p.langues.join(", ").toUpperCase()}
                    {p.fin_mission ? ` · ${k.missionEnd}${t.label.colon} ${fmtDate(p.fin_mission)}` : ""}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        );
      })}
      <p className="fx-muted mt-10 text-[13px]">{k.wageNote}</p>
    </article>
  );
}
