"use client";

// The visit's new moments (brief of 07.10.2026, § 3.2 to 3.4). Every number and every fact comes from its file
// (moments.ts, written by `proxsis moments-presentation` and refused there when it differs from CLAIMS); the
// sentences are in copy.ts. Nothing here computes.
import type { ReactNode } from "react";
import { fmtDate } from "@/lib/dates";
import { VISIT_COPY } from "./copy";
import type { Accelerating, GuidedFacts, ThisWeek } from "./moments";

type Lang = "fr" | "de";

/** A sentence with its values, the figures set off (bold) inside the unchanged words. */
const fillStrong = (text: string, values: Record<string, string | number>, strong: string[] = []): ReactNode[] =>
  text.split(/(\{\w+\})/).map((part, i) => {
    const k = /^\{(\w+)\}$/.exec(part)?.[1];
    if (!k || !(k in values)) return part;
    return strong.includes(k) ? <strong key={i} className="d-num">{values[k]}</strong> : <span key={i}>{values[k]}</span>;
  });

/** « Cette semaine » (§ 3.3, CLAIMS PRES-SEMAINE-1): what Proxsis read and kept the week before the first Monday, after
 *  Hiba's sentence on the mornings and the Monday (suite 10, § 2). The week is incomplete in the frozen data: said under
 *  the line, with where the ten calls really come from. */
export function CetteSemaine({ w, lang }: { w: ThisWeek; lang: Lang }) {
  const t = VISIT_COPY[lang].moments;
  // « du 21 au 27 septembre 2026 » / « vom 21. bis 27. September 2026 »: the month and the year once, at the end
  const du = new Date(`${w.semaine.du}T00:00:00Z`), au = new Date(`${w.semaine.au}T00:00:00Z`);
  const locale = lang === "fr" ? "fr-CH" : "de-CH";
  const day = (d: Date) => new Intl.DateTimeFormat(locale, { day: "numeric", timeZone: "UTC" }).format(d) + (lang === "de" ? "." : "");
  const full = (d: Date) => new Intl.DateTimeFormat(locale, { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }).format(d);
  const sameMonth = du.getUTCMonth() === au.getUTCMonth();
  return (
    <p className="v-semaine" data-testid="cette-semaine">
      <span className="block" data-testid="chaque-matin-visite">{t.morning}</span>
      <span className="block">{fillStrong(t.week, { du: sameMonth ? day(du) : full(du), au: full(au), n: w.lues.total,
        m: w.retenues.total, k: w.appels }, ["n", "m", "k"])}</span>
      <span className="block d-small d-muted" data-testid="cette-semaine-note">{t.weekNote.replace("{k}", String(w.appels))}</span>
    </p>
  );
}

/** « Plusieurs faits vont dans le même sens » (§ 3.2): the published facts of a guided dossier, each with its date and
 *  its source, under the publication. A Bulletin officiel request shows the company's role only (no applicant, no
 *  link); the last award is the publication above, said so rather than repeated as a link. */
export function FaitsConcordants({ f, sources, paperUrl, lang, onSource }: {
  f: GuidedFacts["dossiers"][string]; sources: GuidedFacts["sources"]; paperUrl: string; lang: Lang; onSource: (url: string) => void;
}) {
  const t = VISIT_COPY[lang].moments;
  const bo = `${sources.bulletin_officiel.nom[lang]}, ${sources.bulletin_officiel.mention[lang]}`;
  const plans = f.faits.some((x) => x.type === "demande_autorisation");
  return (
    <section className="v-faits" aria-labelledby="v-faits-titre" data-testid="faits">
      <h3 id="v-faits-titre">{t.factsTitle}</h3>
      <p className="v-faits-phrase">{t.facts}</p>
      <p className="d-small" data-testid="faits-compte">
        {t.factsCount.replace("{n}", String(f.marches_52s.nombre)).replace("{date}", fmtDate(f.marches_52s.au))}
        <span className="d-muted"> · {sources.simap.nom[lang]}</span>
      </p>
      <ul>
        {f.faits.map((x, i) => (
          <li key={`${x.type}-${x.date}-${i}`} data-testid="fait" data-type={x.type}>
            <span className="v-fait-date d-num">{fmtDate(x.date)}</span>
            {x.type === "marche" ? (
              <>
                <span className="v-fait-quoi">
                  {x.libelle[lang]}
                  {x.adjudicateur ? <span className="block d-muted">{x.adjudicateur[lang]}</span> : null}
                  {x.objet ? <span className="block d-muted">{x.objet[lang]}</span> : null}
                  {x.titre_original ? <span className="block d-muted">« {x.titre_original} »</span> : null}
                  <span className="v-fait-source">
                    {x.url === paperUrl ? t.factsAbove : (
                      <button className="v-link" onClick={() => onSource(x.url)}>{sources.simap.nom[lang]} · {t.factsSource}</button>
                    )}
                  </span>
                </span>
              </>
            ) : (
              <>
                <span className="v-fait-quoi">
                  {x.libelle[lang]}<span className="block d-muted">{x.commune}</span>
                  <span className="v-fait-source">{bo}</span>
                </span>
              </>
            )}
          </li>
        ))}
      </ul>
      {plans ? <p className="d-small d-muted" data-testid="faits-plans">{t.factsPlans}</p> : null}
    </section>
  );
}

/** « Celles qui accélèrent » (§ 3.4, CLAIMS REEL-SURPRISE), after the result of the list: descriptive rates over every
 *  Monday of the measure, with the rule and the nuance of CLAIMS. */
export function Accelerent({ a, lang }: { a: Accelerating; lang: Lang }) {
  const t = VISIT_COPY[lang].moments;
  return (
    <div className="v-accel" data-testid="accelerent" data-revealed>
      <p>{fillStrong(t.accel, { n: a.perimetre.semaines, h: a.perimetre.horizon_semaines, p: a.accelerent.affiche[lang],
        q: a.hors_des_dix.affiche[lang] }, ["p", "q"])}</p>
      <p className="d-small d-muted">{t.accelRule.replace("{rule}", a.regle[lang])} {a.nuance[lang]}</p>
    </div>
  );
}
