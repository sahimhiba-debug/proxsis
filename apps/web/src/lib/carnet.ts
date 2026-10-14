// The carnet (brief « à distance », § 6): ONE vocabulary for the decisions on the Monday list and what followed a call,
// shared by the visit and the application. No free text anywhere, so no name of a person can be written into it; kept
// on the device only. Not a CRM: it keeps the decisions on the Monday list, never a client record.
import { frenchDeep } from "@/lib/typo";

export const DECISIONS = ["appeler", "verifier", "revoir", "ecarter"] as const;
export type CarnetDecision = (typeof DECISIONS)[number];
export const MOTIFS = ["client", "contact", "pertinent", "autre"] as const; // why a company is set aside
export type Motif = (typeof MOTIFS)[number];
export const OUTCOMES = ["pasJoint", "pasBesoin", "rappel", "besoin", "etape"] as const; // what followed the call
export type Outcome = (typeof OUTCOMES)[number];
/** « Une conversation utile » : a call back agreed on a date, a confirmed need or an accepted next step. */
export const USEFUL: readonly Outcome[] = ["rappel", "besoin", "etape"];

export interface CarnetEntry {
  decision: CarnetDecision;
  revoir?: string; // « Revoir le… »: AAAA-MM-JJ
  motif?: Motif; // « Écarter »: the closed reason
  confie?: boolean; // handed to the demonstration role (explicitly fictional)
}

const ISO = /^\d{4}-\d{2}-\d{2}$/;

/** A stored entry, field by field: anything unknown is dropped (an entry edited by hand never breaks a screen). */
export function parseEntry(x: unknown): CarnetEntry | null {
  if (!x || typeof x !== "object") return null;
  const o = x as Record<string, unknown>;
  if (!DECISIONS.includes(o.decision as CarnetDecision)) return null;
  const entry: CarnetEntry = { decision: o.decision as CarnetDecision };
  if (o.decision === "revoir") {
    if (typeof o.revoir !== "string" || !ISO.test(o.revoir)) return null;
    entry.revoir = o.revoir;
  }
  if (o.decision === "ecarter") entry.motif = MOTIFS.includes(o.motif as Motif) ? (o.motif as Motif) : "autre";
  if (o.confie === true && o.decision !== "ecarter") entry.confie = true;
  return entry;
}

export const CARNET_COPY = {
  fr: frenchDeep({
    decisions: { appeler: "À appeler", verifier: "À vérifier", revoir: "Revoir le…", ecarter: "Écarter" },
    revoirOn: "Revoir le {date}",
    motifs: { client: "déjà client", contact: "déjà en contact", pertinent: "pas pertinent", autre: "autre" },
    motifLabel: "Pourquoi l'écarter ?",
    dateLabel: "Revoir le",
    outcomes: { pasJoint: "pas joint", pasBesoin: "pas de besoin", rappel: "rappel convenu le…", besoin: "besoin confirmé",
      etape: "prochaine étape acceptée" },
    useful: "Une conversation utile, c'est une date fixée, un besoin confirmé ou une prochaine étape acceptée.",
    role: "Consultant bâtiment",
    roleNote: "rôle fictif de démonstration",
    confide: "Confier à {role}",
    confided: "Confié à {role}",
    noFreeText: "Le carnet n'a aucun champ libre : il ne garde que des choix.",
    // the application's carnet (dossier, call, « Ma semaine »)
    panel: "Carnet",
    decisionTitle: "Votre décision",
    afterCall: "Après l'appel",
    fieldNotes: "Retours du terrain",
    notedOn: "noté le {date}",
    rappelOn: "rappel convenu le {date}",
    rappelDate: "Date du rappel",
    undo: "Retirer la dernière note",
    deviceOnly: "Gardé sur cet appareil seulement, jamais envoyé.",
    trial: {
      title: "Mode essai : semaine témoin",
      on: "Mode essai activé",
      off: "Activer le mode essai",
      prep: "Temps de préparation (minutes)",
      export: "Exporter l'essai (un fichier, sans nom)",
      exportNote: "Le fichier reste sur votre appareil ; il ne va jamais dans le dépôt ni sur le site.",
      count: "{n} entreprises notées",
    },
  }),
  de: {
    decisions: { appeler: "Anrufen", verifier: "Prüfen", revoir: "Wieder ansehen am…", ecarter: "Verwerfen" },
    revoirOn: "Wieder ansehen am {date}",
    motifs: { client: "bereits Kunde", contact: "bereits in Kontakt", pertinent: "nicht relevant", autre: "anderes" },
    motifLabel: "Warum verwerfen?",
    dateLabel: "Wieder ansehen am",
    outcomes: { pasJoint: "nicht erreicht", pasBesoin: "kein Bedarf", rappel: "Rückruf vereinbart am…", besoin: "Bedarf bestätigt",
      etape: "nächster Schritt angenommen" },
    useful: "Ein nützliches Gespräch ist ein vereinbartes Datum, ein bestätigter Bedarf oder ein angenommener nächster Schritt.",
    role: "Personalberatung Bau",
    roleNote: "fiktive Rolle für die Demonstration",
    confide: "Übergeben an {role}",
    confided: "An {role} übergeben",
    noFreeText: "Das Notizbuch hat kein freies Textfeld: Es behält nur Auswahlen.",
    panel: "Notizbuch",
    decisionTitle: "Ihr Entscheid",
    afterCall: "Nach dem Anruf",
    fieldNotes: "Rückmeldungen aus dem Feld",
    notedOn: "notiert am {date}",
    rappelOn: "Rückruf vereinbart am {date}",
    rappelDate: "Datum des Rückrufs",
    undo: "Letzte Notiz entfernen",
    deviceOnly: "Nur auf diesem Gerät gespeichert, nie versendet.",
    trial: {
      title: "Versuchsmodus: Testwoche",
      on: "Versuchsmodus aktiv",
      off: "Versuchsmodus aktivieren",
      prep: "Vorbereitungszeit (Minuten)",
      export: "Versuch exportieren (eine Datei, ohne Namen)",
      exportNote: "Die Datei bleibt auf Ihrem Gerät; sie kommt nie ins Repository oder auf die Website.",
      count: "{n} Unternehmen notiert",
    },
  },
} as const;
