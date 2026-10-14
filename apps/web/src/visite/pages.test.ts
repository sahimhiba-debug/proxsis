import { describe, expect, it } from "vitest";
import claims from "@/data/demo/claims.json";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { allStrings } from "@/test/strings";
import { APERTUS, PORTE } from "./copy";
import { PAGES_COPY } from "./pages";

const shape = (o: unknown): unknown => Array.isArray(o) ? o.map(shape) : o && typeof o === "object"
  ? Object.fromEntries(Object.keys(o).sort().map((k) => [k, shape((o as Record<string, unknown>)[k])])) : typeof o;
const plain = (x: string) => x.replace(/ /g, " ");

describe("pages de la conclusion : vos questions, qui sommes-nous, pour vos équipes techniques", () => {
  it("mêmes clés et mêmes listes en français et en allemand, aucun terme à éviter", () => {
    expect(shape(PAGES_COPY.de)).toEqual(shape(PAGES_COPY.fr));
    for (const lang of ["fr", "de"] as const) {
      expect(allStrings(PAGES_COPY[lang]).flatMap((s) => forbiddenTerms(s, lang))).toEqual([]);
    }
  });

  it("les questions et réponses des briefs, mot pour mot (§ 11 ; brief du 07.10.2026, § 3.6)", () => {
    const qa = Object.fromEntries(PAGES_COPY.fr.questions.items.map((x) => [plain(x.q), plain(x.a)]));
    expect(Object.keys(qa)).toEqual([
      "Pourquoi vous écouter ?", "Pourquoi un marché public serait-il une bonne raison d'appeler ?", "Est-ce que cela existe déjà ?",
      "Pourquoi ne pas simplement consulter simap ?", "Vous allez surtout me ressortir mes clients habituels ?",
      "Nous avons déjà un logiciel pour suivre nos clients.", "Combien de missions pouvez-vous garantir ?",
      "Mes consultants vont-ils vraiment l'utiliser ?", "Combien cela coûte, et comment arrête-t-on ?",
      "Pouvez-vous nous proposer des candidats ?", "Utilisez-vous l'intelligence artificielle ?",
    ]);
    // brief of 07.10.2026, § 3.6, word for word
    expect(qa["Pouvez-vous nous proposer des candidats ?"]).toBe(
      "Oui, dès que vous nous confiez votre vivier, sous accord. Dans cette démonstration, les intérimaires sont fictifs. Les propositions tiennent compte du métier, du permis, de la disponibilité et de la distance.");
    // B5: the duration on the first screen is the measured one, in both languages (CLAIMS PRES-DUREE-1)
    const minutes = (claims as Record<string, Record<string, string>>)["PRES-DUREE-1"].valeur.match(/^(\d+) minutes/)?.[1];
    expect(minutes).toBeDefined();
    expect(PAGES_COPY.fr.accueil.start).toBe(`Voir Proxsis en ${minutes} minutes`);
    expect(PAGES_COPY.de.accueil.start).toBe(`Proxsis in ${minutes} Minuten ansehen`);
    // suite 9, Q02: the direct question is back, « Utilisez-vous l'intelligence artificielle ? »; the honest answer (today,
    // clear rules measured on past Mondays), then the door (suite 9, § 8) with the passage on Apertus word for word; never
    // the acronym, no other provider; « intelligence artificielle » in the question and in the passage only
    const further = "Utilisez-vous l'intelligence artificielle ?";
    const ai = qa[further];
    expect(ai).toBeDefined();
    expect(ai.startsWith("Pas pour la liste : aujourd'hui, elle vient de règles claires, mesurées sur cinquante-sept lundis passés")).toBe(true);
    expect(ai).toContain("Demain, si Flexsis le souhaite");
    expect(ai).toContain(plain(APERTUS.fr));
    expect(ai).not.toMatch(/Pas dans cette démonstration|OpenAI|Anthropic|\bIA\b/);
    expect(`${further} ${ai}`.match(/intelligence artificielle/g)).toHaveLength(2);
    expect(Object.keys(qa)).not.toContain("Proxsis peut-il aller plus loin ?");
    expect(qa["Pourquoi ne pas simplement consulter simap ?"]).toBe(
      "Vous pouvez. Nous préparons une liste adaptée, une question sourcée et le suivi de vos décisions. Le test dira si cela fait gagner du temps.");
    expect(qa["Combien de missions pouvez-vous garantir ?"]).toBe(
      "Aucune aujourd'hui. Nous avons mesuré l'activité publique. Le pilote comptera séparément les conversations utiles, les commandes et les journées supplémentaires facturées.");
    // the two answers prepared by the agent « preuves » (07.10.2026), word for word; « signal » is not on screen
    expect(qa["Pourquoi un marché public serait-il une bonne raison d'appeler ?"]).toBe(
      "Une étude menée au Brésil (Ferraz, Finan et Szerman, NBER, 2015) a observé que les entreprises qui remportent un marché public embauchent davantage, dès le trimestre du contrat et au-delà. Nous ne savons pas encore si cela se traduit en commandes chez vous : c'est ce que le pilote mesurera.");
    expect(qa["Est-ce que cela existe déjà ?"]).toBe(
      "Des services de données de chantier existent, au Royaume-Uni pour les recruteurs, et en Suisse pour les demandes de permis. Proxsis ne vend pas des données : il organise le lundi de vos consultants, leurs décisions et leur suite.");
    expect(qa["Pourquoi vous écouter ?"]).toBe(
      "Parce que nous pouvons vous montrer le travail que le consultant pourrait faire avec ces informations, puis le comparer à sa pratique actuelle. Nous n'avons pas encore démontré le gain chez vous. Si le pilote n'en montre pas suffisamment, nous aurons une raison claire de nous arrêter.");
  });
});

