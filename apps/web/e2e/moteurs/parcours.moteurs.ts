import { expect, test, type Page } from "@playwright/test";
import { ouvrir } from "../attente";
import { VISIT_COPY } from "../../src/visite/copy";
import { VISIT_KEY, VISIT_STEPS } from "../../src/visite/state";

// What the director does with the link, on each engine and each size (playwright.moteurs.config.ts): the first screen,
// the whole visit with « Continuer » only, then the application (« Ma semaine », a dossier, the carnet kept after a
// reload). On every screen: no script error, no request outside the site, no page wider than the screen.

function watch(page: Page): string[] {
  const problems: string[] = [];
  page.on("pageerror", (e) => problems.push(`erreur : ${e.message}`));
  page.on("request", (r) => {
    const url = new URL(r.url());
    if (!["localhost", "127.0.0.1"].includes(url.hostname) && !["data:", "blob:"].includes(url.protocol)) problems.push(`hors du site : ${r.url()}`);
  });
  return problems;
}

const stored = (page: Page) => page.evaluate((key) => localStorage.getItem(key) ?? "", VISIT_KEY);
const LAST = VISIT_STEPS.length - 1;

/** One press of « Continuer » (by a click or by the keyboard), then the screen it leads to: the visit's stored state
 *  has moved (a step or a gesture), and the narration is the one of that step (not the one still fading out). */
async function advance(page: Page, lang: "fr" | "de", press: () => Promise<void>): Promise<number> {
  const before = await stored(page);
  await press();
  await expect.poll(() => stored(page)).not.toBe(before);
  const step = (JSON.parse(await stored(page)) as { step: number }).step;
  await expect(page.getByTestId("narration")).toHaveText(VISIT_COPY[lang].narration[VISIT_STEPS[step].id]);
  // a new step opens at its top: its sentence is on screen (critique of 07.10.2026: it landed mid-scene on a phone)
  if (JSON.parse(before || "{}").step !== step) await expect(page.getByTestId("narration")).toBeInViewport();
  return step;
}

async function notWider(page: Page, where: string, problems: string[]): Promise<void> {
  const [sw, w] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  if (sw > w) problems.push(`${where} : ${sw - w} px de trop en largeur`);
}

for (const lang of ["fr", "de"] as const) {
  const L = (fr: string, de: string) => (lang === "fr" ? fr : de);

  test(`${lang} : du premier écran à la conclusion, avec « Continuer » seulement`, async ({ page }) => {
    const problems = watch(page);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await ouvrir(page, `/${lang}/`);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(L("La prochaine entreprise à appeler.", "Das nächste Unternehmen, das Sie anrufen."));
    await notWider(page, "premier écran", problems);
    await page.getByTestId("start").click();
    const narration = page.getByTestId("narration");
    await expect(narration).toHaveText(L("Lundi, 8 h 03. Quelle entreprise mérite votre premier appel ?",
      "Montag, 8.03 Uhr. Welches Unternehmen verdient Ihren ersten Anruf?"));
    if (lang === "de") await expect(page.getByTestId("review-mention")).toBeVisible();

    const next = page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true });
    const back = page.getByRole("button", { name: L("Revenir à la visite", "Zurück zum Rundgang") });
    const seen = new Set<number>([0]);
    let step = 0;
    for (let i = 0; i < 40 && step < LAST; i++) {
      await notWider(page, `${VISIT_STEPS[step].id}, geste ${i}`, problems);
      // on a phone, the consultant's view opens full screen: back to the visit, as the director would
      if (await back.first().isVisible()) await back.first().click();
      step = await advance(page, lang, () => next.click());
      seen.add(step);
    }
    await expect(narration).toHaveText(L("Votre premier lundi.", "Ihr erster Montag."));
    await notWider(page, "conclusion", problems);
    expect([...seen]).toEqual(VISIT_STEPS.map((_, i) => i)); // every step, in order, none skipped
    expect(problems, problems.join("\n")).toEqual([]);
  });

  test(`${lang} : l'application, un dossier, le carnet gardé après rechargement`, async ({ page }) => {
    const problems = watch(page);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await ouvrir(page, `/${lang}/semaine/M1/`);
    expect(await page.getByTestId("company-card").count()).toBeGreaterThanOrEqual(10); // the ten, and the newcomers
    await notWider(page, "Ma semaine", problems);
    await page.getByTestId("company-card").first().getByRole("heading").getByRole("link").click();
    await expect(page.getByTestId("timeline")).toBeVisible();
    await notWider(page, "dossier", problems);
    await page.getByTestId("carnet-appeler").click();
    await expect(page.getByTestId("carnet-appeler")).toHaveAttribute("aria-pressed", "true");
    await page.reload();
    await expect(page.getByTestId("carnet-appeler")).toHaveAttribute("aria-pressed", "true");
    expect(problems, problems.join("\n")).toEqual([]);
  });
}

// The keyboard alone (no mouse, no touch) takes the director through the visit: « Continuer » is reached with Tab and
// pressed with Enter. Computers only; Safari moves the focus to buttons only with Option+Tab (its default setting), so
// it is left to Chrome and Firefox here.
test("au clavier seulement : toute la visite", async ({ page }, info) => {
  test.skip(!info.project.name.endsWith("ordinateur") || info.project.name.startsWith("webkit"), "ordinateur, Chrome et Firefox");
  const problems = watch(page);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await ouvrir(page, "/fr/presentation/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  const narration = page.getByTestId("narration");
  let step = 0;
  for (let i = 0; i < 40 && step < LAST; i++) {
    let reached = false;
    for (let k = 0; k < 120 && !reached; k++) {
      await page.keyboard.press("Tab");
      reached = await page.evaluate(() => document.activeElement?.textContent?.trim() === "Continuer");
    }
    expect(reached, `« Continuer » atteint au clavier (${VISIT_STEPS[step].id})`).toBe(true);
    step = await advance(page, "fr", () => page.keyboard.press("Enter"));
  }
  await expect(narration).toHaveText("Votre premier lundi.");
  expect(problems, problems.join("\n")).toEqual([]);
});
