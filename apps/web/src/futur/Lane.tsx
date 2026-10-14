// One worker on the calendar of the coming weeks: the mission running until its last day, the first working day
// without a mission (empty), then the possibility in dots up to the week of the estimated need (Monday to Friday,
// dashed), or dots that lead nowhere when nothing fits. Weekends are shaded: a mission ending on a Friday leaves the
// Monday free, never the Saturday. Drawn only (aria-hidden): the sentence under it says the same dates in words.
const DAY = 86_400_000;
const pct = (v: number) => `${(Math.max(0, Math.min(1, v)) * 100).toFixed(3)}%`;

export function dayIndex(from: string, date: string): number {
  return Math.round((Date.parse(`${date}T12:00:00Z`) - Date.parse(`${from}T12:00:00Z`)) / DAY);
}

/** Day of the week of a day index counted from a Monday: 0 = Monday … 5 = Saturday, 6 = Sunday. */
const weekday = (d: number) => ((d % 7) + 7) % 7;

/** The first working day (Monday to Friday) after the last day of a mission, as a day index from the Monday `from`. */
export function firstFreeDay(last: number): number {
  let d = last + 1;
  while (weekday(d) >= 5) d += 1;
  return d;
}

/** `from` must be a Monday (the week of the list). */
export function Lane({ from, days, end, need }: { from: string; days: number; end: string; need: string | null }) {
  const last = dayIndex(from, end); // the last day of the mission
  const free = firstFreeDay(last);
  const needFrom = need === null ? null : dayIndex(from, need); // the Monday of the need's week
  const x = (d: number) => pct(d / days);
  return (
    <div className="fx-lane" aria-hidden>
      {Array.from({ length: Math.ceil(days / 7) }, (_, k) => <span key={`w${k}`} className="fx-lane-weekend" style={{ left: x(k * 7 + 5), width: x(2) }} />)}
      {Array.from({ length: Math.floor(days / 7) + 1 }, (_, k) => <span key={`t${k}`} className="fx-lane-tick" style={{ left: x(k * 7) }} />)}
      <span className="fx-lane-mission" style={{ left: 0, width: x(last + 0.5) }} />
      <span className="fx-lane-end" style={{ left: x(last + 0.5) }} />
      {needFrom !== null ? (
        <>
          {needFrom > free + 1 ? <span className="fx-lane-maybe" style={{ left: x(free + 1), width: x(needFrom - free - 1) }} /> : null}
          <span className="fx-lane-need" style={{ left: x(needFrom), width: x(Math.min(needFrom + 5, days) - needFrom) }} />
        </>
      ) : free + 1 < days ? <span className="fx-lane-none" style={{ left: x(free + 1), width: x(days - free - 1) }} /> : null}
      {free < days ? <span className="fx-lane-free" style={{ left: x(free + 0.5) }} /> : null}
    </div>
  );
}
