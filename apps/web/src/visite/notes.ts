// Presenter mode of the visit (brief « à distance », § 4): for a video call, the same scenes on the shared screen and,
// in a separate window, what to say and do at each step. `say` is said as written; the narration of the screen is
// repeated first, so that the presenter never reads the shared screen. FR and DE (German: to be reviewed).
// Suite 8, § 6: short sentences, everyday words, « vous »; why Iris is called Iris, three reasons (CLAIMS
// EXT-IRIS-MESSAGERE); the mandatory explanation of the first test and the answer to « pourquoi vous écouter ? » (brief
// of 06.10.2026, § 7), word for word.
import { frenchDeep } from "@/lib/typo";
import type { StepId } from "./state";

export interface VisitNote {
  say: string;
  gesture: string;
  proof: string;
  fallback: string;
}

const fr: Record<StepId, VisitNote> = {
  carte: {
    say: "Lundi, 8 h 03. Quelle entreprise mérite votre premier appel ? Voici le Valais. Saxon est déjà préparé. Touchez une commune que vous connaissez : vous voyez les entreprises qui y ont leur siège et, à part, les marchés publiés sur place.",
    gesture: "Laisser le directeur choisir une commune (ou proposer la sienne), puis ouvrir une entreprise de la liste. Dans le coin, Iris pose son point sur l'entreprise préparée : « Repéré ».",
    proof: "Seulement les entreprises dont le dossier passe tous nos contrôles ; le siège et le lieu du marché sont distingués (territoire.json).",
    fallback: "Rester sur Saxon et ouvrir Joseph Carron SA. Si l'on demande pourquoi « Iris » : dans les légendes grecques, Iris est la messagère des dieux (CLAIMS EXT-IRIS-MESSAGERE) ; Iris met les points sur les i ; et « Iris » se dit pareil en français, en allemand et en anglais.",
  },
  dossier: {
    say: "Une entreprise réelle. Une raison publiée. Une question à poser. Sur le papier, le fait publié, avec sa date et sa source. À côté, ce qu'il laisse envisager, ce qui reste à vérifier, et une question pour commencer l'appel.",
    gesture: "« Continuer » fait apparaître la lecture ; « Voir la source » ouvre la publication sur simap.ch.",
    proof: "Une publication datée et sourcée, parue avant le lundi de la liste ; l'estimation est marquée « à confirmer ».",
    fallback: "Lire à voix haute le titre publié et sa date.",
  },
  carnet: {
    say: "Vous décidez. Le carnet garde votre choix : à appeler, à vérifier, revoir plus tard, ou écarter, avec un motif. Rien ne part tout seul. Confiez la piste au consultant : elle arrive en tête de ses trois premiers appels. Comme dit Iris : « Moi, je prépare. Vous, vous décidez. »",
    gesture: "Choisir une décision, puis « Confier à Consultant bâtiment » ; « Continuer » montre la vue du consultant.",
    proof: "Aucun champ libre, donc aucun nom de personne ; « Consultant bâtiment » est un rôle fictif de démonstration.",
    fallback: "Garder l'exemple préparé, « À appeler », et montrer la vue du consultant.",
  },
  suivant: {
    say: "Le lundi suivant, vous ne recommencez pas à zéro. L'entreprise écartée ne revient pas. Le rappel tombe à sa date. La piste gardée revient avec sa prochaine action, et la suivante de la liste prend la place libre. Le premier lundi, Proxsis apporte une information. Le suivant, votre agence retrouve ce qu'elle en a fait.",
    gesture: "« Continuer » fait apparaître le lundi suivant ; à gauche, on peut changer une décision et voir la liste suivre.",
    proof: "La même règle et le même calcul que la liste gelée (lundi_suivant.json) ; aucune publication ni aucun résultat d'appel inventé.",
    fallback: "Dire les trois règles : l'écartée ne revient pas, le rappel tombe à sa date, la place libre est reprise.",
  },
  date: {
    say: "Et la liste, vaut-elle quelque chose ? Choisissez une date. Voici les dix entreprises que la règle simple aurait proposées ce lundi-là, avec seulement ce qui était publié avant. Puis ce qui s'est passé dans les huit semaines. Un nouveau marché n'est pas une commande. Avant cette mesure, nous avons fait un premier examen, plus large : toute la Suisse romande, vingt entreprises par semaine. Sur ce premier examen des marchés publics, notre sélection n'a pas fait mieux qu'une règle simple. Nous gardons donc cette règle comme référence. Ce que nous vous proposons de tester, c'est l'utilité d'une information vérifiable dans le travail de vos consultants : aide-t-elle à préparer les bons appels, et à quel coût ? Le pilote doit nous permettre de le mesurer.",
    gesture: "Exemple préparé : lundi 2 mars 2026 ; s'il propose une date, la saisir. « Continuer » montre les résultats, puis la moyenne.",
    proof: "CLAIMS PRES-DATE-1 et REEL-SPEC-BAT : bâtiment en Valais, dix entreprises par lundi, 57 lundis, moyenne 66,8 %, dix au hasard 20,7 % ; un mauvais lundi s'affiche tel quel. Le premier examen, c'est REEL-T0 : Suisse romande, 1 892 adjudications, 731 entreprises, 44 semaines, vingt entreprises par semaine ; règle simple 55,0 %, sélection plus compliquée 52,7 %.",
    fallback: "Lire la ligne PRES-DATE-1 du registre des chiffres. S'il demande « Alors pourquoi vous écouter ? » : « Parce que nous pouvons vous montrer le travail que le consultant pourrait faire avec ces informations, puis le comparer à sa pratique actuelle. Nous n'avons pas encore démontré le gain chez vous. Si le pilote n'en montre pas suffisamment, nous aurons une raison claire de nous arrêter. »",
  },
  seuil: {
    say: "Combien de journées supplémentaires facturées faut-il pour couvrir le coût ? Avec ces valeurs d'exemple, voici le nombre. Mettez les vôtres. Avec deux fois moins de journées, le résultat peut devenir une perte : elle reste affichée.",
    gesture: "Laisser saisir la marge, le coût du service et le temps des équipes ; puis « Deux fois moins ».",
    proof: "Un seul calcul, le même que la page « Retour sur investissement » ; la marge, pas le chiffre d'affaires ; le temps gagné compté à part.",
    fallback: "Dire le calcul : le coût divisé par la marge d'une journée.",
  },
  pilote: {
    say: "Deux agences, six semaines : votre façon de faire comparée à Proxsis. « Nous continuerons si… » : choisissez l'indicateur et le seuil. C'est une proposition à écrire ensemble, pas un contrat.",
    gesture: "Choisir un indicateur, proposer un seuil.",
    proof: "Le cadre du pilote : docs/affaires/pilote.md (tirage au sort dans chaque agence, indicateurs fixés avant le départ).",
    fallback: "Garder l'exemple préparé : les journées du seuil.",
  },
  conclusion: {
    say: "Votre premier lundi : voici vos choix, noir sur blanc. Ce que vous n'avez pas modifié reste un exemple préparé. Vous pouvez télécharger votre synthèse, ou préparer un e-mail pour l'équipe.",
    gesture: "Montrer « Télécharger ma synthèse » et « Préparer un e-mail » ; puis les liens « Vos questions » et « Pour vos équipes techniques ».",
    proof: "Les saisies ne quittent pas l'appareil ; l'e-mail ne porte aucun montant sans « Inclure mes hypothèses ».",
    fallback: "Lire les trois prochaines étapes.",
  },
};

