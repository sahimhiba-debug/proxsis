"use client";

// Visit, time 1 (brief « à distance », 4.1): the Valais of the swisstopo commune boundaries; the director touches a
// commune (or picks it in the list: on a phone, and for the keyboard) and sees the companies active in our data, those
// whose seat is there and the contracts published there kept apart, only for companies whose dossier passes every
// check (territoire.json). Prepared example: Saxon. Opening a company turns the map into its dossier.
import contours from "@/data/presentation/communes_vs.json";
import { fmtDate } from "@/lib/dates";
import { PButton } from "@/presentation/ui";
import { VISIT_COPY } from "./copy";
import type { VisitAction } from "./state";
import type { TerritoryData } from "./territory";
import { AGENCE_EXEMPLE, AGENCES, autour, centre } from "./agences";
import type { ThisWeek } from "./moments";
import { CetteSemaine } from "./NouveauxMoments";

const [X0, Y0, X1, Y1] = contours.meta.bbox;
const VIEW = `${X0 - 8} ${Y0 - 8} ${X1 - X0 + 16} ${Y1 - Y0 + 16}`;
const NAMES: Record<string, string> = Object.fromEntries(contours.communes.map((c) => [String(c.bfs), c.nom]));
const SHOWN_CONTRACTS = 4;

const CENTRES: Record<string, [number, number]> = Object.fromEntries(contours.communes.map((c) => [String(c.bfs), centre(c.d)]));
const SHOWN_AROUND = 6;

