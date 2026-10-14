import { describe, expect, it } from "vitest";
import metaJson from "@/data/demo/meta.json";
import propositionsJson from "@/data/demo/propositions.json";
import territoire from "@/data/presentation/territoire.json";
import { fmtDate } from "@/lib/dates";
import { getDict } from "@/lib/i18n";
import type { NeedProposals } from "@/lib/types";
import { proposer as build } from "./proposer";

// the demo data as the visit's server page reads it (@/lib/data is server-only)
const proposals = propositionsJson as unknown as Record<string, NeedProposals[]>;
const metiers = (metaJson as unknown as { metiers: Record<string, { fr: string; de: string }> }).metiers;
const contactFrom = { fr: getDict("fr").candidates.contactFrom, de: getDict("de").candidates.contactFrom };
const proposer = (id: string) => build(proposals[id] ?? [], metiers, contactFrom);

const CARRON = "ent-1ef761b229";

describe("« Qui proposer ? » (brief du 07.10.2026, § 3.1)", () => {
  it("trois intérimaires fictifs, ceux de l'application, dans son ordre, avec ses propres raisons", () => {
    const w = proposer(CARRON)!;
    const need = proposals[CARRON].find((n) => n.propositions.length >= 3)!;
    expect(need.fictif).toBe(true);
    expect(w.interimaires.map((x) => x.id)).toEqual(need.propositions.slice(0, 3).map((p) => p.candidate_id));
    for (const [i, x] of w.interimaires.entries()) {
      const p = need.propositions[i];
      expect(x.permis).toBe(p.permis_travail);
      // the availability and the distance are those the application already says, word for word
      expect(p.raisons_fr).toContain(`Disponible dès le ${fmtDate(x.dispo)}`);
      expect(p.raisons_fr.some((r) => r.startsWith(`À ${Math.round(x.km)} km`))).toBe(true);
    }
  });

  it("l'obligation d'annonce : seulement si le poste y est soumis, avec les mots de l'application", () => {
    const w = proposer(CARRON)!;
    const need = proposals[CARRON].find((n) => n.propositions.length >= 3)!;
    expect(Boolean(w.contactLine)).toBe(Boolean(need.annonce?.annonce_requise));
    if (w.contactLine) {
      expect(w.contactLine.fr).toBe(`Poste soumis à l'obligation d'annonce : contact possible dès le ${fmtDate(w.contactDes)}`);
      expect(need.propositions[0].raisons_fr.join(" ")).toContain(`contact possible dès le ${fmtDate(w.contactDes)}`);
    }
  });

  it("aucun nom de personne : un numéro d'intérimaire fictif, au plus trois par entreprise de la carte", () => {
    for (const id of Object.keys(territoire.entreprises)) {
      const w = proposer(id);
      if (!w) continue;
      expect(w.interimaires.length).toBeLessThanOrEqual(3);
      for (const x of w.interimaires) expect(x.id).toMatch(/^cand-\d+$/);
    }
  });
});
