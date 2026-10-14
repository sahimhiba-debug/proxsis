// Texts of the old presentation's acts 4 to 7 that the site still shows, FR and DE: « Choisissez une date »
// (ChooseDate.tsx), the proof dossier and its three dated stories (Proofs.tsx, Stories.tsx), and the act and step
// labels merged into copy.ts. Checked by copy_c.test.ts (vocabulary, same keys FR/DE, no hard-coded digit on screen,
// mandatory sentences word for word). `{…}`: values that come from the data; no figure is written in a screen text.


export const ETAPES_C = ["date", "mesure", "replacer", "calcul", "pilote", "historique", "condition", "synthese"] as const;
/** The three dated stories, out of the guided path since 07.10.2026: kept in the proof dossier (/presentation/preuves/). */
export const RESERVE_C = ["histoire1", "histoire2", "histoire3"] as const;
export type EtapeC = (typeof ETAPES_C)[number] | (typeof RESERVE_C)[number];

const fr = {
  acts: {
    4: "Revenir à ce qui était connu",
    5: "L'hypothèse que vous pouvez faire tomber",
    6: "Six semaines pour décider",
  } as Record<number, string>,
  steps: {
    date: "Choisissez une date",
    histoire1: "Première histoire",
    histoire2: "Deuxième histoire",
    histoire3: "Troisième histoire",
    mesure: "Le premier examen",
    replacer: "Les fins de mission",
    calcul: "Vos hypothèses",
    pilote: "Le pilote proposé",
    historique: "Les informations demandées",
    condition: "Votre condition",
    synthese: "Votre prochain lundi",
  } as Record<EtapeC, string>,
  dir: {
    // The proof dossier (/presentation/preuves/): the three dated stories, kept in reserve since 07.10.2026.
    preuves: {
      title: "Dossier de preuves",
      lead: "Trois histoires datées, choisies pour illustrer, dont une limite. Elles ne mesurent rien : la mesure, c'est « Choisissez une date ».",
      back: "Retour à la présentation",
    },
    // Act 4 (Hiba, 07.10.2026), « Choisissez une date »: the director's own past Monday, the ten companies of the
    // unchanged simple rule that day (publications published before it only), then what they obtained in 8 weeks.
    // The three dated stories that opened act 4 are kept in the proof dossier (/presentation/preuves/).
    date: {
      choose: "Choisissez une date",
      title: "Votre lundi du {date}",
      example: "exemple préparé",
      show: "Voir ce lundi",
      snapped: "Ramenée au lundi de sa semaine.",
      range: "Du {first} au {last} : {w} semaines de publications avant chaque lundi, {h} semaines complètes après.",
      tooEarly: "Trop tôt : il faut {w} semaines de publications avant. Premier lundi possible : {first}.",
      tooLate: "Trop tard : il faut {h} semaines complètes après. Dernier lundi possible : {last}.",
      invalid: "Cette date n'est pas lisible.",
      rule: "La règle simple, inchangée : les {k} entreprises valaisannes du bâtiment qui ont remporté le plus de marchés publics dans les {w} semaines avant ce lundi. Seules les publications parues avant cette date comptent.",
      awards: "{n} marchés en {w} semaines",
      last: "dernier le {date}",
      ask: "Et dans les {h} semaines suivantes ?",
      won: "Nouveau marché publié le {date}",
      wonMore: "Nouveau marché publié le {date}, et {n} autres",
      wonMoreOne: "Nouveau marché publié le {date}, et un autre",
      none: "Pas de nouveau marché public dans les {h} semaines",
      count: "{n} sur {k} ont remporté un nouveau marché public dans les {h} semaines.",
      branch: "Autre inscription de l'entreprise n° {n} (succursale) : comptée à part, comme dans la mesure.",
      all: "Et sur tous les lundis ?",
      // the measure keeps its 57 Mondays (CLAIMS REEL-SPEC-BAT); the first two, with less than a year of publications
      // before them, cannot be chosen (« deux » checked against the data in mondayData.test.ts)
      mean: "Sur les {n} lundis de la mesure, du {from} au {to} : {p} en moyenne. Les deux premiers ne sont pas proposés au choix : il y a moins d'un an de publications avant eux.",
      random: "{k} entreprises tirées au hasard : {p}.",
      aveu: "Sur notre premier test, une sélection plus compliquée n'a pas fait mieux qu'une règle simple. Nous avons gardé la règle simple. Le pilote mesurera si les dossiers préparés aident vos consultants à obtenir des conversations utiles, et à quel coût.",
      // the confession is about REEL-T0, not the measure just shown (agent « preuves », § 4): its own scope, figures read
      // from histoires.json (« vingt » checked against the data in mondayData.test.ts)
      aveuScope: "Ce premier test portait sur un autre périmètre : la construction en Suisse romande, vingt entreprises par semaine pendant {weeks} semaines (règle simple {rule}, sélection plus compliquée {m0}).",
      closing: "Un nouveau marché n'est pas une commande. Avec votre historique de commandes, cette même vue montrerait ce qui compte : lesquelles vous ont appelés.",
      proofs: "Dossier de preuves : trois histoires datées",
    },
    // Act 4: three dated stories, three manual stops each; nothing published after the replayed date is shown or used.
    histoire: {
      statement: "Ce qu'on savait ce jour-là. *Rien de plus.*",
      kicker: "Histoire {n} sur {total}",
      limit: "Une limite",
      stops: {
        known: "Ce qui était connu le {date}",
        signal: "La raison d'appeler",
        after: "Ce qui s'est passé ensuite",
      },
      published: "Publié le {date}",
      hidden: "Pas encore publié le {date}",
      replay: "Rejeu au {date} : aucune information publiée plus tard n'est utilisée, ni à l'écran ni pour établir la liste.",
      interval: "{n} jours entre {from} et {to}",
      intervalOne: "{n} jour entre {from} et {to}",
      intervalSame: "Le même jour : {from} et {to}",
      // Named events of an interval; « demande » only if a request for staff is really documented.
      events: {
        rejeu: "la date rejouée",
        appel: "la publication de l'appel d'offres",
        attribution: "la publication de l'attribution du marché",
        debut: "le début du chantier",
        autorisation: "la demande d'autorisation de construire",
        suivant: "la publication du marché suivant remporté",
        demande: "la demande de personnel documentée",
      },
      question: "Ce chantier demandera-t-il du personnel temporaire ?",
      noAnswer: "Les pièces disponibles ne permettent pas de répondre.",
      need: "Le besoin de personnel reste à confirmer.",
      actions: {
        signal: "Avec ces seules pièces",
        after: "Et ensuite ?",
        next: "Histoire suivante",
        measure: "Le premier examen",
      },
    },
  },
};

