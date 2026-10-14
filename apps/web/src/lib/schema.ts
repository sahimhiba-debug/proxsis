// Schemas of the data the screens read (src/data/demo/, exported by `proxsis export-demo`). The JSON files are static
// and bundled at build time: the test `schema.test.ts` validates each of them against these schemas, and checks at
// compile time that what a schema accepts fits the TypeScript type the screens use (src/lib/types.ts). A file that no
// longer matches fails the tests before it can reach a screen.
import { z } from "zod";

const lang = z.object({ fr: z.string(), de: z.string() });
const redaction = z.object({ type: z.enum(["modele", "apertus"]), fournisseur: z.string(), note: z.string() });
const isoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);

export const source = z.object({
  date: isoDate, titre: z.string(), adjudicateur: z.string().nullable(), montant_chf: z.number().nullable(),
  phase: z.string().nullable(), specialite: z.string().nullable().optional(), url_simap: z.url(),
  url_api: z.string().nullable().optional(), source: z.string(),
});

export const company = z.object({
  id: z.string(), nom: z.string().min(1), ville: z.string(), canton: z.string(), lat: z.number(), lon: z.number(),
  agence: z.string(),
  specialites: z.record(z.string(), z.object({ rang: z.number().nullable(), surprise: z.array(z.string()), confiance: z.string(),
    faiblesses: z.array(z.string()) })),
  chronologie: z.array(source), specialite_principale: z.string(),
  raisons: z.array(z.object({ code: z.string(), fr: z.string(), de: z.string(), court: lang.optional(), url: z.string().optional() })),
  besoin: z.array(z.object({ semaine: isoDate, metier: z.string(), phases: z.array(z.string()).optional(), personnes_bas: z.number(),
    personnes_milieu: z.number(), personnes_haut: z.number() })),
  lots_attendus: z.array(z.object({ phase: z.string(), presence: z.number(), date_p10: isoDate, date_p50: isoDate, date_p90: isoDate })),
  sources: z.array(source), n_52s: z.number().int().nonnegative(), confiance: z.enum(["elevee", "moyenne", "faible"]),
  surprise: z.array(z.string()),
});

export const specialtyList = z.object({
  libelle: lang, ordre: z.string(),
  par_agence: z.record(z.string(), z.object({ entreprises: z.array(z.string()), surprises: z.array(z.string()) })),
  hypotheses: z.array(z.string()),
  backtest: z.object({ p_at_10: z.number().nullable(), taux_de_base: z.number().nullable(), semaines: z.number().nullable(), claim: z.string() }),
});

const proposal = z.object({
  candidate_id: z.string(), libelle: z.string(), score: z.number(), raisons_fr: z.array(z.string()), raisons_de: z.array(z.string()),
  categorie_cct: z.enum(["non_qualifie", "specialise", "qualifie"]), regle_cct: z.string(),
  salaire_minimum_cct_ls_heure: z.number().nullable(), cct_applicable: z.string(), cct_applicable_de: z.string(),
  inscrit_orp: z.boolean(), contact_des: isoDate.nullable(), permis_travail: z.string(), langues: z.array(z.string()),
  localite: z.string(), distance_km: z.number(), fin_mission: isoDate.nullable(), fictif: z.literal(true),
});

export const needProposals = z.object({
  besoin: z.object({ entreprise: z.string(), metier: z.string(), debut: isoDate, n: z.number() }),
  propositions: z.array(proposal),
  entonnoir: z.object({ tous: z.number(), metier: z.number(), certificat: z.number(), disponible: z.number(), distance: z.number() }),
  fictif: z.literal(true),
  annonce: z.object({ soumis: z.boolean().nullable(), annonce_requise: z.boolean().nullable(), genre: z.string().nullable(), site: z.string(),
    publication_libre: isoDate.nullable() }),
});

export const complianceCheck = z.object({
  metier: z.string(), genre: z.string().nullable(), libelle_fr: z.string(), libelle_de: z.string(), correspondance: z.string(),
  soumis: z.boolean().nullable(), annonce_requise: z.boolean().nullable(), exception_code: z.enum(["mission_courte", "inscrit_orp"]).nullable(),
  debut: isoDate, annonce: lang.nullable(), metier_libelle: lang,
});

