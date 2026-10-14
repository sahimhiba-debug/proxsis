import { expect, type Page } from "@playwright/test";

// The size of the guide's Iris (suite 9, § 10: « trop petite pour être reconnue »): at least 56 px high on a phone and
// 72 px on an iPad, her two eyes well visible (shown, lit, inside her head and inside the screen, not covered). Used by
// e2e/guide.spec.ts (Chrome) and e2e/moteurs/guide.moteurs.ts (Chrome and WebKit).
export const TAILLES_TELEPHONE = [[390, 844], [375, 667]] as const;
export const TAILLES_IPAD = [[820, 1180], [1180, 820], [1024, 1366]] as const;
export const MIN_TELEPHONE = 56;
export const MIN_IPAD = 72;

export async function verifierIris(page: Page, [w, h]: readonly [number, number], min: number): Promise<void> {
  await page.setViewportSize({ width: w, height: h });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/fr/presentation/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  const iris = page.getByTestId("guide").getByTestId("iris-petite");
  await expect(iris).toBeVisible();
  const box = await iris.boundingBox();
  expect(box, `${w} × ${h} : la petite Iris`).not.toBeNull();
  expect(box!.height, `${w} × ${h} : hauteur d'Iris (au moins ${min} px)`).toBeGreaterThanOrEqual(min);
  const yeux = iris.locator(".v-iris-oeil");
  await expect(yeux).toHaveCount(2);
  for (const oeil of await yeux.all()) {
    await expect(oeil).toBeVisible();
    const e = await oeil.boundingBox();
    expect(e, `${w} × ${h} : un œil`).not.toBeNull();
    expect(Number(await oeil.evaluate((el) => getComputedStyle(el).opacity)), `${w} × ${h} : l'œil est allumé`).toBe(1);
    // inside her head and inside the screen
    expect(e!.x).toBeGreaterThanOrEqual(box!.x - 0.5);
    expect(e!.x + e!.width).toBeLessThanOrEqual(box!.x + box!.width + 0.5);
    expect(e!.y).toBeGreaterThanOrEqual(Math.max(0, box!.y - 0.5));
    expect(e!.y + e!.height).toBeLessThanOrEqual(Math.min(h, box!.y + box!.height) + 0.5);
    // nothing on top of it: the point at its centre belongs to Iris
    const dessus = await page.evaluate(([x, y]) => !!document.elementFromPoint(x, y)?.closest("[data-testid=iris-petite]"),
      [e!.x + e!.width / 2, e!.y + e!.height / 2]);
    expect(dessus, `${w} × ${h} : rien ne couvre l'œil`).toBe(true);
  }
}
