// « Chaque matin, en direct de simap » (suite 10, § 2) : la section est-elle renouvelée ? Utilisé par controle.mjs ;
// testé par fraicheur.test.mjs. Une fois la section publiée, chaque jour ouvrable (lundi à vendredi) a sa lecture. Le
// planificateur de GitHub démarre souvent avec des heures de retard (jusqu'à 15 h 10 pour la mise à jour quotidienne,
// du 06.10 au 13.10.2026) : la lecture du jour n'est attendue qu'à partir de 16 h, heure de Zurich.
const LATE_HOUR = 16;
const DAY = 86_400_000;

const iso = (t) => new Date(t).toISOString().slice(0, 10);
const weekday = (t) => (new Date(t).getUTCDay() + 6) % 7; // 0 = Monday … 6 = Sunday

/** The reading day expected at `now` ({ day: « AAAA-MM-JJ », hour }, Zurich time). */
export function expectedReading(now) {
  let t = Date.parse(`${now.day}T12:00:00Z`);
  if (!(weekday(t) <= 4 && now.hour >= LATE_HOUR)) t -= DAY; // today only once late enough; otherwise an earlier day
  while (weekday(t) > 4) t -= DAY; // back to the last working day
  return iso(t);
}

/** A sentence for the report when the published section was not renewed, else null (never published: nothing). */
export function staleProblem(live, now) {
  if (live.etat !== "a_jour") return null;
  const expected = expectedReading(now);
  return live.mis_a_jour_le < expected ? `section en direct non renouvelée : lecture du ${live.mis_a_jour_le}, attendue du ${expected}` : null;
}

/** The current day and hour in Zurich. */
export function zurichNow(date = new Date()) {
  const z = Object.fromEntries(new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Zurich", year: "numeric", month: "2-digit",
    day: "2-digit", hour: "2-digit", hourCycle: "h23" }).formatToParts(date).map((p) => [p.type, p.value]));
  return { day: `${z.year}-${z.month}-${z.day}`, hour: Number(z.hour) };
}
