// Schema version 1 of the demo export (python/src/proxsis/demo_export.py).
export type Lang = "fr" | "de";
export type DataType = "RÉEL" | "FICTIF";

export interface Source {
  date: string;
  titre: string;
  adjudicateur: string | null;
  montant_chf: number | null;
  phase: string | null;
  specialite?: string | null;
  url_simap: string;
  url_api?: string | null;
  source: string;
}

export interface Reason {
  code: string;
  fr: string;
  de: string;
  court?: { fr: string; de: string }; // the form shown on a card (« Dernier marché il y a 13 jours »), from the export
  url?: string;
}

export interface NeedRow {
  semaine: string;
  metier: string;
  phases?: string[];
  personnes_bas: number;
  personnes_milieu: number;
  personnes_haut: number;
}

export interface ExpectedLot {
  phase: string;
  presence: number;
  date_p10: string;
  date_p50: string;
  date_p90: string;
}

export interface Company {
  id: string;
  nom: string;
  ville: string;
  canton: string;
  lat: number;
  lon: number;
  agence: string;
  specialites: Record<string, { rang: number | null; surprise: string[]; confiance: string; faiblesses: string[] }>;
  chronologie: Source[];
  specialite_principale: string;
  raisons: Reason[];
  besoin: NeedRow[];
  lots_attendus: ExpectedLot[];
  sources: Source[];
  n_52s: number;
  confiance: "elevee" | "moyenne" | "faible";
  surprise: string[];
}

export interface SpecialtyList {
  libelle: Record<Lang, string>;
  ordre: string;
  par_agence: Record<string, { entreprises: string[]; surprises: string[] }>;
  hypotheses: string[];
  backtest: { p_at_10: number | null; taux_de_base: number | null; semaines: number | null; claim: string };
}

export interface Proposal {
  candidate_id: string;
  libelle: string;
  score: number;
  raisons_fr: string[];
  raisons_de: string[];
  categorie_cct: "non_qualifie" | "specialise" | "qualifie";
  regle_cct: string;
  salaire_minimum_cct_ls_heure: number | null;
  cct_applicable: string;
  cct_applicable_de: string;
  inscrit_orp: boolean;
  contact_des: string | null;
  permis_travail: string;
  langues: string[];
  localite: string;
  distance_km: number;
  fin_mission: string | null;
  fictif: boolean;
}

export interface NeedProposals {
  besoin: { entreprise: string; metier: string; debut: string; n: number };
  propositions: Proposal[];
  entonnoir: { tous: number; metier: number; certificat: number; disponible: number; distance: number };
  fictif: boolean;
  annonce: { soumis: boolean | null; annonce_requise: boolean | null; genre: string | null; site: string; publication_libre: string | null };
}

export interface ComplianceCheck {
  metier: string;
  genre: string | null;
  libelle_fr: string;
  libelle_de: string;
  correspondance: string;
  soumis: boolean | null;
  annonce_requise: boolean | null;
  exception_code: "mission_courte" | "inscrit_orp" | null;
  debut: string;
  annonce: Record<Lang, string>;
  metier_libelle: Record<Lang, string>;
}

/** What a cited fact is: published (real), estimated by Proxsis, published by Flexsis, or fictional (demo). */
export type FactType = "reel" | "estimation" | "maison" | "fictif";

export interface Fact {
  id: number;
  type: FactType;
  code?: string; // stable code of the fact (« adjudication », « frequence », « besoin », « try_hire »…)
  fr: string;
  de: string;
  url: string;
  source: Record<Lang, string>; // who says it, in the page's language
  portee?: Record<Lang, string>; // where a house argument was published
}

export interface Phrase {
  texte: string;
  sources: number[];
}

/** Stable code of a part of the call guide, in the order of the call (python/src/proxsis/call_prep.py, GUIDE_SECTIONS). */
export type GuideCode = "ouverture" | "pourquoi" | "estimation" | "questions" | "apport" | "proposition" | "suite";

export interface GuideSection {
  code: GuideCode;
  titre: string;
  phrases: Phrase[];
}

export interface CallDoc {
  guide: GuideSection[];
  email: { objet: string; phrases: Phrase[] };
}

