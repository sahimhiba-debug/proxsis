import { defineConfig, devices } from "@playwright/test";

// The demo and the visit, replayed three times: online (production server), offline (static snapshot, every external
// request blocked) and in German. Uses the installed Chrome (no browser download).
// Prepare once: `npm run e2e:prepare` (static export to out/, then the normal build for `next start`).
// Ports: E2E_PORT (served build, default 3211) and E2E_STATIC_PORT (static copy, default 4310). A server already on one
// of them is never reused (it could be another version): Playwright stops and says the port is taken.
const phone = { ...devices["Pixel 7"], channel: "chrome" as const };
const PORT = Number(process.env.E2E_PORT ?? 3211);
const STATIC_PORT = Number(process.env.E2E_STATIC_PORT ?? 4310);

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  fullyParallel: false,
  reporter: [["list"]],
  projects: [
    { name: "en-ligne", use: { ...phone, baseURL: `http://localhost:${PORT}` }, metadata: { lang: "fr", offline: false } },
    { name: "hors-ligne", use: { ...phone, baseURL: `http://localhost:${STATIC_PORT}` }, metadata: { lang: "fr", offline: true } },
    { name: "allemand", use: { ...phone, baseURL: `http://localhost:${PORT}` }, metadata: { lang: "de", offline: false } },
  ],
  webServer: [
    { command: `npx next start -p ${PORT}`, url: `http://localhost:${PORT}/fr/`, reuseExistingServer: false, timeout: 60_000 },
    { command: `python3 -m http.server ${STATIC_PORT} -d out`, url: `http://localhost:${STATIC_PORT}/fr/`, reuseExistingServer: false },
  ],
});
