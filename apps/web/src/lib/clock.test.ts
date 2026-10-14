import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";

// The demonstration's « today » is the list's Monday (data/demo/meta.json, `semaine`), written on screen next to every
// count; no screen reads the computer's clock, so the demo shows the same thing on any day of the meeting. The only
// real moment kept is when a call feedback or a return from the field is recorded in the carnet (its own timestamp).
const SRC = join(__dirname, "..");
const ALLOWED = new Set(["components/Feedback.tsx", "futur/CarnetPanel.tsx"]);

function files(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return name === "data" ? [] : files(p);
    return /\.(ts|tsx)$/.test(name) && !/\.test\.tsx?$/.test(name) ? [p] : [];
  });
}

describe("une seule date de démonstration", () => {
  it("aucun écran ne lit l'horloge de l'ordinateur (hors l'heure d'un retour d'appel enregistré)", () => {
    const readers = files(SRC).map((p) => relative(SRC, p))
      .filter((p) => !ALLOWED.has(p) && /new Date\(\s*\)|Date\.now\(\)/.test(readFileSync(join(SRC, p), "utf8")));
    expect(readers).toEqual([]);
  });
});