export interface CallPrep {
  entreprise: string;
  faits: Fact[];
  fr: CallDoc;
  de: CallDoc;
  redaction: Redaction;
}

export interface Worker {
  candidate_id: string;
  libelle: string;
  fin_mission: string;
  metier: string | null;
  fictif: true; // every worker of the demo is invented
  motif_code?: "metier" | "permis" | "distance" | "moment" | "annonce" | "capacite";
  proposition?: {
    entreprise: string;
    nom: string;
    ville: string;
    metier: string;
    semaine: string;
    distance_km: number;
    source: string;
    raison_fr: string;
    raison_de: string;
    contact_des: string | null;
  };
}

export interface Redeploy {
  fictif: boolean;
  date: string;
  fenetre_semaines: number;
  fins_de_mission: number;
  redeployes: number;
  taux_redeploiement: number | null;
  besoins: number;
  travailleurs: Worker[];
}

export interface Kpi {
  valeur: number | null;
  type: DataType;
  claim: string;
  n?: number;
}

export interface Dashboard {
  agences: Record<string, Record<"appels" | "rendez_vous" | "missions_pourvues" | "delai_moyen_jours" | "redeploiement", Kpi>>;
  indicateurs: (Kpi & { code: string; unite: string })[];
}

export interface Agency {
  id: string;
  nom: string;
  adresse: string;
  lat: number;
  lon: number;
  source: string;
  consultants: { code: string; libelle: string; specialite: string; fictif: boolean }[];
}

export interface Candidate {
  candidate_id: string;
  libelle: string;
  specialite: string;
  metier: string;
  categorie_cct: string;
  permis_travail: string;
  langues: string;
  localite: string;
  agence: string;
  statut: string;
  fin_mission: string | null;
  available_from: string;
  fictif: boolean;
}

export interface Claim {
  affirmation: string;
  valeur: string;
  donnees: string;
  commande: string;
  fichier: string;
  limite: string;
}

export interface Meta {
  schema: number;
  semaine: string;
  genere_le: string;
  mention_simap: string;
  avertissement_fictif: string;
  sources: Record<string, string>;
  redaction: Redaction | null;
  jours_feries_valais: string[];
  metiers: Record<string, Record<Lang, string>>;
}

/** « Chaque matin, en direct de simap » (src/data/direct/matin.json, written every working day by
 *  python/src/proxsis/live_week.py): on Monday the week that ended, from Tuesday to Friday the day before. A laureate
 *  carries the identifier of the application's lists (« dans votre liste »). */
export interface LiveLaureate { nom: string; id: string }
export interface LiveContract { date: string; titre: string; adjudicateur: string | null; commune: string | null; laureats: LiveLaureate[]; url: string }
export type CorrectionKind = "correction" | "revocation" | "abandonment";
/** A correction, revocation or abandonment published on simap during the period (passed on: AGB API ch. 5 al. 2). */
export interface LiveCorrection { date: string; type: CorrectionKind; titre: string; url: string }
export type LiveMode = "semaine" | "veille";
export interface LiveFile {
  schema: 2; etat: "a_jour" | "en_attente"; mode: LiveMode | null; periode: { du: string; au: string } | null;
  mis_a_jour_le: string | null; source: string; mention: string; total: number; marches: LiveContract[];
  rectifications?: LiveCorrection[];
}
/** « Choisissez une date »: the same section, frozen, for every Monday that can be chosen (src/data/presentation/matins.json,
 *  `proxsis matins-presentation`): only what was published before that Monday. */
export interface FrozenMornings {
  schema: 1; source: string; mention: string;
  lundis: Record<string, { periode: { du: string; au: string }; total: number; marches: LiveContract[] }>;
}
/** The corrections of the notices of the frozen data (src/data/direct/corrections.json), kept from one reading to the next. */
export interface CorrectionsFile {
  schema: 1; mis_a_jour_le: string | null; source: string; mention: string;
  avis: { projet: string; date: string; type: CorrectionKind; url: string }[];
}

/** Who wrote a call guide's text: the deterministic text model, or Apertus (checked phrase by phrase). */
export interface Redaction { type: "modele" | "apertus"; fournisseur: string; note: string }
