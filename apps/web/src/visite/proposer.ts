// « Qui proposer ? » (brief of 07.10.2026, § 3.1): in the consultant's view, three fictional temps who match the need,
// each with the trade, the work permit, the availability and the distance, taken as they are from the application's
// proposals (src/data/demo/propositions.json, CLAIMS PROP-1; « Candidats proposés »): the same people, the same order,
// nothing invented here. The need is an estimate (to confirm by the call). Built on the server (src/visite/data.ts):
// only these few lines reach the visit, not the whole proposals file.
import { fmtDate } from "@/lib/dates";
import type { NeedProposals } from "@/lib/types";

export interface ProposerRow { id: string; permis: string; dispo: string; km: number }
export interface Proposer {
  metier: { fr: string; de: string };
  debut: string; // the estimated start of the need
  contactDes: string | null; // the post is subject to the reporting obligation: contact possible from this date
  contactLine: { fr: string; de: string } | null; // the application's own words for it (« Candidats proposés »)
  interimaires: ProposerRow[];
}

const nextDay = (iso: string) => new Date(Date.parse(`${iso}T00:00:00Z`) + 86_400_000).toISOString().slice(0, 10);

/** Available from: the day after the current mission ends, else the start of the need (as the application says). */
export function availableFrom(p: NeedProposals["propositions"][number], need: NeedProposals): string {
  return p.fin_mission ? nextDay(p.fin_mission) : need.besoin.debut;
}

/** The first estimated need with three proposals (else the first one), and its first three fictional temps. */
export function proposer(needs: NeedProposals[], metiers: Record<string, { fr: string; de: string }>,
  contactFrom: { fr: string; de: string }): Proposer | null {
  const need = needs.find((n) => n.propositions.length >= 3) ?? needs.find((n) => n.propositions.length > 0);
  if (!need) return null;
  const three = need.propositions.slice(0, 3);
  const label = metiers[need.besoin.metier];
  const contactDes = need.annonce?.annonce_requise ? (three.find((p) => p.contact_des)?.contact_des ?? null) : null;
  return {
    metier: { fr: label?.fr ?? need.besoin.metier, de: label?.de ?? need.besoin.metier },
    debut: need.besoin.debut,
    contactDes,
    contactLine: contactDes ? { fr: contactFrom.fr.replace("{date}", fmtDate(contactDes)), de: contactFrom.de.replace("{date}", fmtDate(contactDes)) } : null,
    interimaires: three.map((p) => ({ id: p.candidate_id, permis: p.permis_travail, dispo: availableFrom(p, need), km: p.distance_km })),
  };
}