type CopyC = typeof fr;

const de: CopyC = {
  acts: {
    4: "Zurück zu dem, was bekannt war",
    5: "Die Annahme, die Sie kippen können",
    6: "Sechs Wochen, um zu entscheiden",
  },
  steps: {
    date: "Wählen Sie ein Datum",
    histoire1: "Erste Geschichte",
    histoire2: "Zweite Geschichte",
    histoire3: "Dritte Geschichte",
    mesure: "Die erste Prüfung",
    replacer: "Die Einsatzenden",
    calcul: "Ihre Annahmen",
    pilote: "Der vorgeschlagene Pilotversuch",
    historique: "Die erbetenen Angaben",
    condition: "Ihre Bedingung",
    synthese: "Ihr nächster Montag",
  },
  dir: {
    preuves: {
      title: "Beweisdossier",
      lead: "Drei datierte Geschichten, zur Veranschaulichung gewählt, darunter eine Grenze. Sie messen nichts: Die Messung ist «Wählen Sie ein Datum».",
      back: "Zurück zur Präsentation",
    },
    date: {
      choose: "Wählen Sie ein Datum",
      title: "Ihr Montag vom {date}",
      example: "vorbereitetes Beispiel",
      show: "Diesen Montag zeigen",
      snapped: "Auf den Montag seiner Woche gebracht.",
      range: "Vom {first} bis {last}: {w} Wochen Publikationen vor jedem Montag, {h} volle Wochen danach.",
      tooEarly: "Zu früh: Es braucht {w} Wochen Publikationen davor. Erster möglicher Montag: {first}.",
      tooLate: "Zu spät: Es braucht {h} volle Wochen danach. Letzter möglicher Montag: {last}.",
      invalid: "Dieses Datum ist nicht lesbar.",
      rule: "Die einfache Regel, unverändert: die {k} Walliser Bauunternehmen, die in den {w} Wochen vor diesem Montag die meisten öffentlichen Aufträge gewonnen haben. Es zählen nur Publikationen, die vor diesem Datum erschienen sind.",
      awards: "{n} Aufträge in {w} Wochen",
      last: "letzter am {date}",
      ask: "Und in den {h} Wochen danach?",
      won: "Neuer Auftrag publiziert am {date}",
      wonMore: "Neuer Auftrag publiziert am {date}, dazu {n} weitere",
      wonMoreOne: "Neuer Auftrag publiziert am {date}, dazu ein weiterer",
      none: "Kein neuer öffentlicher Auftrag in {h} Wochen",
      count: "{n} von {k} haben in {h} Wochen einen neuen öffentlichen Auftrag gewonnen.",
      branch: "Weiterer Eintrag des Unternehmens Nr. {n} (Filiale): separat gezählt, wie in der Messung.",
      all: "Und über alle Montage?",
      mean: "Über die {n} Montage der Messung, vom {from} bis {to}: im Schnitt {p}. Die ersten zwei sind nicht wählbar: Vor ihnen liegt weniger als ein Jahr an Publikationen.",
      random: "{k} zufällig gezogene Unternehmen: {p}.",
      aveu: "Bei unserem ersten Test hat eine kompliziertere Auswahl nicht besser abgeschnitten als eine einfache Regel. Wir haben die einfache Regel behalten. Der Pilotversuch wird messen, ob die vorbereiteten Dossiers Ihren Beraterinnen und Beratern zu nützlichen Gesprächen verhelfen, und zu welchen Kosten.",
      aveuScope: "Dieser erste Test betraf einen anderen Bereich: Bau in der Westschweiz, zwanzig Unternehmen pro Woche während {weeks} Wochen (einfache Regel {rule}, kompliziertere Auswahl {m0}).",
      closing: "Ein neuer öffentlicher Auftrag ist noch keine Bestellung. Mit Ihrer Bestellhistorie würde dieselbe Ansicht zeigen, was zählt: welche Firmen Sie angerufen haben.",
      proofs: "Beweisdossier: drei datierte Geschichten",
    },
    histoire: {
      statement: "Was man an diesem Tag wusste. *Nicht mehr.*",
      kicker: "Geschichte {n} von {total}",
      limit: "Eine Grenze",
      stops: {
        known: "Was am {date} bekannt war",
        signal: "Der Grund anzurufen",
        after: "Was danach geschah",
      },
      published: "Publiziert am {date}",
      hidden: "Am {date} noch nicht publiziert",
      replay: "Stichtag {date}: Keine später publizierte Information wird verwendet, weder auf dem Bildschirm noch für die Liste.",
      interval: "{n} Tage zwischen {from} und {to}",
      intervalOne: "{n} Tag zwischen {from} und {to}",
      intervalSame: "Am selben Tag: {from} und {to}",
      events: {
        rejeu: "dem Stichtag",
        appel: "der Publikation der Ausschreibung",
        attribution: "der Publikation des Zuschlags",
        debut: "dem Baubeginn",
        autorisation: "dem Baugesuch",
        suivant: "der Publikation des nächsten gewonnenen Auftrags",
        demande: "der belegten Personalanfrage",
      },
      question: "Wird diese Baustelle Temporärpersonal brauchen?",
      noAnswer: "Die verfügbaren Unterlagen geben darauf keine Antwort.",
      need: "Der Personalbedarf ist noch zu bestätigen.",
      actions: {
        signal: "Nur mit diesen Unterlagen",
        after: "Und dann?",
        next: "Nächste Geschichte",
        measure: "Die erste Prüfung",
      },
    },
  },
};

export const COPY_C: Record<"fr" | "de", CopyC> = { fr, de };