export function CarteScene({ territory, lang, commune, agence, week, around, thisWeek, dispatch }: {
  territory: TerritoryData; lang: "fr" | "de"; commune: string | null; agence: string | null;
  week: string[]; // the ten companies of the week's list, in its order
  thisWeek: ThisWeek; // « Cette semaine » (brief of 07.10.2026, § 3.3)
  around?: Record<string, string[]>; // the agency's week in the application, in its order (B7): the same list
  dispatch: (a: VisitAction) => void;
}) {
  const t = VISIT_COPY[lang].carte;
  const bfs = commune && territory.communes[commune] ? commune : territory.exemple.commune;
  const place = territory.communes[bfs];
  const companies = territory.entreprises;
  const active = Object.keys(territory.communes).sort((a, b) => NAMES[a].localeCompare(NAMES[b], lang));
  // the prepared company first, then by name
  const seat = [...place.siege].sort((a, b) => Number(b === territory.exemple.entreprise) - Number(a === territory.exemple.entreprise)
    || companies[a].nom.localeCompare(companies[b].nom, lang));
  const open = (id: string) => {
    dispatch({ type: "company", id });
    dispatch({ type: "next" });
  };
  const ag = AGENCES.find((x) => x.id === agence) ?? AGENCES.find((x) => x.id === AGENCE_EXEMPLE)!;
  // the application's week of this agency, in its order (one list, B7); the distance between communes only if it is missing
  const fromApp = (around?.[ag.id] ?? []).filter((id) => id in companies);
  const near = (fromApp.length ? fromApp : autour(week.filter((id) => id in companies), (id) => String(companies[id].commune_siege ?? ""),
    CENTRES, ag, (id) => companies[id].nom)).slice(0, SHOWN_AROUND);
  const tags = (id: string) => [companies[id].guide ? t.toValidate : null, companies[id].consortium ? t.consortium : null]
    .filter(Boolean).join(" · ");
  return (
    <div className="v-carte" data-testid="carte" data-commune={bfs}>
      <figure className="v-map">
        {/* the map is for the eye and the finger; the list beside it is the same choice for the keyboard */}
        <svg className="d-map" viewBox={VIEW} aria-hidden>
          {contours.communes.map((c) => {
            const id = String(c.bfs);
            const on = id in territory.communes;
            return (
              <path key={id} className="commune" d={c.d} fillRule="evenodd" data-on={on || undefined} data-selected={id === bfs || undefined}
                onClick={on ? () => dispatch({ type: "commune", bfs: id }) : undefined}>
                <title>{c.nom}</title>
              </path>
            );
          })}
          {contours.canton ? <path className="canton" d={contours.canton} /> : null}
          {AGENCES.map((x) => {
            const [cx, cy] = CENTRES[x.bfs];
            return (
              <g key={x.id} className="v-agence" data-on={x.id === ag.id || undefined}>
                <rect x={cx - 6} y={cy - 6} width={12} height={12} rx={2} />
                <text x={cx + 10} y={cy - 8}>{x.nom}</text>
              </g>
            );
          })}
        </svg>
        <figcaption className="d-small d-muted">{t.hint}</figcaption>
      </figure>
      <div className="v-panel">
        <CetteSemaine w={thisWeek} lang={lang} />
        <div className="v-agences" role="group" aria-label={t.agency}>
          <p className="d-small d-muted">{t.agency}</p>
          <div className="v-agences-choix">
            {AGENCES.map((x) => (
              <PButton key={x.id} variant="option" className="v-agence-btn" aria-pressed={x.id === ag.id}
                onClick={() => dispatch({ type: "agence", id: x.id })} data-testid={`agence-${x.id}`}>
                {x.nom}
              </PButton>
            ))}
          </div>
        </div>
        <section aria-labelledby="v-around" data-testid="around">
          <h2 id="v-around" className="d-lead">
            {t.around.replace("{name}", ag.nom)}{agence ? null : <span className="d-caps d-muted v-example"> · {VISIT_COPY[lang].example}</span>}
          </h2>
          <ul className="v-companies">
            {near.map((id) => (
              <li key={id}>
                <PButton variant="option" onClick={() => { dispatch({ type: "commune", bfs: String(companies[id].commune_siege) }); open(id); }}
                  data-testid="around-company">
                  <span>
                    <span className="block">{companies[id].nom}</span>
                    <span className="d-small d-muted">{companies[id].ville}{tags(id) ? ` · ${tags(id)}` : ""}</span>
                  </span>
                  <small>{t.open} →</small>
                </PButton>
              </li>
            ))}
          </ul>
          <p className="d-small d-muted">{t.agencyNote}</p>
        </section>
        <label className="d-field v-commune-field">
          <span>{t.pick}</span>
          <select value={bfs} onChange={(e) => dispatch({ type: "commune", bfs: e.target.value })}>
            {active.map((id) => <option key={id} value={id}>{NAMES[id]}</option>)}
          </select>
        </label>
        <h2 className="d-sub" data-testid="commune-name">
          {NAMES[bfs]}{commune ? null : <span className="d-caps d-muted v-example"> · {VISIT_COPY[lang].example}</span>}
        </h2>
        <p className="d-caps d-muted">{t.inOurData}</p>
        <section aria-labelledby="v-seat">
          <h3 id="v-seat" className="d-small d-muted">{t.seat}</h3>
          {seat.length ? (
            <ul className="v-companies">
              {seat.map((id, i) => (
                <li key={id} data-lumiere={i === 0 ? "repere" : undefined}>
                  <PButton variant="option" onClick={() => open(id)} data-testid="seat-company">
                    <span>
                      <span className="block">{companies[id].nom}</span>
                      <span className="d-small d-muted">{companies[id].ville}{tags(id) ? ` · ${tags(id)}` : ""}</span>
                    </span>
                    <small>{t.open} →</small>
                  </PButton>
                </li>
              ))}
            </ul>
          ) : <p className="d-small d-muted">{t.noSeat}</p>}
        </section>
        <section aria-labelledby="v-contracts">
          <h3 id="v-contracts" className="d-small d-muted">{t.contracts}</h3>
          {place.marches.length ? (
            <ul className="v-contracts">
              {place.marches.slice(0, SHOWN_CONTRACTS).map((m) => (
                <li key={`${m.id}-${m.url}`} className="d-small">
                  <span className="d-num d-muted">{fmtDate(m.date)}</span>{" "}
                  <button className="v-link" onClick={() => open(m.id)}>{companies[m.id].nom}</button>
                  <span className="d-muted"> · {t.seatOf.replace("{town}", companies[m.id].ville ?? "")}</span>
                  <span className="block d-muted">« {m.titre} »</span>
                </li>
              ))}
              {place.marches.length > SHOWN_CONTRACTS ? (
                <li className="d-small d-muted">{t.more.replace("{n}", String(place.marches.length - SHOWN_CONTRACTS))}</li>
              ) : null}
            </ul>
          ) : <p className="d-small d-muted">{t.noContract}</p>}
        </section>
        <p className="d-small d-muted">{t.checks}</p>
      </div>
    </div>
  );
}
