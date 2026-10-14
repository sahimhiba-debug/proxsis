import { expect, test } from "@playwright/test";
import semaine from "../src/data/presentation/cette_semaine.json";
import { fmtDate } from "../src/lib/dates";

// Q19 (Hiba, 13.10.2026) : sa phrase du guide reste (« Chaque lundi, je vous dis jusqu'à quelle date chaque source est à
// jour »), donc l'écran du lundi donne une date par source : simap.ch et le Bulletin officiel du Valais (CLAIMS
// PRES-SEMAINE-1, cette_semaine.json), en français et en allemand.
test("l'écran du lundi dit jusqu'à quelle date chaque source est à jour (FR et DE)", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  for (const [lang, bo] of [["fr", "Bulletin officiel du Valais"], ["de", "Amtsblatt des Kantons Wallis"]] as const) {
    await page.goto(`/${lang}/semaine/M1/`);
    const line = page.getByTestId("sources-a-jour");
    await expect(line).toBeVisible();
    await expect(line).toContainText("simap.ch");
    await expect(line).toContainText(fmtDate(semaine.fin_des_donnees.simap));
    await expect(line).toContainText(bo);
    await expect(line).toContainText(fmtDate(semaine.fin_des_donnees.bulletin_officiel));
  }
});
