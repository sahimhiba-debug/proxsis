import { expect, test } from "@playwright/test";
import team from "../src/data/equipe/equipe.json";
import { openStep, STEP_IDS } from "./etape";

// The visit in five times (brief « à distance », § 4): the five times and the conclusion in a bar, « Continuer » and
// « Retour », skipping a time, going straight to the conclusion, coming back later to the same place, switching the
// language without losing the place, and the same without storage (private browsing). FR and DE.
test("visite : avancer, sauter, conclure, reprendre au même endroit, changer de langue", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  const other = lang === "fr" ? "de" : "fr";
  const L = (fr: string, de: string, l: "fr" | "de" = lang) => (l === "fr" ? fr : de);
  await page.goto(`/${lang}/presentation/`);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  const step = page.getByTestId("visit-step");
  await expect(step).toHaveText(L("Temps 1 sur 5", "Schritt 1 von 5"));
  await expect(page.getByRole("navigation", { name: L("Les cinq temps de la visite", "Die fünf Schritte des Rundgangs") })
    .getByRole("button")).toHaveCount(7); // the five times, the conclusion, the four questions
  await expect(page.getByTestId("general-mention")).toContainText(L("Démonstration · entreprises réelles, personnes fictives",
    "Demonstration · echte Unternehmen, fiktive Personen"));
  if (lang === "de") await expect(page.getByTestId("review-mention")).toBeVisible();

  // time 1, the map: Saxon prepared, its companies « in our data » (seat here); another commune from the list; a
  // company opened turns the map into its dossier
  await expect(page.getByTestId("commune-name")).toContainText("Saxon");
  await expect(page.getByTestId("commune-name")).toContainText(L("exemple préparé", "vorbereitetes Beispiel"));
  await expect(page.getByTestId("seat-company").first()).toContainText("Joseph Carron SA");
  await page.getByRole("combobox", { name: L("Commune", "Gemeinde") }).selectOption({ label: "Sion" });
  await expect(page.getByTestId("commune-name")).toHaveText("Sion");
  await expect(page.getByTestId("seat-company")).not.toHaveCount(0);
  await page.getByTestId("seat-company").first().click();
  await expect(page.getByTestId("narration")).toHaveText(L("Une entreprise réelle. Une raison publiée. Une question à poser.",
    "Ein echtes Unternehmen. Ein publizierter Grund. Eine Frage, die Sie stellen können."));
  // the publication on paper first; our reading only after « Continuer »; in German, no call sentence shown as ready
  await expect(page.getByTestId("publication")).toContainText("simap.ch");
  // simap's content apart from ours: the mandatory mention on the paper itself, our count of contracts off the paper
  await expect(page.getByTestId("paper-mention")).toContainText("Les données publiées sur la plateforme www.simap.ch font foi.");
  await expect(page.getByTestId("publication").getByTestId("count")).toHaveCount(0);
  await expect(page.getByTestId("count")).toBeVisible();
  await expect(page.getByTestId("question")).toHaveCount(0);
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await expect(page.getByTestId("question")).toBeVisible();
  if (lang === "de") await expect(page.getByTestId("question-review")).toBeVisible();
  else await expect(page.getByTestId("question")).toContainText("J'ai vu sur simap que vous avez remporté");

  // the carnet: the prepared example (« À appeler », handed over), then his own choice: set aside with a reason; the
  // consultant's view (« Continuer ») does not get the lead
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await expect(page.getByTestId("carnet")).toContainText(L("exemple préparé", "vorbereitetes Beispiel"));
  await page.getByTestId("decide-ecarter").click();
  await page.getByRole("button", { name: L("déjà client", "bereits Kunde") }).click();
  await expect(page.getByTestId("carnet")).not.toContainText(L("exemple préparé", "vorbereitetes Beispiel"));
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await expect(page.getByTestId("consultant-set-aside")).toBeVisible();
  // on a phone the consultant's view opens full screen (no drawn phone): back to the visit
  const back = page.getByRole("button", { name: L("Revenir à la visite", "Zurück zum Rundgang") }).first();
  if (await back.isVisible()) await back.click();
  await page.getByTestId("decide-appeler").click();
  await page.getByTestId("confide").click();
  await expect(page.locator("[data-testid=consultant-row][data-confided]")).toHaveCount(1);

  // time 2: the following Monday keeps the decisions (the prepared examples: one set aside, one to look at again)
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await expect(page.getByTestId("narration")).toHaveText(L("Le lundi suivant, vous ne recommencez pas à zéro.",
    "Am nächsten Montag fangen Sie nicht bei null an."));
  await expect(page.getByTestId("next-monday")).toHaveCount(0);
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await expect(page.getByTestId("next-set-aside")).toContainText("Bitz travaux publics SA");
  await expect(page.locator("[data-testid=next-row][data-kind=recall]")).toContainText("MELLY CONSTRUCTIONS SA");
  await expect(page.getByTestId("next-row")).toHaveCount(10);
  await expect(page.getByText(L("Le premier lundi, Proxsis apporte une information.", "Am ersten Montag bringt Proxsis eine Information."))).toBeInViewport();

  // a time skipped from the bar, its gestures revealed by « Continuer », then the next time
  await page.getByRole("button", { name: L("3 Une date", "3 Ein Datum") }).click();
  await expect(step).toHaveText(L("Temps 3 sur 5", "Schritt 3 von 5"));
  await expect(page.getByTestId("narration")).toHaveText(L("Et la liste, vaut-elle quelque chose ? Choisissez une date.",
    "Und die Liste, ist sie etwas wert? Wählen Sie ein Datum."));
  const next = page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true });
  await next.click();
  await expect(page.getByTestId("date-count")).toBeVisible();
  await next.click();
  await expect(page.getByTestId("date-aveu")).toBeVisible();
  // the confession is about another, wider test than the measure just shown: its scope right under it
  await expect(page.getByTestId("date-aveu-scope")).toContainText(L("Suisse romande, vingt entreprises par semaine pendant 44 semaines",
    "Westschweiz, zwanzig Unternehmen pro Woche während 44 Wochen"));
  await expect(page.getByTestId("date-all")).toContainText(L("Les deux premiers ne sont pas proposés au choix", "Die ersten zwei sind nicht wählbar"));
  await next.click();
  await expect(step).toHaveText(L("Temps 4 sur 5", "Schritt 4 von 5"));
  // time 4: the threshold with the example values; « Deux fois moins » shows a loss, which stays; the threshold stays
  await expect(page.getByTestId("seuil-main")).toHaveText(L("Il suffit de 44 journées supplémentaires facturées pour couvrir le coût.",
    "Es braucht 44 zusätzlich verrechnete Tage, um die Kosten zu decken."));
  await page.getByRole("button", { name: L("Deux fois moins", "Halb so viel") }).click();
  await expect(page.getByTestId("seuil-net")).toHaveAttribute("data-negative", "true");
  await page.getByTestId("seuil-marginPerDay").fill("200");
  await expect(page.getByTestId("seuil-main")).toContainText("22");

  // time 5: « Nous continuerons si… », an indicator and a threshold; then the conclusion: his choices, the rest marked
  // as prepared examples; the e-mail carries no amount in francs unless he asks for it
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await page.getByRole("button", { name: L("les conversations utiles", "die nützlichen Gespräche") }).click();
  await page.getByTestId("pilot-threshold").fill("4");
  await expect(page.getByTestId("pilot-sentence")).toContainText(L("au moins 4 appels préparés sur 10", "mindestens 4 von 10"));
  await page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true }).click();
  await expect(page.getByTestId("recap-critere")).toContainText(L("au moins 4 appels préparés sur 10", "mindestens 4 von 10"));
  await expect(page.getByTestId("recap-critere")).not.toHaveAttribute("data-example");
  await expect(page.getByTestId("recap-seuil")).not.toHaveAttribute("data-example");
  const mail = page.getByTestId("email-link");
  await expect(mail).not.toHaveAttribute("href", /CHF/);
  await page.getByLabel(L("Inclure mes hypothèses (montants en francs)", "Meine Annahmen einschliessen (Beträge in Franken)")).check();
  await expect(mail).toHaveAttribute("href", /CHF/);
  // the discreet pages: « Qui sommes-nous » shows the members Hiba gave, as she wrote them, and no empty slot (suite 6,
  // § 5): no « À compléter », no contact line while she has given none
  await page.getByRole("link", { name: L("Qui sommes-nous", "Wer wir sind") }).click();
  await expect(page.getByTestId("team-member")).toHaveText(team.membres.map((m) => `${m.nom}, ${m.role}`));
  await expect(page.locator("main")).not.toContainText(/À compléter|Noch zu ergänzen|null/);
  await expect(page.getByTestId("team-contact")).toHaveCount(team.contact ? 1 : 0);
  await page.getByRole("link", { name: L("Revenir à la visite", "Zurück zum Rundgang") }).click();
  await expect(step).toHaveText(L("Conclusion", "Abschluss"));
  await page.getByRole("button", { name: L("Retour", "Zurück"), exact: true }).click();
  await page.getByRole("button", { name: L("Retour", "Zurück"), exact: true }).click();

  // back to the date: shown complete
  await page.getByRole("button", { name: L("Retour", "Zurück"), exact: true }).click();
  await expect(page.getByTestId("date-aveu")).toBeVisible();

  // straight to the conclusion, then come back later: the same place
  await page.getByRole("button", { name: L("Aller à la conclusion", "Zum Abschluss") }).click();
  await expect(step).toHaveText(L("Conclusion", "Abschluss"));
  await page.reload();
  await expect(step).toHaveText(L("Conclusion", "Abschluss"));
  await expect(page.getByRole("status")).toHaveText(L("Vous reprenez là où vous vous étiez arrêté.", "Sie machen dort weiter, wo Sie aufgehört haben."));

  // the language changes, the place stays
  await page.getByRole("link", { name: L("Deutsch", "Français") }).click();
  await expect(page).toHaveURL(new RegExp(`/${other}/presentation/`));
  await expect(step).toHaveText(L("Conclusion", "Abschluss", other));
});

