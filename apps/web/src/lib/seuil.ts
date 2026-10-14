// The threshold (brief « à distance », 4.4): « Il suffit de N journées supplémentaires facturées pour couvrir le coût »,
// over a period shown and editable (by default the six weeks of the pilot). ONE calculation for the visit and the
// application's « Retour sur investissement » page. Four rules, each tested (seuil.test.ts):
// - the margin is counted, never the turnover (the field is a margin per billed day);
// - a day without a mission is a missed gain, never a salary cost (no salary appears anywhere);
// - no day is counted twice (one count of additional billed days, whatever brought them);
// - the time saved stays apart while its value is not defined (never turned into francs).
// The start values are EXAMPLES, marked as such, never figures of Flexsis.
import { frenchDeep } from "@/lib/typo";

export interface SeuilInput {
  weeks: number; // the period
  marginPerDay: number; // CHF of margin per additional billed day
  serviceCost: number; // CHF over the period
  teamHours: number; // additional time of the teams over the period
  hourCost: number; // CHF per hour of that time
  days: number; // additional billed days assumed over the period
  savedHours: number; // time saved: shown apart, never in francs
}

export type SeuilField = keyof SeuilInput;

/** Example values only (Hiba's mock-up for the cost of the service, CHF 3 600 over six weeks; the others chosen to make
 *  the example readable): never figures of Flexsis, always marked « exemple » on screen (working notes). */
export const SEUIL_EXAMPLE: SeuilInput = {
  weeks: 6, marginPerDay: 100, serviceCost: 3600, teamHours: 12, hourCost: 60, days: 60, savedHours: 10,
};

/** The fields in the order of the screen, with their limits (whole weeks and days). */
export const SEUIL_FIELDS: { key: SeuilField; max: number; whole?: boolean }[] = [
  { key: "marginPerDay", max: 100_000 },
  { key: "serviceCost", max: 10_000_000 },
  { key: "teamHours", max: 100_000 },
  { key: "hourCost", max: 10_000 },
  { key: "days", max: 100_000, whole: true },
  { key: "savedHours", max: 100_000 },
];
export const WEEKS_MAX = 52;

export interface SeuilResult {
  teamCost: number;
  cost: number; // service + time of the teams, over the period
  breakEvenDays: number | null; // N: the least whole number of billed days whose margin covers the cost; null without margin
  gains: number; // margin of the assumed days (halved with « Deux fois moins »)
  net: number; // may be negative: it stays on screen
  negative: boolean;
}

const clean = (n: number) => (Number.isFinite(n) && n > 0 ? n : 0);

export function seuil(x: SeuilInput, half = false): SeuilResult {
  const teamCost = clean(x.teamHours) * clean(x.hourCost);
  const cost = clean(x.serviceCost) + teamCost;
  const margin = clean(x.marginPerDay);
  const breakEvenDays = margin > 0 ? Math.ceil(cost / margin - 1e-9) : null;
  const gains = clean(x.days) * (half ? 0.5 : 1) * margin;
  const net = gains - cost;
  return { teamCost, cost, breakEvenDays, gains, net, negative: net < 0 };
}

