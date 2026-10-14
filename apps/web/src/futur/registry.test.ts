import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import appels from "@/data/demo/appels.json";
import tableau from "@/data/demo/tableau.json";
import { dictionaries } from "@/i18n/dictionaries";

// « Sources et mesures »: every line of the registry that the application links to (« Voir la mesure et sa méthode »,
// the source numbers of the call guide, the dashboard tiles) is open on the page, never inside the folded registry,
// and says what it means in a plain sentence, in French and in German.
const SRC = join(__dirname, "..");
const page = readFileSync(join(SRC, "app/[lang]/(futur)/mesures/page.tsx"), "utf8");
const listed = (name: string) => [...(page.match(new RegExp(`const ${name} = \\[([^\\]]*)\\]`))?.[1] ?? "").matchAll(/"([A-Z0-9-]+)"/g)].map((m) => m[1]);
const open = new Set([...listed("MEASURED"), ...listed("ESTIMATED"), ...listed("FICTIONAL")]);

function sources(dir: string): string[] {
  return readdirSync(dir).flatMap((n) => {
    const p = join(dir, n);
    if (statSync(p).isDirectory()) return n === "data" ? [] : sources(p);
    return /\.(ts|tsx)$/.test(n) && !n.endsWith(".test.ts") ? [readFileSync(p, "utf8")] : [];
  });
}

describe("le registre des mesures", () => {
  it("chaque ligne liée par l'application est ouverte sur la page, avec une phrase claire en français et en allemand", () => {
    const linked = new Set<string>();
    for (const text of [...sources(SRC), JSON.stringify(appels), JSON.stringify(tableau)]) {
      for (const m of text.matchAll(/mesures\/?#([A-Z][A-Z0-9-]+)/g)) linked.add(m[1]);
      for (const m of text.matchAll(/"claim":\s*"([A-Z][A-Z0-9-]+)"/g)) linked.add(m[1]);
    }
    expect(linked.size).toBeGreaterThan(5);
    const missing = [...linked].filter((id) => !open.has(id));
    expect(missing).toEqual([]);
    for (const id of open) {
      expect(dictionaries.fr.fx.sources.plain[id], `FR ${id}`).toBeTruthy();
      expect(dictionaries.de.fx.sources.plain[id], `DE ${id}`).toBeTruthy();
    }
  });
});
