// Data of the visit's new moments (brief of 07.10.2026, § 3.2 to 3.4), written by `proxsis moments-presentation`
// (python/src/proxsis/visit_moments.py), each file refused there when it differs from its line of CLAIMS.md, and
// checked again here (moments.test.ts). Only the data and their shape: the screens and their sentences are elsewhere.
//
// * « Cette semaine » (cette_semaine.json, CLAIMS PRES-SEMAINE-1): publications read and retained during the week
//   before the first Monday, and the ten calls of its list.
// * « Celles qui accélèrent » (accelerent.json, CLAIMS REEL-SURPRISE): descriptive rates of the measure of « Une date ».
// * « Plusieurs faits vont dans le même sens » (faits.json, CLAIMS PRES-CARRON-1, PRES-BITZ-1, PRES-THELER-1): the
//   published facts of the three guided dossiers, each with its date and its source; for the Bulletin officiel, the
//   company's role only, never the applicant, no link.
import { z } from "zod";
import accelerentJson from "@/data/presentation/accelerent.json";
import semaineJson from "@/data/presentation/cette_semaine.json";
import faitsJson from "@/data/presentation/faits.json";

const lang = z.object({ fr: z.string().min(1), de: z.string().min(1) });
const isoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const provenance = z.object({
  commande: z.literal("proxsis moments-presentation"), calcule_le: isoDate, claims: z.union([z.string(), z.array(z.string())]),
});
const sources = z.object({
  simap: z.object({ nom: lang, mention: z.string().min(1) }),
  bulletin_officiel: z.object({ nom: lang, mention: lang }),
});
const count = z.object({
  total: z.number().int().nonnegative(), simap: z.number().int().nonnegative(), bulletin_officiel: z.number().int().nonnegative(),
}).refine((c) => c.total === c.simap + c.bulletin_officiel, "le total est la somme des deux sources");

export const weekSchema = z.object({
  schema: z.literal(1), claims: z.literal("PRES-SEMAINE-1"), lundi: isoDate, semaine: z.object({ du: isoDate, au: isoDate }),
  liste: z.object({ fichier: z.string().min(1), liste_id: z.string().min(1), specialite: z.string(), region: z.array(z.string()) }),
  fin_des_donnees: z.object({ simap: isoDate, bulletin_officiel: isoDate }),
  lues: count, retenues: count, appels: z.number().int().positive(), sources, provenance,
}).refine((w) => w.retenues.total <= w.lues.total, "on ne retient que ce qui a été lu")
  .refine((w) => w.retenues.bulletin_officiel === 0, "le Bulletin officiel n'entre pas dans l'ordre de la liste")
  .refine((w) => w.semaine.au < w.lundi && w.fin_des_donnees.simap < w.lundi, "rien du lundi de la liste ni d'après");

const rate = z.object({ taux: z.number().min(0).max(1), affiche: lang });
export const acceleratingSchema = z.object({
  schema: z.literal(1), claims: z.literal("REEL-SURPRISE"),
  perimetre: z.object({ specialite: z.string(), region: z.array(z.string()), dix: z.literal(10), semaines: z.number().int().positive(),
    premiere: isoDate, derniere: isoDate, horizon_semaines: z.literal(8) }),
  regle: lang, accelerent: rate.extend({ cas: z.number().int().positive() }), hors_des_dix: rate, nuance: lang,
  de_a_relire: z.literal(true),
  source: z.object({ nom: z.string().min(1), mention: z.string().min(1), mesure: z.string().min(1), mesure_le: isoDate }), provenance,
});

const award = z.object({
  type: z.literal("marche"), date: isoDate, dernier: z.boolean(), libelle: lang, serie: z.string().nullable(),
  adjudicateur: lang.nullable(), objet: lang.nullable(), titre_original: z.string().nullable(), source: z.literal("simap"),
  url: z.string().regex(/^https:\/\/www\.simap\.ch\/(fr|de|it|en)\/project-detail\/[0-9a-f-]{36}$/),
});
// the company's role in a building request of the Bulletin officiel: no applicant, no identifier, no link (strict)
const permit = z.strictObject({
  type: z.literal("demande_autorisation"), date: isoDate, commune: z.string().min(1), role: z.literal("auteur_plans_entreprise"),
  libelle: lang, source: z.literal("bulletin_officiel"),
});
export const factsSchema = z.object({
  schema: z.literal(1), lundi: isoDate,
  dossiers: z.record(z.string(), z.object({
    claims: z.enum(["PRES-CARRON-1", "PRES-BITZ-1", "PRES-THELER-1"]), nom: z.string().min(1), ville: z.string().nullable(),
    marches_52s: z.object({ nombre: z.number().int().positive(), au: isoDate, source: z.literal("simap") }),
    faits: z.array(z.discriminatedUnion("type", [award, permit])).min(1),
  }).refine((d) => d.faits.filter((f) => f.type === "marche" && f.dernier).length === 1, "un seul dernier marché")),
  sources, de_a_relire: z.literal(true), provenance,
});

export type ThisWeek = z.infer<typeof weekSchema>;
export type Accelerating = z.infer<typeof acceleratingSchema>;
export type GuidedFacts = z.infer<typeof factsSchema>;

/** The three files, validated (a file that no longer fits its shape fails here, not on a screen). */
export function visitMoments(): { week: ThisWeek; accelerating: Accelerating; facts: GuidedFacts } {
  return { week: weekSchema.parse(semaineJson), accelerating: acceleratingSchema.parse(accelerentJson), facts: factsSchema.parse(faitsJson) };
}
