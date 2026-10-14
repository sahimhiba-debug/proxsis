import live from "@/data/direct/matin.json";
import type { Dict } from "@/i18n/dictionaries";
import { morningView } from "@/lib/chaqueMatin";
import { fmtDate } from "@/lib/dates";
import type { LiveFile } from "@/lib/types";
import { MorningIris, MorningSound } from "./MorningIris";

/**
 * « Chaque matin, en direct de simap » (suite 10, § 2; « Cette semaine, en direct de simap » from 07.10.2026 to
 * 13.10.2026): a section apart, written every working day from 6 a.m. by an automatic job only when every check passes
 * (python/src/proxsis/live_week.py) — on Monday the week that ended, from Tuesday to Friday the day before. It shows
 * its own date; if a later reading failed, it keeps this last valid version. The Monday list, the presentation and
 * CLAIMS never depend on it; « depuis hier » shows facts, never a score.
 * A laureate already in the list of the week is said so (« dans votre liste »): the list does not change during the week.
 * Conditions of the simap API (ch. 5 al. 2): what simap published sits in its own frame, unchanged, with the mention right
 * under it; our own sentences stay outside; the corrections, revocations and abandonments of the period are passed on.
 * Iris: one toc when the section shows something new, and only if the sound is on; then she keeps watch one turn and
 * stops, since there is text to read (suite 8, complement, § 8).
 */
export function ChaqueMatin({ t, list, file = live as LiveFile }: { t: Dict; list: readonly string[]; file?: LiveFile }) {
  const l = t.fx.live;
  const view = morningView(file, new Set(list));
  const mention = <p className="fx-muted mt-4 text-[14px]" data-testid="live-mention">{t.banner.simap} « {file.mention} »</p>;
  return (
    <section className="mt-16" aria-labelledby="fx-live" data-testid="chaque-matin" data-etat={view.state}>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="flex items-end gap-3">
          <MorningIris nouveau={view.state === "nouveau"} lecture={view.state === "attente" ? null : view.lu} label={l.iris} />
          <h2 id="fx-live" className="fx-display text-[26px]">{l.title}</h2>
        </div>
        {view.state === "attente" ? null : (
          <MorningSound nouveau={view.state === "nouveau"} labels={{ on: l.soundOn, off: l.soundOff, sound: l.sound }} />
        )}
      </div>
      {view.state === "attente" ? (
        <>
          <p className="fx-muted mt-3 max-w-[62ch] text-[15px]">{l.waiting}</p>
          {mention}
        </>
      ) : (
        <>
          <p className="fx-mono fx-muted mt-2 text-[13px]" data-testid="live-period">
            {(view.mode === "semaine" ? l.periodWeek : l.periodDay).replace("{du}", fmtDate(view.periode.du))
              .replace("{au}", fmtDate(view.periode.au)).replace("{veille}", fmtDate(view.periode.au)).replace("{date}", fmtDate(view.lu))}
          </p>
          <p className="fx-muted mt-2 max-w-[62ch] text-[15px]">{l.apart}</p>
          <div className="fx-card mt-5 p-4 sm:p-5" data-testid="live-published" data-nouveau={view.state === "nouveau"}>
            <p className="fx-caps fx-muted">{l.published}</p>
            {view.items.length ? (
              <ol className="mt-3 border-t border-[var(--fx-line)]">
                {view.items.map((c, i) => (
                  <li key={`${c.url}-${i}`} className="border-b border-[var(--fx-line)] py-3" data-testid="live-contract">
                    <p className="fx-caps fx-muted">{fmtDate(c.date)}{c.commune ? ` · ${c.commune}` : ""}</p>
                    <p className="mt-1 text-[15px] leading-snug">
                      <a className="fx-link" href={c.url} target="_blank" rel="noopener noreferrer">«&nbsp;{c.titre}&nbsp;»</a>
                    </p>
                    <p className="fx-muted mt-1 text-[13px]">
                      {c.laureats.length ? `${l.winners}${t.label.colon} ${c.laureats.map((w) => w.nom).join(", ")}` : null}
                      {c.adjudicateur ? `${c.laureats.length ? " · " : ""}${t.company.authority}${t.label.colon} ${c.adjudicateur}` : null}
                    </p>
                    {/* our own mark, apart from what simap published: this company is in the list of the week */}
                    {c.laureats.filter((w) => w.inList).map((w) => (
                      <p key={w.id} className="mt-2"><span className="fx-tag" data-kind="liste" data-testid="in-list">
                        {c.laureats.length > 1 ? `${w.nom} · ` : ""}{l.inList}</span></p>
                    ))}
                  </li>
                ))}
              </ol>
            ) : (
              <p className="mt-3 text-[15px]" data-testid="live-nothing">{view.mode === "semaine" ? l.none : l.nothingNew}</p>
            )}
            {view.total > view.items.length ? (
              <p className="fx-muted mt-3 text-[13px]">{l.more.replace("{n}", String(view.total - view.items.length))}</p>
            ) : null}
            {view.corrections.length ? (
              <div className="mt-5" data-testid="live-corrections">
                <p className="fx-caps fx-muted">{l.corrections}</p>
                <ol className="mt-2">
                  {view.corrections.map((c, i) => (
                    <li key={`${c.url}-${c.date}-${i}`} className="py-2 text-[14px]">
                      <span className="fx-muted">{fmtDate(c.date)} · {l.kind[c.type]}</span>{" "}
                      <a className="fx-link" href={c.url} target="_blank" rel="noopener noreferrer">«&nbsp;{c.titre}&nbsp;»</a>
                    </li>
                  ))}
                </ol>
              </div>
            ) : null}
            {mention}
          </div>
        </>
      )}
    </section>
  );
}