/** A typed value: a positive or zero number within the field's limit (a whole number where asked), else null. */
export function parseAmount(raw: string, max: number, whole = false): number | null {
  const v = Number(raw.replace(/[\s’' ]/g, "").replace(",", "."));
  if (raw.trim() === "" || !Number.isFinite(v) || v < 0 || v > max || (whole && !Number.isInteger(v))) return null;
  return v;
}

export const SEUIL_COPY = {
  fr: frenchDeep({
    question: "Combien de journées supplémentaires facturées faut-il pour couvrir le coût ?",
    result: "Il suffit de {n} journées supplémentaires facturées pour couvrir le coût.",
    resultOne: "Il suffit d'une journée supplémentaire facturée pour couvrir le coût.",
    resultNone: "Aucune journée supplémentaire n'est nécessaire : le coût est nul.",
    noMargin: "Indiquez une marge par journée pour voir le seuil.",
    period: "Sur {weeks} semaines",
    periodLabel: "Période, en semaines",
    perWeek: "soit environ {n} par semaine",
    costLine: "Coût sur la période : CHF {cost} (service CHF {service}, temps des équipes CHF {team}).",
    example: "exemple",
    examples: "Les valeurs de départ sont des exemples, jamais des chiffres de Flexsis.",
    fields: {
      marginPerDay: { label: "Marge par journée facturée (CHF)", hint: "la marge, pas le chiffre d'affaires" },
      serviceCost: { label: "Coût du service sur la période (CHF)", hint: "" },
      teamHours: { label: "Temps supplémentaire des équipes (heures)", hint: "sur la période" },
      hourCost: { label: "Coût d'une heure de ce temps (CHF)", hint: "" },
      days: { label: "Journées supplémentaires facturées, selon vous", hint: "sur la période ; une journée n'est comptée qu'une fois" },
      savedHours: { label: "Temps gagné (heures)", hint: "gardé à part : pas converti en francs" },
    } as Record<SeuilField, { label: string; hint: string }>,
    according: "Selon vos hypothèses",
    net: "CHF {net} sur {weeks} semaines",
    gain: "gain",
    loss: "perte",
    zero: "équilibre",
    lossStays: "Une perte reste une perte : elle reste affichée.",
    half: "Deux fois moins",
    halfOff: "Revenir aux hypothèses",
    halfOn: "Deux fois moins de journées supplémentaires ; le coût ne change pas.",
    saved: "Temps gagné : {h} h, gardé à part tant que sa valeur n'est pas définie.",
    rules: "On compte la marge, pas le chiffre d'affaires. Une journée sans mission est un manque à gagner, pas un coût salarial. Une journée n'est comptée qu'une fois.",
    invalid: "Valeur non prise en compte : un nombre positif, dans la limite du champ (semaines et journées entières).",
    reset: "Revenir aux exemples",
    mention: "Calcul · valeurs d'exemple, jamais des chiffres de Flexsis",
    calendar: {
      title: "Une mission fictive se termine vendredi",
      ends: "mission fictive · fin vendredi",
      free: "sans mission : un manque à gagner",
      next: "suite possible",
      toConfirm: "À confirmer",
      days: ["Lu", "Ma", "Me", "Je", "Ve"],
    },
  }),
  de: {
    question: "Wie viele zusätzlich verrechnete Tage braucht es, um die Kosten zu decken?",
    result: "Es braucht {n} zusätzlich verrechnete Tage, um die Kosten zu decken.",
    resultOne: "Es braucht einen zusätzlich verrechneten Tag, um die Kosten zu decken.",
    resultNone: "Kein zusätzlicher Tag nötig: Die Kosten sind null.",
    noMargin: "Geben Sie eine Marge pro Tag an, um die Schwelle zu sehen.",
    period: "Über {weeks} Wochen",
    periodLabel: "Zeitraum, in Wochen",
    perWeek: "also etwa {n} pro Woche",
    costLine: "Kosten über den Zeitraum: CHF {cost} (Dienst CHF {service}, Zeit der Teams CHF {team}).",
    example: "Beispiel",
    examples: "Die Startwerte sind Beispiele, nie Zahlen von Flexsis.",
    fields: {
      marginPerDay: { label: "Marge pro verrechnetem Tag (CHF)", hint: "die Marge, nicht der Umsatz" },
      serviceCost: { label: "Kosten des Dienstes über den Zeitraum (CHF)", hint: "" },
      teamHours: { label: "Zusätzliche Zeit der Teams (Stunden)", hint: "über den Zeitraum" },
      hourCost: { label: "Kosten einer Stunde dieser Zeit (CHF)", hint: "" },
      days: { label: "Zusätzlich verrechnete Tage, nach Ihrer Annahme", hint: "über den Zeitraum; jeder Tag wird nur einmal gezählt" },
      savedHours: { label: "Gewonnene Zeit (Stunden)", hint: "separat gehalten: nicht in Franken umgerechnet" },
    },
    according: "Nach Ihren Annahmen",
    net: "CHF {net} über {weeks} Wochen",
    gain: "Gewinn",
    loss: "Verlust",
    zero: "ausgeglichen",
    lossStays: "Ein Verlust bleibt ein Verlust: Er bleibt angezeigt.",
    half: "Halb so viel",
    halfOff: "Zurück zu den Annahmen",
    halfOn: "Halb so viele zusätzliche Tage; die Kosten bleiben gleich.",
    saved: "Gewonnene Zeit: {h} Std., separat gehalten, solange ihr Wert nicht festgelegt ist.",
    rules: "Gezählt wird die Marge, nicht der Umsatz. Ein Tag ohne Einsatz ist ein entgangener Gewinn, keine Lohnkosten. Jeder Tag wird nur einmal gezählt.",
    invalid: "Wert nicht übernommen: eine positive Zahl innerhalb der Grenze des Feldes (ganze Wochen und Tage).",
    reset: "Zurück zu den Beispielen",
    mention: "Berechnung · Beispielwerte, nie Zahlen von Flexsis",
    calendar: {
      title: "Ein fiktiver Einsatz endet am Freitag",
      ends: "fiktiver Einsatz · Ende Freitag",
      free: "ohne Einsatz: ein entgangener Gewinn",
      next: "mögliche Fortsetzung",
      toConfirm: "Zu bestätigen",
      days: ["Mo", "Di", "Mi", "Do", "Fr"],
    },
  },
} as const;
