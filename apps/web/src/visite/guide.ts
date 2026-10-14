// Le guide de la visite, Iris (suite 3 du 07.10.2026, § 1 et § 4 : « l'assistante de Proxsis », jamais « IA » ; le bouton
// « Une question ? Demandez à Iris. ») ; d'abord (message de Hiba « Film et visite : nouvelle mascotte », 07.10.2026, § 3) : la mascotte, petite
// dans un coin, une phrase par temps, et « Une question ? » avec six réponses préparées par l'équipe, en français et en
// allemand, tirées des textes de la visite et de CLAIMS.md. Pas de saisie libre, aucune requête réseau, rien derrière
// qui rédige : les réponses sont ces textes, les mêmes pour tout le monde. Les chiffres viennent des données
// (lundis.json, CLAIMS PRES-DATE-1 et REEL-SPEC-BAT), jamais du texte.
import { RULE, sourcesLine } from "@/lib/chaqueMatin";
import { frenchDeep, frenchSpaces } from "@/lib/typo";
import type { MondaysData } from "@/presentation/mondayData";
import { VISIT_COPY } from "./copy";

export const QUESTIONS = ["sources", "appel", "saisies", "pourquoi", "marche", "rapporte"] as const;
export type QuestionGuide = (typeof QUESTIONS)[number];

interface GuideCopy {
  label: string;
  phrases: Record<1 | 2 | 3 | 4 | 5 | 6, string>; // une phrase par temps (6 : la conclusion)
  ask: string;
  prepared: string;
  close: string;
  others: string;
  hide: string;
  show: string;
  still: string; // l'image fixe, quand la 3D ne s'affiche pas
  questions: Record<QuestionGuide, { q: string; a: string }>;
  spotted: string; // l'étiquette de la visée
  recall: string;
}

const fr: GuideCopy = {
  label: "Iris, l'assistante de Proxsis",
  // her sentences (suite 8, § 6), word for word: « Je suis Iris, l'assistante de Proxsis. », « Moi, je prépare. Vous,
  // vous décidez. » and her motto « Iris met les points sur les i. »
  phrases: {
    1: "Je suis Iris, l'assistante de Proxsis. Moi, je prépare. Vous, vous décidez.",
    2: "Le lundi suivant, je retrouve vos choix : vous ne repartez pas de zéro.",
    3: "Choisissez un lundi passé : je ne regarde que ce qui était publié avant.",
    4: "Mettez vos chiffres. Si c'est une perte, je vous la montre aussi.",
    5: "Le critère de réussite, c'est vous qui le fixez.",
    6: "Iris met les points sur les i. Voici vos choix ; ils restent sur cet appareil.",
  },
  ask: "Une question ? Demandez à Iris.",
  prepared: "Réponses préparées par l'équipe",
  close: "Fermer",
  others: "Autres questions",
  hide: "Masquer Iris",
  show: "Afficher Iris",
  still: "Image fixe d'Iris",
  questions: {
    // the gesture of silence (suite 8, § 3): her eyes turn worried on this answer, and she says it
    sources: { q: "D'où viennent les informations ?",
      a: "Je lis deux sources publiques : les marchés publics attribués, publiés sur simap.ch, et les demandes d'autorisation de construire du Bulletin officiel du Valais, relevées à la main pendant le prototype. La carte des communes vient de swisstopo. Chaque information porte sa date et sa source. Chaque lundi, je vous dis jusqu'à quelle date chaque source est à jour." },
    appel: { q: "Proxsis appelle-t-il à ma place ?",
      a: "Non. Je prépare la liste du lundi, le dossier et une question pour commencer l'appel. Le consultant décide s'il appelle : rien ne part tout seul." },
    saisies: { q: "Que deviennent mes saisies ?", a: "{privacy}" },
    pourquoi: { q: "Pourquoi cette entreprise ?",
      a: "C'est la règle simple : pendant les 52 semaines avant ce lundi, elle a remporté le plus de marchés publics dans sa spécialité et sa région, d'après ce qui était publié avant. Le dossier vous montre la publication qui donne la raison d'appeler." },
    marche: { q: "Est-ce que ça marche vraiment ?",
      a: "Avant de vous la proposer, nous avons mis la liste à l'épreuve du passé : {n} lundis, rejoués avec seulement ce qui était publié ce jour-là. Dans le bâtiment en Valais, {rule} des dix entreprises proposées ont remporté un nouveau marché public dans les 8 semaines qui ont suivi. Dix entreprises prises au hasard : {random}. Mais un marché n'est pas une commande : le pilote mesurera ce qui compte pour votre agence." },
    rapporte: { q: "Combien ça rapporte ?",
      a: "Nous ne le savons pas encore : nous avons mesuré l'activité publique, pas vos commandes. Le temps « Un seuil » vous montre combien de journées facturées en plus couvrent le coût. Le pilote les comptera." },
  },
  spotted: "Repéré",
  recall: "Rappel du jour",
};

