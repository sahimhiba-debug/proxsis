import { describe, expect, it } from "vitest";
import type { z } from "zod";
import agences from "@/data/demo/agences.json";
import appels from "@/data/demo/appels.json";
import candidats from "@/data/demo/candidats.json";
import claims from "@/data/demo/claims.json";
import conformite from "@/data/demo/conformite.json";
import entreprises from "@/data/demo/entreprises.json";
import listes from "@/data/demo/listes.json";
import meta from "@/data/demo/meta.json";
import propositions from "@/data/demo/propositions.json";
import redeploiement from "@/data/demo/redeploiement.json";
import tableau from "@/data/demo/tableau.json";
import corrections from "@/data/direct/corrections.json";
import matin from "@/data/direct/matin.json";
import communesVs from "@/data/presentation/communes_vs.json";
import dossiers from "@/data/presentation/dossiers.json";
import histoires from "@/data/presentation/histoires.json";
import lundis from "@/data/presentation/lundis.json";
import matins from "@/data/presentation/matins.json";
import carte from "@/data/sources/carte.json";
import suivant from "@/data/presentation/lundi_suivant.json";
import territoire from "@/data/presentation/territoire.json";
import presentation from "@/data/presentation/presentation.json";
import type { SourceMap } from "./chaqueMatin";
import type { MondaysData } from "@/presentation/mondayData";
import { MENTION_SIMAP } from "@/presentation/SimapMention";
import type { StoriesData } from "@/presentation/storyData";
import type { Curated } from "@/visite/dossier";
import type { NextData } from "@/visite/next";
import type { TerritoryData } from "@/visite/territory";
import * as S from "./schema";
import type * as T from "./types";

// What a schema accepts must fit the type the screens read (checked at compile time: `tsc` fails otherwise).
type Fits<A extends B, B> = A;
export type Checked = [
  Fits<z.infer<typeof S.company>, T.Company>, Fits<z.infer<typeof S.specialtyList>, T.SpecialtyList>,
  Fits<z.infer<typeof S.needProposals>, T.NeedProposals>, Fits<z.infer<typeof S.callPrep>, T.CallPrep>,
  Fits<z.infer<typeof S.redeploy>, T.Redeploy>, Fits<z.infer<typeof S.dashboard>, T.Dashboard>,
  Fits<z.infer<typeof S.agency>, T.Agency>, Fits<z.infer<typeof S.candidate>, T.Candidate>,
  Fits<z.infer<typeof S.claim>, T.Claim>, Fits<z.infer<typeof S.meta>, T.Meta>,
  Fits<z.infer<typeof S.liveMorning>, T.LiveFile>, Fits<z.infer<typeof S.frozenMornings>, T.FrozenMornings>,
  Fits<z.infer<typeof S.sourceMap>, SourceMap>,
  Fits<z.infer<typeof S.correctionsFile>, T.CorrectionsFile>, Fits<z.infer<typeof S.stories>, StoriesData>,
  Fits<z.infer<typeof S.mondays>, MondaysData>, Fits<z.infer<typeof S.territory>, TerritoryData>,
  Fits<z.infer<typeof S.nextMondayData>, NextData>,
  Fits<z.infer<typeof S.curatedDossiers>["dossiers"], Record<string, Curated>>,
];

/** Every problem of a file, with its path in the file, readable in the test report. */
function problems(schema: z.ZodType, data: unknown, file: string): string[] {
  const r = schema.safeParse(data);
  return r.success ? [] : r.error.issues.slice(0, 5).map((i) => `${file} · ${i.path.join(".")} : ${i.message}`);
}
const each = (schema: z.ZodType, data: Record<string, unknown>, file: string) =>
  Object.entries(data).flatMap(([k, v]) => problems(schema, v, `${file}#${k}`));

