import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import agences from "@/data/demo/agences.json";
import appels from "@/data/demo/appels.json";
import entreprises from "@/data/demo/entreprises.json";
import listes from "@/data/demo/listes.json";
import curated from "@/data/presentation/dossiers.json";
import { DUR, EASE } from "../motion";
import {
  CONSULTANT,
  FRAME,
  GUIDED,
  PHONE_MOTION,
  SCREEN,
  SCRIPT,
  fitScale,
  isDark,
  plan,
  stepOfPath,
  urlFor,
} from "./script";

const src = (p: string) => readFileSync(path.resolve(__dirname, "../../..", p), "utf-8");

describe("le script de la démo pilotée", () => {
  it("suit le dossier guidé : Ma semaine → dossier → appel préparé → feuille de synthèse", () => {
    expect(SCRIPT.map((s) => s.id)).toEqual(["semaine", "dossier", "appel", "synthese"]);
  });

  it("ouvre de vraies pages de l'application, en français et en allemand", () => {
    expect(urlFor(0, "fr")).toBe(`/fr/semaine/${CONSULTANT}/`);
    expect(urlFor(1, "de")).toBe(`/de/entreprise/${GUIDED}/`);
    expect(urlFor(2, "fr")).toBe(`/fr/entreprise/${GUIDED}/appel/`);
    expect(urlFor(3, "de")).toBe("/de/presentation/synthese/");
    for (let i = 0; i < SCRIPT.length; i++) expect(urlFor(i, "fr").endsWith("/")).toBe(true); // trailingSlash
    expect(urlFor(99, "fr")).toBe(urlFor(SCRIPT.length - 1, "fr"));
    expect(urlFor(-3, "fr")).toBe(urlFor(0, "fr"));
  });

  it("chaque étape après la première a son geste ; aucun geste ne note un retour d'appel (rien n'est enregistré)", () => {
    expect(SCRIPT[0].gesture).toBeNull();
    expect(SCRIPT.slice(1, 3).map((s) => (s.gesture?.kind === "tap" ? s.gesture.target : null))).toEqual([
      `ouvrir-${GUIDED}`,
      "preparer-appel",
    ]);
    expect(SCRIPT[3].gesture).toEqual({ kind: "open" });
    expect(SCRIPT.some((s) => s.gesture?.kind === "tap" && s.gesture.target.startsWith("retour-"))).toBe(false);
  });

  it("le dossier guidé existe : entreprise réelle, appel préparé, rang de la consultante fictive M1", () => {
    expect(curated.guides).toContain(GUIDED);
    expect((entreprises as Record<string, { nom: string }>)[GUIDED].nom).toBe("Société de Travaux Publics, Joseph Carron SA");
    expect(Object.keys(appels)).toContain(GUIDED);
    const m1 = Object.values(agences as Record<string, { id: string; consultants: { code: string; specialite: string }[] }>)
      .flatMap((a) => a.consultants.map((c) => ({ ...c, agence: a.id })))
      .find((c) => c.code === CONSULTANT);
    expect(m1).toMatchObject({ specialite: "batiment", agence: "martigny" });
    const list = (listes as Record<string, { par_agence: Record<string, { entreprises: string[] }> }>).batiment.par_agence.martigny;
    expect(list.entreprises).toContain(GUIDED);
  });

  it("les boutons visés portent leur attribut data-demo dans l'application", () => {
    expect(src("src/futur/CompanyCard.tsx")).toContain("data-demo={`ouvrir-${c.id}`}");
    expect(src("src/app/[lang]/(futur)/entreprise/[id]/page.tsx")).toContain('data-demo="preparer-appel"');
  });
});

describe("le pilote : geste, saut ou rien", () => {
  it("une flèche vers l'avant joue le geste ; tout le reste saute directement à l'état voulu", () => {
    expect(plan(0, 1)).toEqual({ kind: "gesture", to: 1 });
    expect(plan(2, 3)).toEqual({ kind: "gesture", to: 3 });
    expect(plan(2, 2)).toEqual({ kind: "none", to: 2 });
    expect(plan(null, 2)).toEqual({ kind: "jump", to: 2 }); // first display, or a gesture interrupted
    expect(plan(2, 0)).toEqual({ kind: "jump", to: 0 }); // backwards
    expect(plan(0, 3)).toEqual({ kind: "jump", to: 3 }); // skipping ahead
    expect(plan(3, 9)).toEqual({ kind: "none", to: 3 }); // bounded
  });

  it("retrouve l'étape d'une page ouverte à la main (reprise de la démo)", () => {
    expect(stepOfPath(`/fr/entreprise/${GUIDED}/appel`, "fr", 2)).toBe(2);
    expect(stepOfPath(`/fr/entreprise/${GUIDED}/appel/`, "fr", 0)).toBe(2);
    expect(stepOfPath(`/fr/entreprise/${GUIDED}/`, "fr", 3)).toBe(1);
    expect(stepOfPath("/fr/presentation/synthese/", "fr", 0)).toBe(3);
    expect(stepOfPath("/fr/carte/", "fr", 0)).toBeNull();
    expect(stepOfPath(`/de/semaine/${CONSULTANT}/`, "fr", 0)).toBeNull();
    expect(stepOfPath("", "fr", 0)).toBeNull();
  });
});

describe("le téléphone à l'échelle", () => {
  it("garde la largeur mobile de l'application (390 px) sous la barre d'état", () => {
    expect(SCREEN.width).toBe(390);
    expect(SCREEN.status + SCREEN.app).toBe(844);
    expect(FRAME.width).toBeGreaterThan(SCREEN.width);
  });

  it("met le téléphone à l'échelle de la place disponible, sans le déformer", () => {
    expect(fitScale(FRAME.width / 2, 5000)).toBeCloseTo(0.5);
    expect(fitScale(5000, FRAME.height)).toBeCloseTo(1);
    expect(fitScale(0, 0)).toBeGreaterThan(0);
    expect(fitScale(10000, 10000)).toBe(fitScale(20000, 20000)); // bounded: never larger than a legible maximum
  });

  it("écrit la barre d'état dans la couleur de la page (claire pour l'application, papier pour la synthèse)", () => {
    expect(isDark("oklch(1 0 0)")).toBe(false); // the app's white (Tailwind 4)
    expect(isDark("rgb(238, 234, 223)")).toBe(false); // paper
    expect(isDark("rgb(21, 23, 21)")).toBe(true); // graphite
    expect(isDark("#151715")).toBe(true);
    expect(isDark("oklch(18% 0.01 140)")).toBe(true);
    expect(isDark("")).toBe(false);
  });
});

describe("le mouvement", () => {
  it("n'utilise que la courbe et les trois durées de la présentation", () => {
    for (const t of Object.values(PHONE_MOTION)) {
      expect(t.ease).toEqual(EASE);
      expect(Object.values(DUR)).toContain(t.duration);
    }
  });
});