// à faire relire par une personne germanophone, comme tout l'allemand de la visite
const de: GuideCopy = {
  label: "Iris, die Assistentin von Proxsis",
  phrases: {
    1: "Ich bin Iris, die Assistentin von Proxsis. Ich bereite vor. Sie entscheiden.",
    2: "Am nächsten Montag finde ich Ihre Entscheide wieder: Sie fangen nicht bei null an.",
    3: "Wählen Sie einen vergangenen Montag: Ich schaue nur auf das, was vorher publiziert war.",
    4: "Setzen Sie Ihre Zahlen ein. Gibt es einen Verlust, zeige ich ihn auch.",
    5: "Das Erfolgskriterium legen Sie fest.",
    6: "Iris bringt es auf den Punkt. Hier sind Ihre Entscheide; sie bleiben auf diesem Gerät.",
  },
  ask: "Eine Frage? Fragen Sie Iris.",
  prepared: "Antworten vom Team vorbereitet",
  close: "Schliessen",
  others: "Weitere Fragen",
  hide: "Iris ausblenden",
  show: "Iris einblenden",
  still: "Standbild von Iris",
  questions: {
    sources: { q: "Woher kommen die Informationen?",
      a: "Ich lese zwei öffentliche Quellen: die vergebenen öffentlichen Aufträge auf simap.ch und die Baugesuche im Amtsblatt des Kantons Wallis, die während des Prototyps von Hand erfasst werden. Die Gemeindekarte stammt von swisstopo. Jede Information trägt ihr Datum und ihre Quelle. Jeden Montag sage ich Ihnen, bis zu welchem Datum jede Quelle aktuell ist." },
    appel: { q: "Ruft Proxsis an meiner Stelle an?",
      a: "Nein. Ich bereite die Montagsliste, das Dossier und eine Frage für den Anfang des Anrufs vor. Die Beraterin oder der Berater entscheidet, ob angerufen wird: Nichts geht von selbst hinaus." },
    saisies: { q: "Was geschieht mit meinen Eingaben?", a: "{privacy}" },
    pourquoi: { q: "Warum dieses Unternehmen?",
      a: "Das ist die einfache Regel: In den 52 Wochen vor diesem Montag hat es in seinem Fachbereich und seiner Region die meisten öffentlichen Aufträge gewonnen, nach dem, was vorher publiziert war. Das Dossier zeigt Ihnen die Publikation, die den Grund für den Anruf liefert." },
    marche: { q: "Funktioniert das wirklich?",
      a: "Bevor wir sie Ihnen vorschlagen, haben wir die Liste an der Vergangenheit geprüft: {n} Montage, nachgespielt nur mit dem, was an jenem Tag publiziert war. Im Wallis gewannen {rule} der zehn vorgeschlagenen Bauunternehmen in den 8 Wochen danach einen neuen öffentlichen Auftrag. Zehn zufällig gewählte Unternehmen: {random}. Aber ein Auftrag ist noch keine Bestellung: Der Pilotversuch misst, was für Ihre Filiale zählt." },
    rapporte: { q: "Wie viel bringt das?",
      a: "Das wissen wir noch nicht: Gemessen haben wir die öffentliche Aktivität, nicht Ihre Bestellungen. Der Schritt «Eine Schwelle» zeigt Ihnen, wie viele zusätzlich verrechnete Tage die Kosten decken. Der Pilotversuch zählt sie." },
  },
  spotted: "Erkannt",
  recall: "Rückruf heute",
};

export const GUIDE_COPY: Record<"fr" | "de", GuideCopy> = { fr: frenchDeep(fr), de };

/** La réponse affichée : les chiffres de la mesure et le texte de confidentialité de la visite, jamais écrits ici. */
export function reponse(q: QuestionGuide, lang: "fr" | "de", data: MondaysData): string {
  const v = VISIT_COPY[lang].privacy;
  return GUIDE_COPY[lang].questions[q].a
    .replace("{privacy}", `${v.sent} ${v.kept}`)
    .replace("{n}", String(data.mesure.semaines))
    .replace("{rule}", data.mesure.affiche.regle[lang])
    .replace("{random}", data.mesure.affiche.hasard[lang]);
}

/** Suite 10, § 3: « Et les autres sources ? » — one line under Iris's answer on the sources, the real numbers of the
 *  catalogue (src/data/sources/carte.json, CLAIMS SOURCES-1) and the rule; the same line as on the A4 page. */
export function sourcesAnswer(lang: "fr" | "de"): string {
  return frenchSpaces(`${sourcesLine(lang)} ${RULE[lang]}`, lang);
}
