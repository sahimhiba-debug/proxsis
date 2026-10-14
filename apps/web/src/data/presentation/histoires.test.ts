import { describe, expect, it } from "vitest";
import claims from "@/data/demo/claims.json";
import { forbiddenTerms } from "@/presentation/vocabulary";
import histoires from "./histoires.json";

type Bi = Record<"fr" | "de", string>;
const h = histoires as unknown as {
  source: { mention: string };
  histoires: { id: string; type: string; claims: string; date_T: string; besoin_personnel: Bi;
    arrets: { connu: { pieces: { date: string; titre: string; langue: string }[] }; ensuite: { texte: Bi } } }[];
  mesure: { phrase: Bi; portee: Bi; ecart: { lecture: Bi } };
};

function texts(o: unknown, lang: "fr" | "de"): string[] {
  if (Array.isArray(o)) return o.flatMap((v) => texts(v, lang));
  if (o && typeof o === "object") {
    return Object.entries(o as Record<string, unknown>).flatMap(([k, v]) =>
      k === lang && typeof v === "string" ? [v] : k === "titre" ? [] : texts(v, lang));
  }
  return [];
}

describe("acte 4 : trois histoires datées et l'écran de mesure (données)", () => {
  it("trois histoires, dont une limite, chacune avec sa ligne CLAIMS", () => {
    expect(h.histoires).toHaveLength(3);
    expect(h.histoires.filter((s) => s.type === "limite").length).toBeGreaterThanOrEqual(1);
    const c = claims as Record<string, unknown>;
    expect(h.histoires.every((s) => s.claims in c)).toBe(true);
    expect(h.source.mention).toContain("www.simap.ch font foi");
  });

  it("au premier arrêt, seules des pièces publiées avant la date rejouée", () => {
    for (const s of h.histoires) expect(s.arrets.connu.pieces.every((p) => p.date < s.date_T)).toBe(true);
  });

  it("le besoin de personnel reste à confirmer, partout et dans la limite aussi", () => {
    for (const s of h.histoires) {
      expect(s.besoin_personnel.fr).toBe("Le besoin de personnel reste à confirmer.");
      expect(s.arrets.ensuite.texte.fr).toContain("Le besoin de personnel reste à confirmer.");
      expect(s.arrets.ensuite.texte.de).toContain("Der Personalbedarf ist noch zu bestätigen.");
    }
  });

  it("la mesure : la phrase obligatoire, la portée (pas des embauches) et un écart non établi", () => {
    expect(h.mesure.phrase.fr).toBe(
      "Sur notre premier examen des marchés publics, la sélection proposée n'a pas fait mieux qu'une règle simple.");
    expect(h.mesure.portee.fr).toContain("pas sur des embauches");
    expect(h.mesure.ecart.lecture.fr).toContain("n'est pas établie");
  });

  it("aucun terme à éviter dans les textes FR et DE (titres originaux exceptés)", () => {
    for (const lang of ["fr", "de"] as const) {
      expect(texts(h, lang).flatMap((t) => forbiddenTerms(t, lang))).toEqual([]);
    }
  });

  it("les titres allemands restent dans leur langue (Haut-Valais)", () => {
    const theler = h.histoires.find((s) => s.id.startsWith("theler"))!;
    expect(theler.arrets.connu.pieces.every((p) => p.langue === "de")).toBe(true);
    expect(theler.arrets.connu.pieces.some((p) => p.titre.includes("Abschnitt 3"))).toBe(true);
  });
});
