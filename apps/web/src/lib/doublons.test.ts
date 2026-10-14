import { describe, expect, it } from "vitest";
import entreprises from "@/data/demo/entreprises.json";

// « Vérifie les doublons de noms » (brief « à distance », § 6): two companies of the application whose names differ only
// by accents, case, punctuation, a legal form or small words (« de la », « des ») would be one firm counted twice.
const STOP = /\b(?:sa|sàrl|sarl|ag|gmbh|cie|et|und|de|la|le|les|des|du|d|l)\b/g;
const key = (name: string) => name.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase()
  .replace(/[^a-z0-9]+/g, " ").replace(STOP, " ").replace(/\s+/g, " ").trim();

describe("les noms des entreprises de l'application", () => {
  it("aucun doublon de nom (accents, casse, forme juridique et petits mots mis à part)", () => {
    const seen = new Map<string, string[]>();
    for (const c of Object.values(entreprises as Record<string, { nom: string }>)) seen.set(key(c.nom), [...(seen.get(key(c.nom)) ?? []), c.nom]);
    expect([...seen.values()].filter((names) => names.length > 1)).toEqual([]);
  });
});
