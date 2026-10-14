import { expect, test, type Page } from "@playwright/test";
import { settled } from "./attente";
import { openStep, STEP_IDS } from "./etape";

// simap.ch's general terms (ch. 5): wherever a screen shows simap data, its mandatory mention is there, verbatim (on a
// German screen: the French original, then a labelled translation): on every page of the application (its footer), on
// every step of the presentation that shows simap awards, and on any other screen whose content names simap or links to
// it. Everything revealed, in French and in German. And the application's own mention (« Prototype · concept non
// officiel ») is on every screen.
const MENTION = "Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi.";
const PROTOTYPE = { fr: "Prototype · concept non officiel", de: "Prototyp · inoffizielles Konzept" };
const PAGES = ["/semaine/M1/", "/semaine/", "/entreprise/ent-1ef761b229/", "/entreprise/ent-1ef761b229/appel/",
  "/entreprise/ent-1ef761b229/candidats/", "/carte/", "/redeploiement/", "/conformite/", "/agence/", "/agence/martigny/",
  "/roi/", "/mesures/", "/presentation/synthese/", "/presentation/preuves/", "/", "/une-page/"];
// the steps of the visit that show simap data (src/visite/Visit.tsx)
const SIMAP_STEPS = ["carte", "dossier", "carnet", "suivant", "date", "conclusion"];

/** Whether the screen's content (header and footer aside) shows simap data — a link to a publication or the source
 *  named — and whether the mention is on the screen, verbatim. */
const look = (page: Page) => page.evaluate((mention) => {
  const text = (document.body.innerText ?? "").replace(/\s+/g, " ");
  const main = document.querySelector("main");
  const content = main ? [...main.querySelectorAll("*")].filter((el) => !el.closest("footer, header, [data-testid=simap-mention]")) : [];
  const simap = content.some((el) => (el instanceof HTMLAnchorElement && el.href.includes("simap.ch"))
    || [...el.childNodes].some((n) => n.nodeType === Node.TEXT_NODE && /simap/i.test(n.textContent ?? "")));
  return { simap, mention: text.includes(mention), text };
}, MENTION);

for (const lang of ["fr", "de"] as const) {
  test(`mention simap partout où il y a des données simap, et mention prototype sur chaque page (${lang.toUpperCase()})`, async ({ page }, info) => {
    test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
    test.setTimeout(240_000);
    await page.emulateMedia({ reducedMotion: "reduce" });
    const missing: string[] = [];
    for (const path of PAGES) {
      await page.goto(`/${lang}${path}`);
      const s = await look(page);
      if (!s.mention) missing.push(`${lang}${path} : mention simap absente`);
      if (!s.text.includes(PROTOTYPE[lang])) missing.push(`${lang}${path} : mention prototype absente`);
    }
    await page.goto(`/${lang}/presentation/`);
    for (let step = 0; step < STEP_IDS.length; step++) {
      await openStep(page, step);
      await settled(page);
      const s = await look(page);
      if ((s.simap || SIMAP_STEPS.includes(STEP_IDS[step])) && !s.mention) missing.push(`${lang} présentation, ${STEP_IDS[step]} : mention simap absente`);
      if (!s.text.includes(PROTOTYPE[lang])) missing.push(`${lang} présentation, ${STEP_IDS[step]} : mention prototype absente`);
    }
    expect(missing, missing.join("\n")).toEqual([]);
    expect(STEP_IDS).toEqual(expect.arrayContaining(SIMAP_STEPS)); // a renamed step would silently leave the list
  });
}

// A 13-inch laptop with its browser bars leaves 720 to 800 px of height: the presentation's short-screen layout must
// not hide the foot of the visit, which carries the general mention, simap's mandatory mention and, in German, the
// review notice (a rule of the old presentation hid « the last paragraph » of the mentions: here, the only one).
for (const [w, h] of [[1280, 720], [1440, 800]] as const) {
  test(`les mentions de la visite restent visibles sur un ordinateur de ${w} × ${h}`, async ({ page }, info) => {
    test.skip(info.project.name === "hors-ligne", "deux langues en ligne suffisent");
    test.setTimeout(180_000);
    const lang = info.project.metadata.lang as "fr" | "de";
    await page.setViewportSize({ width: w, height: h });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(`/${lang}/presentation/`);
    const missing: string[] = [];
    for (let step = 0; step < STEP_IDS.length; step++) {
      await openStep(page, step);
      await settled(page);
      if (!(await page.getByTestId("general-mention").isVisible())) missing.push(`${STEP_IDS[step]} : mention générale cachée`);
      const s = await look(page);
      if (SIMAP_STEPS.includes(STEP_IDS[step]) && !s.mention) missing.push(`${STEP_IDS[step]} : mention simap absente`);
      if (lang === "de" && !(await page.getByTestId("review-mention").isVisible())) missing.push(`${STEP_IDS[step]} : relecture cachée`);
    }
    expect(missing, missing.join("\n")).toEqual([]);
  });
}
