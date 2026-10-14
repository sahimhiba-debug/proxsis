import { describe, expect, it } from "vitest";
import { swissAmount } from "./amount";

describe("montant publié : exact, à la suisse, dans les deux langues (contenu de simap non modifié)", () => {
  it("les centimes seulement quand il y en a ; aucun arrondi", () => {
    expect(swissAmount(1574663.35)).toBe("1'574'663.35");
    expect(swissAmount(750969.3)).toBe("750'969.30");
    expect(swissAmount(3994845.7)).toBe("3'994'845.70");
    expect(swissAmount(750969)).toBe("750'969");
    expect(swissAmount(980)).toBe("980");
  });
});
