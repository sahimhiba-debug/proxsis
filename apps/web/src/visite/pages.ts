// The discreet pages of the conclusion (brief « à distance », § 5 and § 11), FR and DE: « Vos questions » (the answers
// of the brief, word for word), « Qui sommes-nous » (only the members Hiba gave, no empty slot) and
// « Pour vos équipes techniques » (sources and licences, the sources' roadmap, data protection, how it works, tests).
import { frenchDeep } from "@/lib/typo";
import { MORNING } from "@/lib/chaqueMatin";
import { APERTUS, PORTE } from "./copy";

const fr = {
  links: {
    questions: "Vos questions",
    equipe: "Qui sommes-nous",
    technique: "Pour vos équipes techniques",
    app: "Ouvrir l'application de démonstration",
  },
  back: "Revenir à la visite",
  // suite 9, § 10: on a phone, the detail of a dense screen opens with a touch (Plus.tsx); on a computer and on paper it
  // is shown as before
  plus: "En savoir plus",
  accueil: {
    title: "La prochaine entreprise à appeler.",
    titleStrong: "à appeler.", // Sora 600, orange (identite.css)
    // the sentence to remember, that the director can repeat to his group (brief of 07.10.2026, suite 2, § 1)
    retenir: "Chaque lundi, chaque consultant sait quelles dix entreprises appeler, pourquoi, et qui leur proposer.",
    subtitle: "Une entreprise réelle. Une raison publiée. Une question à poser.",
    start: "Voir Proxsis en 11 minutes", // measured, clicking only « Continuer » (questionnaire, B5; CLAIMS PRES-DUREE-1)
    summary: "Lire la synthèse (1 page)",
    preview: "Aperçu réel du produit",
    question: "La question d'appel",
  },
  // « Pour votre direction » (brief of 07.10.2026, suite 2, § 8; suite 3, § 3): a printable page to pass on to the
  // group, sober, with no person's name and without naming the group; its words quoted with their sources (CLAIMS
  // EXT-GROUPE-*, EXT-FLEXSIS-MOTS: the group's site is said, never its name or its address); the figures of the proof
  // come from lundis.json (CLAIMS PRES-DATE-1), never from this text
  direction: {
    title: "Pour votre direction",
    link: "Une page pour votre direction",
    retenir: "La phrase à retenir",
    probleme: { h: "Le problème", p: [
      "Dans l'intérim, la mission va souvent à l'agence qui appelle la première, avec des personnes disponibles.",
      "Les raisons d'appeler sont publiques, mais dispersées : marchés attribués, demandes d'autorisation de construire.",
    ] },
    preuve: { h: "La preuve",
      p: "Avant de vous proposer la liste, nous l'avons mise à l'épreuve du passé : {n} lundis, du {from} au {to}, rejoués un par un avec seulement ce qui était publié ce jour-là. Puis nous avons regardé la suite : dans les 8 semaines, en moyenne {rule} des dix entreprises de la liste ont remporté un nouveau marché public. Dix entreprises prises au hasard : {random}.",
      // on a phone, the same figures in one short sentence (the whole proof under « En savoir plus »)
      bref: "Testée sur {n} lundis passés : {rule} des entreprises de la liste ont remporté un nouveau marché public en 8 semaines, contre {random} au hasard.",
      limit: "Un marché remporté n'est pas une commande : c'est ce que l'essai mesurera.",
      claims: "Registre des mesures, ligne PRES-DATE-1" },
    essai: { h: "L'essai sans risque",
      p: "Une semaine avec deux consultants volontaires, dix appels préparés chacun. Rien à installer dans vos systèmes. Vous pouvez vous arrêter à la fin de la semaine." },
    // suite 9, § 8: the three steps of the door (PORTE), each with what it means
    avenir: { h: "L'avenir en trois étapes", steps: [
      { court: PORTE.fr.etapes[0], detail: "Dix appels préparés chacun, et leur avis ; rien à installer ; arrêt possible à la fin de la semaine." },
      { court: PORTE.fr.etapes[1], detail: "En Valais, comparées à votre façon de faire actuelle : une réponse chiffrée, avec vos chiffres ; seuil de réussite et conditions d'arrêt écrits avant de commencer." },
      { court: PORTE.fr.etapes[2], detail: "Puis les autres agences Flexsis, en français et en allemand, un lien avec vos outils et votre historique de commandes, sous accord de confidentialité." },
    ] },
    buts: { h: "Les buts du groupe, et ce que Proxsis y apporte",
      note: "Leurs mots, cités tels quels, avec leur source.",
      items: [
        { claims: "EXT-GROUPE-PARTS", quote: "« atteindre 10 % de parts de marché dans chaque canton d'ici à 2028 »",
          source: "site du groupe, article du 14.02.2024, lu le 07.10.2026",
          how: "Chaque lundi, agence par agence, les entreprises de son canton à appeler en premier, avec la raison de le faire." },
        { claims: "EXT-GROUPE-DELAI", quote: "améliorer « de manière mesurable le time-to-service »",
          source: "site du groupe, article du 12.08.2025, lu le 07.10.2026",
          how: "La raison d'appeler est prête avant l'appel et, avec votre vivier, les personnes à proposer ; l'essai mesurera ce qui change." },
        { claims: "EXT-GROUPE-TECH", quote: "« soutenir le personnel et améliorer son efficacité, et non le remplacer »",
          source: "site du groupe, article du 29.09.2026, lu le 07.10.2026",
          how: "Proxsis prépare, le consultant décide. Rien ne part tout seul." },
        { claims: "EXT-FLEXSIS-MOTS", quote: "Proximité, Humain, Expertise, Identité suisse",
          source: "flexsis.ch, page « Entreprise », lu le 07.10.2026",
          how: "Les entreprises autour de l'agence ; un consultant qui appelle et décide ; une raison datée et sourcée ; des publications suisses, en français et en allemand." },
      ] },
    // the door (suite 9, § 8): Hiba's texts word for word, its five guardrails, then the passage on Apertus, word for word
    // (suite 8, § 6); a possible future, said so
    iris: { h: PORTE.fr.titre, p: [...PORTE.fr.texte], apertus: APERTUS.fr as string, guardsTitle: "Les garde-fous", guards: [...PORTE.fr.gardeFous],
      future: "Rien de cela n'existe aujourd'hui." },
    save: "Enregistrer en PDF",
    visit: "Voir la visite",
    address: "La visite : {url}",
  },
  unePage: {
    title: "Proxsis en une page",
    // suite 10, § 2: Hiba's sentence first, where the Monday is spoken of (src/lib/chaqueMatin.ts)
    what: { h: "Ce que fait Proxsis", p: [
      MORNING.fr,
      "Chaque lundi, Iris, l'assistante de Proxsis, prépare pour chaque consultant dix entreprises à appeler, dans sa spécialité et sa région.",
      "Pour chacune : la publication qui donne une raison d'appeler, avec sa date et sa source ; ce qu'elle laisse envisager, à confirmer ; une question pour commencer l'appel.",
      "Iris prépare, le consultant décide. Le carnet garde ses choix, et le lundi suivant en tient compte.",
    ] },
    measure: { h: "Ce que nous avons vérifié", p: [
      "Avant de vous proposer la liste, nous l'avons mise à l'épreuve du passé : {n} lundis, rejoués un par un avec seulement ce qui était publié ce jour-là. Dans le bâtiment en Valais, {rule} des entreprises proposées ont remporté un nouveau marché public dans les 8 semaines qui ont suivi ; {random} pour des entreprises prises au hasard.",
      "Une sélection plus compliquée n'a pas fait mieux qu'une règle simple : nous avons gardé la règle simple.",
      "Un nouveau marché n'est pas une commande. Le pilote mesurera ce qui compte pour votre agence.",
    ] },
    proposal: { h: "Ce que nous proposons", p: [
      "D'abord une semaine avec deux consultants volontaires, sans rien installer. Puis six semaines dans deux agences, avec et sans Proxsis.",
      "Indicateurs, seuils, responsables, coût maximal et conditions d'arrêt : fixés ensemble avant le départ.",
    ] },
    save: "Enregistrer en PDF",
    visit: "Voir la visite",
    example: "Un exemple réel",
    address: "La visite : {url}",
    // la nouvelle Iris (suite 8, § 10), avec ses phrases (suite 8, § 6) et sa devise : le point sur le « i »
    iris: { name: "Iris", says: "Je suis Iris, l'assistante de Proxsis. Moi, je prépare. Vous, vous décidez.", motto: "Iris met les points sur les i." },
    // the door (suite 9, § 8), a short block: two sentences, then its three steps on one line (PORTE.etapes)
    porte: { h: PORTE.fr.titre,
      p: "Iris pourrait s'installer chez Flexsis, avec un agent qui lit les publications chaque matin et Apertus adapté à ses données, sur ses serveurs ou chez un hébergeur suisse. Rien de cela n'existe aujourd'hui : le consultant décidera, et les données de Flexsis resteront sous son contrôle, en Suisse, avec son accord écrit." },
  },
  questions: {
    title: "Vos questions",
    items: [
      { q: "Pourquoi vous écouter ?", bref: "Pour comparer, sur le terrain, avec votre façon de faire. Le gain chez vous reste à démontrer.",
        a: "Parce que nous pouvons vous montrer le travail que le consultant pourrait faire avec ces informations, puis le comparer à sa pratique actuelle. Nous n'avons pas encore démontré le gain chez vous. Si le pilote n'en montre pas suffisamment, nous aurons une raison claire de nous arrêter." },
      // Hiba's question « … un bon signal ? », without the word « signal » (forbidden on screen, brief § 9); the study is
      // checked on the NBER page (docs/recherche/, agent « preuves »): it measured Brazil, not temporary work
      { q: "Pourquoi un marché public serait-il une bonne raison d'appeler ?", bref: "Au Brésil, une étude a vu ces entreprises embaucher davantage. Chez vous, le pilote le mesurera.",
        a: "Une étude menée au Brésil (Ferraz, Finan et Szerman, NBER, 2015) a observé que les entreprises qui remportent un marché public embauchent davantage, dès le trimestre du contrat et au-delà. Nous ne savons pas encore si cela se traduit en commandes chez vous : c'est ce que le pilote mesurera." },
      { q: "Est-ce que cela existe déjà ?", bref: "Des données de chantier, oui. Proxsis, lui, organise le lundi de vos consultants.",
        a: "Des services de données de chantier existent, au Royaume-Uni pour les recruteurs, et en Suisse pour les demandes de permis. Proxsis ne vend pas des données : il organise le lundi de vos consultants, leurs décisions et leur suite." },
      { q: "Pourquoi ne pas simplement consulter simap ?", bref: "Vous pouvez. Nous ajoutons la liste, la question et le suivi.",
        a: "Vous pouvez. Nous préparons une liste adaptée, une question sourcée et le suivi de vos décisions. Le test dira si cela fait gagner du temps." },
      { q: "Vous allez surtout me ressortir mes clients habituels ?", bref: "Un peu, oui. Dans le carnet, vous pouvez les écarter.",
        a: "Un peu, oui : la règle favorise les entreprises déjà actives. Dans le carnet, vous pouvez écarter vos clients connus. Le pilote mesurera ce que Proxsis apporte sur les entreprises que vous appelez peu." },
      { q: "Nous avons déjà un logiciel pour suivre nos clients.", bref: "Proxsis ne le remplace pas. Il garde seulement vos décisions du lundi.",
        a: "Proxsis ne le remplace pas : il garde seulement vos décisions sur la liste du lundi. Pendant le pilote, nous verrons ce qui peut passer dans votre outil, pour ne rien saisir deux fois." },
      { q: "Combien de missions pouvez-vous garantir ?", bref: "Aucune aujourd'hui. Le pilote mesurera ce qui change.",
        a: "Aucune aujourd'hui. Nous avons mesuré l'activité publique. Le pilote comptera séparément les conversations utiles, les commandes et les journées supplémentaires facturées." },
      { q: "Mes consultants vont-ils vraiment l'utiliser ?", bref: "Nous ne le savons pas encore. Le premier essai le dira.",
        a: "Nous ne le savons pas encore. Le premier essai doit montrer s'ils préparent leurs appels plus vite, et s'ils y reviennent sans qu'on les pousse." },
      { q: "Combien cela coûte, et comment arrête-t-on ?", bref: "Le service et le temps de vos équipes. Le plafond et l'arrêt se fixent avant.",
        a: "Le coût comprend le service et le temps de vos équipes. Avant le pilote, nous fixons ensemble le plafond, le seuil de réussite, le responsable et les conditions d'arrêt." },
      // brief of 07.10.2026, § 3.6: the answer of the brief, word for word
      { q: "Pouvez-vous nous proposer des candidats ?", bref: "Oui, avec votre vivier, sous accord. Ici, les intérimaires sont fictifs.",
        a: "Oui, dès que vous nous confiez votre vivier, sous accord. Dans cette démonstration, les intérimaires sont fictifs. Les propositions tiennent compte du métier, du permis, de la disponibilité et de la distance." },
      // suite 9, Q02: the direct question is back; the honest answer (today, clear rules measured on past Mondays), then the
      // door (suite 9, § 8), with the passage on Apertus word for word (suite 8, § 6); never the acronym
      { q: "Utilisez-vous l'intelligence artificielle ?", bref: "Pas pour la liste : des règles claires, mesurées sur des lundis passés. Demain, peut-être, si Flexsis le souhaite.",
        a: `Pas pour la liste : aujourd'hui, elle vient de règles claires, mesurées sur cinquante-sept lundis passés, et chaque proposition affiche sa raison. Demain, si Flexsis le souhaite : ${APERTUS.fr} Et c'est toujours vous qui décidez.` },
    ],
  },
  equipe: {
    title: "Qui sommes-nous",
    contact: "Contact",
  },
  technique: {
    title: "Pour vos équipes techniques",
    sections: [
      { h: "Sources et licences", p: [
        "simap.ch : adjudications de marchés publics de construction, lues par l'accès officiel, selon ses conditions d'utilisation (version du 30.09.2023) ; le contenu publié n'est pas modifié, il est présenté à part de nos commentaires, avec la mention obligatoire.",
        "Bulletin officiel du Valais : demandes d'autorisation de construire, consultées par une personne ; une demande d'accès est préparée. Aucun script n'interroge le portail.",
        "swisstopo : contours des communes et répertoire des localités, données ouvertes (© swisstopo).",
      ] },
      { h: "Feuille de route des sources", p: [
        "Ce que Proxsis lit aujourd'hui, ce qu'il pourrait lire demain et l'état de chaque accès : page « Sources et mesures » de l'application.",
      ] },
      { h: "Protection des données", p: [
        "Proxsis cible des entreprises, jamais des particuliers. Un filtre écarte les données personnelles avant tout enregistrement ; un test vérifie que rien de ce que le projet publie n'en contient.",
        "Les personnes, missions et candidats de la démonstration sont fictifs et marqués comme tels.",
        "Vos saisies dans la visite restent dans votre navigateur, sur votre appareil ; elles ne sont pas envoyées à notre équipe.",
      ] },
      { h: "Fonctionnement", p: [
        "Chaque lundi, une liste d'entreprises par spécialité et par région, rangée par une règle simple : le nombre de marchés publics remportés en 52 semaines, puis le plus récent.",
        "Pour chaque entreprise, le fait publié qui donne une raison d'appeler, ce qu'il laisse envisager (une estimation à confirmer) et une question d'appel.",
        "Chaque chiffre renvoie à une mesure que l'on peut refaire, décrite avec sa méthode et ses limites (page « Sources et mesures »).",
      ] },
      { h: "Tests", p: [
        "À chaque modification : aucune donnée de particulier dans ce qui est publié, mentions obligatoires présentes, accessibilité, aucune requête hors du site, affichage identique dans deux jours, un mois et trois mois, et reproduction à l'octet des fichiers de données.",
      ] },
    ],
    measures: "Sources et mesures",
  },
  // the roadmap (Hiba, 14.10.2026): her text word for word, without any duration (docs/FEUILLE-DE-ROUTE.md); reached
  // from the end of the visit and from « Pour votre direction »
  feuille: {
    title: "Feuille de route",
    link: "La feuille de route",
    today: { h: "Aujourd'hui", measures: "Sources et mesures", p: "Un prototype en ligne, en français et en allemand, sur téléphone et sur ordinateur. La liste du lundi, mesurée sur 57 lundis passés (voir « Sources et mesures »). Deux sources officielles, et simap lu chaque matin. Les demandes d'accès envoyées : SECO, Zefix, Job-Room, registre des bâtiments. Rien n'est installé chez Flexsis, et aucune donnée de Flexsis n'est utilisée." },
    steps: [
      { h: "Étape 1 : un essai avec deux consultants volontaires, dans une agence", p: "Ils reçoivent la liste chaque lundi et la gardent, la reportent ou l'écartent. On mesure les appels, les rendez-vous et les missions, et on recueille leur avis. Ensuite, on décide : continuer, ajuster ou arrêter." },
      { h: "Étape 2 : l'historique de Flexsis, sous accord de confidentialité", p: "On mesure ce que la liste rapporte vraiment, et on l'adapte à chaque agence et à chaque métier. Les données restent sous le contrôle de Flexsis, en Suisse." },
      { h: "Étape 3 : plus de sources et plus d'agences", p: "Dès que les autorisations arrivent : le Bulletin officiel et le registre du commerce chaque matin, et Zefix. Chaque source est mesurée avant d'entrer dans la liste. On passe à deux agences, en français et en allemand." },
      { h: "Étape 4 : Iris chez Flexsis, si Flexsis le souhaite", p: "Une assistante pour chaque consultant, et un agent qui lit les publications chaque matin. Apertus, adapté aux données de Flexsis, sur ses serveurs ou chez un hébergeur suisse. Les cinq garde-fous s'appliquent toujours." },
      { h: "Étape 5 : toutes les agences, d'abord en Valais, puis dans les autres régions, chacune dans sa langue", p: "" },
    ],
    rule: { h: "La règle", p: "On passe à l'étape suivante seulement avec des résultats mesurés et l'accord de Flexsis." },
  },
};

