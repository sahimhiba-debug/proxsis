import Link from "next/link";
import { CarnetCount } from "@/futur/CarnetPanel";
import type { Dict } from "@/i18n/dictionaries";
import { agencies, dashboard, lists, meta } from "@/lib/data";
import { consultantLabel } from "@/lib/roleLabel";
import type { Kpi } from "@/lib/types";
import { KindTag, type DataKind } from "./KindTag";
import { Tile } from "./Tile";

const kindOf = (k: Kpi): DataKind => (k.type === "RÉEL" ? "reel" : "fictif");
const decimalsOf = (v: number) => (Number.isInteger(v) ? 0 : 1); // measured values keep the decimal of CLAIMS (audit M3)

/**
 * The agency dashboard, futurisme suisse: the agency's activity (fictional until Flexsis provides its history), its
 * consultants (fictional), then what was measured on real public data (only that). Every tile says what it is.
 */
export function AgencyView({ ids, lang, t }: { ids: string[]; lang: string; t: Dict }) {
  const a = t.agency;
  const f = t.fx.agence;
  const bat = lists.batiment?.backtest;
  // only what was measured on real public data: a figure of the fictional world never sits under « mesuré »
  const measured = dashboard.indicateurs.filter((k) => k.valeur !== null && k.type === "RÉEL");
  const label: Record<string, string> = { precision_liste_batiment: f.precision, laureats_nouveaux: f.newcomers };
  const note = (code: string) => (code === "precision_liste_batiment" && bat?.taux_de_base != null
    ? f.versus.replace("{p}", String(bat.taux_de_base).replace(".", lang === "fr" ? "," : ".")) : undefined);
  return (
    <>
      {ids.map((id) => {
        const k = dashboard.agences[id];
        const single = ids.length === 1;
        return (
          <section key={id} className="mt-10" aria-labelledby={`fx-agence-${id}`}>
            <h2 id={`fx-agence-${id}`} className="fx-caps fx-muted mb-4">{single ? f.activity : agencies[id].nom.replace(/^Flexsis\s+/, "")}</h2>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <Tile label={a.calls} value={k.appels.valeur ?? 0} kind={kindOf(k.appels)} claim={k.appels.claim} lang={lang} t={t} />
              <Tile label={a.meetings} value={k.rendez_vous.valeur ?? 0} kind={kindOf(k.rendez_vous)} claim={k.rendez_vous.claim} lang={lang} t={t} />
              <Tile label={a.filled} value={k.missions_pourvues.valeur ?? 0} kind={kindOf(k.missions_pourvues)} claim={k.missions_pourvues.claim} lang={lang} t={t} />
              <Tile label={a.delay} value={k.delai_moyen_jours.valeur ?? 0} decimals={decimalsOf(k.delai_moyen_jours.valeur ?? 0)}
                kind={kindOf(k.delai_moyen_jours)} claim={k.delai_moyen_jours.claim} lang={lang} t={t} />
            </div>
            {single ? (
              <ul className="mt-6 border-t border-[var(--fx-line)]" aria-label={f.consultants}>
                {agencies[id].consultants.map((c) => (
                  <li key={c.code} className="flex items-center justify-between gap-3 border-b border-[var(--fx-line)] py-1">
                    <Link className="fx-link inline-flex min-h-11 items-center text-[15px]" href={`/${lang}/semaine/${c.code}/`}>
                      {consultantLabel(t, lang, c.specialite)}
                    </Link>
                    <KindTag kind="fictif" t={t} />
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        );
      })}
      <p className="fx-muted mt-4 text-[13px]">{a.mockNote}</p>

      <section className="mt-14" aria-labelledby="fx-agence-measured">
        <h2 id="fx-agence-measured" className="fx-caps fx-muted mb-4">{f.measured}</h2>
        {/* autant de colonnes que de mesures (deux aujourd'hui) : pas de colonne vide sur une tablette */}
        <div className={`grid grid-cols-1 gap-3 ${measured.length === 2 ? "sm:grid-cols-2" : "sm:grid-cols-3"}`}>
          {measured.map((k) => {
            const pct = k.unite === "%" ? (k.valeur as number) : (k.valeur as number) * 100;
            return <Tile key={k.code} label={label[k.code] ?? k.code} value={pct} decimals={1} suffix=" %" kind={kindOf(k)}
              claim={k.claim} note={note(k.code)} lang={lang} t={t} />;
          })}
        </div>
        <p className="fx-muted mt-4 text-[13px]">{f.caveat}</p>
      </section>
      <div className="fx-muted mt-10 text-[14px]">
        <CarnetCount lang={lang === "de" ? "de" : "fr"} week={meta.semaine} />
      </div>
    </>
  );
}