const de: Record<StepId, VisitNote> = {
  carte: {
    say: "Montag, 8.03 Uhr. Welches Unternehmen verdient Ihren ersten Anruf? Hier das Wallis. Saxon ist schon vorbereitet. Tippen Sie auf eine Gemeinde, die Sie kennen: Sie sehen die Unternehmen mit Sitz dort und, getrennt davon, die dort publizierten Aufträge.",
    gesture: "Den Direktor eine Gemeinde wählen lassen (oder seine eigene vorschlagen), dann ein Unternehmen der Liste öffnen. In der Ecke setzt Iris ihren Punkt auf das vorbereitete Unternehmen: «Erkannt».",
    proof: "Nur Unternehmen, deren Dossier alle unsere Prüfungen besteht; Sitz und Ort des Auftrags sind getrennt (territoire.json).",
    fallback: "Bei Saxon bleiben und Joseph Carron SA öffnen. Fragt jemand, warum «Iris»: In den griechischen Sagen ist Iris die Botin der Götter (CLAIMS EXT-IRIS-MESSAGERE); «Iris bringt es auf den Punkt» (zu prüfen); und «Iris» klingt auf Französisch, Deutsch und Englisch gleich.",
  },
  dossier: {
    say: "Ein echtes Unternehmen. Ein publizierter Grund. Eine Frage, die Sie stellen können. Auf dem Papier die publizierte Tatsache, mit Datum und Quelle. Daneben, was sie erwarten lässt, was noch zu prüfen ist, und eine Frage für den Anfang des Anrufs.",
    gesture: "«Weiter» zeigt die Lesart; «Quelle ansehen» öffnet die Publikation auf simap.ch.",
    proof: "Eine datierte, belegte Publikation, erschienen vor dem Montag der Liste; die Schätzung ist als «zu bestätigen» markiert.",
    fallback: "Den publizierten Titel und sein Datum vorlesen.",
  },
  carnet: {
    say: "Sie entscheiden. Das Notizbuch behält Ihre Wahl: anrufen, prüfen, später wieder ansehen oder verwerfen, mit einem Grund. Nichts geht von selbst hinaus. Übergeben Sie die Spur der Beratung: Sie steht an der Spitze ihrer drei ersten Anrufe. Wie Iris sagt: «Ich bereite vor. Sie entscheiden.»",
    gesture: "Einen Entscheid wählen, dann «Übergeben an Personalberatung Bau»; «Weiter» zeigt die Ansicht der Beratung.",
    proof: "Kein freies Feld, also kein Personenname; «Personalberatung Bau» ist eine fiktive Rolle.",
    fallback: "Das vorbereitete Beispiel «Anrufen» behalten und die Ansicht der Beratung zeigen.",
  },
  suivant: {
    say: "Am nächsten Montag fangen Sie nicht bei null an. Das verworfene Unternehmen kommt nicht zurück. Die Wiedervorlage fällt auf ihr Datum. Die behaltene Spur kommt mit ihrem nächsten Schritt zurück, und das nächste der Liste nimmt den freien Platz. Am ersten Montag bringt Proxsis eine Information. Am nächsten findet Ihre Filiale wieder, was sie daraus gemacht hat.",
    gesture: "«Weiter» zeigt den nächsten Montag; links kann man einen Entscheid ändern und sieht die Liste folgen.",
    proof: "Dieselbe Regel und dieselbe Berechnung wie die eingefrorene Liste (lundi_suivant.json); keine erfundene Publikation, kein erfundenes Ergebnis.",
    fallback: "Die drei Regeln sagen: Das verworfene kommt nicht zurück, die Wiedervorlage fällt auf ihr Datum, der freie Platz wird besetzt.",
  },
  date: {
    say: "Und die Liste, ist sie etwas wert? Wählen Sie ein Datum. Das sind die zehn Unternehmen, die die einfache Regel an diesem Montag vorgeschlagen hätte, nur mit dem, was vorher publiziert war. Dann, was in den acht Wochen danach geschah. Ein neuer Auftrag ist noch keine Bestellung. Vor dieser Messung haben wir eine erste, breitere Prüfung gemacht: die ganze Westschweiz, zwanzig Unternehmen pro Woche. Bei dieser ersten Prüfung der öffentlichen Aufträge hat unsere Auswahl nicht besser abgeschnitten als eine einfache Regel. Deshalb behalten wir diese Regel als Referenz. Was wir Ihnen zum Testen vorschlagen, ist der Nutzen einer überprüfbaren Information in der Arbeit Ihrer Beraterinnen und Berater: Hilft sie, die richtigen Anrufe vorzubereiten, und zu welchen Kosten? Der Pilotversuch soll es uns ermöglichen, das zu messen.",
    gesture: "Vorbereitetes Beispiel: Montag, 2. März 2026; nennt er ein Datum, eingeben. «Weiter» zeigt die Ergebnisse, dann den Schnitt.",
    proof: "CLAIMS PRES-DATE-1 und REEL-SPEC-BAT: Bau im Wallis, zehn Unternehmen pro Montag, 57 Montage, Schnitt 66,8 %, zehn zufällige 20,7 %; ein schlechter Montag wird so gezeigt. Die erste Prüfung ist REEL-T0: Westschweiz, 1 892 Zuschläge, 731 Unternehmen, 44 Wochen, zwanzig Unternehmen pro Woche; einfache Regel 55,0 %, kompliziertere Auswahl 52,7 %.",
    fallback: "Die Zeile PRES-DATE-1 des Zahlenregisters vorlesen. Fragt er «Warum sollten wir Ihnen dann zuhören?»: «Weil wir Ihnen zeigen können, welche Arbeit die Beraterin oder der Berater mit diesen Informationen leisten könnte, und das dann mit der heutigen Arbeitsweise vergleichen. Den Mehrwert bei Ihnen haben wir noch nicht nachgewiesen. Zeigt der Pilotversuch nicht genug davon, haben wir einen klaren Grund aufzuhören.»",
  },
  seuil: {
    say: "Wie viele zusätzlich verrechnete Tage braucht es, um die Kosten zu decken? Mit diesen Beispielwerten ist das die Zahl. Setzen Sie Ihre ein. Mit halb so vielen Tagen kann das Ergebnis ein Verlust werden: Er bleibt angezeigt.",
    gesture: "Marge, Kosten des Dienstes und Zeit der Teams eingeben lassen; dann «Halb so viel».",
    proof: "Eine einzige Berechnung, dieselbe wie auf der Seite «Rendite»; die Marge, nicht der Umsatz; gewonnene Zeit separat.",
    fallback: "Die Rechnung sagen: die Kosten geteilt durch die Marge eines Tages.",
  },
  pilote: {
    say: "Zwei Filialen, sechs Wochen: Ihre heutige Arbeitsweise im Vergleich mit Proxsis. «Wir machen weiter, wenn…»: Wählen Sie den Indikator und die Schwelle. Ein Vorschlag, den wir gemeinsam ausarbeiten, kein Vertrag.",
    gesture: "Einen Indikator wählen, eine Schwelle vorschlagen.",
    proof: "Rahmen des Pilotversuchs: docs/affaires/pilote.md (Auslosung in jeder Filiale, Indikatoren vor dem Start festgelegt).",
    fallback: "Das vorbereitete Beispiel behalten: die Tage der Schwelle.",
  },
  conclusion: {
    say: "Ihr erster Montag: Hier ist Ihre Auswahl, schwarz auf weiss. Was Sie nicht geändert haben, bleibt ein vorbereitetes Beispiel. Sie können Ihre Zusammenfassung herunterladen oder eine E-Mail an das Team vorbereiten.",
    gesture: "«Meine Zusammenfassung herunterladen» und «E-Mail vorbereiten» zeigen; dann die Links «Ihre Fragen» und «Für Ihre technischen Teams».",
    proof: "Die Eingaben verlassen das Gerät nicht; die E-Mail enthält ohne «Meine Annahmen einschliessen» keine Beträge.",
    fallback: "Die drei nächsten Schritte vorlesen.",
  },
};

export const VISIT_NOTES: Record<"fr" | "de", Record<StepId, VisitNote>> = { fr: frenchDeep(fr), de };
export const NOTE_ROWS = {
  fr: { say: "À dire", gesture: "Geste", proof: "Preuve", fallback: "Repli", next: "Ensuite", title: "Mode présentateur" },
  de: { say: "Zu sagen", gesture: "Geste", proof: "Beleg", fallback: "Ausweg", next: "Danach", title: "Präsentationsmodus" },
} as const;
