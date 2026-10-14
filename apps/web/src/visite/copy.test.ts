import { describe, expect, it } from "vitest";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { allStrings } from "@/test/strings";
import { CARNET_COPY } from "@/lib/carnet";
import { APERTUS, PORTE, VISIT_COPY } from "./copy";
import { GUIDE_COPY } from "./guide";
import { VISIT_NOTES } from "./notes";
import { PAGES_COPY } from "./pages";
import { VISIT_STEPS } from "./state";

/** The words, with the no-break spaces of French typography made ordinary. */
const plain = (x: string) => x.replace(/\u00a0/g, " ");

const shape = (o: unknown): unknown => Array.isArray(o) ? o.map(shape) : o && typeof o === "object"
  ? Object.fromEntries(Object.keys(o).sort().map((k) => [k, shape((o as Record<string, unknown>)[k])])) : typeof o;
const lines = (text: string, width = 45) => text.split(/\s+/).reduce<string[]>((acc, w) => {
  const last = acc.at(-1);
  if (last !== undefined && last.length + 1 + w.length <= width) acc[acc.length - 1] = `${last} ${w}`;
  else acc.push(w);
  return acc;
}, []);

describe("visite : textes FR et DE", () => {
  it("mêmes clés dans les deux langues", () => {
    expect(shape(VISIT_COPY.de)).toEqual(shape(VISIT_COPY.fr));
    expect(shape(CARNET_COPY.de)).toEqual(shape(CARNET_COPY.fr));
  });

  it("le mot fort de chaque narration en est un extrait exact (le texte lu ne change pas)", () => {
    for (const lang of ["fr", "de"] as const) {
      for (const step of VISIT_STEPS) {
        const strong = VISIT_COPY[lang].strong[step.id];
        expect(strong, `${lang} ${step.id}`).toBeTruthy();
        expect(VISIT_COPY[lang].narration[step.id], `${lang} ${step.id}`).toContain(strong);
      }
    }
  });

  it("une narration par étape, trois lignes au plus", () => {
    for (const lang of ["fr", "de"] as const) {
      for (const step of VISIT_STEPS) {
        const n = VISIT_COPY[lang].narration[step.id];
        expect(n, `${lang} ${step.id}`).toBeTruthy();
        expect(lines(n).length, `${lang} « ${n} »`).toBeLessThanOrEqual(3);
      }
    }
  });

  it("aucun terme à éviter (radar, alerte, signal, niveau, jargon)", () => {
    for (const lang of ["fr", "de"] as const) {
      const hits = [...allStrings(VISIT_COPY[lang]), ...allStrings(CARNET_COPY[lang])].flatMap((s) => forbiddenTerms(s, lang));
      expect(hits).toEqual([]);
    }
  });

  it("les phrases du brief, mot pour mot", () => {
    const fr = VISIT_COPY.fr;
    expect(plain(fr.narration.carte)).toBe("Lundi, 8 h 03. Quelle entreprise mérite votre premier appel ?");
    expect(plain(fr.narration.suivant)).toBe("Le lundi suivant, vous ne recommencez pas à zéro.");
    expect(plain(fr.narration.date)).toBe("Et la liste, vaut-elle quelque chose ? Choisissez une date.");
    expect(plain(fr.narration.seuil)).toBe("Combien de journées supplémentaires facturées faut-il pour couvrir le coût ?");
    expect(plain(fr.mentions.general)).toBe("Démonstration · entreprises réelles, personnes fictives");
    expect(plain(fr.privacy.sent)).toBe("Vos saisies ne sont pas envoyées à notre équipe.");
    expect(plain(CARNET_COPY.fr.useful)).toBe("Une conversation utile, c'est une date fixée, un besoin confirmé ou une prochaine étape acceptée.");
    // German stays marked « to be reviewed » until a German speaker has read it (§ 9)
    expect(VISIT_COPY.de.mentions.review).not.toBe("");
    expect(VISIT_COPY.fr.mentions.review).toBe("");
  });
});

