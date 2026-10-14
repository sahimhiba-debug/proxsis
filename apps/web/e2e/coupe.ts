import type { Page } from "@playwright/test";

// Q18 (Hiba, 13.10.2026) : « plus aucun texte coupé au téléphone ». Ce qui se mesure sur une page : un texte coupé par des
// points de suspension, par un débordement caché (en largeur ou en hauteur) ou par le bord de l'écran, un menu dont le
// choix ne tient pas, un texte sous la barre de navigation en bas de page. Utilisé par coupe.spec.ts (Chrome) et
// moteurs/coupe.moteurs.ts (Safari).
export const PAGES = ["/semaine/M1/", "/semaine/S1/", "/semaine/O1/", "/entreprise/ent-1ef761b229/", "/entreprise/ent-1ef761b229/appel/",
  "/entreprise/ent-1ef761b229/candidats/", "/entreprise/ent-866876591f/", "/entreprise/ent-1b28ee92b6/", "/carte/", "/redeploiement/",
  "/conformite/", "/agence/", "/agence/martigny/", "/roi/", "/mesures/", "/", "/semaine/", "/presentation/synthese/",
  "/presentation/preuves/", "/presentation/questions/", "/presentation/equipe/", "/presentation/technique/", "/presentation/feuille-de-route/", "/une-page/"];
export const WIDTHS = [{ width: 360, height: 740 }, { width: 375, height: 667 }, { width: 390, height: 844 }];

/** The texts that do not fit: cut by an ellipsis or a hidden overflow, or running off the screen. */
export function coupes(page: Page) {
  return page.evaluate(() => {
    const out: string[] = [];
    const vw = document.documentElement.clientWidth;
    const said = (el: Element) => (el.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 70);
    const ctx = document.createElement("canvas").getContext("2d");
    for (const el of Array.from(document.querySelectorAll("body *"))) {
      if (!(el instanceof HTMLElement) || !said(el)) continue;
      if (!el.checkVisibility({ visibilityProperty: true, opacityProperty: true })) continue;
      const cs = getComputedStyle(el);
      // the texts for screen readers only are clipped on purpose
      if (cs.position === "absolute" && (cs.clip.startsWith("rect") || cs.clipPath.includes("inset(50%)"))) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) continue;
      const own = Array.from(el.childNodes).some((n) => n.nodeType === Node.TEXT_NODE && (n.textContent ?? "").trim());
      const hidesX = /hidden|clip/.test(cs.overflowX) || cs.textOverflow === "ellipsis";
      const hidesY = /hidden|clip/.test(cs.overflowY) || (cs.getPropertyValue("-webkit-line-clamp") || "none") !== "none";
      // a word wider than its box is broken anywhere (« Einsatzend / e ») unless the browser hyphenates it
      if (own && cs.display !== "inline" && cs.hyphens !== "auto" && ctx) {
        ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        const inner = el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        const spacing = parseFloat(cs.letterSpacing) || 0;
        const words = Array.from(el.childNodes).filter((n) => n.nodeType === Node.TEXT_NODE).flatMap((n) => (n.textContent ?? "").split(/[\s\u00ad]+/));
        for (const w of words) if (w.length > 3 && ctx.measureText(w).width + spacing * w.length > inner + 1) out.push(`mot coupé : « ${w} »`);
      }
      if (hidesX && el.scrollWidth > el.clientWidth + 1) out.push(`coupé en largeur : « ${said(el)} »`);
      else if (hidesY && own && el.scrollHeight > el.clientHeight + 1) out.push(`coupé en hauteur : « ${said(el)} »`);
      else if (own && (r.right > vw + 1 || r.left < -1)) out.push(`hors de l'écran : « ${said(el)} »`);
    }
    // a menu shows its chosen option in its box: the option must fit. The room the menu adds beside its text (the arrow)
    // is measured on the menu itself, at its natural width (its longest option)
    for (const sel of Array.from(document.querySelectorAll("select"))) {
      if (!ctx || !sel.checkVisibility()) continue;
      const cs = getComputedStyle(sel);
      ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
      const width = (t: string) => ctx.measureText(t.trim()).width;
      const shown = sel.clientWidth;
      const style = sel.getAttribute("style");
      sel.style.maxWidth = "none"; sel.style.width = "auto"; sel.style.minWidth = "0";
      const natural = sel.clientWidth;
      if (style === null) sel.removeAttribute("style"); else sel.setAttribute("style", style);
      const room = natural - Math.max(...Array.from(sel.options).map((o) => width(o.textContent ?? "")));
      const text = sel.selectedOptions[0]?.textContent?.trim() ?? "";
      if (text && width(text) + room > shown + 1) out.push(`menu coupé : « ${text} »`);
    }
    return [...new Set(out)];
  });
}

/** At the bottom of a page of the application, the texts under the navigation bar (it is translucent). */
export function sousLaBarre(page: Page) {
  return page.evaluate(async () => {
    window.scrollTo(0, document.documentElement.scrollHeight);
    await new Promise((r) => setTimeout(r, 150));
    const bar = document.querySelector(".fx-tabbar");
    if (!bar || !bar.checkVisibility()) return [];
    const b = bar.getBoundingClientRect();
    const out: string[] = [];
    for (const el of Array.from(document.querySelectorAll("body *"))) {
      if (!(el instanceof HTMLElement) || bar.contains(el) || el.contains(bar)) continue;
      if (getComputedStyle(el).position === "fixed" || el.closest("[class*='fx-tabbar'], dialog")) continue;
      const own = Array.from(el.childNodes).some((n) => n.nodeType === Node.TEXT_NODE && (n.textContent ?? "").trim());
      if (!own || !el.checkVisibility({ visibilityProperty: true, opacityProperty: true })) continue;
      const r = el.getBoundingClientRect();
      if (r.bottom > b.top + 1 && r.top < b.bottom && r.right > b.left && r.left < b.right) {
        out.push(`sous la barre du bas : « ${(el.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 70)} »`);
      }
    }
    return out;
  });
}
