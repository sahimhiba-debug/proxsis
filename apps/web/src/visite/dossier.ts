// Visit, time 1: the dossier of a company opened from the map (brief « à distance », 4.1). The publication (title, date,
// source) stays a published fact on paper; beside it, kept apart, what it lets one consider (an estimate, to confirm),
// what remains to verify, and the question to open the call, grounded in the published fact only. The three guided
// dossiers use their curated reading (still « à valider »); the others, the prepared call of the application.
import { phoneLine, reasonAward } from "@/futur/display";
import type { CallPrep, Company } from "@/lib/types";

type Bi = Record<"fr" | "de", string>;

export interface Curated {
  annonce_url: string;
  envisager: Bi;
  verifier: Record<"fr" | "de", string[]>;
  appel: { question: Bi };
}

export interface VisitDossier {
  id: string;
  nom: string;
  ville: string | null;
  n52: number; // public contracts won in its specialty over 52 weeks (simap.ch)
  guide: boolean;
  publication: { date: string; titre: string; adjudicateur: string | null; montant: number | null; url: string };
  envisager: Bi | null; // an estimate, to confirm with the company
  verifier: Record<"fr" | "de", string[]>;
  question: Bi; // the French one is ready; the German one waits for a German speaker (shown as such)
}

const section = (call: CallPrep | undefined, lang: "fr" | "de", code: string) =>
  call?.[lang].guide.find((g) => g.code === code)?.phrases.map((p) => p.texte) ?? [];

/** The question for the call when no curated reading exists: the sentence of « Ma semaine » (the published fact only,
 *  `phoneLine`), then the question of the guided dossiers (« des semaines ou des métiers… »). */
function grounded(c: Company): Bi | null {
  const fr = phoneLine(c, "fr");
  const de = phoneLine(c, "de");
  return fr && de ? {
    fr: `${fr} Pour ce chantier, y a-t-il des semaines ou des métiers pour lesquels un renfort vous serait utile ?`,
    de: `${de} Gibt es für diese Baustelle Wochen oder Berufe, für die Ihnen eine Verstärkung helfen würde?`,
  } : null;
}

export function visitDossier(id: string, company: Company, call: CallPrep | undefined, curated: Curated | undefined,
  monday: string): VisitDossier {
  const before = company.chronologie.filter((e) => e.date < monday);
  // the curated announcement, else the award that is the reason to call in the application
  const entry = before.find((e) => e.url_simap === (curated?.annonce_url ?? reasonAward(company)?.url_simap));
  const question = curated?.appel.question ?? grounded(company);
  if (!entry || !question) throw new Error(`pas de publication datée avant le ${monday} ni de question fondée sur elle : ${id}`);
  const publication = { date: entry.date, titre: entry.titre, adjudicateur: entry.adjudicateur ?? null,
    montant: entry.montant_chf ?? null, url: entry.url_simap };
  const estimate = { fr: section(call, "fr", "estimation")[0], de: section(call, "de", "estimation")[0] };
  return {
    id,
    nom: company.nom,
    ville: company.ville ?? null,
    n52: company.n_52s,
    guide: Boolean(curated),
    publication,
    envisager: curated?.envisager ?? (estimate.fr && estimate.de ? estimate : null),
    verifier: curated?.verifier ?? { fr: section(call, "fr", "questions"), de: section(call, "de", "questions") },
    question,
  };
}