test("visite sans conservation locale (navigation privée) : elle fonctionne quand même", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.addInitScript(() => {
    Object.defineProperty(window, "localStorage", { get() { throw new DOMException("refusé", "SecurityError"); } });
  });
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(`/${lang}/presentation/`);
  await page.getByRole("button", { name: lang === "fr" ? "Continuer" : "Weiter", exact: true }).click();
  await expect(page.getByTestId("visit-step")).toHaveText(lang === "fr" ? "Temps 1 sur 5" : "Schritt 1 von 5");
  await expect(page.getByTestId("narration")).toHaveText(lang === "fr" ? "Une entreprise réelle. Une raison publiée. Une question à poser."
    : "Ein echtes Unternehmen. Ein publizierter Grund. Eine Frage, die Sie stellen können.");
  expect(errors).toEqual([]);
});

test("mode présentateur : la fenêtre des notes et la visite avancent ensemble", async ({ page, context }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  await page.goto("/fr/presentation/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  const notes = await context.newPage();
  await notes.goto("/fr/presentation/notes/");
  await expect(notes.getByTestId("notes-narration")).toHaveText("Lundi, 8 h 03. Quelle entreprise mérite votre premier appel ?");
  await notes.getByRole("button", { name: "Continuer", exact: true }).click();
  await expect(page.getByTestId("narration")).toHaveText("Une entreprise réelle. Une raison publiée. Une question à poser.");
  await page.getByRole("button", { name: "Retour", exact: true }).click();
  await expect(notes.getByTestId("notes-narration")).toHaveText("Lundi, 8 h 03. Quelle entreprise mérite votre premier appel ?");
});

// The new moments (brief of 07.10.2026, § 3.2 to 3.4): « Cette semaine » at the opening of the first Monday, with the
// incomplete week said; the published facts that go the same way, in the three guided dossiers only (a Bulletin
// officiel request: the company's role, never the applicant); « celles qui accélèrent » after the result, before the
// confession, which stays. Every number comes from its file (moments.test.ts ties them to CLAIMS).
test("visite : cette semaine, les faits qui vont dans le même sens, celles qui accélèrent", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  const L = (fr: string, de: string) => (lang === "fr" ? fr : de);
  const at = async (step: number, reveal: number, company: string | null) => {
    await page.goto(`/${lang}/presentation/`);
    await page.evaluate(([s, r, c]) => localStorage.setItem("proxsis.visite.v1", JSON.stringify({ version: 1, step: s, reveal: r,
      commune: null, agence: null, company: c, carnet: {}, monday: null, seuil: null, half: false, pilot: null, source: null })),
    [step, reveal, company] as const);
    await page.reload();
  };
  await at(0, 0, null);
  await expect(page.getByTestId("cette-semaine")).toContainText(L(
    "La semaine du 21 au 27 septembre 2026, Proxsis a lu 130 publications, en a retenu 15, et vous prépare 10 appels.",
    "In der Woche vom 21. bis 27. September 2026 hat Proxsis 130 Publikationen gelesen, 15 davon ausgewählt und bereitet Ihnen 10 Anrufe vor."));
  await expect(page.getByTestId("cette-semaine-note")).toContainText(L("La dernière semaine complète des données de la démonstration.",
    "Die letzte vollständige Woche der Demonstrationsdaten."));

  // the prepared dossier (Saxon): its count and its last award, which is the publication above
  await at(1, 0, null);
  const faits = page.getByTestId("faits");
  await expect(faits).toContainText(L("Quand plusieurs faits publiés vont dans le même sens, la raison d'appeler est plus solide.",
    "Wenn mehrere publizierte Fakten in dieselbe Richtung weisen, ist der Grund für den Anruf solider."));
  await expect(page.getByTestId("faits-compte")).toContainText("11");
  // its latest award and its three other recent ones (questionnaire of Hiba, 07.10.2026, A4)
  await expect(faits.getByTestId("fait")).toHaveCount(4);
  await expect(faits.getByTestId("fait").first()).toContainText("12.08.2026");
  await expect(faits.getByTestId("fait").last()).toContainText("13.05.2026");
  await expect(page.getByTestId("count")).toHaveCount(0);

  // Bitz: three requests where it drew the plans, with the nuance of CLAIMS, never the applicant, no link
  await at(1, 0, "ent-734d5f7d45");
  await expect(faits.getByTestId("fait")).toHaveCount(4);
  const requests = faits.locator('[data-type="demande_autorisation"]');
  await expect(requests).toHaveCount(3);
  await expect(requests.getByRole("link")).toHaveCount(0);
  await expect(requests.getByRole("button")).toHaveCount(0);
  await expect(page.getByTestId("faits-plans")).toBeVisible();
  await expect(faits).not.toContainText(L("requérant", "Gesuchsteller"));

  // a dossier that is not guided: no such block, its count as before
  await at(1, 0, "ent-034c9b5b0e");
  await expect(page.getByTestId("dossier")).toHaveAttribute("data-company", "ent-034c9b5b0e");
  await expect(faits).toHaveCount(0);
  await expect(page.getByTestId("count")).toBeVisible();

  // « Une date », every Monday shown: the rates, then the confession, unchanged
  await at(4, 2, null);
  const accel = page.getByTestId("accelerent");
  await expect(accel).toContainText("38,3 %");
  await expect(accel).toContainText("17,3 %");
  await expect(accel).toContainText(L("pas une prévision", "keine Vorhersage"));
  await expect(page.getByTestId("date-aveu")).toBeVisible();
  const [a, b] = [await accel.boundingBox(), await page.getByTestId("date-aveu").boundingBox()];
  expect(a!.y).toBeLessThan(b!.y);
});

