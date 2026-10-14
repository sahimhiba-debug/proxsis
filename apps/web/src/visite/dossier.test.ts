import { describe, expect, it } from "vitest";
import curated from "@/data/presentation/dossiers.json";
import territoire from "@/data/presentation/territoire.json";
import { phoneLine } from "@/futur/display";
import appels from "@/data/demo/appels.json";
import entreprises from "@/data/demo/entreprises.json";
import type { CallPrep, Company } from "@/lib/types";
import { visitDossier, type Curated } from "./dossier";

const reading: Record<string, Curated> = curated.dossiers;
// the export, checked against its schema in src/lib/schema.test.ts (lib/data is for the server only)
const companies = entreprises as unknown as Record<string, Company>;
const calls = appels as unknown as Record<string, CallPrep>;
const ids = Object.keys(territoire.entreprises);

describe("visite : le dossier d'une entreprise de la carte", () => {
  it("chaque entreprise de la carte a son dossier, fondé sur une publication parue avant le lundi de la liste", () => {
    for (const id of ids) {
      const d = visitDossier(id, companies[id], calls[id], reading[id], curated.rejeu);
      expect(d.publication.date < curated.rejeu, id).toBe(true);
      expect(d.publication.url.startsWith("https://www.simap.ch/"), id).toBe(true);
      expect(d.verifier.fr.length, id).toBeGreaterThan(0);
    }
  });

  it("les dossiers guidés gardent leur lecture préparée ; les autres ouvrent l'appel sur le seul fait publié", () => {
    const carron = visitDossier("ent-1ef761b229", companies["ent-1ef761b229"], calls["ent-1ef761b229"], reading["ent-1ef761b229"], curated.rejeu);
    expect(carron.guide).toBe(true);
    expect(carron.question).toEqual(reading["ent-1ef761b229"].appel.question);
    expect(carron.publication.url).toBe(reading["ent-1ef761b229"].annonce_url);
    const other = ids.find((id) => !reading[id])!;
    const d = visitDossier(other, companies[other], calls[other], undefined, curated.rejeu);
    expect(d.guide).toBe(false);
    expect(d.question.fr.startsWith(phoneLine(companies[other], "fr")!)).toBe(true);
    expect(d.question.fr).toContain(d.publication.titre.slice(0, 20));
  });
});