// Suite 9, Q05: the German motto « Iris bringt es auf den Punkt. » (to be reviewed), never « den Punkt aufs i »
describe("la devise d'Iris en allemand (Q05)", () => {
  it("de : Iris bringt es auf den Punkt.", () => {
    expect(PAGES_COPY.de.unePage.iris.motto).toBe("Iris bringt es auf den Punkt.");
    expect(JSON.stringify(PAGES_COPY.de)).not.toContain("Punkt aufs i");
  });
});

// Suite 9, § 10: on a phone, « Vos questions » gives each answer in short sentences first; the whole answer of the brief,
// word for word, stays in the page under « En savoir plus » (« Mehr erfahren »). The short answer adds no figure.
describe("vos questions au téléphone : la réponse courte, puis « En savoir plus »", () => {
  for (const lang of ["fr", "de"] as const) {
    it(`${lang} : une réponse courte par question, en phrases courtes, sans chiffre nouveau`, () => {
      expect(PAGES_COPY[lang].plus).toBe(lang === "fr" ? "En savoir plus" : "Mehr erfahren");
      for (const x of PAGES_COPY[lang].questions.items) {
        const bref = plain(x.bref);
        const words = (y: string) => y.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length;
        expect(words(bref), bref).toBeLessThanOrEqual(22);
        for (const sentence of bref.split(/(?<=[.?!])\s+/)) expect(words(sentence), sentence).toBeLessThanOrEqual(14);
        expect(words(bref), bref).toBeLessThan(words(plain(x.a)));
        for (const n of bref.match(/\d+/g) ?? []) expect(plain(x.a), `${n} dans « ${bref} »`).toContain(n);
        expect(bref).not.toMatch(lang === "fr" ? /\bIA\b/ : /\bKI\b/);
      }
    });
  }
});

// Suite 9, § 8: the door on the A4 page, a short block: two sentences at most (in the future or the conditional, with the
// guardrails of the data and of the decision), then the three steps on one line, word for word
describe("la porte sur la page A4", () => {
  for (const lang of ["fr", "de"] as const) {
    it(`${lang} : deux phrases au plus, au conditionnel, avec ses garde-fous`, () => {
      const t = PAGES_COPY[lang].unePage.porte;
      expect(plain(t.h)).toBe(PORTE[lang].titre);
      const text = plain(t.p);
      expect(text.split(/(?<=[.?!])\s+/).length).toBeLessThanOrEqual(2);
      expect(text).toMatch(lang === "fr" ? /pourrait/ : /könnte/);
      expect(text).toMatch(lang === "fr" ? /Rien de cela n'existe aujourd'hui/ : /Nichts davon existiert heute/);
      expect(text).toContain(lang === "fr" ? "sous son contrôle, en Suisse, avec son accord écrit" : "würden unter ihrer Kontrolle bleiben, in der Schweiz, mit ihrer schriftlichen Zustimmung");
      expect(text).toMatch(lang === "fr" ? /le consultant décidera/ : /entscheiden/);
      expect(text).toContain("Apertus");
      expect(text).not.toMatch(lang === "fr" ? /\bIA\b/ : /\bKI\b/);
      expect(forbiddenTerms(text, lang)).toEqual([]);
    });
  }
});


// Suite 10 (13.10.2026): on the A4 page, where the Monday is spoken of, Hiba's sentence word for word; and one line with
// the numbers of the sources and the rule (the line itself is built from the catalogue: guide.ts, sourcesAnswer)
describe("la page A4 : chaque matin, et la carte des sources", () => {
  it("la phrase du lundi ouvre « Ce que fait Proxsis », FR et DE (DE à relire)", () => {
    expect(PAGES_COPY.fr.unePage.what.p[0]).toBe("Chaque matin, Iris lit les marchés publics attribués. Le lundi, elle pose les dix points.");
    expect(PAGES_COPY.de.unePage.what.p[0]).toBe("Jeden Morgen liest Iris die vergebenen öffentlichen Aufträge. Am Montag setzt sie die zehn Punkte.");
  });
});
