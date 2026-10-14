// Daily check of the public demo (scripts/production/domaines.json): on every domain, every page answers 200 (after
// redirects), shows its mandatory mentions, carries the security headers and loads nothing from another site; all
// domains serve the same build (same scripts); and the morning section was renewed. Read-only; lists every problem and
// exits 1 if there is one.
// Usage: node scripts/production/controle.mjs [domaine or origin…]   (Node 22, no dependency; e.g. http://localhost:3216)
import { readFileSync } from "node:fs";
import { staleProblem, zurichNow } from "./fraicheur.mjs";

const conf = JSON.parse(readFileSync(new URL("./domaines.json", import.meta.url), "utf8"));
const domains = process.argv.slice(2).length ? process.argv.slice(2) : conf.domaines;
const problems = [];
const builds = new Map(); // domain → sorted script list of its home page

const decode = (html) => html.replace(/&#x27;|&#39;/g, "'").replace(/&amp;/g, "&").replace(/&nbsp;| /g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");

for (const domain of domains) {
  for (const page of conf.pages) {
    const url = `${domain.startsWith("http") ? domain : `https://${domain}`}${page}`;
    let res;
    try {
      res = await fetch(url, { redirect: "follow", signal: AbortSignal.timeout(30_000), headers: { "user-agent": "Proxsis-controle-quotidien" } });
    } catch (e) {
      problems.push(`${url} : injoignable (${e.cause?.code ?? e.name})`);
      continue;
    }
    if (res.status !== 200) { problems.push(`${url} : ${res.status}`); continue; }
    const html = await res.text();
    const text = decode(html);
    for (const m of conf.marqueurs[page] ?? []) if (!text.includes(m)) problems.push(`${url} : mention absente « ${m} »`);
    for (const h of conf.entetes) if (!res.headers.get(h)) problems.push(`${url} : en-tête ${h} absent`);
    // what the page LOADS (scripts, styles, fonts, images, frames); links someone may click are not loads
    const loads = [...html.matchAll(/<(?:script|img|iframe|source)\b[^>]*\ssrc="(https?:\/\/[^"]+)"|<link\b[^>]*\shref="(https?:\/\/[^"]+)"/g)]
      .map((m) => m[1] ?? m[2]);
    const outside = loads.filter((u) => new URL(u).hostname !== new URL(res.url).hostname);
    if (outside.length) problems.push(`${url} : ressource externe ${outside[0]}`);
    if (page === conf.pages[0]) builds.set(domain, [...new Set(html.match(/\/_next\/static\/[^"']+\.js/g) ?? [])].sort().join(" "));
  }
}
// « Chaque matin, en direct de simap » (file of the checked-out default branch): once the section has been published,
// every working day has its reading (fraicheur.mjs, tested by fraicheur.test.mjs), or the morning job did not run
const live = JSON.parse(readFileSync(new URL(`../../${conf.matin_en_direct}`, import.meta.url), "utf8"));
const stale = staleProblem(live, zurichNow());
if (stale) problems.push(stale);

const distinct = new Set([...builds.values()]);
if (distinct.size > 1) problems.push(`les domaines ne servent pas la même version : ${[...builds.keys()].join(", ")}`);

console.log(`Contrôle de ${domains.join(", ")} (${conf.pages.length} pages chacun) : ${problems.length ? `${problems.length} problème(s)` : "tout va bien"}`);
for (const p of problems) console.log(`- ${p}`);
process.exit(problems.length ? 1 : 0);
