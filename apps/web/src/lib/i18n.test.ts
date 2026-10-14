import { describe, expect, it } from "vitest";
import { fmtStamp } from "./i18n";

describe("un moment noté sur l'appareil", () => {
  it("s'écrit à la suisse, sans secondes ni AM/PM, quelle que soit la langue du navigateur", () => {
    const at = new Date(2026, 9, 7, 1, 42, 33).toISOString(); // 7 October 2026, 01:42:33 on this device
    expect(fmtStamp(at, "fr")).toBe("07.10.2026 à 01:42");
    expect(fmtStamp(at, "de")).toBe("07.10.2026 um 01:42");
  });
});
