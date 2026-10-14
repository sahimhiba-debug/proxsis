import { expect, test } from "@playwright/test";
import { MIN_IPAD, MIN_TELEPHONE, TAILLES_IPAD, TAILLES_TELEPHONE, verifierIris } from "./iris-taille";

// The guide of the visit: Iris, the hammer of the bisse (suite 8, § 3), small in a corner, one sentence per time,
// « Une question ? » with six answers prepared by the team, no free input, no request outside the site; hidden from
// « Options » (the presenter's choice); her gesture on a card: the orange dot lands with its label (« Repéré »).
test("le guide : une phrase par temps, six réponses préparées, aucune requête hors du site", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  const L = (fr: string, de: string) => (lang === "fr" ? fr : de);
  const outside: string[] = [];
  page.on("request", (r) => { const u = new URL(r.url()); if (!["localhost", "127.0.0.1"].includes(u.hostname) && !["data:", "blob:"].includes(u.protocol)) outside.push(r.url()); });
  await page.goto(`/${lang}/presentation/`);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  const guide = page.getByTestId("guide");
  await expect(guide).toBeVisible();
  // Iris introduces herself (suite 3, § 1): « l'assistante de Proxsis », never « IA »; her button (§ 4)
  await expect(page.getByTestId("guide-phrase")).toHaveText(lang === "fr" ? /^Je suis Iris, l'assistante de Proxsis\./ : /^Ich bin Iris, die Assistentin von Proxsis\./);
  await expect(page.getByTestId("iris-petite")).toBeVisible(); // the new Iris, standing on her handle (no WebGL any more)
  await expect(page.getByTestId("guide-ask")).toHaveText(L("Une question ? Demandez à Iris.", "Eine Frage? Fragen Sie Iris."));
  await expect(page.getByTestId("guide")).not.toContainText(/\bIA\b|\bKI\b/);
  // her gesture: the dot lands on the prepared company, labelled, on the map
  await expect(page.getByTestId("visee")).toHaveAttribute("data-cible", "repere");
  await expect(page.getByTestId("visee")).toContainText(L("Repéré", "Erkannt"));
  // six prepared questions; an answer; its figures come from the data
  await page.getByTestId("guide-ask").click();
  await expect(page.getByTestId("guide-panel").getByRole("button")).toHaveCount(7); // six questions and « Fermer »
  await expect(page.getByTestId("guide-prepared")).toHaveText(L("Réponses préparées par l'équipe", "Antworten vom Team vorbereitet"));
  await page.getByTestId("guide-q-marche").click();
  await expect(page.getByTestId("guide-answer")).toContainText("66,8 %");
  await expect(page.getByTestId("guide-answer")).toContainText("20,7 %");
  await expect(page.locator("[data-testid=guide-panel] input, [data-testid=guide-panel] textarea")).toHaveCount(0); // nothing to type
  await page.keyboard.press("Escape");
  await expect(page.getByTestId("guide-panel")).toHaveCount(0);
  // the next time, its own sentence
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click(); // the dossier's gesture
  await expect(page.getByTestId("visee")).toHaveAttribute("data-cible", "question"); // from the published fact to the question
  await expect(page.locator("[data-testid=visee] .v-point")).toHaveCount(1);
  expect(outside).toEqual([]);
});

test("la petite Iris est une image (aucun WebGL) ; masquée depuis « Options », elle le reste", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  await page.addInitScript(() => {
    const get = HTMLCanvasElement.prototype.getContext;
    // @ts-expect-error a browser without WebGL2: Iris does not need it any more
    HTMLCanvasElement.prototype.getContext = function (type: string, ...rest: unknown[]) { return type === "webgl2" ? null : get.call(this, type, ...rest); };
  });
  await page.goto("/fr/presentation/");
  await expect(page.getByTestId("iris-petite")).toBeVisible();
  await expect(page.getByRole("img", { name: /Iris/ }).first()).toBeVisible();
  await page.getByRole("button", { name: /Options/ }).click();
  await page.getByTestId("guide-toggle").click();
  await expect(page.getByTestId("guide")).toHaveCount(0);
  await expect(page.getByTestId("lumiere")).toHaveCount(0);
  await page.reload();
  await expect(page.getByTestId("guide")).toHaveCount(0);
});

test("mouvement réduit : le point est déjà posé, sans chute, le titre sans miroitement", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/fr/presentation/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.getByTestId("visee")).toHaveAttribute("data-immobile", "true");
  expect(await page.locator("[data-testid=visee] .v-point").evaluate((el) => getComputedStyle(el).animationName)).toBe("none");
  const anim = await page.getByTestId("narration").evaluate((el) => getComputedStyle(el).animationName);
  expect(anim).toBe("none");
});

// Suite 9, § 10: the guide's Iris is big enough to be recognised, at least 56 px on a phone and 72 px on an iPad, her
// eyes well visible (WebKit: e2e/moteurs/guide.moteurs.ts)
test("la petite Iris du guide : au moins 56 px au téléphone, 72 px à l'iPad, les yeux bien visibles", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit (les tailles changent dans le test)");
  for (const size of TAILLES_TELEPHONE) await verifierIris(page, size, MIN_TELEPHONE);
  for (const size of TAILLES_IPAD) await verifierIris(page, size, MIN_IPAD);
});

