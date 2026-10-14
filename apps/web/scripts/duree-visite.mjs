// The duration written on the first screen (questionnaire of Hiba, 07.10.2026, B5: « Mesurer la vraie durée, puis
// l'écrire »; CLAIMS PRES-DUREE-1). The director clicks only « Continuer », from the first screen to the conclusion; at
// each gesture we count the words he has on screen without scrolling (visible text, closed details left out), each text
// once per visit. The reading pace is not assumed: it is the one of Iris's voice, measured on her 12 takes (words of
// the transcriptions over the length of the MP3s), a pace read aloud, slower than reading silently: the duration is an
// upper bound. A machine measure, to be confirmed with two people who do not know Proxsis (C5).
//
//   STATIC_EXPORT=1 npx next build && python3 -m http.server 4350 -d out     # the export, served locally
//   node scripts/duree-visite.mjs fr 1440 900 --rythme 178.4                 # FR, computer; then de, and 390 844
import { chromium } from "@playwright/test";

const [lang = "fr", width = "1440", height = "900"] = process.argv.slice(2).filter((a) => !a.startsWith("--") && !/^\d+\.\d+$/.test(a));
const pace = Number(process.argv[process.argv.indexOf("--rythme") + 1]) || 0;
const base = process.env.DUREE_URL ?? "http://localhost:4350";
const L = (fr, de) => (lang === "fr" ? fr : de);
const words = (s) => (s.match(/[\p{L}\p{N}][\p{L}\p{N}'’.,-]*/gu) || []).length;

const browser = await chromium.launch({ channel: "chrome" });
const page = await browser.newPage({ viewport: { width: Number(width), height: Number(height) } });
await page.goto(`${base}/${lang}/`);
await page.waitForTimeout(800);
const onScreen = () => page.evaluate(() => {
  const out = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walk.nextNode(); n; n = walk.nextNode()) {
    const t = n.textContent.replace(/\s+/g, " ").trim();
    const el = n.parentElement;
    if (!t || !el) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden" || cs.display === "none" || Number(cs.opacity) < 0.2) continue;
    if (el.closest("details:not([open]) > :not(summary)") || el.closest("[aria-hidden=true]") || el.closest(".sr-only")) continue;
    const r = document.createRange();
    r.selectNodeContents(n);
    const b = r.getBoundingClientRect();
    if (b.width && b.height && b.bottom > 0 && b.top < innerHeight) {
      out.push((el.closest("[data-testid]")?.getAttribute("data-testid") || el.tagName) + "|" + t);
    }
  }
  return out;
});
const seen = new Set();
const fresh = (texts) => texts.filter((k) => !seen.has(k) && seen.add(k)).reduce((a, k) => a + words(k.split("|").slice(1).join("|")), 0);

const first = fresh(await onScreen());
await page.getByTestId("start").click();
const next = page.getByRole("button", { name: L("Continuer", "Weiter"), exact: true });
const back = page.getByRole("button", { name: L("Revenir à la visite", "Zurück zum Rundgang") });
const end = L("Votre premier lundi.", "Ihr erster Montag.");
let visit = 0;
let gestures = 0;
for (let i = 0; i < 40; i++) {
  await page.waitForTimeout(1200); // the screen settled, as the director reads it
  visit += fresh(await onScreen());
  if ((await page.getByTestId("narration").innerText()).trim() === end) break;
  if (await back.first().isVisible()) await back.first().click(); // on a phone, the consultant's view: back to the visit
  const before = await page.evaluate(() => localStorage.getItem("proxsis.visite.v1"));
  await next.click({ timeout: 15000 });
  await page.waitForFunction((b) => localStorage.getItem("proxsis.visite.v1") !== b, before);
  gestures++;
}
await browser.close();
const total = first + visit;
const minutes = pace ? total / pace : null;
console.log(JSON.stringify({ lang, width: Number(width), height: Number(height), premierEcran: first, visite: visit, total,
  gestes: gestures + 1, rythme: pace || null, minutes: minutes && Math.round(minutes * 10) / 10 }));
