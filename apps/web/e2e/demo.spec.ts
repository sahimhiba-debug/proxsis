import { expect, test } from "@playwright/test";

// The demo path of « Lundi 8 h à Martigny », screen by screen, in the order of the 12-minute script.
const TEXT = {
  fr: { week: "Ma semaine", call: "Préparer l'appel", rdv: "Rendez-vous obtenu", saved: "noté le", cand: "Candidats proposés",
        redeploy: "Fin de mission, prochaine mission", comp: "Conformité", free: "Publication libre dès le", agency: "Tableau de bord d'agence",
        measures: "Ce qu'on a mesuré", test: "Testez l'app", next: "Suivant", fictif: "Fictif", reel: "Réel" },
  de: { week: "Meine Woche", call: "Anruf vorbereiten", rdv: "Termin vereinbart", saved: "notiert am", cand: "Vorgeschlagene Kandidaten",
        redeploy: "Einsatzende, nächster Einsatz", comp: "Stellenmeldepflicht", free: "Freie Publikation ab", agency: "Filial-Dashboard",
        measures: "Was wir gemessen haben", test: "App testen", next: "Weiter", fictif: "Fiktiv", reel: "Real" },
};
// French interface words that must never appear on a German screen (publication titles stay in their language).
const FR_UI = ["Ma semaine", "Préparer l'appel", "Pourquoi cette entreprise", "Retour d'appel", "Candidats proposés", "Tableau de bord",
  "réseau Flexsis", "lots publiés", "phasage", "candidats fictifs", "Portée", "Vaut pour", "base non configurée", "proposés par"];

test("le parcours de démo se joue sans erreur", async ({ page }, info) => {
  const { lang, offline } = info.project.metadata as { lang: "fr" | "de"; offline: boolean };
  const T = TEXT[lang];
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text()); // a resource that fails to load (a 404) is an error too
  });
  if (offline) {
    await page.route(/^https?:\/\/(?!localhost)/, (r) => r.abort()); // the network is down during the demo
  }

  // 1. The consultant's week (the presentation has its own test: presentation.spec.ts)
  await page.goto(`/${lang}/semaine/M1/`);
  await expect(page).toHaveURL(new RegExp(`/${lang}/semaine/M1/`));

  // 2. Ma semaine: real companies, fictional consultant, simap mention
  await expect(page.getByRole("heading", { level: 1, name: T.week })).toBeVisible();
  await expect(page.getByTestId("company-card").first()).toBeVisible();
  // one line says what is real and what is fictional (futurisme suisse, 06.10.2026)
  await expect(page.getByTestId("demo-banner")).toContainText(lang === "fr" ? "personnes fictives" : "fiktive Personen");
  await expect(page.getByTestId("simap-mention")).toContainText("www.simap.ch font foi");

  // 3. Company sheet → 4. Prepare the call
  await page.getByTestId("company-card").first().getByRole("heading").getByRole("link").click();
  await expect(page.getByTestId("timeline")).toBeVisible();
  const sheet = new URL(page.url()).pathname;
  await page.getByRole("link", { name: T.call }).first().click();
  await expect(page.getByRole("heading", { level: 1, name: T.call })).toBeVisible();
  await expect(page.locator("#fait-1")).toBeVisible();
  // the sentence to say on the phone: the published fact only (Hiba, 07.10.2026)
  // in German, no call sentence is shown as ready until a German speaker has read it: the fact, under review (§ 9)
  if (lang === "fr") await expect(page.getByTestId("phone-line").first()).toContainText("J'ai vu sur simap");
  // the published title, exact and whole, as a quotation under the simple sentence (questionnaire of 07.10.2026, B8)
  if (lang === "fr") await expect(page.getByTestId("phone-title").first()).toBeVisible();
  else await expect(page.getByText("Der deutsche Anrufsatz wird noch von einer deutschsprachigen Person geprüft.").first()).toBeVisible();
  await expect(page.locator("sup a").first()).toBeVisible();

  // 5. The carnet (brief « à distance », § 6): a decision, then what followed the call, dated and apart from the facts
  await page.getByTestId("carnet-appeler").click();
  await expect(page.getByTestId("carnet-appeler")).toHaveAttribute("aria-pressed", "true");
  await page.getByTestId("suite-etape").click();
  await expect(page.getByTestId("field-notes")).toContainText(T.saved);
  // a second touch the same day is not a second call; the chosen outcome shows; a wrong note is taken back
  await page.getByTestId("suite-pasJoint").click();
  await page.getByTestId("suite-pasJoint").click();
  await expect(page.getByTestId("suite-pasJoint")).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByTestId("field-notes").getByRole("listitem")).toHaveCount(2);
  await page.getByTestId("suite-undo").click();
  await expect(page.getByTestId("field-notes").getByRole("listitem")).toHaveCount(1);
  await expect(page.getByTestId("suite-etape")).toHaveAttribute("aria-pressed", "true");

  // 6. Proposed candidates (fictional, with CCT category)
  await page.goto(sheet);
  await page.getByRole("link", { name: T.cand }).click();
  await expect(page.getByRole("heading", { level: 1, name: T.cand })).toBeVisible();
  await expect(page.getByTestId("candidate").first()).toContainText(T.fictif);

  // 7. End of mission, next mission
  await page.goto(`/${lang}/redeploiement/`);
  await expect(page.getByRole("heading", { level: 1, name: T.redeploy })).toBeVisible();
  // one mention in words for the scene (§ 7.1, mixed scene), the figure as a sentence, never a display number
  await expect(page.getByTestId("redeploy-rate")).toContainText(lang === "fr" ? "Intérimaires et missions fictifs" : "Mitarbeitende und Einsätze fiktiv");

  // 8. Compliance: a subject post with its countdown
  await page.goto(`/${lang}/conformite/`);
  await expect(page.getByRole("heading", { level: 1 })).toContainText(T.comp);
  await expect(page.getByTestId("free-date").first()).toContainText(T.free);

  // 9. Agency dashboard (chef d'agence): every figure carries its type
  await page.goto(`/${lang}/agence/martigny/`);
  // under « measured », only what was measured on real public data: no fictional figure there
  const measured = page.locator('section[aria-labelledby="fx-agence-measured"]');
  await expect(measured).toContainText(T.reel);
  await expect(measured).not.toContainText(T.fictif);
  await expect(page.getByRole("heading", { level: 1 })).toContainText(T.agency);
  const kpis = page.getByTestId("kpi");
  await expect(kpis.first()).toBeVisible();
  for (const k of await kpis.all()) await expect(k.locator("[data-kind]")).toHaveCount(1);

  // 10. What we measured
  await page.goto(`/${lang}/mesures/`);
  await expect(page.getByRole("heading", { level: 1, name: T.measures })).toBeVisible();
  await expect(page.locator("#REEL-SPEC-BAT")).toBeVisible();

  if (lang === "de") {
    for (const path of ["/de/semaine/M1/", "/de/entreprise/ent-1ef761b229/", "/de/entreprise/ent-1ef761b229/appel/", "/de/carte/",
      "/de/redeploiement/", "/de/agence/", "/de/conformite/", "/de/presentation/"]) {
      await page.goto(path);
      const body = await page.locator("main").innerText();
      for (const w of FR_UI) expect(body, `${path} : « ${w} »`).not.toContain(w);
    }
  }
  expect(errors, errors.join("\n")).toEqual([]);
});
