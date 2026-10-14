import { describe, expect, it } from "vitest";
import { allStrings } from "@/test/strings";
import { COPY_C, ETAPES_C, RESERVE_C } from "./copy_c";
import { forbiddenTerms } from "./vocabulary";

const LANGS = ["fr", "de"] as const;

/** The key tree of an object (array lengths included), to compare FR and DE. */
function shape(o: unknown): unknown {
  if (Array.isArray(o)) return o.map(shape);
  if (o && typeof o === "object") {
    return Object.fromEntries(Object.keys(o).sort().map((k) => [k, shape((o as Record<string, unknown>)[k])]));
  }
  return typeof o;
}

/** Every value stored under a key named `name`, anywhere in the object. */
function under(o: unknown, name: string): string[] {
  if (Array.isArray(o)) return o.flatMap((x) => under(x, name));
  if (o && typeof o === "object") {
    return Object.entries(o).flatMap(([k, v]) => (k === name ? allStrings(v) : under(v, name)));
  }
  return [];
}

/** Greedy wrap at `width` signs, without the italic markers: the length check of a statement. */
function wrap(text: string, width = 45): string[] {
  const lines: string[] = [];
  let line = "";
  for (const w of text.replace(/\*/g, "").split(/\s+/).filter(Boolean)) {
    if (!line) line = w;
    else if (line.length + 1 + w.length <= width) line += ` ${w}`;
    else {
      lines.push(line);
      line = w;
    }
  }
  if (line) lines.push(line);
  return lines;
}

describe("« Choisissez une date » et le dossier de preuves : textes FR et DE", () => {
  it("aucun terme à éviter", () => {
    for (const lang of LANGS) {
      const hits = allStrings(COPY_C[lang]).flatMap((s) => forbiddenTerms(s, lang).map((t) => `${t} ← « ${s.slice(0, 60)} »`));
      expect(hits).toEqual([]);
    }
  });

  it("mêmes clés en français et en allemand, mêmes longueurs de listes", () => {
    expect(shape(COPY_C.de)).toEqual(shape(COPY_C.fr));
  });

  it("aucun chiffre écrit dans les textes de l'écran : les valeurs viennent des données, par des marqueurs {…}", () => {
    for (const lang of LANGS) {
      const withDigits = allStrings(COPY_C[lang]).filter((s) => /\d/.test(s.replace(/\{[^}]*\}/g, "")));
      expect(withDigits).toEqual([]);
    }
  });

  it("chaque énoncé tient en trois lignes de 45 signes au plus", () => {
    for (const lang of LANGS) {
      const statements = under(COPY_C[lang], "statement");
      expect(statements.length).toBeGreaterThanOrEqual(1);
      for (const s of statements) {
        const lines = wrap(s);
        expect(lines.length, `${lang} « ${s} »`).toBeLessThanOrEqual(3);
        for (const line of lines) expect(line.length, `${lang} « ${line} »`).toBeLessThanOrEqual(45);
        expect(s, "un énoncé ne porte aucune valeur des données").not.toMatch(/\{/);
      }
    }
  });

  it("aucune phrase sur le nom (brief à distance, § 2 : « C'est un nom de travail » seulement si on le demande)", () => {
    for (const lang of LANGS) {
      const about = allStrings(COPY_C[lang]).filter((s) => /\b(?:le nom|ce nom|nom de travail|der Name|Arbeitsname)\b/i.test(s));
      expect(about).toEqual([]);
    }
  });

  it("italiques bien fermés, aucune « ß » (orthographe suisse), jamais 729 entreprises", () => {
    for (const lang of LANGS) {
      for (const s of allStrings(COPY_C[lang])) {
        expect((s.match(/\*/g) ?? []).length % 2, s).toBe(0);
        expect(s).not.toMatch(/ß/);
        expect(s).not.toMatch(/\b729\b/);
      }
    }
  });

  it("phrases obligatoires reprises mot pour mot (brief, direction de Hiba)", () => {
    const fr = COPY_C.fr.dir;
    expect(fr.histoire.need).toBe("Le besoin de personnel reste à confirmer.");
    // « Choisissez une date » (Hiba, brief « à distance », 4.3), word for word
    expect(fr.date.closing).toBe(
      "Un nouveau marché n'est pas une commande. Avec votre historique de commandes, cette même vue montrerait ce qui compte : lesquelles vous ont appelés.",
    );
    expect([fr.date.choose, fr.date.title]).toEqual(["Choisissez une date", "Votre lundi du {date}"]);
    expect(fr.date.aveu).toBe(
      "Sur notre premier test, une sélection plus compliquée n'a pas fait mieux qu'une règle simple. Nous avons gardé la règle simple. Le pilote mesurera si les dossiers préparés aident vos consultants à obtenir des conversations utiles, et à quel coût.",
    );
    expect(fr.histoire.stops).toEqual({
      known: "Ce qui était connu le {date}",
      signal: "La raison d'appeler", // « un lundi, pas un radar » (Hiba, 07.10.2026), was « Ce qu'on pouvait signaler »
      after: "Ce qui s'est passé ensuite",
    });

    const de = COPY_C.de.dir;
    expect(de.histoire.need).toBe("Der Personalbedarf ist noch zu bestätigen.");
  });

  it("un titre pour chaque étape et chaque histoire du dossier de preuves", () => {
    for (const lang of LANGS) expect(Object.keys(COPY_C[lang].steps).sort()).toEqual([...ETAPES_C, ...RESERVE_C].sort());
  });
});
