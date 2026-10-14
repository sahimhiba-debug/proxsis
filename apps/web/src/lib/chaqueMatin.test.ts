import { describe, expect, it } from "vitest";
import claims from "@/data/demo/claims.json";
import matin from "@/data/direct/matin.json";
import matins from "@/data/presentation/matins.json";
import lundis from "@/data/presentation/lundis.json";
import carte from "@/data/sources/carte.json";
import { forbiddenTerms } from "@/presentation/vocabulary";
import type { LiveFile } from "./types";
import { MORNING, NOTHING_NEW, IN_YOUR_LIST, RULE, SECTION_TITLE, morningView, sourcesLine, type SourceMap } from "./chaqueMatin";

// Suite 10 (13.10.2026): « Chaque matin » and the map of the sources. Hiba's sentences word for word in French; the
// German is a proposal to review (Hiba does not read German); the numbers of the sources come from their file
// (`proxsis carte-sources`, CLAIMS SOURCES-1), never from the text.
const contract = (date: string, ids: string[]) => ({ date, titre: `Route (${date})`, adjudicateur: "Commune de Sion", commune: "Sion",
  laureats: ids.map((id) => ({ nom: `Entreprise ${id} SA`, id })), url: "https://www.simap.ch/fr/project-detail/95465d92-7be7-46b7-862a-a376ca087134" });
const file = (over: Partial<LiveFile>): LiveFile => ({ schema: 2, etat: "a_jour", mode: "veille", periode: { du: "2026-10-12", au: "2026-10-12" },
  mis_a_jour_le: "2026-10-13", source: "simap.ch", mention: matin.mention, total: 0, marches: [], rectifications: [], ...over });

describe("les phrases de la consigne, mot pour mot", () => {
  it("français", () => {
    expect(MORNING.fr).toBe("Chaque matin, Iris lit les marchés publics attribués. Le lundi, elle pose les dix points.");
    expect(SECTION_TITLE.fr).toBe("Chaque matin, en direct de simap");
    expect(NOTHING_NEW.fr).toBe("Rien de nouveau depuis hier. Iris veille.");
    expect(IN_YOUR_LIST.fr).toBe("dans votre liste");
    expect(RULE.fr).toBe("Proxsis ne lit que ce qu'il a le droit de lire, et ne promet que ce qu'il a mesuré.");
  });
  it("aucun mot à éviter, en français ni en allemand (l'allemand reste à relire)", () => {
    for (const lang of ["fr", "de"] as const) {
      for (const text of [MORNING[lang], SECTION_TITLE[lang], NOTHING_NEW[lang], IN_YOUR_LIST[lang], RULE[lang], sourcesLine(lang)]) {
        expect(forbiddenTerms(text, lang), text).toEqual([]);
        expect(text.trim()).not.toBe("");
      }
    }
  });
});

describe("la carte des sources : les vrais nombres, comptés dans le catalogue", () => {
  it("la ligne dit les nombres du fichier, ceux de la ligne SOURCES-1 de CLAIMS", () => {
    const c = carte as SourceMap;
    expect(sourcesLine("fr")).toBe(`${c.etudiees} sources étudiées : ${c.en_service.nombre} en service, ${c.demandes.nombre} couvertes par une demande `
      + `d'accès envoyée, ${c.ecartees.nombre} écartées. Les autres : conditions à vérifier, ou rien d'utile pour la liste.`);
    const claim = (claims as Record<string, { valeur: string }>)["SOURCES-1"];
    for (const figure of [`${c.etudiees} sources`, `${c.en_service.nombre} en service`, `${c.demandes.nombre} couvertes`, `${c.ecartees.nombre} écartées`]) {
      expect(claim.valeur).toContain(figure);
    }
    expect(c.etudiees).toBe(c.en_service.nombre + c.demandes.nombre + c.ecartees.nombre + c.autres.nombre);
  });
  it("les nombres changent avec le fichier, jamais dans le texte", () => {
    const other = { ...(carte as SourceMap), etudiees: 70, ecartees: { ...(carte as SourceMap).ecartees, nombre: 11 } };
    expect(sourcesLine("de", other)).toMatch(/^70 Quellen geprüft: 2 in Betrieb, 4 .* 11 ausgeschlossen\./);
  });
});

describe("« Chaque matin, en direct de simap » : ce que la section montre", () => {
  it("en attente tant que la tâche du matin n'a rien publié ; le fichier du dépôt, en attente ou publié, se lit", () => {
    expect(morningView({ ...file({}), etat: "en_attente", mode: null, periode: null, mis_a_jour_le: null }, new Set()).state).toBe("attente");
    // the morning job runs these tests after writing the file: they hold whatever the state of the repository's file
    const repo = morningView(matin as LiveFile, new Set());
    expect(repo.state === "attente" ? (matin as LiveFile).etat : "a_jour").toBe((matin as LiveFile).etat);
  });
  it("du mardi au vendredi : la veille, et « dans votre liste » pour une entreprise de la liste de la semaine", () => {
    const v = morningView(file({ total: 2, marches: [contract("2026-10-12", ["ent-a"]), contract("2026-10-12", ["ent-b", "ent-c"])] }),
      new Set(["ent-c"]));
    expect(v.state).toBe("nouveau");
    if (v.state === "attente") throw new Error();
    expect(v.mode).toBe("veille");
    expect(v.items.map((c) => c.laureats.map((w) => w.inList))).toEqual([[false], [false, true]]);
  });
  it("un jour sans nouveau marché : rien de nouveau (les rectifications restent dites)", () => {
    const v = morningView(file({ rectifications: [{ date: "2026-10-12", type: "abandonment", titre: "X", url: contract("", []).url }] }), new Set());
    expect(v.state).toBe("rien");
    if (v.state === "attente") throw new Error();
    expect(v.corrections).toHaveLength(1);
  });
  it("le lundi, rien ne change : la semaine écoulée", () => {
    const v = morningView(file({ mode: "semaine", periode: { du: "2026-10-05", au: "2026-10-11" }, mis_a_jour_le: "2026-10-12", total: 1,
      marches: [contract("2026-10-07", ["ent-a"])] }), new Set(["ent-a"]));
    expect(v.state === "nouveau" && v.mode === "semaine" && v.items[0].laureats[0].inList).toBe(true);
  });
});

describe("« Choisissez une date » : la même section, figée, pour chaque lundi au choix", () => {
  it("chaque lundi au choix a sa section, avec seulement ce qui était publié avant ce lundi", () => {
    const offered = lundis.lundis.filter((m) => m.choisissable).map((m) => m.lundi);
    expect(Object.keys(matins.lundis)).toEqual(offered);
    for (const [monday, m] of Object.entries(matins.lundis)) {
      expect(m.marches.every((c) => c.date < monday && c.date >= m.periode.du && c.date <= m.periode.au), monday).toBe(true);
    }
    expect(matins.mention).toBe(matin.mention);
  });
  it("« dans votre liste » : les dix entreprises de ce lundi-là, reconnues par leur identifiant", () => {
    const ex = lundis.choix.exemple;
    const ten = new Set(lundis.lundis.find((m) => m.lundi === ex)!.dix.map((c) => c.id));
    const v = morningView({ ...file({}), mode: "semaine", periode: matins.lundis[ex as keyof typeof matins.lundis].periode, mis_a_jour_le: ex,
      total: matins.lundis[ex as keyof typeof matins.lundis].total, marches: matins.lundis[ex as keyof typeof matins.lundis].marches }, ten);
    if (v.state === "attente") throw new Error();
    expect(v.items.some((c) => c.laureats.some((w) => w.inList))).toBe(true);
  });
});
