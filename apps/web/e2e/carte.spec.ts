import { expect, test } from "@playwright/test";

// « Carte »: the period chooser moves through the published contracts, and the page never asks the network for map
// tiles (the commune boundaries are embedded: the map is the same without Wi-Fi).
test("la carte change de semaine et ne demande rien au réseau", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  const outside: string[] = [];
  page.on("request", (r) => { if (!/^https?:\/\/localhost/.test(r.url())) outside.push(r.url()); });
  await page.goto("/fr/carte/");
  // it opens on the 14 days before the list's Monday (the same « recent » as « Ma semaine »), never on an empty week
  const week = page.getByTestId("map-week");
  await expect(week).toContainText("Du 21.09 au 04.10.2026");
  await expect(week).toContainText("17 marchés publiés");
  await expect(page.getByTestId("map-list").getByRole("listitem")).toHaveCount(17);
  // one week earlier; at the far end the button stays focusable (the focus is never lost)
  const prev = page.getByRole("button", { name: "Une semaine plus tôt" });
  await prev.click();
  await expect(week).toContainText("Du 14.09 au 27.09.2026");
  await expect(page.getByTestId("map-list").getByRole("listitem")).toHaveCount(28);
  await page.getByRole("slider", { name: "Choisir la période" }).press("Home");
  await expect(week).toContainText("Du 06.07 au 19.07.2026");
  await prev.focus();
  await prev.press("Enter");
  await expect(prev).toBeFocused();
  await expect(prev).toHaveAttribute("aria-disabled", "true");
  await expect(week).toContainText("Du 06.07 au 19.07.2026");
  expect(outside).toEqual([]);
});
