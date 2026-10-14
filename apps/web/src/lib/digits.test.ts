import { describe, expect, it } from "vitest";
import { groupDigits } from "./digits";

describe("chiffres du calculateur, écrits pareil sur le serveur et dans le navigateur", () => {
  it("groupe les milliers à la suisse et garde les décimales demandées", () => {
    expect(groupDigits(46773.4, 0, "fr-CH")).toBe("46 773");
    expect(groupDigits(46773.4, 0, "de-CH")).toBe("46’773");
    expect(groupDigits(5.25, 1, "fr-CH")).toBe("5,3");
    expect(groupDigits(1234567.891, 1, "de-CH")).toBe("1’234’567.9");
    expect(groupDigits(-1050, 0, "fr-CH")).toBe("−1 050");
    expect(groupDigits(-0.01, 1, "fr-CH")).toBe("0,0");
  });
});
