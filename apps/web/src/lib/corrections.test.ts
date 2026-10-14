import { describe, expect, it } from "vitest";
import corrections from "@/data/direct/corrections.json";
import { correctionSentence, correctionsFor } from "./corrections";
import type { CorrectionsFile } from "./types";

const P = "95465d92-7be7-46b7-862a-a376ca087134";
const file: CorrectionsFile = { schema: 1, mis_a_jour_le: "2026-10-19", source: "simap.ch", mention: "…",
  avis: [{ projet: P, date: "2026-10-08", type: "correction", url: `https://www.simap.ch/fr/project-detail/${P}` },
    { projet: P, date: "2026-10-14", type: "revocation", url: `https://www.simap.ch/fr/project-detail/${P}` }] };

describe("rectifications des avis figés (AGB API simap, ch. 5 al. 2)", () => {
  it("une page simap du projet, en français ou en allemand, retrouve ses rectifications ; les autres rien", () => {
    expect(correctionsFor(`https://www.simap.ch/de/project-detail/${P}`, file).map((n) => n.date)).toEqual(["2026-10-08", "2026-10-14"]);
    expect(correctionsFor("https://www.simap.ch/fr/project-detail/11111111-2222-4333-8444-555555555555", file)).toEqual([]);
    expect(correctionsFor("app:/carte/", file)).toEqual([]);
    expect(correctionsFor(null, file)).toEqual([]);
  });

  it("la phrase dit le fait, sa date, et que la version officielle fait foi", () => {
    expect(correctionSentence("correction", "2026-10-08", "fr").replace(/[\u00a0\u202f]/g, " ")).toBe(
      "Cette publication a été rectifiée sur simap le 08.10.2026 ; la version officielle fait foi.");
    expect(correctionSentence("abandonment", "2026-10-08", "de")).toBe(
      "Diese Publikation wurde am 08.10.2026 auf simap abgebrochen; massgebend ist die offizielle Fassung.");
  });

  it("le fichier du site part vide : aucune rectification inventée", () => {
    expect((corrections as CorrectionsFile).avis).toEqual([]);
  });
});