const fact = z.object({
  id: z.number().int().positive(), type: z.enum(["reel", "estimation", "maison", "fictif"]), code: z.string().optional(),
  fr: z.string().min(1), de: z.string().min(1), url: z.string().min(1), source: lang, portee: lang.optional(),
});
const phrase = z.object({ texte: z.string(), sources: z.array(z.number().int()) });
const callDoc = z.object({
  guide: z.array(z.object({ code: z.enum(["ouverture", "pourquoi", "estimation", "questions", "apport", "proposition", "suite"]),
    titre: z.string(), phrases: z.array(phrase) })),
  email: z.object({ objet: z.string().min(1), phrases: z.array(phrase) }),
});
export const callPrep = z.object({
  entreprise: z.string(), faits: z.array(fact), fr: callDoc, de: callDoc,
  redaction,
});

const worker = z.object({
  candidate_id: z.string(), libelle: z.string(), fin_mission: isoDate, metier: z.string().nullable(), fictif: z.literal(true),
  motif_code: z.enum(["metier", "permis", "distance", "moment", "annonce", "capacite"]).optional(),
  proposition: z.object({ entreprise: z.string(), nom: z.string(), ville: z.string(), metier: z.string(), semaine: isoDate,
    distance_km: z.number(), source: z.string(), raison_fr: z.string(), raison_de: z.string(), contact_des: isoDate.nullable() }).optional(),
});
export const redeploy = z.object({
  fictif: z.literal(true), date: isoDate, fenetre_semaines: z.number(), fins_de_mission: z.number(), redeployes: z.number(),
  taux_redeploiement: z.number().nullable(), besoins: z.number(), travailleurs: z.array(worker),
});

const kpi = z.object({ valeur: z.number().nullable(), type: z.enum(["RÉEL", "FICTIF"]), claim: z.string(), n: z.number().optional() });
export const dashboard = z.object({
  agences: z.record(z.string(), z.object({ appels: kpi, rendez_vous: kpi, missions_pourvues: kpi, delai_moyen_jours: kpi, redeploiement: kpi })),
  indicateurs: z.array(kpi.extend({ code: z.string(), unite: z.string() })),
});

export const agency = z.object({
  id: z.string(), nom: z.string(), adresse: z.string(), lat: z.number(), lon: z.number(), source: z.string(),
  consultants: z.array(z.object({ code: z.string(), libelle: z.string(), specialite: z.string(), fictif: z.literal(true) })),
});

export const candidate = z.object({
  candidate_id: z.string(), libelle: z.string(), specialite: z.string(), metier: z.string(), categorie_cct: z.string(),
  permis_travail: z.string(), langues: z.string(), localite: z.string(), agence: z.string(), statut: z.string(),
  fin_mission: isoDate.nullable(), available_from: isoDate, fictif: z.literal(true),
});

export const claim = z.object({
  affirmation: z.string().min(1), valeur: z.string().min(1), donnees: z.string(), commande: z.string(), fichier: z.string(),
  limite: z.string(),
});

export const meta = z.object({
  schema: z.number(), semaine: isoDate, genere_le: z.string(), mention_simap: z.string().min(1), avertissement_fictif: z.string(),
  sources: z.record(z.string(), z.string()), redaction: redaction.nullable(),
  jours_feries_valais: z.array(isoDate), metiers: z.record(z.string(), lang),
});

// ---------------------------------------------------------------- presentation (src/data/presentation/) and the live
// morning section (src/data/direct/matin.json, rewritten every working day by an automatic job: its tests run before any commit)

const isoWeek = z.string().regex(/^\d{4}-S\d{2}$/); // « 2026-S32 » (python: proxsis.gazette_pdf.iso_week)
const place = z.object({ commune: z.string().min(1), lat: z.number(), lon: z.number(), total: z.number().int().nonnegative(),
  semaines: z.record(isoWeek, z.number().int().nonnegative()) });
