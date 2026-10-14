// Texts of « Votre prochain lundi » — public screen (three lines at most per scene) and presenter notes, FR and DE.
// Checked by vocabulary.test.ts: no internal jargon in anything the director reads or hears.

import { COPY_C } from "./copy_c";

export type PLang = "fr" | "de";


const fr = {
  controls: {
    head: "En-tête de la présentation",
    foot: "Mentions et navigation de la présentation",
  },
  acts: {
    1: "La demande urgente",
    2: "Le Valais se réveille",
    3: "Les entreprises que vous reconnaissez",
    ...COPY_C.fr.acts,
    7: "Votre prochain lundi",
  } as Record<number, string>,
  source: { unavailable: "Source indisponible pour le moment. La référence reste affichée ci-dessus.", mention: "Mention obligatoire",
    mentionOriginal: "", translation: "" },
  steps: {
    lundi: "Lundi", heure: "8 h 03", demande: "La demande", territoire: "Le territoire", annonce: "L'annonce",
    choix: "Les entreprises", entreprise: "L'entreprise", raison: "La raison d'appeler", appel: "L'appel préparé",
    telephone: "Sur son téléphone",
    personnes: "Les personnes", mission: "La mission suivante", verifications: "Les vérifications", decision: "Votre décision",
    ...COPY_C.fr.steps,
  } as Record<string, string>,
  // Editorial direction (06.10.2026, maquette de Hiba): *words between stars* are set in serif italic.
  dir: {
    // the product's name, its signature and what it is, next to the logo (brief of Hiba, 07.10.2026)
    name: "Proxsis",
    // the promise in one sentence, on the opening and at the end (Hiba, 07.10.2026): no figure, the pilot measures
    promise: "Avec Proxsis, chaque consultant commence sa semaine avec dix appels préparés, et une raison vérifiable pour chacun. Combien de missions cela vous apportera, c'est ce que le pilote mesurera.",
    signature: "La prochaine entreprise à appeler.",
    prototype: "Prototype · concept non officiel",
    // act 4: names of the published pieces and of the intervals (the facts themselves come from histoires.json)
    stories: { award: "Adjudication", tender: "Appel d'offres", open: "encore en appel d'offres ce jour-là", day1: "jour",
      days: "jours", source: "Source" },
  },
};

type Copy = typeof fr;

const de: Copy = {
  controls: {
    head: "Kopfzeile der Präsentation",
    foot: "Hinweise und Navigation der Präsentation",
  },
  acts: {
    1: "Die dringende Anfrage",
    2: "Das Wallis erwacht",
    3: "Die Unternehmen, die Sie kennen",
    ...COPY_C.de.acts,
    7: "Ihr nächster Montag",
  },
  source: { unavailable: "Quelle im Moment nicht verfügbar. Die Referenz bleibt oben angezeigt.", mention: "Pflichthinweis",
    mentionOriginal: " (Originalwortlaut, Französisch)",
    translation: "Übersetzung (nicht amtlich): «Dies ist keine amtliche Publikation. Massgebend sind die auf der Plattform www.simap.ch publizierten Daten.»" },
  steps: {
    lundi: "Montag", heure: "8.03 Uhr", demande: "Die Anfrage", territoire: "Das Gebiet", annonce: "Die Publikation",
    choix: "Die Unternehmen", entreprise: "Das Unternehmen", raison: "Der Grund für den Anruf", appel: "Der vorbereitete Anruf",
    telephone: "Auf dem Telefon",
    personnes: "Die Personen", mission: "Der nächste Einsatz", verifications: "Die Prüfungen", decision: "Ihre Entscheidung",
    ...COPY_C.de.steps,
  },
  dir: {
    name: "Proxsis",
    // DE: to be read again by a German speaker
    promise: "Mit Proxsis beginnt jede Beraterin und jeder Berater die Woche mit zehn vorbereiteten Anrufen und einem überprüfbaren Grund für jeden. Wie viele Einsätze Ihnen das bringt, misst der Pilot.",
    signature: "Das nächste Unternehmen, das Sie anrufen.",
    prototype: "Prototyp · inoffizielles Konzept",
    stories: { award: "Zuschlag", tender: "Ausschreibung", open: "an diesem Tag noch ausgeschrieben", day1: "Tag",
      days: "Tage",
      source: "Quelle" },
  },
};

export const COPY: Record<PLang, Copy> = { fr, de };
export type PresentationCopy = Copy;
