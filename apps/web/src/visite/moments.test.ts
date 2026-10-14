import { describe, expect, it } from "vitest";
import claimsJson from "@/data/demo/claims.json";
import entreprisesJson from "@/data/demo/entreprises.json";
import dossiers from "@/data/presentation/dossiers.json";
import suivant from "@/data/presentation/lundi_suivant.json";
import lundis from "@/data/presentation/lundis.json";
import { fmtDate } from "@/lib/dates";
import { forbiddenTerms } from "@/presentation/vocabulary";
import { visitMoments } from "./moments";

// The new moments of the visit (brief of 07.10.2026, § 3.2 to 3.4): every figure of the files is the one of its line
// of CLAIMS.md (claims.json, re-exported from it), and fits the other data of the visit.
const claims = claimsJson as Record<string, { affirmation: string; valeur: string; donnees: string; commande: string; fichier: string; limite: string }>;
const companies = entreprisesJson as unknown as Record<string, { chronologie: { date: string; url_simap: string }[] }>;
const { week, accelerating, facts } = visitMoments();

function allStrings(x: unknown): string[] {
  if (typeof x === "string") return [x];
  if (Array.isArray(x)) return x.flatMap(allStrings);
  if (x && typeof x === "object") return Object.values(x).flatMap(allStrings);
  return [];
}
// the texts meant for the screen, per language (sources' names, labels, rules and nuances)
const shown = (x: unknown, lang: "fr" | "de"): string[] =>
  x && typeof x === "object" && !Array.isArray(x)
    ? Object.entries(x).flatMap(([k, v]) => (k === lang && typeof v === "string" ? [v] : shown(v, lang)))
    : Array.isArray(x) ? x.flatMap((v) => shown(v, lang)) : [];

describe("« La semaine du … » (brief du 07.10.2026, § 3.3 ; questionnaire, A3 ; CLAIMS PRES-SEMAINE-1)", () => {
  const line = claims["PRES-SEMAINE-1"];

  it("les nombres sont ceux de la ligne du registre, mot pour mot", () => {
    expect(line.donnees).toBe("RÉEL");
    expect(line.commande).toBe("proxsis moments-presentation");
    expect(line.fichier).toContain("apps/web/src/data/presentation/cette_semaine.json");
    const { lues, retenues } = week;
    expect(line.valeur).toContain(`${lues.total} publications lues (${lues.simap} adjudications simap, ${lues.bulletin_officiel} demandes d'autorisation du Bulletin officiel)`);
    expect(line.valeur).toContain(`${retenues.total} retenues (${retenues.simap} adjudications simap, ${retenues.bulletin_officiel} du Bulletin officiel)`);
    expect(line.valeur).toContain(`${week.appels} appels`);
    expect(line.affirmation).toContain(`du ${fmtDate(week.semaine.du)} au ${fmtDate(week.semaine.au)}`);
    expect(line.limite).toContain(fmtDate(week.fin_des_donnees.simap));
    expect(line.limite).toContain(fmtDate(week.fin_des_donnees.bulletin_officiel));
  });

  it("c'est la semaine du premier lundi de la visite, ses dix appels, et rien après la fin des données", () => {
    expect(week.lundi).toBe(dossiers.rejeu);
    expect(week.appels).toBe(dossiers.dix.length);
    expect(week.appels).toBe(10);
    expect(week.liste.fichier).toBe(dossiers.liste_gelee);
    expect(week.fin_des_donnees.simap).toBe(lundis.source.fin_des_donnees);
    expect(week.fin_des_donnees.simap).toBe(suivant.fin_des_donnees);
    // Monday to Sunday, the last week before the list that both sources hold whole (A3): it ends before the end of
    // the simap data and of the Bulletin officiel import, and the week after it is cut by them
    const day = (iso: string) => Date.parse(`${iso}T00:00:00Z`);
    expect(new Date(day(week.semaine.du)).getUTCDay()).toBe(1);
    expect(day(week.semaine.au) - day(week.semaine.du)).toBe(6 * 86_400_000);
    expect(week.semaine.au < week.fin_des_donnees.simap && week.semaine.au < week.fin_des_donnees.bulletin_officiel).toBe(true);
    const nextEnd = new Date(day(week.semaine.au) + 7 * 86_400_000).toISOString().slice(0, 10);
    expect(nextEnd > week.fin_des_donnees.simap || nextEnd > week.fin_des_donnees.bulletin_officiel).toBe(true);
    expect(nextEnd < week.lundi).toBe(true);
  });

  it("la phrase du brief, avec ces nombres, n'a aucun mot à éviter", () => {
    const fr = `La semaine du 21 au 27 septembre 2026, Proxsis a lu ${week.lues.total} publications, en a retenu ${week.retenues.total}, et vous prépare ${week.appels} appels.`;
    expect(fr).toBe("La semaine du 21 au 27 septembre 2026, Proxsis a lu 130 publications, en a retenu 15, et vous prépare 10 appels.");
    expect(week.semaine).toEqual({ du: "2026-09-21", au: "2026-09-27" });
    expect(forbiddenTerms(fr, "fr")).toEqual([]);
    for (const lang of ["fr", "de"] as const) expect(shown(week.sources, lang).flatMap((s) => forbiddenTerms(s, lang))).toEqual([]);
    expect(week.sources.bulletin_officiel.mention.fr).toBe("relevé manuel pendant le prototype");
    expect(week.sources.simap.mention).toBe(lundis.source.mention);
  });
});

