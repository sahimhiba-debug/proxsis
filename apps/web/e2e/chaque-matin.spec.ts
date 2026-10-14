import { expect, test } from "@playwright/test";
import matin from "../src/data/direct/matin.json";
import matins from "../src/data/presentation/matins.json";
import lundis from "../src/data/presentation/lundis.json";
import carte from "../src/data/sources/carte.json";
import { openStep, STEP_IDS } from "./etape";

// Suite 10 (Hiba, 13.10.2026): « Chaque matin » and the map of the sources, where they are said — the application (the
// Monday page and its section « Chaque matin, en direct de simap »), the page « Sources et mesures », the visit
// (the first Monday, Iris's answer on the sources, « Choisissez une date ») and the A4 page. FR and DE (DE to review).
const MENTION = "Les données publiées sur la plateforme www.simap.ch font foi.";
const L = (lang: "fr" | "de", fr: string, de: string) => (lang === "fr" ? fr : de);
const morning = (lang: "fr" | "de") => L(lang, "Chaque matin, Iris lit les marchés publics attribués. Le lundi, elle pose les dix points.",
  "Jeden Morgen liest Iris die vergebenen öffentlichen Aufträge. Am Montag setzt sie die zehn Punkte.");
const numbers = (lang: "fr" | "de") => L(lang, `${carte.etudiees} sources étudiées`, `${carte.etudiees} Quellen geprüft`);
const rule = (lang: "fr" | "de") => L(lang, "Proxsis ne lit que ce qu'il a le droit de lire, et ne promet que ce qu'il a mesuré.",
  "Proxsis liest nur, was es lesen darf, und verspricht nur, was es gemessen hat.");
const plain = (s: string) => s.replace(/ /g, " ");

test("l'application : la phrase du lundi, puis la section « Chaque matin, en direct de simap » avec la mention de simap", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/semaine/M1/`);
  await expect(page.getByTestId("chaque-matin-phrase")).toHaveText(morning(lang));
  const section = page.getByTestId("chaque-matin");
  await expect(section.getByRole("heading", { level: 2 })).toHaveText(L(lang, "Chaque matin, en direct de simap", "Jeden Morgen, direkt von simap"));
  await expect(section.getByTestId("live-mention")).toContainText(MENTION);
  await expect(section.getByTestId("matin-iris").getByRole("img")).toBeVisible();
  // the file of the repository waits for the morning job (its start waits for Hiba's agreement); once published, a day
  // with something new or a day without
  await expect(section).toHaveAttribute("data-etat", matin.etat === "en_attente" ? "attente" : matin.marches.length ? "nouveau" : "rien");
});

test("« Sources et mesures » : les vrais nombres du catalogue, la règle, les demandes envoyées, les raisons des sources écartées", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/mesures/`);
  const top = page.getByTestId("sources-carte");
  await expect(top).toContainText(numbers(lang));
  await expect(top).toContainText(L(lang, `${carte.en_service.nombre} en service, ${carte.demandes.nombre} couvertes par une demande d'accès envoyée, ${carte.ecartees.nombre} écartées`,
    `${carte.en_service.nombre} in Betrieb, ${carte.demandes.nombre} mit versandtem Zugangsgesuch, ${carte.ecartees.nombre} ausgeschlossen`));
  await expect(page.getByTestId("sources-regle")).toHaveText(rule(lang));
  const sent = page.locator("[data-testid=source][data-statut=envoyee]");
  await expect(sent).toHaveCount(4);
  await expect(sent.first()).toContainText(L(lang, "Demande envoyée (octobre 2026)", "Gesuch versandt (Oktober 2026)"));
  await expect(page.locator("[data-testid=source][data-source=portail]")).toContainText(L(lang,
    "le Bulletin officiel et le registre du commerce, chaque matin, sans saisie", "das Amtsblatt und das Handelsregister, jeden Morgen"));
  const families = page.getByTestId("ecartee");
  await expect(families).toHaveCount(Object.keys(carte.ecartees.familles).length);
  await expect(families.first()).toContainText(L(lang, "faillites ou les poursuites", "Konkurse oder Betreibungen"));
  await expect(page.locator("#SOURCES-1")).toBeVisible(); // the figures' line of the registry, open on the page
});

test("la visite : la phrase du lundi au premier lundi ; la carte des sources dans la réponse d'Iris sur les sources", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/`);
  await openStep(page, STEP_IDS.indexOf("carte"));
  await expect(page.getByTestId("chaque-matin-visite")).toHaveText(plain(morning(lang)));
  await page.getByTestId("guide-ask").click();
  await page.getByTestId("guide-q-sources").click();
  const line = page.getByTestId("guide-sources-carte");
  await expect(line).toContainText(numbers(lang));
  await expect(line).toContainText(rule(lang));
});

test("« Choisissez une date » : la même section pour le lundi choisi, figée, seulement ce qui était publié avant", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/presentation/`);
  await openStep(page, STEP_IDS.indexOf("date")); // the least favourable Monday, 03.11.2025 (e2e/etape.ts)
  const monday = await page.getByTestId("date-monday").getAttribute("data-monday");
  const frozen = matins.lundis[monday as keyof typeof matins.lundis];
  const details = page.getByTestId("matin-fige");
  await details.locator("summary").click();
  await expect(details.getByTestId("matin-fige-contrat")).toHaveCount(Math.min(frozen.marches.length, 60));
  await expect(details).toContainText(MENTION);
  const ten = new Set(lundis.lundis.find((m) => m.lundi === monday)!.dix.map((c) => c.id));
  const inList = frozen.marches.filter((c) => c.laureats.some((w) => ten.has(w.id))).length;
  await expect(details.getByTestId("in-list")).toHaveCount(frozen.marches.reduce((n, c) => n + c.laureats.filter((w) => ten.has(w.id)).length, 0));
  expect(inList).toBeGreaterThan(0);
});

test("la page A4 : la phrase du lundi et la carte des sources, sur une seule page", async ({ page }, info) => {
  const lang = info.project.metadata.lang as "fr" | "de";
  await page.goto(`/${lang}/une-page/`);
  await expect(page.getByTestId("une-page")).toContainText(plain(morning(lang)));
  await expect(page.getByTestId("une-sources")).toContainText(numbers(lang));
  await expect(page.getByTestId("une-sources")).toContainText(rule(lang));
});
