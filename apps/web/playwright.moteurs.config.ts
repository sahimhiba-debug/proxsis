import { defineConfig, devices, type Project } from "@playwright/test";

// The first screen, the visit and the application on the three browser engines (brief « à distance », § 10): Chrome
// (Chromium), Safari (WebKit) and Firefox, each on a phone, a tablet and a computer, without an account, from the static
// export (what the director receives). Chrome is the installed one; WebKit and Firefox are Playwright's own builds,
// installed in CI (`npx playwright install --with-deps webkit firefox`). On a machine that only has Chrome:
// MOTEURS=chrome.
//
//   npm run build:static        # the export in out/ (or MOTEURS_DIR=<folder>)
//   npm run moteurs             # the nine combinations
//   MOTEURS=chrome npm run moteurs
const PORT = Number(process.env.MOTEURS_PORT ?? 4340);
const DIR = process.env.MOTEURS_DIR ?? "out";
const ENGINES = (process.env.MOTEURS ?? "chrome,webkit,firefox").split(",").map((s) => s.trim());

const phone = { viewport: { width: 390, height: 844 } };
const tablet = { viewport: { width: 820, height: 1180 } };
const computer = { viewport: { width: 1440, height: 900 } };
// Firefox has no mobile emulation (no isMobile): the phone and the tablet are its window at their size, with touch off
const all: Project[] = [
  { name: "chrome-telephone", use: { ...devices["Pixel 7"], channel: "chrome" } },
  { name: "chrome-tablette", use: { ...devices["Galaxy Tab S4"], ...tablet, channel: "chrome" } },
  { name: "chrome-ordinateur", use: { ...devices["Desktop Chrome"], ...computer, channel: "chrome" } },
  { name: "webkit-telephone", use: { ...devices["iPhone 14"] } },
  { name: "webkit-tablette", use: { ...devices["iPad (gen 11)"] } },
  { name: "webkit-ordinateur", use: { ...devices["Desktop Safari"], ...computer } },
  { name: "firefox-telephone", use: { ...devices["Desktop Firefox"], ...phone } },
  { name: "firefox-tablette", use: { ...devices["Desktop Firefox"], ...tablet } },
  { name: "firefox-ordinateur", use: { ...devices["Desktop Firefox"], ...computer } },
];

export default defineConfig({
  testDir: "./e2e/moteurs",
  testMatch: /.*\.moteurs\.ts$/,
  outputDir: "./test-results/moteurs",
  timeout: 120_000,
  fullyParallel: true,
  reporter: [["list"]],
  use: { baseURL: `http://localhost:${PORT}`, locale: "fr-CH", timezoneId: "Europe/Zurich" },
  projects: all.filter((p) => ENGINES.includes(p.name!.split("-")[0])),
  webServer: { command: `python3 -m http.server ${PORT} -d ${DIR}`, url: `http://localhost:${PORT}/fr/`, reuseExistingServer: false,
    stderr: "ignore" }, // the server notes every request
});