describe("« Celles qui accélèrent » (brief du 07.10.2026, § 3.4 ; CLAIMS REEL-SURPRISE)", () => {
  const line = claims["REEL-SURPRISE"];

  it("les taux sont ceux du registre, avec sa nuance", () => {
    const { accelerent: a, hors_des_dix: h, perimetre: p } = accelerating;
    expect(line.valeur).toContain(`« activité qui bondit » ${a.affiche.fr} (${a.cas} cas repérés) contre ${h.affiche.fr} de base hors top ${p.dix}`);
    expect([a.affiche.fr, a.cas, h.affiche.fr]).toEqual(["38,3 %", 298, "17,3 %"]);
    expect(a.affiche.de).toBe(a.affiche.fr);
    expect(line.limite).toContain("taux descriptifs");
    expect(line.limite).toContain("non indépendants");
    expect(accelerating.nuance.fr).toContain("une même entreprise peut compter plusieurs semaines");
    // the displayed rates round the measured ones
    expect(`${(100 * a.taux).toFixed(1).replace(".", ",")} %`).toBe(a.affiche.fr);
    expect(`${(100 * h.taux).toFixed(1).replace(".", ",")} %`).toBe(h.affiche.fr);
  });

  it("ce sont les lundis de « Une date » : même mesure, mêmes semaines", () => {
    const p = accelerating.perimetre;
    expect([p.semaines, p.premiere, p.derniere]).toEqual([lundis.mesure.semaines, lundis.mesure.premiere, lundis.mesure.derniere]);
    expect(p.dix).toBe(lundis.regle.k);
    expect(p.region).toEqual(lundis.regle.region);
    expect(claims["REEL-SPEC-BAT"].affirmation).toContain(`${p.semaines} semaines (${p.premiere} à ${p.derniere})`);
  });

  it("aucun mot à éviter ; l'allemand reste à relire", () => {
    for (const lang of ["fr", "de"] as const) {
      expect([...shown(accelerating.regle, lang), ...shown(accelerating.nuance, lang)].flatMap((s) => forbiddenTerms(s, lang))).toEqual([]);
    }
    expect(accelerating.de_a_relire).toBe(true);
  });
});

describe("« Plusieurs faits vont dans le même sens » (brief du 07.10.2026, § 3.2)", () => {
  it("seulement les trois dossiers guidés, chacun avec sa ligne du registre", () => {
    expect(Object.keys(facts.dossiers).sort()).toEqual([...dossiers.guides].sort());
    expect(Object.values(facts.dossiers).map((d) => d.claims).sort()).toEqual(["PRES-BITZ-1", "PRES-CARRON-1", "PRES-THELER-1"]);
  });

  it("chaque fait est dans sa ligne : date, nombre de marchés, commune ; rien de plus", () => {
    for (const [id, d] of Object.entries(facts.dossiers)) {
      const line = claims[d.claims];
      expect(line.donnees).toBe("RÉEL");
      const last = d.faits.find((f) => f.type === "marche" && f.dernier)!;
      expect(line.valeur.startsWith(`${d.marches_52s.nombre} ; dernier publié le ${fmtDate(last.date)} (`)).toBe(true);
      for (const f of d.faits) {
        expect(line.valeur).toContain(fmtDate(f.date));
        if (f.type === "marche") {
          // a published award of the company, as the application lists it
          expect(companies[id].chronologie.some((c) => c.date === f.date && c.url_simap === f.url)).toBe(true);
          if (f.adjudicateur) expect(line.valeur).toContain(f.adjudicateur.fr);
          if (f.objet) expect(line.valeur).toContain(f.objet.fr);
          if (f.titre_original) expect(line.valeur).toContain(`« ${f.titre_original} »`);
        } else {
          expect(line.valeur).toContain(f.commune);
          expect(Object.keys(f).sort()).toEqual(["commune", "date", "libelle", "role", "source", "type"]);
        }
      }
      const permits = d.faits.filter((f) => f.type === "demande_autorisation");
      if (permits.length) expect(line.valeur).toContain(`${permits.length} demandes d'autorisation où elle est **auteure des plans**`);
      const dates = d.faits.map((f) => f.date);
      expect(dates).toEqual([...dates].sort().reverse());
    }
    const theler = Object.values(facts.dossiers).find((d) => d.claims === "PRES-THELER-1")!;
    const ng24 = theler.faits.filter((f) => f.type === "marche" && f.serie === "NG24").map((f) => fmtDate(f.date)).reverse();
    expect(claims["PRES-THELER-1"].valeur).toContain(`${ng24.length} tronçons NG24 attribués, publiés les ${ng24.slice(0, -1).join(", ")} et ${ng24.at(-1)}`);
  });

  it("le Bulletin officiel : relevé manuel, le rôle de l'entreprise seulement, jamais un particulier", () => {
    expect(facts.sources.bulletin_officiel.mention).toEqual({ fr: "relevé manuel pendant le prototype", de: "während des Prototyps von Hand erfasst" });
    expect(facts.sources.simap.mention).toBe(lundis.source.mention);
    const text = JSON.stringify(facts);
    expect(text).not.toMatch(/particulier|requérant|requerant|\[masqué\]/i);
    for (const lang of ["fr", "de"] as const) {
      expect(shown(facts.dossiers, lang).flatMap((s) => forbiddenTerms(s, lang))).toEqual([]);
      expect(shown(facts.sources, lang).flatMap((s) => forbiddenTerms(s, lang))).toEqual([]);
    }
    expect(facts.de_a_relire).toBe(true);
    expect(allStrings(facts).every((s) => !s.includes("/pdf"))).toBe(true); // no link to a published request
  });
});
