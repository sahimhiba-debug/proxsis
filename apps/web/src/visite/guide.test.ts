import { describe, expect, it } from "vitest";
import lundis from "@/data/presentation/lundis.json";
import carte from "@/data/sources/carte.json";
import type { MondaysData } from "@/presentation/mondayData";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { allStrings } from "@/test/strings";
import { GUIDE_COPY, QUESTIONS, reponse, sourcesAnswer } from "./guide";

const data = lundis as unknown as MondaysData;
const shape = (o: unknown): unknown => (typeof o === "string" ? "s" : Object.fromEntries(Object.entries(o as object).map(([k, v]) => [k, shape(v)])));

describe("le guide de la visite : une phrase par temps, six réponses préparées, rien à saisir", () => {
  it("les mêmes textes en français et en allemand, aucun vide", () => {
    expect(shape(GUIDE_COPY.de)).toEqual(shape(GUIDE_COPY.fr));
    for (const lang of ["fr", "de"] as const) for (const s of allStrings(GUIDE_COPY[lang])) expect(s.trim()).not.toBe("");
  });

  it("six questions, celles du message de Hiba, dans cet ordre", () => {
    expect(QUESTIONS).toEqual(["sources", "appel", "saisies", "pourquoi", "marche", "rapporte"]);
    expect(QUESTIONS.map((q) => GUIDE_COPY.fr.questions[q].q)).toEqual(["D'où viennent les informations ?",
      "Proxsis appelle-t-il à ma place ?", "Que deviennent mes saisies ?", "Pourquoi cette entreprise ?",
      "Est-ce que ça marche vraiment ?", "Combien ça rapporte ?"].map((s) => s.replace(" ?", " ?")));
  });

  it("les chiffres viennent des données (CLAIMS REEL-SPEC-BAT), la confidentialité des textes de la visite", () => {
    const fr = reponse("marche", "fr", data);
    expect(fr).toContain(`${data.mesure.semaines} lundis`);
    expect(fr).toContain(data.mesure.affiche.regle.fr);
    expect(fr).toContain(data.mesure.affiche.hasard.fr);
    expect(fr).not.toMatch(/\{\w+\}/);
    expect(reponse("saisies", "fr", data)).toContain("ne sont pas envoyées à notre équipe");
    expect(reponse("marche", "de", data)).toContain(data.mesure.affiche.regle.de);
    // « combien ça rapporte » : aucun chiffre de gain, puisqu'aucun n'est mesuré
    expect(reponse("rapporte", "fr", data)).not.toMatch(/\d/);
  });

  it("aucun mot interdit à l'écran (vocabulaire de la visite)", () => {
    for (const lang of ["fr", "de"] as const) {
      const bad = allStrings(GUIDE_COPY[lang]).flatMap((s) => forbiddenTerms(s, lang));
      expect(bad).toEqual([]);
    }
  });

  it("les phrases d'Iris de la suite 8, mot pour mot ; la date des sources chaque lundi, le silence d'une source pour demain (suite 9, Q04, Q05)", () => {
    const plain = (x: string) => x.replace(/\u00a0/g, " ");
    expect(plain(GUIDE_COPY.fr.phrases[1])).toBe("Je suis Iris, l'assistante de Proxsis. Moi, je prépare. Vous, vous décidez.");
    expect(Object.values(GUIDE_COPY.fr.phrases).filter((p) => plain(p).includes("Iris met les points sur les i."))).toHaveLength(1);
    expect(plain(GUIDE_COPY.fr.ask)).toBe("Une question ? Demandez à Iris.");
    // Q04: no longer a promise of today; each Monday, the date up to which each source is up to date
    expect(plain(reponse("sources", "fr", data))).toContain("Chaque lundi, je vous dis jusqu'à quelle date chaque source est à jour.");
    expect(plain(reponse("sources", "fr", data))).not.toContain("se tait");
    expect(plain(reponse("sources", "de", data))).toContain("Jeden Montag sage ich Ihnen, bis zu welchem Datum jede Quelle aktuell ist.");
    expect(plain(reponse("sources", "de", data))).not.toMatch(/schweigt|verstummt/);
    // Q05: the German motto, to be reviewed
    expect(Object.values(GUIDE_COPY.de.phrases).filter((p) => plain(p).includes("Iris bringt es auf den Punkt."))).toHaveLength(1);
    expect(allStrings(GUIDE_COPY.de).join(" ")).not.toContain("Punkt aufs i");
    for (const lang of ["fr", "de"] as const) expect(allStrings(GUIDE_COPY[lang]).join(" ")).not.toMatch(/\bIA\b|\bKI\b/);
  });
});

// suite 10, § 3: « Et les autres sources ? » — in the visit, one line under Iris's answer on the sources: the real numbers
// of the catalogue (src/data/sources/carte.json, CLAIMS SOURCES-1) and the rule, the same as on the A4 page
describe("la carte des sources, sous la réponse d'Iris sur les sources", () => {
  it("les nombres du catalogue et la règle, en une ligne, FR et DE (DE à relire)", () => {
    expect(sourcesAnswer("fr").replace(/ /g, " ")).toBe(`${carte.etudiees} sources étudiées : ${carte.en_service.nombre} en service, `
      + `${carte.demandes.nombre} couvertes par une demande d'accès envoyée, ${carte.ecartees.nombre} écartées. Les autres : conditions à `
      + "vérifier, ou rien d'utile pour la liste. Proxsis ne lit que ce qu'il a le droit de lire, et ne promet que ce qu'il a mesuré.");
    expect(sourcesAnswer("de")).toContain(`${carte.etudiees} Quellen geprüft`);
    for (const lang of ["fr", "de"] as const) expect(forbiddenTerms(sourcesAnswer(lang), lang)).toEqual([]);
  });
});
