import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

// Suite 9, Q09 (13.10.2026): no real person of Flexsis or of its group in the repository, not even inside a source
// address. The full address of EXT-GROUPE-DELAI stays in a local file outside Git (data/reel).
describe("le registre des affirmations ne nomme aucune personne réelle du groupe", () => {
  const racine = join(__dirname, "../../../../..");
  for (const fichier of ["CLAIMS.md", "apps/web/src/data/demo/claims.json"]) {
    it(fichier, () => {
      const texte = readFileSync(join(racine, fichier), "utf8");
      expect(texte).not.toMatch(/tobien|sebastian/i);
      expect(texte).not.toMatch(/interiman-group\.ch\/nouvelle-recrue/i);
    });
  }
});
