import { expect, test } from "@playwright/test";

// The new Iris outside the guide (suite 8): the sound never starts by itself and one button cuts it (§ 5); the dot on
// the « i » of the first screen, complete without motion (§ 4); the application's icons, Iris's head (§ 3).

test("le son : rien avant un geste ; un bouton toujours visible le coupe, et le choix reste", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  const sons: string[] = [];
  page.on("request", (r) => { if (r.url().includes("/iris/sons/")) sons.push(r.url()); });
  await page.goto("/fr/presentation/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  const son = page.getByTestId("son");
  await expect(son).toBeVisible();
  await expect(son).toHaveAttribute("aria-pressed", "true");
  const box = await son.boundingBox();
  expect(box && box.height).toBeGreaterThanOrEqual(44); // au doigt
  expect(sons).toEqual([]); // aucun son chargé avant un geste du visiteur
  await son.click();
  await expect(son).toHaveAttribute("aria-pressed", "false");
  await page.reload();
  await expect(page.getByTestId("son")).toHaveAttribute("aria-pressed", "false");
});

test("le point du « i » : sans mouvement, le logo complet, le point posé, pas d'Iris", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(`/${lang}/`);
  const logo = page.getByTestId("logo-iris");
  await expect(logo).toBeVisible();
  await expect(logo).toHaveAttribute("aria-label", /^Proxsis · /);
  const etat = await logo.evaluate((el) => {
    const paths = [...el.querySelectorAll("svg > path")];
    const dot = paths.find((p) => p.getAttribute("fill") === "#E6530F");
    const iris = el.querySelector("svg > g[opacity]");
    return { dot: dot?.getAttribute("opacity"), iris: iris?.getAttribute("opacity") };
  });
  expect(etat.dot).toBe("1");
  expect(etat.iris).toBe("0");
});

test("le point du « i » : avec le mouvement, Iris frappe puis s'efface, et plus rien ne bouge", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  await page.goto("/fr/");
  await page.evaluate(() => sessionStorage.clear());
  await page.reload();
  await page.waitForTimeout(2600);
  const etat = await page.getByTestId("logo-iris").evaluate((el) => ({
    dot: [...el.querySelectorAll("svg > path")].find((p) => p.getAttribute("fill") === "#E6530F")?.getAttribute("opacity"),
    iris: el.querySelector("svg > g[opacity]")?.getAttribute("opacity"),
  }));
  expect(etat.dot).toBe("1");
  expect(Number(etat.iris)).toBe(0);
});

test("les icônes : la tête d'Iris, aux bonnes tailles, dans le manifeste", async ({ page, request }, info) => {
  test.skip(info.project.name === "allemand", "une passe en ligne et une hors ligne");
  const manifest = await (await request.get("/manifest.webmanifest")).json();
  const icons = manifest.icons as { src: string; sizes: string; purpose?: string }[];
  expect(icons.map((i) => i.src)).toEqual(["/icon-192.png", "/icon-512.png", "/icon-512-maskable.png"]);
  expect(icons.some((i) => i.purpose === "maskable")).toBe(true);
  await page.goto("/fr/");
  for (const { src, sizes } of icons) {
    const [w] = sizes.split("x").map(Number);
    const dims = await page.evaluate(async (u) => { const im = new Image(); im.src = u; await im.decode(); return [im.naturalWidth, im.naturalHeight]; }, src);
    expect(dims).toEqual([w, w]);
  }
  for (const u of ["/favicon.ico", "/apple-icon.png", "/icon.png"]) expect((await request.get(u)).status()).toBe(200);
});