// The director's mode (brief of 07.10.2026, suite 2, § 5): four questions, four answers of one sentence, each leading to
// the time of the visit that shows it; from the first screen and from the bar; Escape closes, the focus comes back.
test("visite : quatre questions, quatre réponses", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  const L = (fr: string, de: string) => (lang === "fr" ? fr : de);
  await page.goto(`/${lang}/`);
  await page.evaluate(() => localStorage.clear());
  await page.getByTestId("questions-link").click();
  const dialog = page.getByRole("dialog", { name: L("Quatre questions, quatre réponses", "Vier Fragen, vier Antworten") });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByTestId("question-item")).toHaveCount(4);
  await expect(dialog).toContainText(L("Qui appeler lundi ?", "Wen rufe ich am Montag an?"));
  await dialog.getByRole("button", { name: L("Voir : le seuil", "Ansehen: die Schwelle") }).click();
  await expect(dialog).toHaveCount(0);
  await expect(page.getByTestId("narration")).toHaveText(L("Combien de journées supplémentaires facturées faut-il pour couvrir le coût ?",
    "Wie viele zusätzlich verrechnete Tage braucht es, um die Kosten zu decken?"));
  // from the bar: Escape closes it and gives the focus back to the button that opened it
  const open = page.getByTestId("open-questions");
  await open.click();
  await expect(dialog).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  await expect(open).toBeFocused();
  await expect(page.getByTestId("narration")).toHaveText(L("Combien de journées supplémentaires facturées faut-il pour couvrir le coût ?",
    "Wie viele zusätzlich verrechnete Tage braucht es, um die Kosten zu decken?"));
});

