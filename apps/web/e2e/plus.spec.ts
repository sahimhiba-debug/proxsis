import { expect, test, type Locator, type Page } from "@playwright/test";

// Suite 9, § 10: on a phone, the densest screens (« Vos questions », the summary, « Pour votre direction », the Monday
// list) keep one idea in view; the detail opens with a touch under « En savoir plus » (« Mehr erfahren »), a real button
// of at least 44 × 44 px. The figures, the sources and the mentions stay in the page; on a computer and on paper,
// nothing is folded. The projects of playwright.config.ts are a phone (Pixel 7).

const label = (lang: "fr" | "de") => (lang === "fr" ? "En savoir plus" : "Mehr erfahren");

/** Every « En savoir plus » of the page: named, folded, at least 44 × 44 px. */
async function boutons(page: Page, lang: "fr" | "de"): Promise<Locator> {
  const all = page.getByTestId("plus");
  expect(await all.count()).toBeGreaterThan(0);
  for (const b of await all.all()) {
    await expect(b).toBeVisible();
    await expect(b).toHaveAccessibleName(new RegExp(`^${label(lang)}`));
    await expect(b).toHaveAttribute("aria-expanded", "false");
    const r = await b.boundingBox();
    expect(r!.width, "largeur du bouton").toBeGreaterThanOrEqual(44);
    expect(r!.height, "hauteur du bouton").toBeGreaterThanOrEqual(44);
  }
  return all;
}

/** The page is shorter folded than unfolded: the detail really waits for a touch. */
async function plusCourte(page: Page, ratio: number): Promise<void> {
  const folded = await page.evaluate(() => document.documentElement.scrollHeight);
  for (const b of await page.getByTestId("plus").all()) await b.click();
  const open = await page.evaluate(() => document.documentElement.scrollHeight);
  expect(folded, `${folded} px plié, ${open} px déplié`).toBeLessThan(open * ratio);
}

test("au téléphone, « Vos questions » : une réponse courte, la réponse entière sous « En savoir plus »", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/questions/`);
  await boutons(page, lang);
  const first = page.getByTestId("question-item").first();
  await expect(first.getByTestId("question-bref")).toBeVisible();
  await expect(first.getByTestId("question-answer")).toBeHidden();
  await first.getByTestId("plus").click();
  await expect(first.getByTestId("plus")).toHaveAttribute("aria-expanded", "true");
  await expect(first.getByTestId("question-answer")).toBeVisible();
  // every whole answer stays in the page, the study with its source among them
  await expect(page.getByTestId("question-answer")).toHaveCount(11);
  await expect(page.getByTestId("question-item").nth(1)).toContainText("NBER, 2015");
  await page.goto(`/${lang}/presentation/questions/`);
  await plusCourte(page, 0.7);
});

test("au téléphone, « Pour votre direction » : une idée par section, le détail sous « En savoir plus »", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/direction/`);
  await boutons(page, lang);
  // the proof in one short sentence, with its figures (CLAIMS PRES-DATE-1); the whole proof and its line of the registry
  // stay in the page
  const bref = page.getByTestId("direction-preuve-bref");
  await expect(bref).toBeVisible();
  for (const x of ["57", "66,8", "20,7"]) await expect(bref).toContainText(x);
  await expect(page.getByTestId("direction-preuve").locator("a")).toHaveAttribute("href", `/${lang}/mesures/#PRES-DATE-1`);
  // the door: its sentences in view, its guardrails under « En savoir plus », « none of this exists today » in view
  const door = page.getByTestId("direction-iris");
  await expect(door.getByTestId("direction-garde-fous")).toBeHidden();
  await expect(page.getByTestId("direction-futur")).toBeVisible();
  await door.getByTestId("plus").click();
  await expect(door.getByTestId("direction-garde-fous")).toBeVisible();
  await expect(door.getByTestId("direction-garde-fous")).toContainText(lang === "fr"
    ? "Les données de Flexsis resteront sous son contrôle, en Suisse, avec son accord écrit."
    : "Die Daten von Flexsis werden unter ihrer Kontrolle bleiben, in der Schweiz, mit ihrer schriftlichen Zustimmung.");
  await page.goto(`/${lang}/presentation/direction/`);
  await plusCourte(page, 0.75);
});

test("au téléphone, la synthèse : vos choix d'abord, les trois étapes sous « En savoir plus »", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/synthese/`);
  await boutons(page, lang);
  const steps = page.getByTestId("synthese-etapes").locator("ol");
  await expect(steps).toBeHidden();
  await page.getByTestId("synthese-etapes").getByTestId("plus").click();
  await expect(steps).toBeVisible();
  await expect(steps.locator("li")).toHaveCount(3);
});

test("au téléphone, la liste du lundi : les sept autres appels en bref, la phrase d'appel sous « En savoir plus »", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.emulateMedia({ reducedMotion: "reduce" }); // the cards enter with a small movement: measured once settled
  await page.goto(`/${lang}/semaine/M1/`);
  const cards = page.getByTestId("company-card");
  expect(await cards.count()).toBeGreaterThanOrEqual(10); // ten in the ranking, then the newcomers
  // the first three calls keep their sentence in view
  for (let i = 0; i < 3; i++) await expect(cards.nth(i).getByTestId("phone-line")).toBeVisible();
  await boutons(page, lang);
  const fourth = cards.nth(3);
  await expect(fourth.getByTestId("phone-line")).toBeHidden();
  await fourth.getByTestId("plus").click();
  await expect(fourth.getByTestId("phone-line")).toBeVisible();
  await page.goto(`/${lang}/semaine/M1/`);
  await plusCourte(page, 0.85);
});

test("sur un ordinateur et sur papier, rien n'est plié", async ({ page }, info) => {
  test.skip(info.project.name === "hors-ligne", "deux passes suffisent (en ligne, allemand)");
  const lang = info.project.metadata.lang as "fr" | "de";
  for (const media of ["screen", "print"] as const) {
    await page.setViewportSize(media === "screen" ? { width: 1440, height: 900 } : { width: 412, height: 915 });
    await page.emulateMedia({ media });
    for (const path of ["presentation/questions/", "presentation/direction/", "presentation/synthese/"]) {
      await page.goto(`/${lang}/${path}`);
      await expect(page.getByTestId("plus").first()).toBeHidden();
      for (const b of await page.getByTestId("plus").all()) await expect(b).toBeHidden();
    }
    await expect(page.getByTestId("synthese-etapes").locator("ol")).toBeVisible();
    await page.goto(`/${lang}/presentation/direction/`);
    await expect(page.getByTestId("direction-garde-fous")).toBeVisible();
    await expect(page.getByTestId("direction-preuve-bref")).toBeHidden();
  }
});

test("au téléphone, la porte de « Pour votre direction » garde en vue le premier garde-fou (relecture neuve du 13.10)", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/direction/`);
  const porte = page.getByTestId("direction-iris");
  await expect(porte.getByTestId("garde-fou-bref")).toBeVisible();
  await expect(porte.getByTestId("garde-fou-bref")).toHaveText(lang === "fr" ? /Iris proposera, le consultant décidera/ : /Iris wird vorschlagen/);
  await expect(porte.getByTestId("direction-futur")).toBeVisible();
  await expect(porte.getByTestId("direction-garde-fous")).toBeHidden();
});
