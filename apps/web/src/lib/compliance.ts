// Countdown of the job-reporting obligation (art. 53b al. 5-6 OSE; SECO directive B16-B17): the restriction runs
// over the 5 working days that follow the day the vacancy went online; Saturdays, Sundays and public holidays do
// not count; free publication the next calendar day. Same algorithm as python/src/proxsis/compliance.py.

function addDays(iso: string, n: number): string {
  const d = new Date(`${iso}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}

function isWorkingDay(iso: string, holidays: Set<string>): boolean {
  const wd = new Date(`${iso}T12:00:00Z`).getUTCDay();
  return wd !== 0 && wd !== 6 && !holidays.has(iso);
}

export function freePublicationDate(online: string, holidays: Iterable<string>, n = 5): string {
  const hol = new Set(holidays);
  let d = online;
  let counted = 0;
  while (counted < n) {
    d = addDays(d, 1);
    if (isWorkingDay(d, hol)) counted += 1;
  }
  return addDays(d, 1);
}

/** Working days of restriction still to run on ``today`` (0 when publication is free). */
export function remainingWorkingDays(online: string, today: string, holidays: Iterable<string>, n = 5): number {
  const hol = new Set(holidays);
  const free = freePublicationDate(online, hol, n);
  if (today >= free) return 0;
  if (today <= online) return n;
  let d = today;
  let left = 0;
  while (d < free) {
    if (isWorkingDay(d, hol)) left += 1;
    d = addDays(d, 1);
  }
  return Math.min(left, n);
}