// The proof he runs himself (suite 2, § 6) and the future in three steps (§ 7), with « Iris demain » (suite 3, § 3) and
// the years ahead with their sources, in « Une décision » and in the conclusion.
test("visite : la preuve sur le passé, l'avenir en trois étapes, Iris demain", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  const L = (fr: string, de: string) => (lang === "fr" ? fr : de);
  const at = async (step: number) => {
    await page.goto(`/${lang}/presentation/`);
    await page.evaluate((s) => localStorage.setItem("proxsis.visite.v1", JSON.stringify({ version: 1, step: s, reveal: 0,
      commune: null, agence: null, company: null, carnet: {}, monday: null, seuil: null, half: false, pilot: null, source: null })), step);
    await page.reload();
  };
  await at(4);
  await expect(page.getByTestId("preuve")).toHaveText(L(
    "Mettez Proxsis à l'épreuve : choisissez un lundi passé, et regardez ce qui s'est passé ensuite.",
    "Stellen Sie Proxsis auf die Probe: Wählen Sie einen vergangenen Montag und sehen Sie, was danach geschah."));
  for (const step of [6, 7]) {
    await at(step);
    const avenir = page.getByTestId("avenir");
    await expect(avenir.getByRole("heading", { level: 2 })).toHaveText(L("Si la solution vous intéresse", "Wenn die Lösung Sie interessiert"));
    await expect(avenir.getByTestId("avenir-step")).toHaveCount(3);
    // suite 8, § 6: in step 3, the passage on Apertus (Hiba's words), and no other provider named
    await expect(avenir.getByTestId("avenir-step").nth(2)).toContainText(L("Ici, ils resteraient chez vous.", "Hier würden sie bei Ihnen bleiben."));
    await expect(avenir).not.toContainText(/OpenAI|Anthropic/);
    await expect(avenir.getByTestId("avenir-step").first()).toContainText(L("Vous pouvez arrêter", "Sie können aufhören"));
    // suite 9, § 8: the third step says the door, word for word
    await expect(avenir.getByTestId("avenir-porte")).toHaveText(L(
      "Si les résultats sont là : Iris installée chez Flexsis, avec Apertus adapté à ses données, chez elle.",
      "Wenn die Ergebnisse stimmen: Iris bei Flexsis eingerichtet, mit Apertus, angepasst an ihre Daten, bei ihr im Haus."));
    // the door, « Demain, si Flexsis le souhaite »: closed at first, then the agent, Apertus on their servers, Iris's
    // sentence of the silence in the future, its guardrails with it (on a phone, under « En savoir plus »); a possible
    // future, said so
    const iris = avenir.getByTestId("iris-demain");
    await expect(iris).not.toHaveAttribute("open");
    await expect(iris.locator("summary")).toHaveText(L("Demain, si Flexsis le souhaite", "Morgen, wenn Flexsis es wünscht"));
    await iris.locator("summary").click();
    await expect(iris).toContainText(L("un agent qui lit les publications chaque matin et propose les appels.",
      "ein Agent, der jeden Morgen die Publikationen liest und die Anrufe vorschlägt."));
    await expect(iris).toContainText(L("Sur vos serveurs ou chez un hébergeur suisse. Vos données ne sortiraient jamais.",
      "Auf Ihren Servern oder bei einem Schweizer Hoster. Ihre Daten würden das Haus nie verlassen."));
    await expect(iris.getByTestId("porte-silence")).toContainText(L("Et si une source se tait, je vous le dirai.",
      "Und wenn eine Quelle verstummt, werde ich es Ihnen sagen."));
    await expect(iris).toContainText(L("rien de cela n'existe aujourd'hui", "Nichts davon existiert heute"));
    await expect(iris.getByTestId("porte-garde-fous")).toBeHidden();
    await iris.getByTestId("plus").click();
    await expect(iris.getByTestId("porte-garde-fous")).toBeVisible();
    await expect(iris.getByTestId("porte-garde-fous")).toContainText(L("Iris proposera, le consultant décidera, toujours.",
      "Iris wird vorschlagen, die Beraterin oder der Berater wird entscheiden, immer."));
    await expect(iris.getByTestId("porte-garde-fous")).toContainText(L(
      "Les données de Flexsis resteront sous son contrôle, en Suisse, avec son accord écrit.",
      "Die Daten von Flexsis werden unter ihrer Kontrolle bleiben, in der Schweiz, mit ihrer schriftlichen Zustimmung."));
    await expect(iris).not.toContainText(/\bIA\b|\bKI\b/);
    await expect(page.getByTestId("years").getByRole("link")).toHaveCount(2);
  }
});

