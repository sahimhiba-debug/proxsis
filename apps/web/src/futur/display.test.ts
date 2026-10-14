import { describe, expect, it } from "vitest";
import entreprises from "@/data/demo/entreprises.json";
import metaJson from "@/data/demo/meta.json";
import type { Company } from "@/lib/types";
import { frenchSpaces, isRecent, longDay, phoneLine, phoneParts, reasonAward, shortWhy, timelinePoints, usageName, whyNow } from "./display";

// the demo data as the pages read it (@/lib/data is server-only)
const companies = entreprises as unknown as Record<string, Company>;
const meta = metaJson as unknown as { semaine: string };

describe("futurisme : affichage sans nouveau fait", () => {
  // Q17 (Hiba, 13.10.2026) : « Joseph Carron SA » en entier partout où c'est un titre ; sans sa forme juridique, une
  // entreprise se lit comme une personne. Le titre garde donc la forme juridique ; il retire la description avant la
  // virgule, celle d'après (quand la forme juridique est déjà là) et la succursale ; jamais un mot du nom.
  it("le titre d'une entreprise garde sa forme juridique : jamais un nom qui se lit comme une personne", () => {
    expect(usageName("Société de Travaux Publics, Joseph Carron SA")).toBe("Joseph Carron SA");
    expect(usageName("Theler AG, Bauunternehmung")).toBe("Theler AG");
    expect(usageName("Bitz travaux publics SA")).toBe("Bitz travaux publics SA");
    expect(usageName("MELLY CONSTRUCTIONS SA")).toBe("Melly Constructions SA");
    expect(usageName("Walpen AG Hoch- und Tiefbau")).toBe("Walpen AG Hoch- und Tiefbau");
    expect(usageName("RITHNER SA")).toBe("Rithner SA");
    expect(usageName("Ulrich Imboden AG")).toBe("Ulrich Imboden AG");
    expect(usageName("SA")).toBe("SA");
    expect(usageName("Entreprise Manenti, Farquet et Cie SA")).toBe("Entreprise Manenti, Farquet et Cie SA");
    expect(usageName("JM ROSSA SA")).toBe("JM Rossa SA");
    expect(usageName("ABI-NETTOYAGES Sàrl")).toBe("Abi-Nettoyages Sàrl");
    expect(usageName("Ascenseurs Schindler SA succursale de Sion")).toBe("Ascenseurs Schindler SA");
    expect(usageName("swisspro SR SA, succursale de Sion")).toBe("swisspro SR SA");
    for (const c of Object.values(companies)) {
      const t = usageName(c.nom);
      // every company keeps a legal form in its title when its legal name has one
      if (/\b(SA|AG|Sàrl|SARL|GmbH)\b/.test(c.nom)) expect(t, c.nom).toMatch(/\b(SA|AG|Sàrl|SARL|GmbH)\b/);
    }
  });

  it("la micro-frise a exactement autant de points que de marchés de la spécialité sur 52 semaines, pour chaque entreprise", () => {
    for (const c of Object.values(companies)) {
      const pts = timelinePoints(c, meta.semaine);
      expect(pts.length).toBe(c.n_52s);
      expect(pts.every((p) => p.x > 0 && p.x <= 1)).toBe(true);
    }
  });

  it("un signal est récent à moins de 14 jours, jamais dans le futur", () => {
    expect(isRecent("2026-09-22", "2026-10-05")).toBe(true);
    expect(isRecent("2026-09-21", "2026-10-05")).toBe(false);
    expect(isRecent("2026-10-06", "2026-10-05")).toBe(false);
  });

  it("« pourquoi maintenant » reprend mot pour mot une raison de l'export", () => {
    for (const c of Object.values(companies)) {
      const r = whyNow(c.raisons);
      if (r) expect(c.raisons).toContain(r);
    }
    expect(whyNow([])).toBeNull();
  });

  it("la phrase de la carte est un début mot pour mot de la raison de l'export", () => {
    for (const c of Object.values(companies)) {
      for (const lang of ["fr", "de"] as const) {
        const r = whyNow(c.raisons);
        const s = shortWhy(r, lang);
        if (r && s) expect(r[lang].startsWith(s)).toBe(true);
      }
    }
    const r = { code: "dernier_marche", fr: "Dernier marché il y a 54 jours : « X » (Y)", de: "Letzter Zuschlag vor 54 Tagen: «X» (Y)",
      court: { fr: "Dernier marché il y a 54 jours", de: "Letzter Zuschlag vor 54 Tagen" } };
    expect(shortWhy(r, "fr")).toBe("Dernier marché il y a 54 jours");
    expect(shortWhy(r, "de")).toBe("Letzter Zuschlag vor 54 Tagen");
    expect(shortWhy({ code: "marches_52s", fr: "21 marchés", de: "21 Aufträge" }, "fr")).toBe("21 marchés"); // no short form
  });

  it("l'annonce du dossier est le marché de la raison d'appeler, celui que cite la liste ; la date du lundi est écrite en toutes lettres", () => {
    const c = companies["ent-1ef761b229"];
    expect(reasonAward(c)?.date).toBe([...c.chronologie].map((s) => s.date).sort().at(-1));
    // a company whose latest contract is in another specialty: the dossier, the phone and the list cite the same one
    for (const x of Object.values(companies)) {
      const said = x.raisons.find((r) => r.code === "dernier_marche")?.fr ?? "";
      if (said) expect(said, x.nom).toContain(reasonAward(x)!.titre.trim().slice(0, 30));
    }
    expect(longDay("2026-10-05", "fr")).toBe("Lundi 5\u00a0octobre");
    expect(longDay("2026-10-05", "de")).toBe("Montag, 5.\u00a0Oktober");
  });

  it("la typographie française ne change que des espaces, jamais un mot ni un signe", () => {
    const text = "Estimation Proxsis, à confirmer avec vous : métiers « maçon » ; Quand le chantier démarre-t-il ?";
    const out = frenchSpaces(text, "fr");
    expect(out).toBe("Estimation Proxsis, à confirmer avec vous\u00a0: métiers «\u00a0maçon\u00a0» ; Quand le chantier démarre-t-il\u00a0?".replace(" ;", "\u00a0;"));
    expect(out.replace(/\u00a0/g, " ")).toBe(text);
    expect(frenchSpaces("Wann beginnt die Baustelle?", "de")).toBe("Wann beginnt die Baustelle?");
  });

  it("la phrase au téléphone : une phrase simple avec la date de l'avis, puis le titre publié, entier et exact, cité (B8)", () => {
    const frame = { fr: /^J'ai vu sur simap que vous avez remporté un marché publié le (\d\d\.\d\d\.\d{4})\u00a0: «\u00a0(.+)\u00a0»$/,
      de: /^Ich habe auf simap gesehen, dass Sie einen Auftrag gewonnen haben, publiziert am (\d\d\.\d\d\.\d{4}): «(.+)»$/ };
    for (const c of Object.values(companies)) {
      const last = reasonAward(c);
      for (const lang of ["fr", "de"] as const) {
        const m = phoneLine(c, lang)?.match(frame[lang]);
        expect(m, `${c.nom} ${lang} : ${phoneLine(c, lang)}`).toBeTruthy();
        expect(m![1]).toBe(`${last!.date.slice(8, 10)}.${last!.date.slice(5, 7)}.${last!.date.slice(0, 4)}`);
        // the title is the published one, whole: nothing cut, nothing added
        expect(m![2].replace(/\u00a0/g, " ")).toBe(lang === "fr" ? frenchSpaces(last!.titre.trim(), "fr").replace(/\u00a0/g, " ") : last!.titre.trim());
        expect(phoneParts(c, lang)!.title).toBe(last!.titre.trim());
      }
    }
    const carron = companies["ent-1ef761b229"];
    expect(phoneParts(carron, "fr")).toEqual({ lead: "J'ai vu sur simap que vous avez remporté un marché publié le 12.08.2026 :",
      title: "94 Le Cotterg - Les Chenevaires / Restructuration routière avec revêtement bitumineux" });
  });
});


describe("consortiums : les membres seulement quand la publication les nomme", () => {
  it("sépare les membres nommés, signale un consortium sans membres, laisse une entreprise seule", async () => {
    const { consortiumMembers } = await import("./display");
    expect(consortiumMembers("Consortium PraderLosinger – Implenia")).toEqual(["PraderLosinger", "Implenia"]);
    expect(consortiumMembers("ARGE Bächler + Güttinger AG / Volken Group")).toEqual(["Bächler + Güttinger AG", "Volken Group"]);
    expect(consortiumMembers("Consortium des entreprises du Groupe JPF - Michel Démolition SA & Bernard Torrent SA"))
      .toEqual(["Groupe JPF", "Michel Démolition SA", "Bernard Torrent SA"]);
    expect(consortiumMembers("Consortium Galerie du Fregnoley")).toEqual([]);
    expect(consortiumMembers("Société de Travaux Publics, Joseph Carron SA")).toBeNull();
  });
});