const counts = z.record(z.string(), z.number().int().nonnegative());

export const presentationData = z.object({
  prepare_le: isoDate,
  territoire: z.object({ total_publications: z.number().int().nonnegative(), n_communes: z.number().int().nonnegative(),
    periode: z.object({ debut: isoDate, fin: isoDate }).nullable(), semaines: z.array(isoWeek), communes: z.array(place),
    hors_carte: counts, source: lang }),
  marches: z.object({ total: z.number().int().nonnegative(), communes: z.array(place), hors_carte: counts, source: z.string().min(1) }),
  exemples: z.array(z.object({ url: z.url(), commune: z.string(), lat: z.number(), lon: z.number(), date: isoDate })),
});

const langList = z.object({ fr: z.array(z.string()), de: z.array(z.string()) });
export const curatedDossiers = z.object({
  rejeu: isoDate, dix: z.array(z.string()).length(10), guides: z.array(z.string()).min(1), en_preparation: z.array(z.string()),
  validation: z.literal("a_valider"), // the companies and the stories stay « à valider par les consultants »
  dossiers: z.record(z.string(), z.object({ annonce_url: z.url(), activite: lang, envisager: lang, verifier: langList,
    appel: z.object({ intro: lang, question: lang }), metier_mission: z.string(), travailleur_fictif: z.string().optional() })),
});

const storyPiece = z.object({ type: z.enum(["appel_offres", "adjudication"]), numero: z.string(), date: isoDate, titre: z.string(),
  objet: lang.nullable(), adjudicateur: z.string().nullable(), montant_chf: z.number().nullable().optional(),
  ouvert_a_T: z.boolean().optional(), url: z.url() });
const story = z.object({
  id: z.string(), type: z.enum(["reussite", "limite"]), claims: z.string().min(1),
  entreprise: z.object({ id: z.string(), nom: z.string(), ville: z.string() }), region: lang, date_T: isoDate,
  arrets: z.object({
    connu: z.object({ date: isoDate, pieces: z.array(storyPiece), texte: lang, contexte: z.object({ texte: lang }).optional() }),
    signalement: z.object({ texte: lang }),
    ensuite: z.object({ evenements: z.array(storyPiece), texte: lang, autres_traces: z.object({ source: lang,
      publications: z.array(z.object({ id: z.string(), date: isoDate, commune: z.string(), url: z.url() })) }).optional() }),
  }),
  intervalles: z.array(z.object({ code: z.string(), nom: lang, debut: isoDate, fin: isoDate, jours: z.number().int(),
    arret: z.enum(["connu", "ensuite"]), prevu: z.boolean().optional() })),
  besoin_personnel: lang,
});
export const stories = z.object({
  validation: z.literal("a_valider"),
  source: z.object({ nom: z.string(), mention: z.string().min(1), perimetre: lang }),
  regle: lang, histoires: z.array(story).length(3),
  mesure: z.object({ claims: z.string().min(1), phrase: lang, definition: lang, portee: lang, perimetre: z.object({ texte: lang }),
    valeurs: z.array(z.object({ code: z.string(), nom: lang, pct: z.number(), affiche: lang })),
    ecart: z.object({ nom: lang, affiche: lang, lecture: lang }) }),
});

const mondayCompany = z.object({ rang: z.number().int().min(1).max(10), id: z.string().min(1), nom: z.string().min(1),
  ville: z.string().nullable(), marches_52s: z.number().int().nonnegative(), dernier_marche: isoDate,
  autre_inscription_de: z.number().int().min(1).max(10).nullable(),
  nouveau_marche: z.object({ date: isoDate, titre: z.string().nullable(), url: z.url(), nombre: z.number().int().positive() }).nullable() });