// « Pour votre direction » (suite 2, § 8): reached by a discreet link from the conclusion; the sentence to remember, the
// proof over the Mondays of the measure with its line of the registry, the group's goals in its words with their
// sources, the group and any person never named; the door (suite 9, § 8) said as a possible future; one A4 sheet.
test("visite : une page pour votre direction", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  const L = (fr: string, de: string) => (lang === "fr" ? fr : de);
  await page.goto(`/${lang}/presentation/`);
  await page.evaluate(() => localStorage.setItem("proxsis.visite.v1", JSON.stringify({ version: 1, step: 7, reveal: 0, commune: null,
    agence: null, company: null, carnet: {}, monday: null, seuil: null, half: false, pilot: null, source: null })));
  await page.reload();
  await page.getByTestId("direction-link").click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(L("Pour votre direction", "Für Ihre Geschäftsleitung"));
  const main = page.getByTestId("pour-direction");
  await expect(page.getByTestId("direction-retenir")).toContainText(L("Chaque lundi, chaque consultant sait", "Jeden Montag weiss"));
  await expect(page.getByTestId("direction-preuve")).toContainText("57");
  await expect(page.getByTestId("direction-preuve")).toContainText("66,8");
  await expect(page.getByTestId("direction-preuve")).toContainText("20,7");
  // its line of the registry: in the page (on a phone, under « En savoir plus »)
  await expect(page.getByTestId("direction-preuve").locator("a")).toHaveAttribute("href", `/${lang}/mesures/#PRES-DATE-1`);
  await expect(page.getByTestId("direction-buts").locator("[data-claims]")).toHaveCount(4);
  await expect(main).toContainText("07.10.2026");
  await expect(main).not.toContainText(/interiman/i);
  await expect(main.locator('a[href*="interiman"]')).toHaveCount(0);
  await expect(page.getByTestId("direction-iris")).toContainText(L("Rien de cela n'existe aujourd'hui", "Nichts davon existiert heute"));
  await expect(page.getByTestId("direction-iris")).toContainText(L("Ici, ils resteraient chez vous.", "Hier würden sie bei Ihnen bleiben."));
  // suite 9, § 8: the door, its title, the agent, its guardrails, and the three steps (the third one: Iris at Flexsis)
  await expect(page.getByTestId("direction-iris").getByRole("heading", { level: 2 })).toHaveText(L("Demain, si Flexsis le souhaite", "Morgen, wenn Flexsis es wünscht"));
  await expect(page.getByTestId("direction-iris")).toContainText(L("un agent qui lit les publications chaque matin", "ein Agent, der jeden Morgen die Publikationen liest"));
  await expect(page.getByTestId("direction-garde-fous").locator("li")).toHaveCount(5);
  await expect(page.getByTestId("direction-avenir").locator("li")).toHaveCount(3);
  await expect(page.getByTestId("direction-avenir").locator("li").nth(2)).toContainText(L(
    "Si les résultats sont là : Iris installée chez Flexsis, avec Apertus adapté à ses données, chez elle.",
    "Wenn die Ergebnisse stimmen: Iris bei Flexsis eingerichtet, mit Apertus, angepasst an ihre Daten, bei ihr im Haus."));
  await expect(main).not.toContainText(/OpenAI|Anthropic|\bIA\b|\bKI\b/);
  await expect(page.getByRole("button", { name: L("Enregistrer en PDF", "Als PDF speichern") })).toBeVisible();
  // a page to pass on: one A4 sheet on paper, the door included
  const pdf = await page.pdf({ format: "A4", printBackground: true });
  expect((pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) ?? []).length, "pages imprimées").toBe(1);
});

// Suite 9, Q08: in « Qui proposer ? », one short and honest sentence on fairness (CLAIMS EQ-1, fictional people), no figure
const EQUITE = {
  fr: "Le genre, l'âge et la nationalité n'entrent pas dans le choix. L'expérience compte : les plus jeunes sont donc un peu moins souvent proposés. Nous mesurons cet écart (pour l'instant sur des personnes fictives).",
  de: "Geschlecht, Alter und Nationalität fliessen nicht in die Auswahl ein. Erfahrung zählt: Jüngere werden deshalb etwas seltener vorgeschlagen. Wir messen diesen Unterschied (vorerst mit fiktiven Personen).",
};
test("« Qui proposer ? » dit ce qui entre dans le choix, et ce qui n'y entre pas (Q08)", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/`);
  await openStep(page, STEP_IDS.indexOf("dossier"));
  const equite = page.getByTestId("who-to-propose").getByTestId("who-equity").first();
  await expect(equite).toBeVisible();
  expect((await equite.innerText()).replace(/\u00a0/g, " ")).toBe(EQUITE[lang]);
});
