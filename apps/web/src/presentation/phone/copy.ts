// Texts of the piloted phone demo, FR and DE (Swiss usage: « ss », never « ß »).
// Checked against vocabulary.ts and free of figures except the replayed Monday (copy.test.ts).
import type { PLang, StepId } from "./script";

/** Mentions at the level of the information (brief, storyboard § 0): the same wording as the presentation. */
export const MENTIONS = {
  fr: {
    real: "Entreprise réelle",
    published: "Information publiée",
    toConfirm: "Besoin à confirmer",
    fictionalPerson: "Personne fictive",
    illustrative: "Situation illustrative",
  },
  de: {
    real: "Reales Unternehmen",
    published: "Veröffentlichte Information",
    toConfirm: "Bedarf zu bestätigen",
    fictionalPerson: "Fiktive Person",
    illustrative: "Beispielsituation",
  },
} as const;

type StepCopy = { label: string; caption: string; mention: string[] };

interface PhoneCopy {
  phone: { label: string; frameTitle: string; clock: string; legend: string; skip: string };
  pilot: { hint: string; paused: string; resume: string };
  review: { title: string; kicker: string; step: string; keys: string; still: string; motion: string;
    language: string; route: string; prev: string; next: string };
  steps: Record<StepId, StepCopy>;
}

const M = MENTIONS;

const fr: PhoneCopy = {
  phone: {
    label: "Téléphone : l'application Proxsis, de vraies pages à taille mobile",
    frameTitle: "Application Proxsis (page réelle)",
    clock: "8:03",
    legend: "Application · prototype, concept non officiel",
    skip: "Passer le téléphone",
  },
  pilot: {
    hint: "Démo pilotée · touchez l'écran pour prendre la main",
    paused: "Vous avez la main : la démo attend.",
    resume: "Reprendre la démo",
  },
  review: {
    title: "Démo pilotée : le téléphone",
    kicker: "Démo pilotée · l'application réelle",
    step: "Étape {n} sur {total}",
    keys: "← → pour avancer ou revenir",
    still: "Sans mouvement",
    motion: "Avec mouvement",
    language: "Deutsch",
    route: "Le parcours",
    prev: "Retour",
    next: "Continuer",
  },
  steps: {
    semaine: {
      label: "Ma semaine",
      caption: "Lundi 5 octobre 2026, rejoué : à Martigny, la liste des entreprises à appeler cette semaine.",
      mention: [M.fr.real, M.fr.fictionalPerson],
    },
    dossier: {
      label: "Le dossier",
      caption: "Un geste ouvre l'entreprise : pourquoi elle est sur la liste et ce qui a été publié, avec la source.",
      mention: [M.fr.real, M.fr.published],
    },
    appel: {
      label: "L'appel préparé",
      caption: "L'appel est prêt : une ouverture et la raison d'appeler, chaque phrase reliée à sa source.",
      mention: [M.fr.published, M.fr.toConfirm],
    },
    synthese: {
      label: "La synthèse",
      caption: "La même feuille, lisible sur un téléphone : la version imprimable, lue depuis la séance de cet appareil.",
      mention: [M.fr.real],
    },
  },
};

const de: PhoneCopy = {
  phone: {
    label: "Telefon: die App Proxsis, echte Seiten in Handygrösse",
    frameTitle: "App Proxsis (echte Seite)",
    clock: "8:03",
    legend: "App · Prototyp, inoffizielles Konzept",
    skip: "Telefon überspringen",
  },
  pilot: {
    hint: "Gesteuerte Demo · Bildschirm berühren, um selbst zu übernehmen",
    paused: "Sie haben übernommen: Die Demo wartet.",
    resume: "Demo fortsetzen",
  },
  review: {
    title: "Gesteuerte Demo: das Telefon",
    kicker: "Gesteuerte Demo · die echte App",
    step: "Schritt {n} von {total}",
    keys: "← → zum Weiter- oder Zurückgehen",
    still: "Ohne Bewegung",
    motion: "Mit Bewegung",
    language: "Français",
    route: "Der Ablauf",
    prev: "Zurück",
    next: "Weiter",
  },
  steps: {
    semaine: {
      label: "Meine Woche",
      caption: "Montag, 5. Oktober 2026, nachgespielt: in Martigny die Liste der Unternehmen, die diese Woche anzurufen sind.",
      mention: [M.de.real, M.de.fictionalPerson],
    },
    dossier: {
      label: "Das Dossier",
      caption: "Eine Geste öffnet das Unternehmen: warum es auf der Liste steht und was publiziert wurde, mit Quelle.",
      mention: [M.de.real, M.de.published],
    },
    appel: {
      label: "Der vorbereitete Anruf",
      caption: "Der Anruf ist vorbereitet: ein Einstieg und der Grund für den Anruf, jeder Satz mit seiner Quelle.",
      mention: [M.de.published, M.de.toConfirm],
    },
    synthese: {
      label: "Die Zusammenfassung",
      caption: "Dieselbe Seite, auf einem Telefon lesbar: die Druckversion, aus der Sitzung dieses Geräts gelesen.",
      mention: [M.de.real],
    },
  },
};

export const PHONE_COPY: Record<PLang, PhoneCopy> = { fr, de };
