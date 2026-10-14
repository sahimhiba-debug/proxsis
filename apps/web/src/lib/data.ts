// Demo data, read at build time on the server (pages are statically generated): nothing here reaches the
// client bundle unless a page passes it down explicitly.
import "server-only";

import agencesJson from "@/data/demo/agences.json";
import appelsJson from "@/data/demo/appels.json";
import candidatsJson from "@/data/demo/candidats.json";
import claimsJson from "@/data/demo/claims.json";
import conformiteJson from "@/data/demo/conformite.json";
import entreprisesJson from "@/data/demo/entreprises.json";
import listesJson from "@/data/demo/listes.json";
import metaJson from "@/data/demo/meta.json";
import propositionsJson from "@/data/demo/propositions.json";
import redeploiementJson from "@/data/demo/redeploiement.json";
import tableauJson from "@/data/demo/tableau.json";
import type {
  Agency,
  CallPrep,
  Candidate,
  Claim,
  Company,
  ComplianceCheck,
  Dashboard,
  Meta,
  NeedProposals,
  Redeploy,
  SpecialtyList,
} from "./types";

// TypeScript infers literal types from the JSON (optional keys, never[] for an empty list) that are narrower or wider
// than the types the screens read; the casts below are safe because src/lib/schema.test.ts validates every file
// against its schema AND checks at compile time that each schema fits the type it is cast to.
export const meta = metaJson as Meta;
export const agencies = agencesJson as unknown as Record<string, Agency>;
export const companies = entreprisesJson as unknown as Record<string, Company>;
export const lists = listesJson as unknown as Record<string, SpecialtyList>;
export const proposals = propositionsJson as unknown as Record<string, NeedProposals[]>;
export const candidates = candidatsJson as unknown as Record<string, Candidate>;
export const redeploy = redeploiementJson as unknown as Redeploy;
export const compliance = conformiteJson as unknown as Record<string, ComplianceCheck[]>;
export const calls = appelsJson as unknown as Record<string, CallPrep>;
export const dashboard = tableauJson as unknown as Dashboard;
export const claims = claimsJson as unknown as Record<string, Claim>;


export function consultant(code: string) {
  for (const a of Object.values(agencies)) {
    const c = a.consultants.find((x) => x.code === code);
    if (c) return { ...c, agence: a };
  }
  return null;
}

export function allConsultants() {
  return Object.values(agencies).flatMap((a) => a.consultants.map((c) => ({ ...c, agence: a })));
}

/** Companies of a consultant's list: same agency, same specialty, in list order; then the surprises. */
export function weekList(code: string): { ranked: Company[]; surprises: Company[]; specialty: string } | null {
  const c = consultant(code);
  if (!c) return null;
  const l = lists[c.specialite];
  const part = l?.par_agence[c.agence.id];
  if (!part) return { ranked: [], surprises: [], specialty: c.specialite };
  return {
    ranked: part.entreprises.map((id) => companies[id]).filter(Boolean),
    surprises: part.surprises.map((id) => companies[id]).filter(Boolean),
    specialty: c.specialite,
  };
}
