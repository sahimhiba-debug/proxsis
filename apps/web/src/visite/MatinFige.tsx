"use client";

// « Choisissez une date » (suite 10, § 2): the section « Chaque matin, en direct de simap » of the chosen Monday, frozen
// (src/data/presentation/matins.json, `proxsis matins-presentation`): the Valais construction contracts awarded during
// the week that ended the day before, as simap published them, and only what was published before that Monday. Folded:
// it is opened by whoever wants it, and the timed path of the visit does not change. « dans votre liste »: a company of
// the ten of that Monday. What simap published sits in its own frame, our mark apart, the mention right under it.
import { fmtDate } from "@/lib/dates";
import { frenchSpaces } from "@/lib/typo";
import { morningView } from "@/lib/chaqueMatin";
import { COPY } from "@/presentation/copy";
import type { FrozenMornings } from "@/lib/types";
import { VISIT_COPY } from "./copy";

export function MatinFige({ data, monday, ten, lang, onSource }: {
  data: FrozenMornings; monday: string; ten: readonly string[]; lang: "fr" | "de"; onSource: (url: string) => void;
}) {
  const frozen = data.lundis[monday];
  if (!frozen) return null;
  const t = VISIT_COPY[lang].matin;
  const view = morningView({ schema: 2, etat: "a_jour", mode: "semaine", periode: frozen.periode, mis_a_jour_le: monday, source: data.source,
    mention: data.mention, total: frozen.total, marches: frozen.marches }, new Set(ten));
  if (view.state === "attente") return null;
  const quote = (s: string) => (lang === "fr" ? frenchSpaces(`« ${s} »`, "fr") : `«${s}»`);
  const colon = lang === "fr" ? "\u00a0: " : ": ";
  return (
    <details className="v-matin" data-testid="matin-fige" data-monday={monday}>
      <summary>{t.summary}</summary>
      <p className="d-small d-muted">{t.period.replace("{du}", fmtDate(view.periode.du)).replace("{au}", fmtDate(view.periode.au))}</p>
      <div className="v-matin-cadre">
        <p className="d-caps d-muted">{t.published}</p>
        {view.items.length ? (
          <ol>
            {view.items.map((c, i) => (
              <li key={`${c.url}-${i}`} data-testid="matin-fige-contrat">
                <span className="d-small d-muted block">{fmtDate(c.date)}{c.commune ? ` · ${c.commune}` : ""}</span>
                <button type="button" className="v-link v-matin-titre" onClick={() => onSource(c.url)}>{quote(c.titre)}</button>
                <span className="d-small d-muted block">
                  {c.laureats.length ? `${t.winners}${colon}${c.laureats.map((w) => w.nom).join(", ")}` : null}
                  {c.adjudicateur ? `${c.laureats.length ? " · " : ""}${t.authority}${colon}${c.adjudicateur}` : null}
                </span>
                {c.laureats.filter((w) => w.inList).map((w) => (
                  <span key={w.id} className="v-matin-liste" data-testid="in-list">{c.laureats.length > 1 ? `${w.nom} · ` : ""}{t.inList}</span>
                ))}
              </li>
            ))}
          </ol>
        ) : <p className="d-small">{t.none}</p>}
        {view.total > view.items.length ? <p className="d-small d-muted">{t.more.replace("{n}", String(view.total - view.items.length))}</p> : null}
        {/* the mention of simap, as everywhere in the visit (presentation/Frame.tsx, SimapLine), with its own test id: the
            footer of the step keeps the one « simap-mention » of the screen */}
        <p className="d-small d-muted" data-testid="matin-fige-mention">
          {COPY[lang].source.mention}{COPY[lang].source.mentionOriginal}{colon}«&nbsp;{data.mention}&nbsp;»{lang === "de" ? ` ${COPY[lang].source.translation}` : ""}
        </p>
      </div>
    </details>
  );
}
