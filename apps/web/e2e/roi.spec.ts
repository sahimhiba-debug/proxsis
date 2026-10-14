import { expect, test } from "@playwright/test";

// « Retour sur investissement » is the threshold of the visit (brief « à distance », 4.4): the same calculation and the
// same example values; half the days with the same cost gives a loss that stays on screen; a typed value is checked.
test("le calculateur de l'application est le seuil de la visite", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  await page.goto("/fr/roi/");
  await expect(page.getByTestId("roi-main")).toHaveText("Il suffit de 44 journées supplémentaires facturées pour couvrir le coût.");
  const net = page.getByTestId("roi-net");
  await expect(net).toContainText("680"); // 60 × 100 − (3 600 + 12 × 60) = 1 680 CHF over 6 weeks
  await expect(net).toHaveAttribute("data-negative", "false");
  await page.getByRole("button", { name: "Deux fois moins" }).click();
  await expect(net).toHaveAttribute("data-negative", "true"); // 30 × 100 − 4 320 = −1 320
  await expect(net).toContainText("320");
  await expect(page.getByTestId("roi-main")).toContainText("44"); // the threshold does not move: the cost is the same
  await page.getByTestId("roi-days").fill("2,5");
  await expect(page.getByRole("status").filter({ hasText: "entières" })).toBeVisible();
});
