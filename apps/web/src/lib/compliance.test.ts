import { describe, expect, it } from "vitest";
import cases from "./compliance-cases.json";
import { freePublicationDate, remainingWorkingDays } from "./compliance";

describe("job-reporting countdown", () => {
  it("matches the official example of the SECO directive (online 5.7.2021 → free 13.7.2021)", () => {
    expect(freePublicationDate("2021-07-05", [])).toBe("2021-07-13");
  });

  it("skips Valais holidays like the Python module", () => {
    const h = ["2026-12-08", "2026-12-25", "2026-11-01"];
    expect(freePublicationDate("2026-12-07", h)).toBe("2026-12-16");
    expect(freePublicationDate("2026-10-30", h)).toBe("2026-11-07");
  });

  it("counts the working days left", () => {
    expect(remainingWorkingDays("2021-07-05", "2021-07-05", [])).toBe(5);
    expect(remainingWorkingDays("2021-07-05", "2021-07-09", [])).toBe(2); // Fri 9 and Mon 12 remain
    expect(remainingWorkingDays("2021-07-05", "2021-07-13", [])).toBe(0);
  });

  it("gives the same date as the Python calculation for every day of 2026 (shared cases, compliance-cases.json)", () => {
    const wrong = cases.cas.filter((c) => freePublicationDate(c.en_ligne, cases.jours_feries) !== c.publication_libre);
    expect(cases.cas).toHaveLength(365);
    expect(wrong).toEqual([]);
  });

  it("counts the whole restriction before the vacancy goes online and none from the free day", () => {
    for (const c of cases.cas.slice(0, 40)) {
      expect(remainingWorkingDays(c.en_ligne, c.en_ligne, cases.jours_feries)).toBe(5);
      expect(remainingWorkingDays(c.en_ligne, c.publication_libre, cases.jours_feries)).toBe(0);
    }
  });
});