export const mondays = z.object({
  schema: z.literal(1), claims: z.literal("REEL-SPEC-BAT"),
  source: z.object({ nom: z.string(), mention: z.string().min(1), debut_des_donnees: isoDate, fin_des_donnees: isoDate }),
  regle: z.object({ specialite: z.string(), region: z.array(z.string()), k: z.literal(10), ordre: z.literal("frequence_52s"),
    horizon_jours: z.number().int(), historique_jours: z.number().int() }),
  choix: z.object({ premier: isoDate, dernier: isoDate, nombre: z.number().int().positive(), exemple: isoDate }),
  mesure: z.object({ semaines: z.number().int().positive(), premiere: isoDate, derniere: isoDate, regle: z.number(), hasard: z.number(),
    affiche: z.object({ regle: lang, hasard: lang }) }),
  lundis: z.array(z.object({ lundi: isoDate, choisissable: z.boolean(), historique_jours: z.number().int(),
    entreprises_classees: z.number().int().positive(), entreprises_actives: z.number().int().nonnegative(),
    obtenu: z.number().int().min(0).max(10), dix: z.array(mondayCompany).length(10) })
    .refine((m) => m.obtenu === m.dix.filter((c) => c.nouveau_marche).length, "le nombre obtenu est celui des dix")),
}).refine((d) => d.lundis.filter((m) => m.choisissable).length === d.choix.nombre, "le nombre de lundis au choix")
  .refine((d) => d.lundis.some((m) => m.lundi === d.choix.exemple && m.choisissable), "l'exemple préparé est un lundi au choix");

const territoryContract = z.object({ id: z.string().min(1), date: isoDate, titre: z.string(), url: z.url() });
export const territory = z.object({
  schema: z.literal(1), lundi: isoDate, source: z.object({ nom: z.string(), mention: z.string().min(1) }),
  controles: z.record(z.string(), z.string().min(1)),
  exemple: z.object({ commune: z.string().regex(/^\d+$/), entreprise: z.string().min(1) }),
  communes: z.record(z.string().regex(/^\d+$/), z.object({ siege: z.array(z.string()), marches: z.array(territoryContract) })),
  entreprises: z.record(z.string(), z.object({ nom: z.string().min(1), ville: z.string().nullable(), commune_siege: z.number().int().positive(),
    guide: z.boolean(), consortium: z.boolean() })),
  exclues: z.array(z.object({ id: z.string(), nom: z.string(), controles_echoues: z.array(z.string()).min(1) })),
}).refine((d) => d.communes[d.exemple.commune]?.siege.includes(d.exemple.entreprise), "l'exemple préparé est sur la carte")
  .refine((d) => Object.values(d.communes).every((c) => [...c.siege, ...c.marches.map((m) => m.id)].every((id) => id in d.entreprises)),
    "chaque entreprise de la carte passe les contrôles");

export const nextMondayData = z.object({
  schema: z.literal(1), premier: isoDate, lundi: isoDate, fin_des_donnees: isoDate, regle: z.string().min(1),
  classement: z.array(z.object({ id: z.string().min(1), nom: z.string().min(1), ville: z.string().nullable(),
    rang: z.number().int().positive() })).min(10),
  nouvelles_publications: z.array(z.string()),
});

export const communes = z.object({
  meta: z.object({ source: z.string().min(1), attribution: z.string().min(1), licence: z.string().min(1), url: z.url(),
    projection: z.object({ lon0: z.number(), lat1: z.number(), k: z.number(), cos_lat: z.number() }),
    bbox: z.tuple([z.number(), z.number(), z.number(), z.number()]) }),
  canton: z.string().min(1),
  communes: z.array(z.object({ bfs: z.number().int().positive(), nom: z.string().min(1), d: z.string().startsWith("M") })),
});

const liveContract = z.object({ date: isoDate, titre: z.string().min(1), adjudicateur: z.string().nullable(), commune: z.string().nullable(),
  laureats: z.array(z.object({ nom: z.string().min(1), id: z.string().regex(/^ent-[0-9a-f]{10}$/) })), url: z.url() });
