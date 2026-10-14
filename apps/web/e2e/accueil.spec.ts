import { expect, test } from "@playwright/test";

// The first screen of proxsis.vercel.app (brief « à distance », § 3): the title, the subtitle, a real view of the
// product, « Voir Proxsis en 11 minutes » that starts the visit, « Lire la synthèse (1 page) », the language and the
// prototype mention; under 1 MB transferred.
test("premier écran : le titre, l'aperçu réel, la visite en un geste, la synthèse d'une page", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  const L = (fr: string, de: string) => (lang === "fr" ? fr : de);
  await page.goto(`/${lang}/`);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(L("La prochaine entreprise à appeler.", "Das nächste Unternehmen, das Sie anrufen."));
  await expect(page.getByText(L("Une entreprise réelle. Une raison publiée. Une question à poser.",
    "Ein echtes Unternehmen. Ein publizierter Grund. Eine Frage, die Sie stellen können."))).toBeVisible();
  await expect(page.getByText(L("Prototype · concept non officiel", "Prototyp · inoffizielles Konzept"))).toBeVisible();
  await expect(page.getByText("Société de Travaux Publics, Joseph Carron SA")).toBeVisible();
  await page.getByRole("link", { name: L("Lire la synthèse (1 page)", "Die Zusammenfassung lesen (1 Seite)") }).click();
  await expect(page.getByTestId("une-page")).toContainText("66,8 %");
  await expect(page.getByTestId("une-page")).toContainText("20,7 %");
  await page.goto(`/${lang}/`);
  await page.getByTestId("start").click();
  await expect(page.getByTestId("narration")).toHaveText(L("Lundi, 8 h 03. Quelle entreprise mérite votre premier appel ?",
    "Montag, 8.03 Uhr. Welches Unternehmen verdient Ihren ersten Anruf?"));
});

test("« Proxsis en une page » : un exemple réel, l'adresse de la visite, et une seule page A4 à l'impression", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/une-page/`);
  await expect(page.getByTestId("une-example")).toContainText("Joseph Carron SA");
  await expect(page.getByTestId("visit-address")).toContainText(`/${lang}/presentation/`);
  // la nouvelle Iris et sa devise (suite 8, § 10) : une image nommée, et le point sur le « i »
  await expect(page.getByTestId("une-iris").getByRole("img", { name: "Iris" })).toBeVisible();
  // suite 9, Q05: the German motto « Iris bringt es auf den Punkt. » (to be reviewed)
  await expect(page.getByTestId("une-iris")).toContainText(lang === "fr" ? "Iris met les points sur les i." : "Iris bringt es auf den Punkt.");
  // suite 9, § 8: the door, a short block, its three steps on one line, word for word
  await expect(page.getByTestId("une-porte").getByRole("heading")).toHaveText(lang === "fr" ? "Demain, si Flexsis le souhaite" : "Morgen, wenn Flexsis es wünscht");
  await expect(page.getByTestId("une-etapes")).toContainText(lang === "fr"
    ? "3. Si les résultats sont là : Iris installée chez Flexsis, avec Apertus adapté à ses données, chez elle."
    : "3. Wenn die Ergebnisse stimmen: Iris bei Flexsis eingerichtet, mit Apertus, angepasst an ihre Daten, bei ihr im Haus.");
  const pdf = await page.pdf({ format: "A4", printBackground: true });
  const pages = (pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) ?? []).length;
  expect(pages, "pages imprimées").toBe(1);
});

test("« Télécharger ma synthèse » : une indication d'exemple pour l'ensemble, l'adresse de la visite, une seule page A4", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/synthese/`);
  await expect(page.getByTestId("synthese-all-example")).toHaveCount(1);
  await expect(page.getByTestId("visit-address")).toContainText(`/${lang}/presentation/`);
  const pdf = await page.pdf({ format: "A4", printBackground: true });
  expect((pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) ?? []).length, "pages imprimées").toBe(1);
});

test("premier écran : moins de 1 Mo transférés", async ({ page }, info) => {
  // measured as the director receives it: minified and compressed (next start, like Vercel); the static copy served by
  // Python's server (« hors-ligne ») is not compressed, and the development server not minified
  test.skip(String(info.project.use.baseURL).includes(":3210") || info.project.name === "hors-ligne",
    "mesuré sur la version servie compressée (en ligne, allemand)");
  await page.goto("/fr/", { waitUntil: "networkidle" });
  const bytes = await page.evaluate(() => (performance.getEntriesByType("navigation") as PerformanceResourceTiming[])
    .concat(performance.getEntriesByType("resource") as PerformanceResourceTiming[])
    .reduce((n, e) => n + (e.transferSize || e.encodedBodySize || 0), 0));
  expect(bytes, `${bytes} octets transférés`).toBeLessThan(1_000_000);
});
