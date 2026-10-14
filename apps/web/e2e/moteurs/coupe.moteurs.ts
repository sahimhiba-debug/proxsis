import {  expect, test } from "@playwright/test";
import { ouvrir, settled } from "../attente";
import { coupes, PAGES, sousLaBarre } from "../coupe";
import { openStep, STEP_IDS } from "../etape";

// Q18 (Hiba, 13.10.2026) : « plus aucun texte coupé au téléphone », aussi dans le moteur de Safari (iPhone 14, 390 px),
// sur la version statique que reçoit le directeur : chaque page de l'application, chaque temps de la visite, FR et DE.
// Deux tests par langue, l'application puis la visite : d'un seul tenant, ils dépassaient le délai dans WebKit sur la CI
// (délai dépassé, pas un texte coupé).
for (const lang of ["fr", "de"]) {
  test(`aucun texte coupé au téléphone (application, ${lang.toUpperCase()})`, async ({ page }, info) => {
    test.skip(!info.project.name.endsWith("-telephone"), "le téléphone seulement");
    test.setTimeout(900_000);
    await page.emulateMedia({ reducedMotion: "reduce" });
    const found: string[] = [];
    for (const path of PAGES) {
      await ouvrir(page, `/${lang}${path}`);
      await settled(page);
      for (const c of [...await coupes(page), ...await sousLaBarre(page)]) found.push(`${lang}${path} · ${c}`);
    }
    expect(found, found.join("\n")).toEqual([]);
  });
  test(`aucun texte coupé au téléphone (visite, ${lang.toUpperCase()})`, async ({ page }, info) => {
    test.skip(!info.project.name.endsWith("-telephone"), "le téléphone seulement");
    test.setTimeout(900_000);
    await page.emulateMedia({ reducedMotion: "reduce" });
    const found: string[] = [];
    await ouvrir(page, `/${lang}/presentation/`);
    for (let i = 0; i < STEP_IDS.length; i++) {
      await openStep(page, i);
      await settled(page);
      for (const c of await coupes(page)) found.push(`${lang} visite ${STEP_IDS[i]} · ${c}`);
    }
    expect(found, found.join("\n")).toEqual([]);
  });
}
