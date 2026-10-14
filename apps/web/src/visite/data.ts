// The data of the visit, built on the server from the exports (each JSON file is checked against its schema, and the
// schema against these types, in src/lib/schema.test.ts): the same for the visit and its printable summary.
import curated from "@/data/presentation/dossiers.json";
import suivant from "@/data/presentation/lundi_suivant.json";
import lundis from "@/data/presentation/lundis.json";
import matins from "@/data/presentation/matins.json";
import territoire from "@/data/presentation/territoire.json";
import { calls, companies, lists, meta, proposals } from "@/lib/data";
import { getDict } from "@/lib/i18n";
import { visitDossier, type Curated } from "./dossier";
import { firstTest } from "./firstTest";
import { visitMoments } from "./moments";
import { AGENCES } from "./agences";
import { proposer, type Proposer } from "./proposer";
import type { VisitData } from "./Visit";

export function visitData(lang: "fr" | "de"): VisitData {
  const territory = territoire as unknown as VisitData["territory"];
  const reading: Record<string, Curated> = curated.dossiers;
  return {
    lang,
    mondays: lundis as unknown as VisitData["mondays"],
    territory,
    dossiers: Object.fromEntries(Object.keys(territory.entreprises).map((id) =>
      [id, visitDossier(id, companies[id], calls[id], reading[id], curated.rejeu)])),
    ten: curated.dix.map((id) => ({ id, nom: companies[id]?.nom ?? id, ville: companies[id]?.ville ?? null })),
    next: suivant as unknown as VisitData["next"],
    firstTest: firstTest(),
    proposer: Object.fromEntries(Object.keys(territory.entreprises).map((id) => [id, proposer(proposals[id] ?? [], meta.metiers,
      { fr: getDict("fr").candidates.contactFrom, de: getDict("de").candidates.contactFrom })])
      .filter((x): x is [string, Proposer] => x[1] !== null)),
    moments: visitMoments(),
    // one list in the visit and in the application (questionnaire of 07.10.2026, B7): around each agency, the order of
    // that agency's week in the application (the ten of the frozen list, nearest first)
    around: Object.fromEntries(AGENCES.map((a) => [a.id, lists.batiment?.par_agence[a.id]?.entreprises ?? []])),
    // « Choisissez une date »: the section « Chaque matin » of each Monday that can be chosen, frozen (suite 10, § 2)
    mornings: matins as unknown as VisitData["mornings"],
  };
}
