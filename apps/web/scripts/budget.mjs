// The phone performance budget (perf-budget.json), checked with Lighthouse on a running production server.
// Usage (from apps/web): npx next build && npx next start -p 3216 &   then   node scripts/budget.mjs http://localhost:3216
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const base = process.argv[2] ?? "http://localhost:3216";
const budget = JSON.parse(readFileSync(new URL("../perf-budget.json", import.meta.url), "utf8"));
const dir = mkdtempSync(join(tmpdir(), "budget-"));
const broken = [];
for (const page of budget.pages) {
  const out = join(dir, `${page.replace(/\W+/g, "_")}.json`);
  execFileSync("npx", ["--yes", `lighthouse@${budget.lighthouse}`, base + page, "--quiet", "--chrome-flags=--headless=new",
    "--output=json", `--output-path=${out}`], { stdio: "ignore" });
  const r = JSON.parse(readFileSync(out, "utf8"));
  const score = (k) => Math.round(r.categories[k].score * 100);
  const a = r.audits;
  const got = {
    performance: score("performance"), accessibility: score("accessibility"), "best-practices": score("best-practices"),
    "largest-contentful-paint-ms": a["largest-contentful-paint"].numericValue, "total-blocking-time-ms": a["total-blocking-time"].numericValue,
    "cumulative-layout-shift": a["cumulative-layout-shift"].numericValue, "total-byte-weight-kib": a["total-byte-weight"].numericValue / 1024,
  };
  for (const [k, min] of Object.entries(budget.minimum)) if (got[k] < min) broken.push(`${page} ${k} ${got[k]} < ${min}`);
  for (const [k, max] of Object.entries(budget.maximum)) if (got[k] > max) broken.push(`${page} ${k} ${Math.round(got[k] * 100) / 100} > ${max}`);
  console.log(page, JSON.stringify(got, (k, v) => (typeof v === "number" ? Math.round(v * 100) / 100 : v)));
}
if (broken.length) {
  console.error(`budget dépassé :\n${broken.join("\n")}`);
  process.exit(1);
}
console.log("budget respecté");
