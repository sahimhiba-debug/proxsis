import { expect, test } from "@playwright/test";
import { settled } from "./attente";

// WCAG 2.4.11: the element that receives the keyboard focus is never hidden, neither under the sticky header nor under
// the floating tab bar, nor below the bottom of the screen (forwards and backwards, phone and laptop).
const PAGES = ["/fr/semaine/M1/", "/fr/entreprise/ent-1ef761b229/", "/fr/entreprise/ent-1ef761b229/appel/",
  "/de/entreprise/ent-1ef761b229/appel/", "/fr/carte/", "/fr/redeploiement/", "/de/redeploiement/"];
const SIZES = [[390, 844], [1366, 768], [1440, 900]] as const;

for (const [w, h] of SIZES) {
  test(`le focus clavier reste visible en ${w} × ${h}`, async ({ page }, info) => {
    test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
    test.setTimeout(240_000);
    await page.setViewportSize({ width: w, height: h });
    await page.emulateMedia({ reducedMotion: "reduce" });
    const hidden: string[] = [];
    for (const path of PAGES) {
      await page.goto(path);
      await settled(page);
      for (const key of ["Tab", "Shift+Tab"]) {
        await page.evaluate(() => { (window as unknown as { seen: WeakSet<Element> }).seen = new WeakSet(); });
        for (let i = 0; i < 200; i++) {
          await page.keyboard.press(key);
          const r = await page.evaluate(() => {
            const el = document.activeElement as HTMLElement | null;
            if (!el || el === document.body) return null;
            const seen = (window as unknown as { seen: WeakSet<Element> }).seen;
            if (seen.has(el)) return { name: "", covered: false, again: true };
            seen.add(el);
            const name = `${el.tagName.toLowerCase()} « ${(el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 40)} »`;
            const bars = [document.querySelector(".fx-head"), document.querySelector(".fx-tabbar")];
            if (bars.some((b) => b?.contains(el))) return { name, covered: false };
            // each line box of the element (a link may wrap): its top, middle and bottom must show the element itself
            const boxes = [...el.getClientRects()].filter((b) => b.height > 0 && b.width > 0);
            let covered = false;
            for (const b of boxes) {
              const x = Math.min(Math.max(b.left + b.width / 2, 1), innerWidth - 1);
              for (const y of [b.top + 2, b.top + b.height / 2, b.bottom - 2]) {
                if (y < 0 || y > innerHeight) { covered = true; break; }
                const at = document.elementFromPoint(x, y);
                if (!at || !(el.contains(at) || at.contains(el))) { covered = true; break; }
              }
            }
            return { name, covered };
          });
          if (!r) continue;
          if ("again" in r) break; // the whole page has been walked through
          if (r.covered) hidden.push(`${path} ${key} : ${r.name}`);
        }
      }
    }
    expect(hidden, hidden.join("\n")).toEqual([]);
  });
}

// The head of a dossier or of a call card stays in view while the evidence scrolls only when it fits whole under the
// page header; otherwise it scrolls with the page (nothing of it is ever out of reach). The tallest heads measured.
test("l'en-tête collant d'un dossier ou d'une fiche d'appel tient toujours dans l'écran", async ({ page }, info) => {
  test.skip(info.project.name !== "en-ligne", "une seule passe suffit");
  test.setTimeout(120_000);
  const over: string[] = [];
  for (const [w, h] of [[1280, 720], [1280, 800], [1366, 768], [1440, 900], [1920, 1080]] as const) {
    await page.setViewportSize({ width: w, height: h });
    for (const path of ["/de/entreprise/ent-9ee20debe5/", "/fr/entreprise/ent-9ee20debe5/", "/de/entreprise/ent-1ef761b229/appel/",
      "/fr/entreprise/ent-1ef761b229/appel/"]) {
      await page.goto(path);
      const r = await page.evaluate(() => {
        const head = document.querySelector(".fx-dossier-head") as HTMLElement;
        const sticky = getComputedStyle(head).position === "sticky";
        return { sticky, bottom: parseFloat(getComputedStyle(head).top || "0") + head.getBoundingClientRect().height };
      });
      if (r.sticky && r.bottom > h) over.push(`${w} × ${h} ${path} : ${Math.round(r.bottom - h)} px hors écran`);
    }
  }
  expect(over, over.join("\n")).toEqual([]);
});
