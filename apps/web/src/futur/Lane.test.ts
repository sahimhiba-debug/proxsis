import { describe, expect, it } from "vitest";
import { dayIndex, firstFreeDay } from "./Lane";

describe("la frise d'une fin de mission", () => {
  it("le premier jour libre est un jour ouvré : une mission finie le vendredi libère le lundi, jamais le samedi", () => {
    const from = "2026-10-05"; // a Monday
    expect(firstFreeDay(dayIndex(from, "2026-10-09"))).toBe(dayIndex(from, "2026-10-12")); // Friday → Monday
    expect(firstFreeDay(dayIndex(from, "2026-10-10"))).toBe(dayIndex(from, "2026-10-12")); // Saturday → Monday
    expect(firstFreeDay(dayIndex(from, "2026-10-11"))).toBe(dayIndex(from, "2026-10-12")); // Sunday → Monday
    expect(firstFreeDay(dayIndex(from, "2026-10-06"))).toBe(dayIndex(from, "2026-10-07")); // Tuesday → Wednesday
  });
});
