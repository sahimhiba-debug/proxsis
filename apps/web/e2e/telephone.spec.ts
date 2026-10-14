import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { settled } from "./attente";

// C2 « démo vivante » : the real app in a phone, piloted by the arrows (Ma semaine → dossier → appel préparé →
// feuille de synthèse). Real pages, not a video; interruptible; a still version; the presenter can take over; the
// demo never records anything (no call feedback is touched).
const GUIDED = "ent-1ef761b229";
test.use({ viewport: { width: 1920, height: 1080 }, isMobile: false, hasTouch: false, deviceScaleFactor: 1 });

const appPath = (page: Page) =>
  page.getByTestId("phone-app").evaluate((el) => (el as HTMLIFrameElement).contentWindow?.location.pathname ?? "");

async function open(page: Page, lang: "fr" | "de", errors: string[]) {
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto(`/${lang}/presentation/telephone/`);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect.poll(() => appPath(page)).toBe(`/${lang}/semaine/M1/`);
  await expect(page.getByTestId("phone-demo")).toHaveAttribute("data-shown", "0");
}

test("sans mouvement : les quatre étapes, le retour en arrière, la reprise en main, rien d'enregistré", async ({ browser }, info) => {
  test.skip(info.project.name !== "en-ligne", "une passe suffit");
  const page = await browser.newPage({ baseURL: info.project.use.baseURL, viewport: { width: 1920, height: 1080 }, reducedMotion: "reduce" });
  const errors: string[] = [];
  await open(page, "fr", errors);
  const app = page.frameLocator('[data-testid="phone-app"]');
  const demo = page.getByTestId("phone-demo");
  await expect(app.getByRole("heading", { name: "Ma semaine" })).toBeVisible();

  await page.keyboard.press("ArrowRight");
  await expect.poll(() => appPath(page)).toBe(`/fr/entreprise/${GUIDED}/`);
  await expect(app.getByRole("heading", { name: "Joseph Carron SA" })).toBeVisible();

  await page.keyboard.press("ArrowRight");
  await expect.poll(() => appPath(page)).toBe(`/fr/entreprise/${GUIDED}/appel/`);
  await expect(app.getByRole("heading", { name: "Préparer l'appel" })).toBeVisible();

  await page.keyboard.press("ArrowRight"); // the summary sheet of the session, on a phone
  await expect.poll(() => appPath(page)).toBe("/fr/presentation/synthese/");
  await expect(app.getByRole("heading", { name: /Votre premier lundi/ })).toBeVisible();
  await expect(app.getByTestId("synthese")).toBeVisible(); // the visit's printable summary (since 07.10.2026)
  await expect(page.getByTestId("finger")).toHaveCount(0); // still: no finger left over the screen

  // backwards: a direct jump; nothing was ever recorded on the device
  await page.keyboard.press("ArrowLeft");
  await expect(demo).toHaveAttribute("data-shown", "2");
  const records = await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem("proxsis.carnet.v1") ?? "{}")).length);
  expect(records).toBe(0);
  await page.keyboard.press("Home");
  await expect.poll(() => appPath(page)).toBe("/fr/semaine/M1/");

  // the presenter takes over: the pilot pauses until « Reprendre la démo »
  await app.getByRole("link", { name: "Carte" }).click();
  await expect(page.getByRole("button", { name: "Reprendre la démo" })).toBeVisible();
  await expect.poll(() => appPath(page)).toBe("/fr/carte/");
  await page.getByRole("button", { name: "Reprendre la démo" }).click();
  await expect.poll(() => appPath(page)).toBe("/fr/semaine/M1/");
  await expect(page.getByRole("button", { name: "Reprendre la démo" })).toHaveCount(0);

  // taking over on a step page: the demo resumes from there
  await app.locator(`[data-demo="ouvrir-${GUIDED}"]`).click();
  await expect.poll(() => appPath(page)).toBe(`/fr/entreprise/${GUIDED}/`);
  await page.getByRole("button", { name: "Reprendre la démo" }).click();
  await expect(demo).toHaveAttribute("data-shown", "1");
  await expect(page.getByTestId("review-step")).toContainText("2");

  expect(errors).toEqual([]);
  await page.close();
});

