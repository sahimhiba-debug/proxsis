#!/usr/bin/env node
// Les captures de la visite et de l'application, à chaque taille demandée (suite 8, § 8), en français et en allemand,
// avec Chrome (le Chrome du Mac) et WebKit (le moteur de Safari, celui de l'iPhone et de l'iPad), sur la version
// statique du site (apps/web/out, `STATIC_EXPORT=1 npx next build`). Une seule commande pour tout refaire :
//   node scripts/captures/captures.mjs [--moteurs chrome,webkit] [--tailles 390x844,…] [--langues fr,de] [--pages accueil,visite,…]
// Sortie : --sortie <dossier> (par défaut, captures/ à la racine du dépôt, hors Git) : <moteur>/<taille>/<langue>-<n°>-<nom>.png et
// captures.json (la liste, avec les défauts mesurés : débordement horizontal, cibles de moins de 44 px).
import { createReadStream, existsSync, mkdirSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const OUT_SITE = join(ROOT, "apps/web/out");
const require = createRequire(join(ROOT, "apps/web/package.json"));
const { chromium, webkit } = require("@playwright/test");
const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, all) => (x.startsWith("--") ? [...a, [x.slice(2), all[i + 1]]] : a), []));
const SORTIE = resolve(args.sortie || join(ROOT, "captures"));
const MOTEURS = (args.moteurs || "chrome,webkit").split(",");
const TAILLES = (args.tailles || "390x844,375x667,820x1180,1180x820,1024x1366,1440x900,1920x1080").split(",");
const LANGUES = (args.langues || "fr,de").split(",");
const PAGES = (args.pages || "accueil,visite,questions,synthese,direction,une-page,semaine").split(",");

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".png": "image/png", ".webp": "image/webp",
  ".svg": "image/svg+xml", ".json": "application/json", ".woff2": "font/woff2", ".mp3": "audio/mpeg", ".ico": "image/x-icon", ".txt": "text/plain" };
const server = createServer((req, res) => {
  let p = join(OUT_SITE, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (existsSync(p) && statSync(p).isDirectory()) p = join(p, "index.html");
  if (!existsSync(p) && existsSync(`${p}.html`)) p = `${p}.html`;
  if (!p.startsWith(OUT_SITE) || !existsSync(p)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" });
  createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

/** Ce qui ne va pas à l'écran : la page déborde en largeur, des cibles tactiles de moins de 44 px. */
async function defauts(page) {
  return page.evaluate(() => {
    const W = document.documentElement.clientWidth;
    const deborde = document.documentElement.scrollWidth > W + 1;
    // la zone qui répond au doigt : celle du libellé pour une case à cocher ; un lien d'évitement caché (1 × 1 px) ne compte pas
    const zone = (e) => (e.matches("input[type=checkbox], input[type=radio]") && e.closest("label") ? e.closest("label") : e).getBoundingClientRect();
    const petites = [...document.querySelectorAll("a[href], button, [role=button], input, select")]
      .filter((e) => { const r = zone(e); const s = getComputedStyle(e); return r.width > 2 && r.height > 2 && s.visibility !== "hidden" && (r.height < 44 || r.width < 44); })
      .map((e) => `${e.tagName.toLowerCase()}${e.getAttribute("data-testid") ? `[${e.getAttribute("data-testid")}]` : ""} « ${(e.textContent || e.getAttribute("aria-label") || "").trim().slice(0, 30)} » ${Math.round(zone(e).width)}×${Math.round(zone(e).height)}`);
    return { deborde, largeurPage: document.documentElement.scrollWidth, petites: petites.slice(0, 12) };
  });
}

const liste = [];
for (const m of MOTEURS) {
  const browser = m === "webkit" ? await webkit.launch() : await chromium.launch({ channel: "chrome" });
  for (const taille of TAILLES) {
    const [w, h] = taille.split("x").map(Number);
    for (const lang of LANGUES) {
      const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, reducedMotion: "reduce", locale: lang === "fr" ? "fr-CH" : "de-CH" });
      const page = await ctx.newPage();
      const dir = join(SORTIE, m, taille);
      mkdirSync(dir, { recursive: true });
      const prendre = async (n, nom) => {
        await page.waitForTimeout(900); // la fin des fondus (même sans mouvement, certaines entrées durent un instant)
        const f = join(dir, `${lang}-${String(n).padStart(2, "0")}-${nom}.png`);
        await page.screenshot({ path: f, fullPage: false });
        liste.push({ moteur: m, taille, lang, n, nom, fichier: f, ...(await defauts(page)) });
      };
      let n = 0;
      if (PAGES.includes("accueil")) { await page.goto(`${base}/${lang}/`); await prendre(++n, "accueil"); }
      if (PAGES.includes("visite")) {
        await page.goto(`${base}/${lang}/presentation/`);
        await page.evaluate(() => localStorage.clear());
        await page.reload();
        const next = page.getByRole("button", { name: lang === "fr" ? "Continuer" : "Weiter", exact: true });
        for (let i = 0; i < 30; i++) {
          const etape = await page.locator(".v-visit").getAttribute("data-scene").catch(() => "?");
          await prendre(++n, `visite-${String(i).padStart(2, "0")}-${etape}`);
          // la vue du consultant s'ouvre par-dessus la visite au téléphone : on la referme, comme le ferait le visiteur
          const fermer = page.locator(".v-close:visible").first();
          if (await fermer.isVisible().catch(() => false)) { await fermer.click(); await prendre(++n, `visite-${String(i).padStart(2, "0")}-${etape}-fermee`); }
          if (!(await next.isVisible().catch(() => false)) || !(await next.isEnabled().catch(() => false))) break;
          await next.click();
        }
      }
      for (const [cle, chemin] of [["questions", "presentation/questions/"], ["synthese", "presentation/synthese/"], ["direction", "presentation/direction/"], ["une-page", "une-page/"], ["semaine", "semaine/M1/"]]) {
        if (!PAGES.includes(cle)) continue;
        const r = await page.goto(`${base}/${lang}/${chemin}`);
        if (r && r.ok()) await prendre(++n, cle);
      }
      await ctx.close();
    }
  }
  await browser.close();
}
server.close();
writeFileSync(join(SORTIE, "captures.json"), JSON.stringify(liste, null, 2));
const ko = liste.filter((x) => x.deborde);
console.log(`${liste.length} captures · ${ko.length} avec débordement horizontal${ko.length ? ` : ${ko.slice(0, 6).map((x) => `${x.moteur}/${x.taille}/${x.lang}-${x.nom}`).join(", ")}` : ""}`);
