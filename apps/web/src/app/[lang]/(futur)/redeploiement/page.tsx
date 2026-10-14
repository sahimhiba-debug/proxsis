import Link from "next/link";
import { usageName } from "@/futur/display";
import { dayIndex, Lane } from "@/futur/Lane";
import { WorkerHead } from "@/futur/WorkerHead";
import { meta, redeploy } from "@/lib/data";
import { fmtDayMonth } from "@/lib/dates";
import { fmtDate, getDict, type Lang } from "@/lib/i18n";
import type { Worker } from "@/lib/types";

export async function generateMetadata({ params }: PageProps<"/[lang]/redeploiement">) {
  const { lang } = await params;
  return { title: getDict(lang).redeploy.title };
}

const DAY = 86_400_000;
const plusDays = (iso: string, n: number) => new Date(Date.parse(`${iso}T12:00:00Z`) + n * DAY).toISOString().slice(0, 10);

// « Fin de mission », futurisme suisse: a calendar of the coming weeks. For each (fictional) worker, the mission until
// its last day, the first free working day, and the possibility — in dots — of a next mission where a company that has
// just won a public contract (real) will probably need the trade (estimated). Grouped by the week in which the mission
// ends. The fictional rate is a sentence, never a display figure (design critique, round 1): one mention in words says
// what is fictional, what is real and what is estimated, for the whole scene (DESIGN.md § 7).
export default async function RedeployPage({ params }: PageProps<"/[lang]/redeploiement">) {
  const { lang: l } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const f = t.fx.fin;
  const r = redeploy;
  const from = meta.semaine;
  const reach = Math.max(...r.travailleurs.flatMap((w) => [dayIndex(from, w.fin_mission) + 2,
    w.proposition ? dayIndex(from, w.proposition.semaine) + 7 : 0]));
  const days = Math.ceil(reach / 7) * 7;
  const mondays = Array.from({ length: days / 7 }, (_, k) => plusDays(from, 7 * k));
  const workers = [...r.travailleurs].sort((a, b) => a.fin_mission.localeCompare(b.fin_mission) || a.libelle.localeCompare(b.libelle));
  const groups = mondays.map((m) => ({ monday: m, workers: workers.filter((w) => w.fin_mission >= m && w.fin_mission < plusDays(m, 7)) }))
    .filter((g) => g.workers.length);
  const motifs = Object.entries(r.travailleurs.reduce<Record<string, number>>((acc, w) => {
    if (!w.proposition && w.motif_code) acc[w.motif_code] = (acc[w.motif_code] ?? 0) + 1;
    return acc;
  }, {})).sort((a, b) => b[1] - a[1]);
  const trade = (w: Worker) => (w.metier ? meta.metiers[w.metier]?.[lang] ?? w.metier : "—");
  // the weeks the calendar actually shows (the data's window counts whole weeks from the list's Monday; a mission
  // ending on the Monday after it opens one more)
  const groupWeeks = groups.length ? dayIndex(from, groups[groups.length - 1].monday) / 7 + 1 : r.fenetre_semaines;

  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{t.redeploy.title}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{f.title}</span>
      </h1>
      <p className="fx-muted mt-4 max-w-[62ch] text-[16px] leading-relaxed">{f.lead.replace("{n}", String(groupWeeks))}</p>

      <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section className="fx-raised p-6" data-testid="redeploy-rate" aria-labelledby="fx-fin-rate">
          <h2 id="fx-fin-rate" className="fx-caps fx-muted">{f.rateTitle}</h2>
          <p className="mt-4"><span className="fx-tag fx-mention" data-kind="fictif">{f.mention}</span></p>
          <p className="mt-4 text-[18px] leading-snug">
            {f.rateSentence.replace("{k}", String(r.redeployes)).replace("{n}", String(r.fins_de_mission))}
          </p>
          <p className="fx-muted mt-3 text-[14px] leading-relaxed">{t.redeploy.note}</p>
          <p className="mt-2 text-[14px]"><Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/mesures/#REDEP-1`}>{t.fx.howMeasure}</Link></p>
        </section>
        <section className="fx-card p-6" aria-labelledby="fx-fin-none">
          <h2 id="fx-fin-none" className="fx-caps fx-muted">{f.noneTitle.replace("{n}", String(r.fins_de_mission - r.redeployes))}</h2>
          <ul className="mt-3 border-t border-[var(--fx-line)]">
            {motifs.map(([code, n]) => (
              <li key={code} className="flex items-baseline justify-between gap-4 border-b border-[var(--fx-line)] py-3 text-[15px]">
                <span>{t.redeploy.motif[code as keyof typeof t.redeploy.motif] ?? code}</span>
                <span className="fx-mono fx-muted">{n}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <p className="mt-10 flex flex-wrap gap-x-6 gap-y-2 text-[13px]" aria-hidden>
        <span className="inline-flex items-center gap-2"><i className="fx-key-mission" />{f.legendMission}</span>
        <span className="inline-flex items-center gap-2"><i className="fx-key-free" />{f.legendFree}</span>
        <span className="inline-flex items-center gap-2"><i className="fx-key-maybe" />{f.legendMaybe}</span>
        <span className="inline-flex items-center gap-2"><i className="fx-key-need" />{f.legendNeed}</span>
        <span className="inline-flex items-center gap-2"><i className="fx-key-weekend" />{f.legendWeekend}</span>
      </p>

      {groups.map((g) => (
        <section key={g.monday} className="mt-10" aria-labelledby={`fx-fin-${g.monday}`}>
          <h2 id={`fx-fin-${g.monday}`} className="fx-caps fx-muted flex flex-wrap items-center gap-3">
            {f.weekOf.replace("{date}", fmtDate(g.monday))} <span className="fx-tag" data-kind="fictif">{f.fictionalWorkers}</span>
          </h2>
          <div className="fx-fin-row mt-3 px-4 sm:px-5" aria-hidden>
            <span className="hidden lg:block" />
            <div className="fx-lane-axis">
              {mondays.map((m, k) => <span key={m} className="fx-mono" style={{ left: `${(k * 7 * 100) / days}%` }}>{fmtDayMonth(m)}</span>)}
            </div>
          </div>
          <ol className="mt-1 space-y-3">
            {g.workers.map((w) => {
              const p = w.proposition;
              return (
                <li key={w.candidate_id} className="fx-card fx-fin-row p-4 sm:p-5" data-testid="worker">
                  <WorkerHead w={w} t={t} trade={trade} />
                  <div>
                  <div className="mt-3 lg:mt-0"><Lane from={from} days={days} end={w.fin_mission} need={p ? p.semaine : null} /></div>
                  {p ? (
                    <div className="mt-3">
                      <p className="fx-muted text-[13px]">{f.next}</p>
                      <Link className="fx-link inline-flex min-h-11 min-w-11 items-center text-[16px]" href={`/${lang}/entreprise/${p.entreprise}/`}>{usageName(p.nom)}</Link>
                      <p className="fx-muted text-[14px] leading-snug">
                        {p.ville} · {f.needFrom.replace("{date}", fmtDate(p.semaine))} · {f.distance.replace("{n}", p.distance_km.toFixed(0)).replace(" km", "\u00a0km")}
                      </p>
                      {p.contact_des ? <p className="fx-muted mt-1 text-[13px]">{t.redeploy.contactFrom.replace("{date}", fmtDate(p.contact_des))}</p> : null}
                    </div>
                  ) : (
                    <p className="fx-muted mt-3 text-[15px]">
                      {t.redeploy.notPlaced}{t.label.colon} {w.motif_code ? t.redeploy.motif[w.motif_code] : "—"}
                    </p>
                  )}
                  </div>
                </li>
              );
            })}
          </ol>
        </section>
      ))}
    </div>
  );
}