test("avec mouvement : le doigt se déplace, touche, l'onde part, la page change ; une flèche interrompt", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une passe suffit");
  const errors: string[] = [];
  await open(page, "fr", errors);
  await page.keyboard.press("ArrowRight");
  await expect(page.getByTestId("finger")).toBeVisible();
  await expect(page.getByTestId("ripple")).toHaveCount(1, { timeout: 5000 });
  await expect.poll(() => appPath(page)).toBe(`/fr/entreprise/${GUIDED}/`);
  await expect(page.getByTestId("phone-demo")).toHaveAttribute("data-shown", "1");

  // two arrows in a row: the running gesture stops and the phone lands on the asked step
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");
  await expect(page.getByTestId("phone-demo")).toHaveAttribute("data-shown", "3", { timeout: 15_000 });
  await expect.poll(() => appPath(page)).toBe("/fr/presentation/synthese/");
  expect(errors).toEqual([]);
});

test("en allemand, et page de relecture accessible", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une passe suffit");
  const errors: string[] = [];
  await page.emulateMedia({ reducedMotion: "reduce" }); // contrast is measured on the settled screen, as everywhere else
  await open(page, "de", errors);
  await expect(page.getByTestId("review-caption")).toContainText("Meine Woche");
  await settled(page);
  const { violations } = await new AxeBuilder({ page }).analyze(); // the app inside the phone included
  expect(violations.map((v) => `${v.id} (${v.impact})`)).toEqual([]);
  expect(errors).toEqual([]);
});

test("au clavier : « Passer le téléphone » saute l'application ; une touche dans le téléphone donne la main", async ({ browser }, info) => {
  test.skip(info.project.name !== "en-ligne", "une passe suffit");
  const page = await browser.newPage({ baseURL: info.project.use.baseURL, viewport: { width: 1920, height: 1080 }, reducedMotion: "reduce" });
  const errors: string[] = [];
  await open(page, "fr", errors);
  const skip = page.getByRole("button", { name: "Passer le téléphone" });
  for (let i = 0; i < 12 && !(await skip.evaluate((el) => el === document.activeElement)); i++) await page.keyboard.press("Tab");
  await expect(skip).toBeFocused();
  expect((await skip.boundingBox())?.width ?? 0).toBeGreaterThan(40); // visible while it has the focus
  await page.keyboard.press("Enter");
  expect(await page.evaluate(() => document.activeElement?.classList.contains("ph-line"))).toBe(true);
  await expect(page.getByTestId("phone-demo")).toHaveAttribute("data-paused", "false");

  // back into the phone with the keyboard, then a key used there: the demo waits, as after a touch
  await page.keyboard.press("Shift+Tab");
  await page.keyboard.press("Shift+Tab");
  await expect(page.getByRole("button", { name: "Reprendre la démo" })).toBeVisible();
  await expect(page.getByTestId("phone-demo")).toHaveAttribute("data-paused", "true");
  expect(errors).toEqual([]);
  await page.close();
});

test("format téléphone : le téléphone tient dans l'écran, sans défilement horizontal", async ({ browser }, info) => {
  test.skip(info.project.name !== "en-ligne", "une passe suffit");
  const page = await browser.newPage({ baseURL: info.project.use.baseURL, viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
  await page.goto("/fr/presentation/telephone/");
  await expect.poll(() => appPath(page)).toBe("/fr/semaine/M1/");
  const box = await page.getByTestId("phone-frame").boundingBox();
  expect(box && box.x >= 0 && box.x + box.width <= 390).toBe(true);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.close();
});
