import { expect, test } from "@playwright/test";
import { ouvrir } from "../attente";

// A finger on the real engines (suite 8, § 8 ; audit of 13.10.2026): on the phone and the tablet of each engine — WebKit is
// the engine of the iPhone and the iPad, where a native menu kept its own small height — every control of the visit's
// header, of the bar of the five times, of the guide and every menu (communes, decisions) is at least 44 × 44 px, at each
// step reached with « Continuer » only.
for (const lang of ["fr", "de"] as const) {
  test(`${lang} : au doigt, chaque commande et chaque menu de la visite fait au moins 44 × 44 px`, async ({ page }, info) => {
    test.skip(info.project.name.endsWith("ordinateur"), "au doigt : téléphone et tablette");
    test.setTimeout(180_000);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await ouvrir(page, `/${lang}/presentation/`);
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    const petits = new Set<string>();
    const next = page.getByRole("button", { name: lang === "fr" ? "Continuer" : "Weiter", exact: true });
    for (let i = 0; i < 30; i++) {
      // toutes les commandes mesurées en un seul appel dans la page (un aller-retour par élément dépassait le temps
      // limite sous WebKit, sur la machine d'intégration) ; visibles = boîte non vide, ni masquées ni cachées
      const tailles = await page.evaluate(() =>
        [...document.querySelectorAll(".d-head-right > *, .v-progress button, [data-testid=guide-ask], .v-main select")]
          .map((el) => ({ el, r: el.getBoundingClientRect(), s: getComputedStyle(el) }))
          .filter(({ r, s }) => r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none")
          .map(({ el, r }) => ({ nom: (el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 24), w: r.width, h: r.height })));
      for (const t of tailles) if (t.w < 43.5 || t.h < 43.5) petits.add(`« ${t.nom} » ${Math.round(t.w)}×${Math.round(t.h)}`);
      // la vue du consultant s'ouvre par-dessus la visite au téléphone : on la referme, comme le ferait le visiteur
      const fermer = page.locator(".v-close:visible").first();
      if (await fermer.isVisible().catch(() => false)) await fermer.click({ timeout: 5000 });
      if (!(await next.isVisible().catch(() => false)) || !(await next.isEnabled().catch(() => false))) break;
      await next.click({ timeout: 5000 });
      await page.waitForTimeout(250);
    }
    expect([...petits], [...petits].join("\n")).toEqual([]);
  });
}
