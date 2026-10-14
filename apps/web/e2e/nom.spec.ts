import { expect, test } from "@playwright/test";

// The built pages, as a visitor reads them (visible text, tab title, installable app's manifest): Proxsis, its
// signature and the prototype mention, never the old name. French and German.
const PAGES = ["/semaine/M1/", "/entreprise/ent-1ef761b229/", "/entreprise/ent-1ef761b229/appel/", "/carte/", "/redeploiement/",
  "/conformite/", "/agence/martigny/", "/mesures/", "/roi/", "/presentation/", "/presentation/notes/", "/", "/une-page/"];
const SIGNATURE = { fr: "La prochaine entreprise à appeler.", de: "Das nächste Unternehmen, das Sie anrufen." };

test("Proxsis partout, jamais l'ancien nom (FR et DE)", async ({ page, request }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  const found: string[] = [];
  for (const lang of ["fr", "de"] as const) {
    for (const path of PAGES) {
      await page.goto(`/${lang}${path}`);
      const text = `${await page.title()}\n${await page.locator("body").innerText()}`;
      if (/flex[\s-]?radar/i.test(text)) found.push(`/${lang}${path}`);
      expect(await page.title(), `/${lang}${path}`).toContain("Proxsis");
    }
    await page.goto(`/${lang}/semaine/M1/`);
    await expect(page.getByText(SIGNATURE[lang]).first()).toBeVisible();
  }
  expect(found).toEqual([]);
  const manifest = await (await request.get("/manifest.webmanifest")).json();
  expect(manifest.name).toBe("Proxsis");
  // installed on a phone: full screen, on the consultant's application (not on the director's first screen)
  expect(manifest.display).toBe("standalone");
  expect(manifest.start_url).toBe("/fr/application/");
  expect(JSON.stringify(manifest)).not.toMatch(/flex[\s-]?radar/i);
});
