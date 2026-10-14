import { readFileSync } from "node:fs";
import { join } from "node:path";
import { expect, test } from "@playwright/test";

// The main screens of the application and of the visit (the list below), in French and in German, compared pixel by pixel with its
// reference (playwright.visuel.config.ts). The clock is fixed to the morning after the demo week's Monday; with
// VISUEL_DECALAGE_JOURS=n it runs n days later, and the screens must stay identical (nothing may drift with time: the
// screens count from the list's Monday, never from the computer's clock).
const COMPANY = "ent-1ef761b229"; // Joseph Carron SA, the company of the demo path
const SCREENS: [name: string, path: string][] = [
  ["accueil", "/"], // the first screen, the one the director sees first (missing until 07.10.2026)
  ["semaines", "/semaine/"],
  ["ma-semaine", "/semaine/M1/"],
  ["dossier", `/entreprise/${COMPANY}/`],
  ["appel", `/entreprise/${COMPANY}/appel/`],
  ["candidats", `/entreprise/${COMPANY}/candidats/`],
  ["carte", "/carte/"],
  ["fin-de-mission", "/redeploiement/"],
  ["conformite", "/conformite/"],
  ["agences", "/agence/"],
  ["agence-martigny", "/agence/martigny/"],
  ["roi", "/roi/"],
  ["mesures", "/mesures/"],
  ["presentation", "/presentation/"],
  ["notes", "/presentation/notes/"],
  ["synthese", "/presentation/synthese/"],
  ["direction", "/presentation/direction/"],
];
const DEMO_MORNING = Date.parse("2026-10-06T08:00:00+02:00");
// long lists (conformité: 35 000 px on a phone) are compared on their first 8 000 px: the references stay small enough
// to live in the repository; the content of the whole list is checked by the end-to-end tests
const MAX_HEIGHT = 8_000;
const DAY = 86_400_000;
const shift = Number(process.env.VISUEL_DECALAGE_JOURS ?? 0);

// The references depend on the browser's text rendering, and the system's Chrome updates itself: before comparing
// pixels, check that this is the browser that took them (review 1, I9). After a Chrome update, look at the new
// screens, then regenerate the references (`npm run visuel -- --update-snapshots`) and write the new version here.
const REFERENCE_BROWSER = readFileSync(join(__dirname, "references", process.platform, "NAVIGATEUR.txt"), "utf8").trim();
test.beforeAll(async ({ browser }) => {
  const major = (v: string) => v.split(".")[0];
  if (major(browser.version()) !== major(REFERENCE_BROWSER)) {
    throw new Error(`références prises avec Chrome ${REFERENCE_BROWSER}, ce navigateur est Chrome ${browser.version()} : `
      + "vérifier les écrans, puis régénérer les références et mettre à jour references/<plateforme>/NAVIGATEUR.txt");
  }
});

for (const lang of ["fr", "de"] as const) {
  for (const [name, path] of SCREENS) {
    test(`${lang} · ${name}`, async ({ page }) => {
      await page.clock.setFixedTime(DEMO_MORNING + shift * DAY);
      // the screens never depend on the network: map tiles, if any, are refused like in a room without Wi-Fi
      await page.route(/^https?:\/\/(?!localhost)/, (r) => r.abort());
      await page.goto(`/${lang}${path}`, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForFunction(() =>
        document.getAnimations().every((a) => a.playState !== "running" || a.effect?.getTiming().iterations === Infinity));
      const { width, height } = await page.evaluate(() => ({ width: window.innerWidth, height: document.documentElement.scrollHeight }));
      // « Chaque matin, en direct de simap » changes every working day by design: it is masked, the rest must not move. Iris's
      // 3D image (WebGL) varies by a few pixels between two runs of the same machine: her canvas is masked too, her
      // sentence and her button are compared (her look is checked by e2e/guide.spec.ts and by eye)
      await expect(page).toHaveScreenshot(`${lang}-${name}.png`,
        { fullPage: true, clip: { x: 0, y: 0, width, height: Math.min(height, MAX_HEIGHT) },
          mask: [page.getByTestId("chaque-matin"), page.locator(".v-mascotte canvas")] });
    });
  }
}
