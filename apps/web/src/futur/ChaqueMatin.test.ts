import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import matin from "@/data/direct/matin.json";
import { dictionaries } from "@/i18n/dictionaries";
import type { LiveFile } from "@/lib/types";
import { ChaqueMatin } from "./ChaqueMatin";

// « Chaque matin, en direct de simap » (suite 10, § 2), rendered as the server sends it: the waiting section (the file of
// the repository), a day with something new, a day without, and the Monday (the week that ended). The mention of simap
// is in every state.
const MENTION = "Les données publiées sur la plateforme www.simap.ch font foi.";
const URL = "https://www.simap.ch/fr/project-detail/95465d92-7be7-46b7-862a-a376ca087134";
const contract = (date: string, nom: string, id: string) => ({ date, titre: `Réfection de la route (${date})`, adjudicateur: "Commune de Sion",
  commune: "Sion", laureats: [{ nom, id }], url: URL });
const day = (over: Partial<LiveFile>): LiveFile => ({ schema: 2, etat: "a_jour", mode: "veille", periode: { du: "2026-10-12", au: "2026-10-12" },
  mis_a_jour_le: "2026-10-13", source: "simap.ch", mention: matin.mention, total: 0, marches: [], rectifications: [], ...over });
const html = (file: LiveFile, lang: "fr" | "de" = "fr", list: string[] = []) =>
  renderToStaticMarkup(createElement(ChaqueMatin, { t: dictionaries[lang], list, file }))
    .replace(/&#x27;/g, "'").replace(/&quot;/g, "\"").replace(/\u00a0/g, " ");

describe("la section « Chaque matin, en direct de simap »", () => {
  it("en attente : le titre, ce qui viendra, la mention", () => {
    const out = html({ ...day({}), etat: "en_attente", mode: null, periode: null, mis_a_jour_le: null });
    expect(out).toContain("Chaque matin, en direct de simap");
    expect(out).toContain("Chaque jour ouvrable");
    expect(out).toContain(MENTION);
    expect(out).not.toContain("data-toc");
    expect(out).not.toContain('data-testid="matin-son"'); // nothing to hear while the section waits
  });
  it("un jour avec du nouveau : la veille, l'entreprise, le marché, l'adjudicateur, la date, le lien, « dans votre liste »", () => {
    const out = html(day({ total: 2, marches: [contract("2026-10-12", "Bitz travaux publics SA", "ent-734d5f7d45"),
      contract("2026-10-12", "Exemple Construction SA", "ent-0123456789")] }), "fr", ["ent-734d5f7d45"]);
    expect(out).toContain("Publiés le 12.10.2026");
    expect(out).toContain("Bitz travaux publics SA");
    expect(out).toContain("« Réfection de la route (2026-10-12) »");
    expect(out).toContain("Commune de Sion");
    expect(out).toContain(`href="${URL}"`);
    expect(out.match(/dans votre liste/g)).toHaveLength(1); // Bitz only: the other one is not in the list
    expect(out).toContain('data-nouveau="true"');
    expect(out).toContain(MENTION);
    expect(out).not.toContain("Rien de nouveau depuis hier");
  });
  it("un jour sans nouveau marché : « Rien de nouveau depuis hier. Iris veille. »", () => {
    const out = html(day({}));
    expect(out).toContain("Rien de nouveau depuis hier. Iris veille.");
    expect(out).toContain('data-nouveau="false"');
    expect(out).toContain(MENTION);
  });
  it("le lundi : la semaine écoulée, comme avant", () => {
    const out = html(day({ mode: "semaine", periode: { du: "2026-10-05", au: "2026-10-11" }, mis_a_jour_le: "2026-10-12", total: 1,
      marches: [contract("2026-10-07", "Bitz travaux publics SA", "ent-734d5f7d45")] }));
    expect(out).toContain("Semaine du 05.10.2026 au 11.10.2026");
    const empty = html(day({ mode: "semaine", periode: { du: "2026-10-05", au: "2026-10-11" }, mis_a_jour_le: "2026-10-12" }));
    expect(empty).toContain("Aucun marché de construction attribué en Valais n'a été publié cette semaine-là.");
  });
  it("le fichier du dépôt, en attente ou publié par la tâche du matin, se rend avec la mention de simap", () => {
    expect(html(matin as LiveFile)).toContain(MENTION);
  });
  it("en allemand, les mêmes états (textes à relire)", () => {
    expect(html(day({}), "de")).toContain("Seit gestern nichts Neues. Iris wacht.");
    expect(html(day({ total: 1, marches: [contract("2026-10-12", "Bitz travaux publics SA", "ent-734d5f7d45")] }), "de", ["ent-734d5f7d45"]))
      .toContain("in Ihrer Liste");
  });
});
