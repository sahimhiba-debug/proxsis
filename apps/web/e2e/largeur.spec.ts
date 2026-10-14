import { expect, test } from "@playwright/test";
import { settled } from "./attente";
import { openStep, STEP_IDS } from "./etape";

// No page of the application scrolls sideways on a narrow phone, in French or in German (a long German word, a mention
// that does not wrap, a grid track sized by its content would push the page).
const PAGES = ["/semaine/M1/", "/entreprise/ent-1ef761b229/", "/entreprise/ent-1ef761b229/appel/", "/entreprise/ent-1ef761b229/candidats/",
  "/carte/", "/redeploiement/", "/conformite/", "/agence/", "/agence/martigny/", "/roi/", "/mesures/", "/", "/semaine/", "/presentation/synthese/",
  "/presentation/preuves/", "/presentation/questions/", "/presentation/equipe/", "/presentation/technique/", "/presentation/feuille-de-route/", "/une-page/"];

test("aucune page ne défile de côté au téléphone (320 et 390 px, FR et DE)", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  test.setTimeout(240_000);
  const wide: string[] = [];
  for (const w of [320, 390]) {
    await page.setViewportSize({ width: w, height: 800 });
    for (const lang of ["fr", "de"]) {
      for (const path of PAGES) {
        await page.goto(`/${lang}${path}`);
        const sw = await page.evaluate(() => document.documentElement.scrollWidth);
        if (sw > w) wide.push(`${w} px ${lang}${path} : +${sw - w} px`);
      }
    }
  }
  expect(wide, wide.join("\n")).toEqual([]);
});

// The presentation opened on a phone (from a link): no step pushes the page sideways either, and nothing of a scene runs
// under the mentions and the navigation (the phone of act 3 did, by 445 to 652 px).
test("la présentation ne défile pas de côté sur un téléphone et rien ne passe sous la navigation (320 et 390 px, FR et DE)", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  test.setTimeout(420_000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  const wide: string[] = [];
  for (const w of [320, 390]) {
    await page.setViewportSize({ width: w, height: 800 });
    for (const lang of ["fr", "de"]) {
      await page.goto(`/${lang}/presentation/`);
      for (let i = 0; i < STEP_IDS.length; i++) {
        await openStep(page, i);
        await settled(page);
        const sw = await page.evaluate(() => Math.max(document.documentElement.scrollWidth, document.querySelector(".d-main")?.scrollWidth ?? 0));
        if (sw > w) wide.push(`${w} px ${lang} ${STEP_IDS[i]} : +${sw - w} px`);
        const under = await page.evaluate(() => {
          const foot = document.querySelector(".d-foot");
          const scene = document.querySelector(".v-scene");
          if (!foot || !scene) return 9999;
          let bottom = 0;
          for (const el of scene.querySelectorAll("*")) {
            if (el.closest(".v-consultant[data-open]")) continue; // the consultant's view opens full screen on purpose
            const r = el.getBoundingClientRect();
            if (r.height > 0 && el.checkVisibility({ visibilityProperty: true })) bottom = Math.max(bottom, r.bottom);
          }
          return Math.round(bottom - foot.getBoundingClientRect().top);
        });
        if (under > 0) wide.push(`${w} px ${lang} ${STEP_IDS[i]} : ${under} px sous la navigation`);
      }
    }
  }
  expect(wide, wide.join("\n")).toEqual([]);
});

// On an iPad held sideways (1180 × 820), the agency dashboard uses its width: no grid keeps an empty column on the right
// (the two measured tiles sat in a three-column grid, a third of the screen empty, seen in the film).
test("le tableau de bord d'agence n'a pas de colonne vide sur iPad (1180 × 820, FR et DE)", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  await page.setViewportSize({ width: 1180, height: 820 });
  const gaps: string[] = [];
  for (const lang of ["fr", "de"]) {
    await page.goto(`/${lang}/agence/`);
    const vide = await page.evaluate(() => {
      const grid = document.querySelector("#fx-agence-measured + div");
      if (!grid || !grid.lastElementChild) return -1;
      return Math.round(grid.getBoundingClientRect().right - grid.lastElementChild.getBoundingClientRect().right);
    });
    if (vide < 0 || vide > 4) gaps.push(`${lang} : ${vide} px vides à droite de la dernière mesure`);
  }
  expect(gaps, gaps.join("\n")).toEqual([]);
});

// A finger, not a pointer (suite 8, § 8): on a phone and on an iPad held sideways, every control of the visit's header,
// of the bar of the five times and of the guide is at least 44 × 44 px (the sound button was 15 px wide, « Options »
// 26 px high on the iPad, the times 28 px wide on the phone), and so is the language link of the first screen.
test("au doigt : les commandes de la visite font au moins 44 × 44 px (390 × 844 et 1180 × 820)", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  const petits: string[] = [];
  const mesurer = async (ou: string, selecteur: string) => {
    for (const b of await page.locator(selecteur).all()) {
      if (!(await b.isVisible())) continue;
      const r = await b.boundingBox();
      if (r && (r.width < 43.5 || r.height < 43.5)) petits.push(`${ou} « ${((await b.textContent()) || (await b.getAttribute("aria-label")) || "").trim().slice(0, 24)} » ${Math.round(r.width)}×${Math.round(r.height)}`);
    }
  };
  for (const [w, h] of [[390, 844], [1180, 820]]) {
    await page.setViewportSize({ width: w, height: h });
    await page.goto("/fr/");
    await mesurer(`${w} accueil`, "header a[hreflang]");
    await page.goto("/fr/presentation/");
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await mesurer(`${w} visite`, ".d-head-right > *, .v-progress button, [data-testid=guide-ask]");
  }
  expect(petits, petits.join("\n")).toEqual([]);
});