// Suite 8, § 6: the passage on Apertus, Hiba's words, everywhere the visit speaks of it (the visit, its pages, Iris's
// answers, the presenter's notes); « intelligence artificielle » only inside it, once; never the sentence of B3, never
// another provider named, never « un iris orange » (the name has three other reasons now).
describe("le discours de la suite 8 : le passage sur Apertus, partout où l'on en parle", () => {
  const everything = (lang: "fr" | "de") =>
    [VISIT_COPY[lang], PAGES_COPY[lang], GUIDE_COPY[lang], VISIT_NOTES[lang]].flatMap((x) => allStrings(x)).map(plain);

  it("la porte et le passage Apertus ne parlent qu'au futur ou au conditionnel (suite 9, § 8 : rien de cela n'existe encore)", () => {
    const presentFr = [/\bpeut s'appuyer\b/, /\bOn peut l'adapter\b/, /\bne quittent jamais\b/, /\brestent chez vous\b/, /\bvoit ce qu'Iris\b/, /\bpeut le corriger\b/, /\brestent sous son contrôle\b/, /\best mesurée avant\b/, /\bIris propose,/, /\bne classe ni ne surveille\b/];
    const presentDe = [/\bkann sich Proxsis\b/, /\bMan kann sie\b/, /\bverlassen das Unternehmen nie\b/, /\bHier bleiben sie\b/, /\bAlle sehen\b/, /\bbleiben unter ihrer Kontrolle\b/, /\bIris schlägt vor\b/, /\bIris bewertet oder überwacht\b/];
    const fr = [APERTUS.fr, ...PORTE.fr.gardeFous, ...PORTE.fr.texte, ...PORTE.fr.etapes];
    const de = [APERTUS.de, ...PORTE.de.gardeFous, ...PORTE.de.texte, ...PORTE.de.etapes];
    for (const x of fr) for (const r of presentFr) expect(x, x.slice(0, 60)).not.toMatch(r);
    for (const x of de) for (const r of presentDe) expect(x, x.slice(0, 60)).not.toMatch(r);
  });
  it("la synthèse : la 3e étape est celle de la porte, avec ses garde-fous au futur (suite 9, § 8)", () => {
    const p = (x: string) => x.replace(/\u00a0/g, " ").replace(/\u202f/g, " ");
    expect(p(VISIT_COPY.fr.conclusion.next.steps[2])).toContain(p(PORTE.fr.etapes[2]).replace(/\.$/, ""));
    expect(p(VISIT_COPY.de.conclusion.next.steps[2])).toContain(p(PORTE.de.etapes[2]).replace(/\.$/, ""));
    expect(p(VISIT_COPY.fr.conclusion.next.steps[2])).toContain("rien de cela n'existe aujourd'hui");
    expect(p(VISIT_COPY.de.conclusion.next.steps[2])).toContain("nichts davon gibt es heute");
  });
  it("le passage, mot pour mot, au conditionnel (suite 9, § 8 : la porte se dit au futur ou au conditionnel)", () => {
    expect(APERTUS.fr).toBe("Pour aller plus loin, Proxsis pourrait s'appuyer sur Apertus, l'intelligence artificielle suisse et ouverte. On pourrait l'adapter à vos données et la faire tourner chez vous : vos textes ne quitteraient jamais l'entreprise. Avec un service en ligne, ils partent chez un fournisseur, souvent à l'étranger. Ici, ils resteraient chez vous.");
    expect(forbiddenTerms(APERTUS.fr, "fr")).toEqual([]);
    expect(forbiddenTerms(APERTUS.de, "de")).toEqual([]);
  });

  for (const lang of ["fr", "de"] as const) {
    it(`${lang} : Apertus ou l'intelligence artificielle, c'est toujours ce passage ; ni B3 ni autre fournisseur`, () => {
      const term = lang === "fr" ? "intelligence artificielle" : "künstliche Intelligenz";
      const texts = everything(lang);
      // suite 9, Q02 and § 8: the direct question carries the words too (never the acronym)
      const question = lang === "fr" ? "Utilisez-vous l'intelligence artificielle ?" : "Setzen Sie künstliche Intelligenz ein?";
      expect(texts.map((x) => x.replace(/\u00a0/g, " "))).toContain(question);
      // suite 9, § 8: the door (« Demain, si Flexsis le souhaite ») says Apertus and « intelligence artificielle » in full,
      // in the future or the conditional (PORTE, and its short block on the A4 page); never the acronym
      // and step 4 of the roadmap (Hiba, 14.10.2026), her own words: « Apertus, adapté aux données de Flexsis… »
      const door = new Set([...allStrings(PORTE[lang]), plain(PAGES_COPY[lang].unePage.porte.p), plain(VISIT_COPY[lang].conclusion.next.steps[2]),
        plain(PAGES_COPY[lang].feuille.steps[3].p)]);
      expect(texts.filter((x) => door.has(x)).length).toBeGreaterThanOrEqual(door.size);
      for (const x of door) expect(x).not.toMatch(lang === "fr" ? /\bIA\b/ : /\bKI\b/);
      for (const x of texts.filter((y) => y.replace(/\u00a0/g, " ") !== question && !door.has(y))) {
        if (x.includes("Apertus") || x.toLowerCase().includes(term.toLowerCase())) expect(x, x.slice(0, 80)).toContain(APERTUS[lang]);
        expect(x.replace(APERTUS[lang], "").toLowerCase(), x.slice(0, 80)).not.toContain(term.toLowerCase());
        expect(x, x.slice(0, 80)).not.toMatch(/OpenAI|Anthropic|Pas dans cette démonstration|Nicht in dieser Demonstration|iris orange|orangen Iris/i);
      }
      // the step « Ensuite », the page for the direction, the answer to « Utilisez-vous l'intelligence artificielle ? »
      expect(texts.filter((x) => x.includes(APERTUS[lang]))).toHaveLength(3);
    });
  }
});