type PagesCopy = typeof fr;

const de: PagesCopy = {
  links: {
    questions: "Ihre Fragen",
    equipe: "Wer wir sind",
    technique: "Für Ihre technischen Teams",
    app: "Die Demonstrationsanwendung öffnen",
  },
  back: "Zurück zum Rundgang",
  plus: "Mehr erfahren",
  accueil: {
    title: "Das nächste Unternehmen, das Sie anrufen.",
    titleStrong: "das Sie anrufen.",
    retenir: "Jeden Montag weiss jede Beraterin und jeder Berater, welche zehn Unternehmen anzurufen sind, warum, und wen man ihnen vorschlagen kann.",
    subtitle: "Ein echtes Unternehmen. Ein publizierter Grund. Eine Frage, die Sie stellen können.",
    start: "Proxsis in 11 Minuten ansehen",
    summary: "Die Zusammenfassung lesen (1 Seite)",
    preview: "Echter Einblick in das Produkt",
    question: "Die Frage für den Anruf",
  },
  direction: {
    title: "Für Ihre Geschäftsleitung",
    link: "Eine Seite für Ihre Geschäftsleitung",
    retenir: "Der Satz, den man sich merkt",
    probleme: { h: "Das Problem", p: [
      "In der Temporärbranche geht der Auftrag oft an die Filiale, die zuerst anruft, mit verfügbaren Personen.",
      "Die Gründe für einen Anruf sind öffentlich, aber verstreut: vergebene Aufträge, Baugesuche.",
    ] },
    preuve: { h: "Der Nachweis",
      p: "Bevor wir Ihnen die Liste vorschlagen, haben wir sie an der Vergangenheit geprüft: {n} Montage, vom {from} bis {to}, einer nach dem anderen nachgespielt, nur mit dem, was an jenem Tag publiziert war. Dann haben wir geschaut, was danach kam: Innerhalb von 8 Wochen haben im Durchschnitt {rule} der zehn Unternehmen der Liste einen neuen öffentlichen Auftrag erhalten. Zehn zufällig gewählte Unternehmen: {random}.",
      bref: "Getestet an {n} vergangenen Montagen: {rule} der Unternehmen der Liste gewannen in 8 Wochen einen neuen öffentlichen Auftrag, gegenüber {random} zufällig.",
      limit: "Ein gewonnener Auftrag ist keine Bestellung: Das wird der Versuch messen.",
      claims: "Register der Messungen, Zeile PRES-DATE-1" },
    essai: { h: "Der Versuch ohne Risiko",
      p: "Eine Woche mit zwei freiwilligen Beraterinnen oder Beratern, je zehn vorbereitete Anrufe. Nichts in Ihren Systemen zu installieren. Sie können am Ende der Woche aufhören." },
    avenir: { h: "Die Zukunft in drei Schritten", steps: [
      { court: PORTE.de.etapes[0], detail: "Je zehn vorbereitete Anrufe und ihre Meinung; nichts zu installieren; Abbruch am Ende der Woche möglich." },
      { court: PORTE.de.etapes[1], detail: "Im Wallis, verglichen mit Ihrer heutigen Arbeitsweise: eine bezifferte Antwort mit Ihren Zahlen; Erfolgsschwelle und Abbruchbedingungen vor dem Start schriftlich festgelegt." },
      { court: PORTE.de.etapes[2], detail: "Dann die anderen Flexsis-Filialen, auf Französisch und Deutsch, eine Verbindung mit Ihren Werkzeugen und Ihre Auftragshistorie, unter Vertraulichkeitsvereinbarung." },
    ] },
    buts: { h: "Die Ziele der Gruppe, und was Proxsis dazu beiträgt",
      note: "Ihre Worte, unverändert zitiert (Originalwortlaut, Französisch), mit Quelle.",
      items: [
        { claims: "EXT-GROUPE-PARTS", quote: "« atteindre 10 % de parts de marché dans chaque canton d'ici à 2028 »",
          source: "Website der Gruppe, Artikel vom 14.02.2024, gelesen am 07.10.2026",
          how: "Jeden Montag, Filiale für Filiale, die Unternehmen ihres Kantons, die zuerst anzurufen sind, mit dem Grund dafür." },
        { claims: "EXT-GROUPE-DELAI", quote: "améliorer « de manière mesurable le time-to-service »",
          source: "Website der Gruppe, Artikel vom 12.08.2025, gelesen am 07.10.2026",
          how: "Der Grund für den Anruf liegt vor dem Anruf bereit und, mit Ihrem Pool, die vorzuschlagenden Personen; der Versuch misst, was sich ändert." },
        { claims: "EXT-GROUPE-TECH", quote: "« soutenir le personnel et améliorer son efficacité, et non le remplacer »",
          source: "Website der Gruppe, Artikel vom 29.09.2026, gelesen am 07.10.2026",
          how: "Proxsis bereitet vor, die Beraterin oder der Berater entscheidet. Nichts geht von selbst hinaus." },
        { claims: "EXT-FLEXSIS-MOTS", quote: "Proximité, Humain, Expertise, Identité suisse",
          source: "flexsis.ch, Seite « Entreprise », gelesen am 07.10.2026",
          how: "Die Unternehmen rund um die Filiale; eine Person, die anruft und entscheidet; ein datierter Grund mit Quelle; Schweizer Publikationen, auf Französisch und Deutsch." },
      ] },
    iris: { h: PORTE.de.titre, p: [...PORTE.de.texte], apertus: APERTUS.de, guardsTitle: "Die Leitplanken", guards: [...PORTE.de.gardeFous],
      future: "Nichts davon existiert heute." },
    save: "Als PDF speichern",
    visit: "Den Rundgang ansehen",
    address: "Der Rundgang: {url}",
  },
  unePage: {
    title: "Proxsis auf einer Seite",
    what: { h: "Was Proxsis tut", p: [
      MORNING.de, // suite 10, § 2: to review
      "Jeden Montag bereitet Iris, die Assistentin von Proxsis, für jede Beraterin und jeden Berater zehn Unternehmen zum Anrufen vor, im eigenen Fachbereich und in der eigenen Region.",
      "Für jedes: die Publikation, die einen Grund zum Anruf gibt, mit Datum und Quelle; was sie erwarten lässt, zu bestätigen; eine Frage für den Anfang des Anrufs.",
      "Iris bereitet vor, die Beraterin oder der Berater entscheidet. Das Notizbuch behält ihre Entscheide, und der nächste Montag berücksichtigt sie.",
    ] },
    measure: { h: "Was wir geprüft haben", p: [
      "Bevor wir Ihnen die Liste vorschlagen, haben wir sie an der Vergangenheit geprüft: {n} Montage, einer nach dem anderen nachgespielt, nur mit dem, was an jenem Tag publiziert war. Bei der Bauliste im Wallis gewannen {rule} der vorgeschlagenen Unternehmen in den 8 Wochen danach einen neuen öffentlichen Auftrag; {random} bei zufällig gewählten Unternehmen.",
      "Eine kompliziertere Auswahl schnitt nicht besser ab als eine einfache Regel: Wir haben die einfache Regel behalten.",
      "Ein neuer Auftrag ist noch keine Bestellung. Der Pilotversuch misst, was für Ihre Filiale zählt.",
    ] },
    proposal: { h: "Was wir vorschlagen", p: [
      "Zuerst eine Woche mit zwei freiwilligen Beraterinnen oder Beratern, ohne etwas zu installieren. Dann sechs Wochen in zwei Filialen, mit und ohne Proxsis.",
      "Indikatoren, Schwellen, Verantwortliche, Höchstkosten und Abbruchbedingungen: gemeinsam vor dem Start festgelegt.",
    ] },
    save: "Als PDF speichern",
    visit: "Den Rundgang ansehen",
    example: "Ein echtes Beispiel",
    address: "Der Rundgang: {url}",
    // zu prüfen (Deutsch)
    iris: { name: "Iris", says: "Ich bin Iris, die Assistentin von Proxsis. Ich bereite vor. Sie entscheiden.", motto: "Iris bringt es auf den Punkt." },
    porte: { h: PORTE.de.titre,
      p: "Iris könnte bei Flexsis einziehen, mit einem Agenten, der jeden Morgen die Publikationen liest, und mit Apertus, angepasst an ihre Daten, auf ihren Servern oder bei einem Schweizer Hoster. Nichts davon existiert heute: Die Beraterin oder der Berater wird entscheiden, und die Daten von Flexsis würden unter ihrer Kontrolle bleiben, in der Schweiz, mit ihrer schriftlichen Zustimmung." },
  },
  questions: {
    title: "Ihre Fragen",
    items: [
      { q: "Warum sollten wir Ihnen zuhören?", bref: "Um vor Ort mit Ihrer Arbeitsweise zu vergleichen. Den Mehrwert bei Ihnen müssen wir noch zeigen.",
        a: "Weil wir Ihnen zeigen können, welche Arbeit die Beraterin oder der Berater mit diesen Informationen leisten könnte, und das dann mit der heutigen Arbeitsweise vergleichen. Den Mehrwert bei Ihnen haben wir noch nicht nachgewiesen. Zeigt der Pilotversuch nicht genug davon, haben wir einen klaren Grund aufzuhören." },
      { q: "Warum wäre ein öffentlicher Auftrag ein guter Grund für einen Anruf?", bref: "In Brasilien sah eine Studie diese Unternehmen mehr einstellen. Bei Ihnen misst es der Pilotversuch.",
        a: "Eine in Brasilien durchgeführte Studie (Ferraz, Finan und Szerman, NBER, 2015) hat beobachtet, dass Unternehmen, die einen öffentlichen Auftrag gewinnen, mehr Personal einstellen, schon im Quartal des Vertrags und darüber hinaus. Ob sich das bei Ihnen in Bestellungen niederschlägt, wissen wir noch nicht: Das wird der Pilotversuch messen." },
      { q: "Gibt es das schon?", bref: "Baustellendaten, ja. Proxsis organisiert den Montag Ihrer Beraterinnen und Berater.",
        a: "Dienste mit Baustellendaten gibt es: im Vereinigten Königreich für Personalvermittler, in der Schweiz für Baugesuche. Proxsis verkauft keine Daten: Es organisiert den Montag Ihrer Beraterinnen und Berater, ihre Entscheide und was darauf folgt." },
      { q: "Warum nicht einfach simap anschauen?", bref: "Das können Sie. Wir fügen die Liste, die Frage und die Nachverfolgung hinzu.",
        a: "Das können Sie. Wir bereiten eine passende Liste, eine belegte Frage und die Nachverfolgung Ihrer Entscheide vor. Der Test wird zeigen, ob das Zeit spart." },
      { q: "Zeigen Sie mir vor allem meine bisherigen Kunden?", bref: "Ein wenig, ja. Im Notizbuch können Sie sie verwerfen.",
        a: "Ein wenig, ja: Die Regel bevorzugt Unternehmen, die bereits aktiv sind. Im Notizbuch können Sie Ihre bekannten Kunden verwerfen. Der Pilotversuch misst, was Proxsis bei den Unternehmen bringt, die Sie selten anrufen." },
      { q: "Wir haben bereits eine Software, um unsere Kunden zu verfolgen.", bref: "Proxsis ersetzt sie nicht. Es behält nur Ihre Entscheide zur Montagsliste.",
        a: "Proxsis ersetzt sie nicht: Es behält nur Ihre Entscheide zur Montagsliste. Während des Pilotversuchs schauen wir, was in Ihr Werkzeug übernommen werden kann, damit nichts zweimal erfasst wird." },
      { q: "Wie viele Einsätze können Sie garantieren?", bref: "Heute keine. Der Pilotversuch misst, was sich ändert.",
        a: "Heute keine. Gemessen haben wir die öffentliche Aktivität. Der Pilotversuch zählt getrennt die nützlichen Gespräche, die Bestellungen und die zusätzlich verrechneten Tage." },
      { q: "Werden meine Beraterinnen und Berater es wirklich nutzen?", bref: "Das wissen wir noch nicht. Der erste Versuch wird es zeigen.",
        a: "Das wissen wir noch nicht. Der erste Versuch soll zeigen, ob sie ihre Anrufe schneller vorbereiten und ob sie von selbst darauf zurückkommen." },
      { q: "Was kostet das, und wie hört man auf?", bref: "Der Dienst und die Zeit Ihrer Teams. Obergrenze und Abbruch legen wir vorher fest.",
        a: "Die Kosten umfassen den Dienst und die Zeit Ihrer Teams. Vor dem Pilotversuch legen wir gemeinsam die Obergrenze, die Erfolgsschwelle, die verantwortliche Person und die Abbruchbedingungen fest." },
      { q: "Können Sie uns Kandidatinnen und Kandidaten vorschlagen?", bref: "Ja, mit Ihrem Pool, unter Vereinbarung. Hier sind die Temporärmitarbeitenden fiktiv.",
        a: "Ja, sobald Sie uns Ihren Pool anvertrauen, mit einer Vereinbarung. In dieser Demonstration sind die Temporärmitarbeitenden fiktiv. Die Vorschläge berücksichtigen Beruf, Arbeitsbewilligung, Verfügbarkeit und Distanz." },
      { q: "Setzen Sie künstliche Intelligenz ein?", bref: "Nicht für die Liste: klare Regeln, gemessen an vergangenen Montagen. Morgen vielleicht, wenn Flexsis es wünscht.",
        a: `Nicht für die Liste: Heute stammt sie aus klaren Regeln, gemessen an siebenundfünfzig vergangenen Montagen, und jeder Vorschlag zeigt seinen Grund. Morgen, wenn Flexsis es wünscht: ${APERTUS.de} Und die Entscheidung liegt immer bei Ihnen.` },
    ],
  },
  equipe: {
    title: "Wer wir sind",
    contact: "Kontakt",
  },
  technique: {
    title: "Für Ihre technischen Teams",
    sections: [
      { h: "Quellen und Lizenzen", p: [
        "simap.ch: Zuschläge öffentlicher Bauaufträge, über den offiziellen Zugang gelesen, gemäss den Nutzungsbedingungen (Fassung vom 30.09.2023); der publizierte Inhalt wird nicht verändert, er wird getrennt von unseren Kommentaren gezeigt, mit dem Pflichthinweis.",
        "Amtsblatt des Kantons Wallis: Baugesuche, von einer Person eingesehen; ein Zugangsgesuch ist vorbereitet. Kein Skript fragt das Portal ab.",
        "swisstopo: Gemeindegrenzen und Ortschaftenverzeichnis, offene Daten (© swisstopo).",
      ] },
      { h: "Fahrplan der Quellen", p: [
        "Was Proxsis heute liest, was es morgen lesen könnte, und der Stand jedes Zugangs: Seite «Quellen und Messungen» der Anwendung.",
      ] },
      { h: "Datenschutz", p: [
        "Proxsis zielt auf Unternehmen, nie auf Privatpersonen. Ein Filter entfernt Personendaten vor jeder Speicherung; ein Test prüft, dass nichts, was das Projekt veröffentlicht, solche enthält.",
        "Die Personen, Einsätze und Kandidierenden der Demonstration sind fiktiv und als solche gekennzeichnet.",
        "Ihre Eingaben im Rundgang bleiben in Ihrem Browser, auf Ihrem Gerät; sie werden nicht an unser Team gesendet.",
      ] },
      { h: "Funktionsweise", p: [
        "Jeden Montag eine Liste von Unternehmen pro Fachbereich und Region, geordnet nach einer einfachen Regel: Anzahl gewonnener öffentlicher Aufträge in 52 Wochen, dann der jüngste.",
        "Für jedes Unternehmen die publizierte Tatsache, die einen Grund zum Anruf gibt, was sie erwarten lässt (eine zu bestätigende Schätzung) und eine Frage für den Anruf.",
        "Jede Zahl verweist auf eine Messung, die man wiederholen kann, mit Methode und Grenzen beschrieben (Seite «Quellen und Messungen»).",
      ] },
      { h: "Tests", p: [
        "Bei jeder Änderung: keine Personendaten in dem, was veröffentlicht wird, Pflichthinweise vorhanden, Barrierefreiheit, keine Anfrage ausserhalb der Website, gleiche Anzeige in zwei Tagen, einem Monat und drei Monaten, und bytegenaue Wiederherstellung der Datendateien.",
      ] },
    ],
    measures: "Quellen und Messungen",
  },
  // the roadmap, German to review (à relire): Hiba does not read German
  feuille: {
    title: "Fahrplan",
    link: "Der Fahrplan",
    today: { h: "Heute", measures: "Quellen und Messungen", p: "Ein Online-Prototyp, auf Französisch und Deutsch, auf dem Telefon und am Computer. Die Montagsliste, gemessen an 57 vergangenen Montagen (siehe «Quellen und Messungen»). Zwei amtliche Quellen, und simap wird jeden Morgen gelesen. Die versandten Zugangsgesuche: SECO, Zefix, Job-Room, Gebäude- und Wohnungsregister. Bei Flexsis ist nichts installiert, und es werden keine Daten von Flexsis verwendet." },
    steps: [
      { h: "Schritt 1: ein Versuch mit zwei freiwilligen Beraterinnen oder Beratern in einer Agentur", p: "Sie erhalten die Liste jeden Montag und behalten, verschieben oder verwerfen jeden Eintrag. Gemessen werden die Anrufe, die Termine und die Einsätze, und ihre Meinung wird eingeholt. Danach wird entschieden: weitermachen, anpassen oder aufhören." },
      { h: "Schritt 2: die Vergangenheitsdaten von Flexsis, unter einer Vertraulichkeitsvereinbarung", p: "Gemessen wird, was die Liste wirklich bringt, und sie wird an jede Agentur und jeden Beruf angepasst. Die Daten bleiben unter der Kontrolle von Flexsis, in der Schweiz." },
      { h: "Schritt 3: mehr Quellen und mehr Agenturen", p: "Sobald die Bewilligungen vorliegen: das Amtsblatt und das Handelsregister jeden Morgen, und Zefix. Jede Quelle wird gemessen, bevor sie in die Liste aufgenommen wird. Danach zwei Agenturen, auf Französisch und auf Deutsch." },
      { h: "Schritt 4: Iris bei Flexsis, wenn Flexsis es wünscht", p: "Eine Assistentin für jede Beraterin und jeden Berater, und ein Agent, der jeden Morgen die Publikationen liest. Apertus, an die Daten von Flexsis angepasst, auf den eigenen Servern oder bei einem Schweizer Hoster. Die fünf Leitplanken gelten immer." },
      { h: "Schritt 5: alle Agenturen, zuerst im Wallis, dann in den anderen Regionen, jede in ihrer Sprache", p: "" },
    ],
    rule: { h: "Die Regel", p: "Der nächste Schritt erfolgt nur mit gemessenen Ergebnissen und mit der Zustimmung von Flexsis." },
  },
};

export const PAGES_COPY: Record<"fr" | "de", PagesCopy> = { fr: frenchDeep(fr), de };
