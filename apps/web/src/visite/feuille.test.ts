import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { PAGES_COPY } from "./pages";

// The roadmap (Hiba, 14.10.2026): her text word for word in French (German to review), without any duration (no week,
// month or date), reached from the end of the visit and from « Pour votre direction ».
describe("la feuille de route", () => {
  const fr = PAGES_COPY.fr.feuille;
  const plain = (x: string) => x.replace(/ /g, " ");

  it("fr : le texte de la consigne, mot pour mot", () => {
    expect(plain(fr.today.p)).toBe("Un prototype en ligne, en français et en allemand, sur téléphone et sur ordinateur. La liste du lundi, mesurée sur 57 lundis passés (voir « Sources et mesures »). Deux sources officielles, et simap lu chaque matin. Les demandes d'accès envoyées : SECO, Zefix, Job-Room, registre des bâtiments. Rien n'est installé chez Flexsis, et aucune donnée de Flexsis n'est utilisée.");
    expect(fr.steps.map((s) => plain(`${s.h}.${s.p ? ` ${s.p}` : ""}`))).toEqual([
      "Étape 1 : un essai avec deux consultants volontaires, dans une agence. Ils reçoivent la liste chaque lundi et la gardent, la reportent ou l'écartent. On mesure les appels, les rendez-vous et les missions, et on recueille leur avis. Ensuite, on décide : continuer, ajuster ou arrêter.",
      "Étape 2 : l'historique de Flexsis, sous accord de confidentialité. On mesure ce que la liste rapporte vraiment, et on l'adapte à chaque agence et à chaque métier. Les données restent sous le contrôle de Flexsis, en Suisse.",
      "Étape 3 : plus de sources et plus d'agences. Dès que les autorisations arrivent : le Bulletin officiel et le registre du commerce chaque matin, et Zefix. Chaque source est mesurée avant d'entrer dans la liste. On passe à deux agences, en français et en allemand.",
      "Étape 4 : Iris chez Flexsis, si Flexsis le souhaite. Une assistante pour chaque consultant, et un agent qui lit les publications chaque matin. Apertus, adapté aux données de Flexsis, sur ses serveurs ou chez un hébergeur suisse. Les cinq garde-fous s'appliquent toujours.",
      "Étape 5 : toutes les agences, d'abord en Valais, puis dans les autres régions, chacune dans sa langue.",
    ]);
    expect(plain(fr.rule.p)).toBe("On passe à l'étape suivante seulement avec des résultats mesurés et l'accord de Flexsis.");
  });

  for (const lang of ["fr", "de"] as const) {
    const t = PAGES_COPY[lang].feuille;
    const all = [t.title, t.today.h, t.today.p, t.today.measures, ...t.steps.flatMap((s) => [s.h, s.p]), t.rule.h, t.rule.p];
    it(`${lang} : aucune durée, ni semaine, ni mois, ni date ; aucun mot à éviter`, () => {
      expect(t.steps).toHaveLength(5);
      const text = all.join(" ");
      expect(text).not.toMatch(lang === "fr" ? /\b(semaines?|mois|jours?|ans?|années?|trimestres?|dates?)\b/i : /\b(Wochen?|Monate?n?|Tage?n?|Jahre?n?|Quartale?|Datum)\b/i);
      expect(text.replace(/\b57\b/, "").replace(/(Étape|Schritt) [1-5]/g, "")).not.toMatch(/\d/);
      expect(all.flatMap((x) => forbiddenTerms(x, lang))).toEqual([]);
    });
  }

  it("est reliée à la fin de la visite et à « Pour votre direction »", () => {
    for (const f of ["Conclusion.tsx", "PourDirection.tsx"]) {
      expect(readFileSync(new URL(`./${f}`, import.meta.url), "utf8")).toContain('visitPath(lang, "feuille-de-route")');
    }
  });
});
