import { expect, test } from "@playwright/test";
import { settled } from "./attente";
import { coupes, PAGES, sousLaBarre, WIDTHS } from "./coupe";
import { openStep, STEP_IDS } from "./etape";

// Q18 (Hiba, 13.10.2026) : « plus aucun texte coupé au téléphone ». Sur chaque page de l'application et chaque temps de
// la visite, à 360, 375 et 390 px, en français et en allemand (mesures : coupe.ts).
test("aucun texte coupé au téléphone dans l'application (360, 375 et 390 px, FR et DE)", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  test.setTimeout(600_000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  const found: string[] = [];
  for (const size of WIDTHS) {
    await page.setViewportSize(size);
    for (const lang of ["fr", "de"]) {
      for (const path of PAGES) {
        await page.goto(`/${lang}${path}`);
        await settled(page);
        for (const c of [...await coupes(page), ...await sousLaBarre(page)]) found.push(`${size.width} px ${lang}${path} · ${c}`);
      }
    }
  }
  expect(found, found.join("\n")).toEqual([]);
});

test("aucun texte coupé au téléphone dans la visite (360, 375 et 390 px, FR et DE, chaque temps)", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  test.setTimeout(600_000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  const found: string[] = [];
  for (const size of WIDTHS) {
    await page.setViewportSize(size);
    for (const lang of ["fr", "de"]) {
      await page.goto(`/${lang}/presentation/`);
      for (let i = 0; i < STEP_IDS.length; i++) {
        await openStep(page, i);
        await settled(page);
        for (const c of await coupes(page)) found.push(`${size.width} px ${lang} ${STEP_IDS[i]} · ${c}`);
      }
    }
  }
  expect(found, found.join("\n")).toEqual([]);
});
