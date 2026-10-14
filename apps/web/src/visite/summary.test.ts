import { describe, expect, it } from "vitest";
import appels from "@/data/demo/appels.json";
import entreprises from "@/data/demo/entreprises.json";
import curated from "@/data/presentation/dossiers.json";
import lundis from "@/data/presentation/lundis.json";
import type { CallPrep, Company } from "@/lib/types";
import type { MondaysData } from "@/presentation/mondayData";
import { visitDossier, type Curated } from "./dossier";
import { initialVisit, reduce } from "./state";
import { emailText, summaryRows } from "./summary";

/** The words, with the no-break spaces of French typography made ordinary. */
const plain = (x: string) => x.replace(/\u00a0/g, " ");

const companies = entreprises as unknown as Record<string, Company>;
const calls = appels as unknown as Record<string, CallPrep>;
const reading: Record<string, Curated> = curated.dossiers;
const CARRON = "ent-1ef761b229";
const dossiers = { [CARRON]: visitDossier(CARRON, companies[CARRON], calls[CARRON], reading[CARRON], curated.rejeu) };
const base = { lang: "fr" as const, dossiers, exampleCompany: CARRON, mondays: lundis as unknown as MondaysData };

describe("visite : « Votre premier lundi »", () => {
  it("sans aucun choix, tout est marqué « exemple préparé », jamais présenté comme sa décision", () => {
    const rows = summaryRows({ ...base, s: initialVisit() });
    expect(rows.map((r) => r.key)).toEqual(["entreprise", "question", "date", "seuil", "critere"]);
    expect(rows.every((r) => r.example)).toBe(true);
    expect(rows[0].value).toContain("À appeler");
    expect(rows[2].value).toContain("02.03.2026");
    expect(rows[3].value).toContain("44 journées");
  });

  it("ses choix sont les siens ; une piste écartée ne garde pas de question d'appel", () => {
    let s = reduce(initialVisit(), { type: "decide", company: CARRON, entry: { decision: "ecarter", motif: "client" } });
    s = reduce(s, { type: "monday", value: "2025-11-03" });
    s = reduce(s, { type: "pilot", value: { indicator: "utiles", threshold: 4 } });
    const rows = summaryRows({ ...base, s });
    const by = Object.fromEntries(rows.map((r) => [r.key, r]));
    expect(by.entreprise).toMatchObject({ example: false });
    expect(by.entreprise.value).toContain("déjà client");
    expect(plain(by.question.value)).toBe("Question non retenue : la piste est écartée.");
    expect(by.date.example).toBe(false);
    expect(plain(by.date.value)).toBe("Lundi 03.11.2025 : 4 sur 10 ont remporté un nouveau marché public dans les 8 semaines.");
    expect(by.critere.value).toBe("Nous continuerons si au moins 4 appels préparés sur 10 mènent à une conversation utile.");
    expect(by.seuil.example).toBe(true);
  });

  it("l'e-mail ne porte aucun montant en francs, sauf s'il le demande", () => {
    const rows = summaryRows({ ...base, s: initialVisit() });
    expect(emailText(rows, "fr", false).body).not.toMatch(/CHF/);
    expect(emailText(rows, "fr", true).body).toMatch(/CHF/);
    expect(emailText(rows, "fr", false).subject).toBe("Proxsis — mon premier lundi");
  });
});