describe("les données des écrans suivent leur schéma", () => {
  it("chaque fichier de la démonstration est valide (export de proxsis export-demo)", () => {
    const found = [
      ...problems(S.meta, meta, "meta.json"),
      ...each(S.company, entreprises, "entreprises.json"),
      ...each(S.specialtyList, listes, "listes.json"),
      ...each(S.agency, agences, "agences.json"),
      ...each(S.candidate, candidats, "candidats.json"),
      ...each(S.claim, claims, "claims.json"),
      ...each(S.callPrep, appels, "appels.json"),
      ...Object.entries(propositions).flatMap(([k, v]) => (v as unknown[]).flatMap((x, i) => problems(S.needProposals, x, `propositions.json#${k}[${i}]`))),
      ...Object.entries(conformite).flatMap(([k, v]) => (v as unknown[]).flatMap((x, i) => problems(S.complianceCheck, x, `conformite.json#${k}[${i}]`))),
      ...problems(S.redeploy, redeploiement, "redeploiement.json"),
      ...problems(S.dashboard, tableau, "tableau.json"),
    ];
    expect(found).toEqual([]);
  });

  it("chaque fichier de la présentation et la section en direct sont valides", () => {
    const found = [
      ...problems(S.presentationData, presentation, "presentation.json"),
      ...problems(S.curatedDossiers, dossiers, "dossiers.json"),
      ...problems(S.stories, histoires, "histoires.json"),
      ...problems(S.mondays, lundis, "lundis.json"),
      ...problems(S.territory, territoire, "territoire.json"),
      ...problems(S.nextMondayData, suivant, "lundi_suivant.json"),
      ...problems(S.communes, communesVs, "communes_vs.json"),
      ...problems(S.liveMorning, matin, "direct/matin.json"),
      ...problems(S.frozenMornings, matins, "matins.json"),
      ...problems(S.sourceMap, carte, "sources/carte.json"),
      ...problems(S.correctionsFile, corrections, "direct/corrections.json"),
    ];
    expect(found).toEqual([]);
  });

  it("la mention simap écrite dans la présentation est mot pour mot celle des données (une seule source : le moteur)", () => {
    expect(MENTION_SIMAP).toBe((meta as { mention_simap: string }).mention_simap);
    expect((matin as { mention: string }).mention).toBe(MENTION_SIMAP);
    expect(matins.mention).toBe(MENTION_SIMAP);
    expect(lundis.source.mention).toBe(MENTION_SIMAP);
    expect(territoire.source.mention).toBe(MENTION_SIMAP);
  });

  it("chaque candidat est rattaché à une agence par son identifiant (jointure sans texte affiché)", () => {
    const ids = new Set(Object.keys(agences));
    const strays = Object.values(candidats as Record<string, { agence: string }>).filter((c) => !ids.has(c.agence));
    expect(strays.map((c) => c.agence)).toEqual([]);
  });

  it("la section du matin refuse une lecture à jour sans date, un compte incohérent ou une publication du jour même", () => {
    const upToDate = { schema: 2, etat: "a_jour", mode: "veille", periode: { du: "2026-10-12", au: "2026-10-12" }, mis_a_jour_le: "2026-10-13",
      source: "simap.ch", mention: "Ceci n'est pas une publication officielle.", total: 1,
      marches: [{ date: "2026-10-12", titre: "Route", adjudicateur: null, commune: "Sion", laureats: [{ nom: "Exemple SA", id: "ent-0123456789" }],
        url: "https://www.simap.ch/" }] };
    expect(problems(S.liveMorning, upToDate, "ok")).toEqual([]);
    expect(problems(S.liveMorning, { ...upToDate, mis_a_jour_le: null }, "sans date")).not.toEqual([]);
    expect(problems(S.liveMorning, { ...upToDate, total: 0 }, "compte")).not.toEqual([]);
    expect(problems(S.liveMorning, { ...upToDate, marches: [{ ...upToDate.marches[0], date: "2026-10-13" }],
      periode: { du: "2026-10-12", au: "2026-10-13" } }, "jour même")).not.toEqual([]);
    expect(problems(S.liveMorning, { ...upToDate, marches: [{ ...upToDate.marches[0], laureats: ["Exemple SA"] }] }, "lauréat sans identifiant")).not.toEqual([]);
    const rectified = { ...upToDate, rectifications: [{ date: "2026-10-12", type: "revocation", titre: "Route",
      url: "https://www.simap.ch/fr/project-detail/95465d92-7be7-46b7-862a-a376ca087134" }] };
    expect(problems(S.liveMorning, rectified, "rectification")).toEqual([]);
    expect(problems(S.liveMorning, { ...rectified, rectifications: [{ ...rectified.rectifications[0], type: "avis" }] }, "type")).not.toEqual([]);
  });

  it("les rectifications des avis figés : une page simap du projet, rien du lundi de la lecture", () => {
    const P = "95465d92-7be7-46b7-862a-a376ca087134";
    const ok = { schema: 1, mis_a_jour_le: "2026-10-12", source: "simap.ch", mention: "Ceci n'est pas une publication officielle.",
      avis: [{ projet: P, date: "2026-10-08", type: "correction", url: `https://www.simap.ch/fr/project-detail/${P}` }] };
    expect(problems(S.correctionsFile, ok, "ok")).toEqual([]);
    expect(problems(S.correctionsFile, { ...ok, avis: [{ ...ok.avis[0], date: "2026-10-12" }] }, "lundi")).not.toEqual([]);
    expect(problems(S.correctionsFile, { ...ok, avis: [{ ...ok.avis[0], url: "https://www.simap.ch/fr/project-detail/11111111-2222-4333-8444-555555555555" }] }, "autre projet")).not.toEqual([]);
  });

  it("un fichier qui ne suit plus son schéma est refusé (le contrôle n'est pas une passoire)", () => {
    const broken = { ...(redeploiement as object), fictif: false };
    expect(problems(S.redeploy, broken, "redeploiement.json")).not.toEqual([]);
    const lost = { ...(meta as object), semaine: "lundi" };
    expect(problems(S.meta, lost, "meta.json")).not.toEqual([]);
  });
});
