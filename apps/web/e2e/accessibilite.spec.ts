import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { settled } from "./attente";
import { openStep, STEP_IDS } from "./etape";

// Accessibility (axe-core, every rule, every impact, contrast included): no violation at all, on every page of the
// application, every step of the presentation (everything revealed), the presenter's notes and the phone demo, in
// French and in German, on a phone and on a computer.
const PAGES = ["/semaine/M1/", "/semaine/", "/entreprise/ent-1ef761b229/", "/entreprise/ent-1ef761b229/appel/",
  "/entreprise/ent-1ef761b229/candidats/", "/carte/", "/redeploiement/", "/conformite/", "/agence/", "/agence/martigny/",
  "/roi/", "/mesures/", "/presentation/synthese/", "/presentation/preuves/", "/presentation/questions/", "/", "/une-page/",
  "/presentation/equipe/", "/presentation/technique/", "/presentation/feuille-de-route/", "/presentation/notes/",
  "/presentation/telephone/"];

async function violations(page: Page, where: string): Promise<string[]> {
  const { violations } = await new AxeBuilder({ page }).analyze();
  return violations.map((v) => `${where} : ${v.id} (${v.impact}) — ${v.nodes.length} élément(s) : ${v.nodes[0]?.target.join(" ")}`);
}

for (const [device, size] of [["téléphone", null], ["ordinateur", { width: 1440, height: 900 }]] as const) {
  for (const lang of ["fr", "de"]) {
    test(`aucune violation d'accessibilité, ${lang.toUpperCase()}, ${device}`, async ({ page }, info) => {
      test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
      test.setTimeout(300_000);
      if (size) await page.setViewportSize(size);
      // contrast is measured on the settled screen, not halfway through a fade (the presentation follows this setting)
      await page.emulateMedia({ reducedMotion: "reduce" });
      const problems: string[] = [];
      for (const path of PAGES) {
        await page.goto(`/${lang}${path}`);
        await settled(page);
        problems.push(...(await violations(page, `${lang}${path}`)));
      }
      await page.goto(`/${lang}/presentation/`);
      for (let step = 0; step < STEP_IDS.length; step++) {
        await openStep(page, step);
        await settled(page);
        problems.push(...(await violations(page, `${lang} présentation, ${STEP_IDS[step]}`)));
      }
      expect(problems, problems.join("\n")).toEqual([]);
    });
  }
}

test("pages légères sur téléphone", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  for (const path of ["/fr/semaine/M1/", "/fr/conformite/"]) {
    await page.goto(path, { waitUntil: "networkidle" });
    const html = await page.content();
    expect(html.length, `${path} : HTML ${html.length} octets`).toBeLessThan(1_500_000);
  }
});
