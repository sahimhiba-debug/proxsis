import type { Page } from "@playwright/test";

/**
 * Waits until the screen has settled, in the page and in its frames (the phone of the presentation): fonts loaded, no
 * finite CSS or Web animation running, and no opacity or transform changing for 750 ms (three looks 250 ms apart) —
 * Motion animates some values from JavaScript, outside document.getAnimations(), some after a delay. Endless animations
 * are left aside.
 * Measurements (axe, sizes, positions) are taken on the settled screen, never after a fixed pause.
 */
export async function settled(page: Page): Promise<void> {
  for (const frame of page.frames()) {
    await frame.evaluate(() => document.fonts.ready);
    await frame.waitForFunction(() =>
      document.getAnimations().every((a) => a.playState !== "running" || a.effect?.getTiming().iterations === Infinity));
  }
  const look = () => Promise.all(page.frames().map((frame) => frame.evaluate(() => {
    const endless = new Set(document.getAnimations().filter((a) => a.effect?.getTiming().iterations === Infinity)
      .map((a) => (a.effect as KeyframeEffect | null)?.target));
    return [...document.querySelectorAll("body *")].filter((e) => !endless.has(e))
      .map((e) => { const s = getComputedStyle(e); return `${s.opacity} ${s.transform}`; }).join("|");
  }).catch(() => ""))).then((parts) => parts.join("§"));
  let before = await look();
  let still = 0;
  for (let i = 0; i < 40; i++) {
    await page.waitForTimeout(250);
    const now = await look();
    still = now === before ? still + 1 : 0;
    if (still === 3) return;
    before = now;
  }
  throw new Error("l'écran bouge encore après 10 s");
}

/**
 * Opens a page of the static export. WebKit sometimes waits forever for the end of a load from the local test server
 * (python http.server): without a limit of its own, `goto` then takes the whole test's time. Each navigation gets one
 * minute and, if that is reached, one more try; a text that is really cut is still reported.
 */
export async function ouvrir(page: Page, url: string): Promise<void> {
  try {
    await page.goto(url, { timeout: 60_000 });
  } catch (e) {
    if (!(e instanceof Error) || e.name !== "TimeoutError") throw e;
    await page.goto(url, { timeout: 60_000 });
  }
}
