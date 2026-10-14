"use client";

import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState, type ReactNode } from "react";
import { fmtDayMonth } from "@/lib/dates";
import { labelSide } from "./region";

export interface MapPlace { ville: string; left: number; top: number; companies: string[] }
export interface MapContract { company: string; name: string; ville: string; date: string; titre: string }
export interface MapWeek { from: string; to: string }
interface WeekMapLabels {
  week: string; prev: string; next: string; slider: string; signals: string; signal1: string; none: string;
  listTitle: string; recent: string; company: string; agency: string; colon: string;
}

const pct = (v: number) => `${(v * 100).toFixed(2)}%`;
const FRAME_W = 600; // reference frame for the labels (the map scales; the labels keep their side)

/**
 * The Valais, period by period: the boundaries come from the server (children, no script), the companies of the lists
 * are quiet dots at their commune, and the communes where a contract was published in the 14 days of the chosen period
 * (the same « recent » as « Ma semaine ») breathe in copper, named, with their count when there are several. The slider
 * and the two buttons move the period by one week; the list says the same thing in words (keyboard, screen readers).
 * The buttons stay focusable at the ends (aria-disabled), so the focus is never lost.
 */
export function WeekMap({ children, ratio, places, agencies, contracts, weeks, lang, t }: {
  children: ReactNode; ratio: number; places: MapPlace[]; agencies: { name: string; left: number; top: number }[];
  contracts: MapContract[]; weeks: MapWeek[]; lang: string; t: WeekMapLabels;
}) {
  const [i, setI] = useState(weeks.length - 1); // the 14 days before the list's Monday
  const [said, setSaid] = useState(""); // announced after a button press (the slider announces its own value)
  const w = weeks[i];
  const shown = contracts.filter((c) => c.date >= w.from && c.date <= w.to).sort((a, b) => a.date.localeCompare(b.date));
  const perPlace = new Map<string, number>();
  for (const c of shown) perPlace.set(c.ville, (perPlace.get(c.ville) ?? 0) + 1);
  const label = t.week.replace("{from}", fmtDayMonth(w.from)).replace("{to}", `${fmtDayMonth(w.to)}.${w.to.slice(0, 4)}`);
  const count = shown.length === 1 ? t.signal1 : t.signals.replace("{n}", String(shown.length));
  const whole = `${label}${t.colon} ${count}`;
  const go = (k: number) => {
    const next = Math.max(0, Math.min(weeks.length - 1, k));
    if (next === i) return;
    setI(next);
    const nw = weeks[next];
    const n = contracts.filter((c) => c.date >= nw.from && c.date <= nw.to).length;
    setSaid(`${t.week.replace("{from}", fmtDayMonth(nw.from)).replace("{to}", `${fmtDayMonth(nw.to)}.${nw.to.slice(0, 4)}`)}${t.colon} ${
      n === 1 ? t.signal1 : t.signals.replace("{n}", String(n))}`);
  };
  const H = FRAME_W / ratio;
  const dots = [...places.map((p) => ({ x: p.left * FRAME_W, y: p.top * H })), ...agencies.map((a) => ({ x: a.left * FRAME_W, y: a.top * H }))];
  const named = (text: string, left: number, top: number) => {
    const a = { x: left * FRAME_W, y: top * H };
    return labelSide(a, text, dots.filter((d) => Math.hypot(d.x - a.x, d.y - a.y) > 1), FRAME_W, H);
  };
  const agencyNames = new Set(agencies.map((a) => a.name));
  const withCount = (ville: string) => ((perPlace.get(ville) ?? 0) > 1 ? `${ville} · ${perPlace.get(ville)}` : ville);
  return (
    <div className="lg:grid lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:items-start lg:gap-10">
      <div className="fx-map-col">
        <div className="fx-week-control">
          <button type="button" className="fx-tool" onClick={() => go(i - 1)} aria-disabled={i === 0} aria-label={t.prev}>
            <ChevronLeft aria-hidden className="size-4" strokeWidth={1.5} />
          </button>
          <div className="min-w-0 flex-1">
            <p data-testid="map-week">
              <span className="fx-mono block text-[13px] sm:text-[15px]">{label}</span>
              <span className="fx-caps fx-copper mt-1 block">{count}</span>
            </p>
            <input type="range" min={0} max={weeks.length - 1} step={1} value={i} onChange={(e) => { setI(Number(e.target.value)); setSaid(""); }}
              className="fx-range mt-2 w-full" aria-label={t.slider} aria-valuetext={whole} />
          </div>
          <button type="button" className="fx-tool" onClick={() => go(i + 1)} aria-disabled={i === weeks.length - 1} aria-label={t.next}>
            <ChevronRight aria-hidden className="size-4" strokeWidth={1.5} />
          </button>
          <span className="sr-only" aria-live="polite">{said}</span>
        </div>

        <div className="fx-map-frame mt-4" style={{ aspectRatio: ratio }} role="img" aria-label={whole}>
          {children}
          {places.map((p) => {
            const lit = perPlace.has(p.ville);
            return (
              <span key={p.ville} className="fx-map-dot" data-recent={lit} aria-hidden
                style={{ left: pct(p.left), top: pct(p.top), ["--s" as string]: lit ? "8px" : "5px" }}>
                {lit ? <span className="fx-map-pulse" /> : null}
                {/* a commune with an agency is named by the agency's label */}
                {lit && !agencyNames.has(p.ville) ? (
                  <span className="fx-caps fx-copper fx-map-label" data-side={named(withCount(p.ville), p.left, p.top)}>{withCount(p.ville)}</span>
                ) : null}
              </span>
            );
          })}
          {agencies.map((a) => (
            <span key={a.name} className="fx-map-home" style={{ left: pct(a.left), top: pct(a.top) }} aria-hidden>
              <span className={`fx-caps fx-map-label${perPlace.has(a.name) ? " fx-copper" : ""}`} data-side="above">{withCount(a.name)}</span>
            </span>
          ))}
        </div>
        <p className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-[13px]">
          <span className="inline-flex items-center gap-2"><i className="fx-map-key" data-recent="true" aria-hidden />{t.recent}</span>
          <span className="inline-flex items-center gap-2"><i className="fx-map-key" aria-hidden />{t.company}</span>
          <span className="inline-flex items-center gap-2"><i className="fx-map-key fx-map-key-ring" aria-hidden />{t.agency}</span>
        </p>
      </div>

      <section className="mt-10 lg:mt-0" aria-labelledby="fx-week-list">
        <h2 id="fx-week-list" className="fx-caps fx-muted mb-4">{t.listTitle}</h2>
        {shown.length ? (
          <ol className="border-t border-[var(--fx-line)]" data-testid="map-list">
            {shown.map((c, k) => (
              <li key={`${c.company}-${c.date}-${k}`} className="border-b border-[var(--fx-line)] py-3">
                <p className="fx-caps fx-muted">{fmtDayMonth(c.date)} · {c.ville}</p>
                <p className="mt-1 text-[16px]">
                  <Link className="fx-link inline-flex min-h-11 items-center" href={`/${lang}/entreprise/${c.company}/`}>{c.name}</Link>
                </p>
                <p className="fx-muted text-[14px] leading-snug">{lang === "fr" ? `« ${c.titre} »` : `«${c.titre}»`}</p>
              </li>
            ))}
          </ol>
        ) : <p className="fx-muted text-[15px]">{t.none}</p>}
      </section>
    </div>
  );
}
