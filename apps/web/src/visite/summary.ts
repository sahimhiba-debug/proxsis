// The conclusion « Votre premier lundi » (brief « à distance », § 5): his choices, and what he did not change marked
// « exemple préparé », never shown as his decision. The same rows feed the screen, the printable summary and the e-mail.
// The e-mail carries no financial figure unless he ticks « inclure mes hypothèses ». Pure, tested (summary.test.ts).
import { CARNET_COPY } from "@/lib/carnet";
import { fmtDate } from "@/lib/dates";
import { groupDigits } from "@/lib/digits";
import { SEUIL_COPY, SEUIL_EXAMPLE, seuil } from "@/lib/seuil";
import type { MondaysData } from "@/presentation/mondayData";
import { EXAMPLE_ENTRY } from "./consultant";
import { VISIT_COPY } from "./copy";
import type { VisitDossier } from "./dossier";
import { examplePilot, pilotSentence } from "./pilot";
import type { VisitState } from "./state";

export interface SummaryRow {
  key: "entreprise" | "question" | "date" | "seuil" | "critere";
  label: string;
  value: string;
  example: boolean; // a prepared example he did not change
  financial: boolean; // a figure in francs: left out of the e-mail unless he asks for it
}

export interface SummaryInputs {
  lang: "fr" | "de";
  s: VisitState;
  dossiers: Record<string, VisitDossier>;
  exampleCompany: string;
  mondays: MondaysData;
}

export function summaryRows({ lang, s, dossiers, exampleCompany, mondays }: SummaryInputs): SummaryRow[] {
  const t = VISIT_COPY[lang].conclusion;
  const c = CARNET_COPY[lang];
  const company = s.company && dossiers[s.company] ? s.company : exampleCompany;
  const d = dossiers[company];
  const own = s.carnet[company];
  const e = own ?? EXAMPLE_ENTRY;
  const decision = e.decision === "ecarter" ? `${t.setAside} · ${c.motifs[e.motif ?? "autre"]}`
    : e.decision === "revoir" && e.revoir ? c.revoirOn.replace("{date}", fmtDate(e.revoir))
    : `${c.decisions[e.decision]}${e.confie ? ` · ${c.confided.replace("{role}", c.role)} (${c.roleNote})` : ""}`;
  const mondayIso = s.monday ?? mondays.choix.exemple;
  const m = mondays.lundis.find((x) => x.lundi === mondayIso && x.choisissable) ?? mondays.lundis.find((x) => x.lundi === mondays.choix.exemple)!;
  const x = s.seuil ?? SEUIL_EXAMPLE;
  const r = seuil(x, s.half);
  const nf = (n: number) => groupDigits(n, 0, lang === "de" ? "de-CH" : "fr-CH");
  const sv = SEUIL_COPY[lang];
  const threshold = r.breakEvenDays === null ? sv.noMargin : (r.breakEvenDays === 1 ? sv.resultOne : sv.result.replace("{n}", nf(r.breakEvenDays)));
  const pilot = s.pilot ?? examplePilot(r.breakEvenDays);
  return [
    { key: "entreprise", label: t.rows.entreprise, value: `${d.nom} — ${decision}`, example: !own, financial: false },
    // a lead set aside keeps no call question (nothing is shown as approved)
    { key: "question", label: t.rows.question, example: !s.company && !own, financial: false,
      value: e.decision === "ecarter" ? t.noQuestion
        : lang === "fr" ? `« ${d.question.fr} »` : `${t.factOnly.replace("{titre}", d.publication.titre).replace("{date}", fmtDate(d.publication.date))}` },
    { key: "date", label: t.rows.date, example: !s.monday, financial: false,
      value: t.dateValue.replace("{date}", fmtDate(m.lundi)).replace("{n}", String(m.obtenu)).replace("{k}", String(m.dix.length)) },
    { key: "seuil", label: t.rows.seuil, example: !s.seuil && !s.half, financial: true,
      value: t.seuilValue.replace("{result}", threshold).replace("{weeks}", nf(x.weeks)).replace("{cost}", nf(r.cost)) },
    { key: "critere", label: t.rows.critere, value: pilotSentence(pilot, lang), example: !s.pilot, financial: false },
  ];
}

/** The e-mail for the team: subject and text, no attachment; no figure in francs unless `withHypotheses`. */
export function emailText(rows: SummaryRow[], lang: "fr" | "de", withHypotheses: boolean): { subject: string; body: string } {
  const t = VISIT_COPY[lang].conclusion.email;
  const example = VISIT_COPY[lang].example;
  const lines = rows.filter((r) => withHypotheses || !r.financial)
    .map((r) => `- ${r.label} : ${r.value}${r.example ? ` (${example})` : ""}`.replace(" : ", lang === "de" ? ": " : " : "));
  return { subject: t.subject, body: [t.hello, "", t.intro, ...lines, "", t.examples, "", t.bye].join("\n") };
}
