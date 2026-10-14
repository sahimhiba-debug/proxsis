// « Qui proposer ? » (brief of 07.10.2026, § 3.1; suite 2, § 4: at the heart of the story): beside the reason to call,
// three fictional temps who match the estimated need, as the application proposes them (src/visite/proposer.ts), each
// with the trade, the work permit, the availability and the distance; « Intérimaires fictifs »; the reporting obligation
// in the application's words when the post is subject to it. No team size: CLAIMS has no line for it, so nothing shows.
// Suite 9, Q08: what enters the choice and what does not (gender, age, nationality), and the age gap measured (EQ-1).
import { fmtDate } from "@/lib/dates";
import { VISIT_COPY } from "./copy";
import type { Proposer } from "./proposer";

export function QuiProposer({ who, lang, story = false }: { who: Proposer; lang: "fr" | "de"; story?: boolean }) {
  const t = VISIT_COPY[lang].carnet;
  return (
    <div className="v-who" role="region" aria-label={t.who} data-testid="who-to-propose">
      <h3 className="d-lead v-who-head">{t.who} <span className="px-statut">{t.fictional}</span></h3>
      {story ? <p className="d-small v-who-story">{t.whoStory}</p> : null}
      <p className="d-small d-muted">{t.whoNeed.replace("{metier}", who.metier[lang]).replace("{date}", fmtDate(who.debut))}</p>
      <ul className="v-who-list">
        {who.interimaires.map((w) => (
          <li key={w.id} className="v-who-card" data-testid="who-row">
            <span className="v-who-name">{t.worker.replace("{n}", w.id.replace(/^cand-/, ""))}</span>
            <span className="d-small">
              {who.metier[lang]} · {t.permit.replace("{p}", w.permis)} · {t.from.replace("{date}", fmtDate(w.dispo))} · {t.km.replace("{n}", String(Math.round(w.km)))}
            </span>
          </li>
        ))}
      </ul>
      {who.contactLine ? <p className="d-small" data-testid="who-announce">{who.contactLine[lang]}</p> : null}
      <p className="d-small">{t.yourPool}</p>
      <p className="d-small d-muted" data-testid="who-equity">{t.equite}</p>
    </div>
  );
}
