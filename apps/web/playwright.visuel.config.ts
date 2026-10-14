import { defineConfig } from "@playwright/test";

// Visual references of every screen, phone and desktop, French and German: the proof that a change which should not
// touch the screen (refactoring, dependency, date) changes nothing. Served from the static export, every external
// request blocked, motion reduced, clock fixed (see e2e/visuel/ecrans.visuel.ts).
//
//   npm run build:static                      # the export in out/ (or VISUEL_DIR=<folder>)
//   npm run visuel                            # compare with the references
//   npm run visuel -- --update-snapshots      # only after a change of screen that was wanted, reviewed and committed
//
// References depend on the operating system's font rendering: they are kept per platform (macOS today), with the
// version of Chrome that took them (references/<platform>/NAVIGATEUR.txt, checked before any comparison).
const PORT = Number(process.env.VISUEL_PORT ?? 4330);
const DIR = process.env.VISUEL_DIR ?? "out";

export default defineConfig({
  testDir: "./e2e/visuel",
  testMatch: /.*\.visuel\.ts$/,
  snapshotPathTemplate: "{testDir}/references/{platform}/{projectName}/{arg}{ext}",
  outputDir: "./test-results/visuel",
  timeout: 60_000,
  fullyParallel: true,
  reporter: [["list"]],
  expect: {
    toHaveScreenshot: { maxDiffPixels: 0, animations: "disabled", caret: "hide", scale: "css" },
  },
  use: { baseURL: `http://localhost:${PORT}`, channel: "chrome", reducedMotion: "reduce", locale: "fr-CH",
    timezoneId: "Europe/Zurich" },
  projects: [
    { name: "telephone", use: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true } },
    { name: "ordinateur", use: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 } },
  ],
  webServer: { command: `python3 -m http.server ${PORT} -d ${DIR}`, url: `http://localhost:${PORT}/fr/`, reuseExistingServer: false },
});
