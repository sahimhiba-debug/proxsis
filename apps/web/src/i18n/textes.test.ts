import { describe, expect, it } from "vitest";
import { dictionaries } from "@/i18n/dictionaries";
import { COPY } from "@/presentation/copy";
import { PHONE_COPY } from "@/presentation/phone/copy";

// Every interface text exists in French AND in German: same keys, no empty text, no array of a different length
// (the application, the presentation with its notes, the phone demo).
function leaves(o: unknown, path = ""): Map<string, unknown> {
  const out = new Map<string, unknown>();
  if (o && typeof o === "object") {
    for (const [k, v] of Object.entries(o)) for (const [p, x] of leaves(v, path ? `${path}.${k}` : k)) out.set(p, x);
  } else out.set(path, o);
  return out;
}

const SETS: [string, unknown, unknown][] = [
  ["application (dictionaries.ts)", dictionaries.fr, dictionaries.de],
  ["présentation (copy.ts, copy_c.ts)", COPY.fr, COPY.de],
  ["démo au téléphone (phone/copy.ts)", PHONE_COPY.fr, PHONE_COPY.de],
];

describe("chaque texte existe en français et en allemand", () => {
  for (const [name, fr, de] of SETS) {
    it(name, () => {
      const f = leaves(fr);
      const d = leaves(de);
      expect([...d.keys()].filter((k) => !f.has(k)), "clés seulement en allemand").toEqual([]);
      expect([...f.keys()].filter((k) => !d.has(k)), "clés seulement en français").toEqual([]);
      const empty = [...f.entries(), ...d.entries()].filter(([, v]) => typeof v === "string" && v.trim() === "").map(([k]) => k);
      // a few keys are empty on purpose in one language: the original's label, and the mentions that German texts are
      // being reviewed (§ 9 of the brief « à distance »), are only needed in German
      expect(empty.filter((k) => !/^(?:source\.(mentionOriginal|translation)|fx\.(phoneReview|guideReview|reviewDe))$/.test(k))).toEqual([]);
    });
  }
});
