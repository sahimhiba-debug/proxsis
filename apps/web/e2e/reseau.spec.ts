import { expect, test } from "@playwright/test";
import { openStep, STEP_IDS } from "./etape";

// No call outside the site while the demo runs: every page of the application, every step of the presentation
// (everything revealed) and the phone demo, in French and in German, are opened while every request is recorded; not one
// may leave localhost (fonts, data and scripts are in the build). The offline runs block such requests; this test
// shows there are none to block. Links to simap.ch are only followed when someone clicks them.
const PAGES = ["/", "/semaine/M1/", "/semaine/", "/entreprise/ent-1ef761b229/", "/entreprise/ent-1ef761b229/appel/",
  "/entreprise/ent-1ef761b229/candidats/", "/carte/", "/redeploiement/", "/conformite/", "/agence/", "/agence/martigny/",
  "/roi/", "/mesures/", "/presentation/synthese/", "/presentation/preuves/", "/presentation/questions/", "/une-page/",
  "/presentation/equipe/", "/presentation/technique/", "/presentation/feuille-de-route/", "/presentation/notes/",
  "/presentation/telephone/"];

test("aucune requête hors du site, sur toutes les pages et toutes les étapes, FR et DE", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  test.setTimeout(300_000);
  const outside = new Set<string>();
  let seen = 0;
  page.on("request", (r) => {
    seen++;
    const url = new URL(r.url());
    if (!["localhost", "127.0.0.1"].includes(url.hostname) && !["data:", "blob:"].includes(url.protocol)) outside.add(r.url());
  });
  for (const lang of ["fr", "de"]) {
    for (const path of PAGES) {
      await page.goto(path === "/" ? "/" : `/${lang}${path}`, { waitUntil: "networkidle" });
    }
    await page.goto(`/${lang}/presentation/`);
    for (let step = 0; step < STEP_IDS.length; step++) {
      await openStep(page, step, { waitUntil: "networkidle" });
    }
  }
  expect([...outside]).toEqual([]);
  expect(seen).toBeGreaterThan(100); // the recording worked
});
