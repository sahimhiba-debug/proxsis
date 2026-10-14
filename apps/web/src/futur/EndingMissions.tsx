import Link from "next/link";
import type { Dict } from "@/i18n/dictionaries";
import { fmtDate } from "@/lib/i18n";
import type { Worker } from "@/lib/types";
import { usageName } from "./display";
import { KindTag } from "./KindTag";
import { dayIndex, Lane } from "./Lane";
import { WorkerHead } from "./WorkerHead";

const DAYS = 28; // the four weeks from the demo Monday, the window of « Fin de mission »

/**
 * « Fins de mission à replacer », the second block of « Ma semaine » (Hiba, 07.10.2026): the consultant's own temps
 * whose mission ends soon (fictional, marked), each with the next mission possible in dots — a company that has just
 * won a public contract (real) and will probably need the trade (estimated, to confirm). No figure of gain here: the
 * gain stays a hypothesis of the presentation's calculator.
 */
export function EndingMissions({ workers, from, lang, t, trade }: {
  workers: Worker[]; from: string; lang: string; t: Dict; trade: (w: Worker) => string;
}) {
  const f = t.fx.fin;
  if (!workers.length) return null;
  return (
    <section className="mt-16" aria-labelledby="fx-ending" data-testid="ending-missions">
      <h2 id="fx-ending" className="fx-display flex flex-wrap items-center gap-3 text-[26px]">
        {t.fx.ending.title} <KindTag kind="fictif" t={t} />
      </h2>
      <p className="fx-muted mb-5 mt-2 max-w-[60ch] text-[15px]">{t.fx.ending.line}</p>
      <ol className="space-y-3">
        {workers.map((w) => {
          const p = w.proposition;
          return (
            <li key={w.candidate_id} className="fx-card fx-fin-row p-4 sm:p-5">
              <WorkerHead w={w} t={t} trade={trade} />
              <div>
                <div className="mt-3 lg:mt-0">
                  <Lane from={from} days={Math.max(DAYS, Math.ceil((dayIndex(from, p?.semaine ?? from) + 7) / 7) * 7)}
                    end={w.fin_mission} need={p ? p.semaine : null} />
                </div>
                {p ? (
                  <div className="mt-3">
                    <p className="fx-muted text-[13px]">{f.next}</p>
                    <Link className="fx-link inline-flex min-h-11 min-w-11 items-center text-[16px]" href={`/${lang}/entreprise/${p.entreprise}/`}>{usageName(p.nom)}</Link>
                    <p className="fx-muted text-[14px] leading-snug">{p.ville} · {f.needFrom.replace("{date}", fmtDate(p.semaine))}</p>
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
      <p className="mt-4 text-[14px]">
        <Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/redeploiement/`}>{t.fx.ending.all}</Link>
      </p>
    </section>
  );
}