const correctionKind = z.enum(["correction", "revocation", "abandonment"]);
const simapProjectPage = z.string().regex(/^https:\/\/www\.simap\.ch\/(fr|de|it|en)\/project-detail\/[0-9a-f-]{36}$/);
const period = z.object({ du: isoDate, au: isoDate });
// « Chaque matin, en direct de simap » (suite 10, § 2): on Monday the week that ended, from Tuesday to Friday the day
// before; never anything of the day of the reading (AGB API simap ch. 5 al. 2)
export const liveMorning = z.object({
  schema: z.literal(2), etat: z.enum(["a_jour", "en_attente"]), mode: z.enum(["semaine", "veille"]).nullable(),
  periode: period.nullable(), mis_a_jour_le: isoDate.nullable(), source: z.literal("simap.ch"), mention: z.string().min(1),
  total: z.number().int().nonnegative(), marches: z.array(liveContract),
  rectifications: z.array(z.object({ date: isoDate, type: correctionKind, titre: z.string().min(1), url: simapProjectPage })).optional(),
}).refine((w) => w.etat === "en_attente" || (w.mode !== null && w.periode !== null && w.mis_a_jour_le !== null), "une lecture à jour a sa date et sa période")
  .refine((w) => w.total >= w.marches.length, "le total compte au moins les marchés montrés")
  .refine((w) => [...w.marches, ...(w.rectifications ?? [])].every((c) => w.mis_a_jour_le !== null && c.date < w.mis_a_jour_le
    && w.periode !== null && c.date >= w.periode.du && c.date <= w.periode.au), "rien du jour de la lecture, rien hors de la période");
// « Choisissez une date »: the same section, frozen, for every Monday that can be chosen
export const frozenMornings = z.object({
  schema: z.literal(1), source: z.literal("simap.ch"), mention: z.string().min(1),
  lundis: z.record(isoDate, z.object({ periode: period, total: z.number().int().nonnegative(), marches: z.array(liveContract) })),
}).refine((f) => Object.entries(f.lundis).every(([monday, m]) => m.marches.every((c) => c.date < monday)), "seulement ce qui était publié avant ce lundi");
// the map of the sources (suite 10, § 3), counted from data/catalogue.csv by `proxsis carte-sources` (CLAIMS SOURCES-1)
const countOf = z.number().int().nonnegative();
export const sourceMap = z.object({
  schema: z.literal(1), claims: z.literal("SOURCES-1"), catalogue: z.literal("data/catalogue.csv"), etudiees: countOf,
  en_service: z.object({ nombre: countOf, lignes: z.array(z.string()) }),
  demandes: z.object({ nombre: countOf, liste: z.array(z.object({ cle: z.enum(["portail", "zefix", "jobroom", "regbl"]), lignes: z.array(z.string()),
    fichier: z.string().startsWith("docs/demandes/"), statut: z.literal("envoyee"), mois: z.string().regex(/^\d{4}-\d{2}$/) })) }),
  ecartees: z.object({ nombre: countOf, familles: z.record(z.enum(["particuliers", "conditions", "prive", "injoignable"]), z.array(z.string())) }),
  autres: z.object({ nombre: countOf, conditions_a_verifier: countOf, sans_usage_pour_la_liste: countOf }),
}).refine((c) => c.etudiees === c.en_service.nombre + c.demandes.nombre + c.ecartees.nombre + c.autres.nombre, "les groupes font le total")
  .refine((c) => c.autres.nombre === c.autres.conditions_a_verifier + c.autres.sans_usage_pour_la_liste, "les autres font leur total");
export const correctionsFile = z.object({
  schema: z.literal(1), mis_a_jour_le: isoDate.nullable(), source: z.literal("simap.ch"), mention: z.string().min(1),
  avis: z.array(z.object({ projet: z.string().regex(/^[0-9a-f-]{36}$/), date: isoDate, type: correctionKind, url: simapProjectPage })),
}).refine((f) => f.avis.every((n) => n.url.endsWith(`/${n.projet}`)), "chaque avis renvoie à la page de son projet")
  .refine((f) => f.avis.every((n) => f.mis_a_jour_le !== null && n.date < f.mis_a_jour_le), "rien du lundi de la lecture (règle des 8 h)");
