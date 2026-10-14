"use client";

// Le logo du premier écran (suite 8, § 4) : les lettres montent, le « i » sans point, Iris entre et frappe : toc, une
// petite onde orange, la diagonale se pose avec un léger rebond ; puis plus rien ne bouge. Une seule fois par visite
// (dans cet onglet). Sans mouvement : le logo complet, le point déjà posé. Le son ne part jamais tout seul : toucher le
// logo arme le son et rejoue le geste (sans mouvement : seulement le toc).
import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { createLogoIris } from "./logo.js";
import { armerSon, jouerToc } from "./sons";

const VU = "proxsis.logo.vu";
const deja = () => { try { return sessionStorage.getItem(VU) === "1"; } catch { return false; } };
const noter = () => { try { sessionStorage.setItem(VU, "1"); } catch { /* sans stockage : il rejouera, c'est tout */ } };
const reduit = () => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function LogoIris({ title, variant = "tampon", className, replay }: {
  title: string; variant?: "tampon" | "chute"; className?: string; replay: string; // replay : « Rejouer le toc »
}) {
  const boite = useRef<HTMLButtonElement>(null);
  const anim = useRef<{ tl: gsap.core.Timeline; tocs: number[] } | null>(null);
  useEffect(() => {
    const el = boite.current;
    if (!el) return;
    el.querySelector("svg")?.remove();
    const immobile = reduit() || deja();
    const a = createLogoIris(el, { gsap, base: "/iris/logo/", ext: "webp", variant, color: "currentColor", reduced: immobile, title });
    el.querySelector("svg")?.setAttribute("aria-hidden", "true"); // le nom est porté par le bouton
    anim.current = immobile ? null : { tl: a.tl, tocs: a.tocs };
    if (!immobile) { a.tl.play(0); noter(); }
    return () => { a.tl.kill(); };
  }, [variant, title]);
  const rejouer = () => {
    armerSon();
    if (reduit() || !anim.current) {
      if (!anim.current && !reduit()) {
        // déjà vu dans cet onglet : on reconstruit l'animation pour la rejouer une fois
        const el = boite.current;
        if (!el) return;
        el.querySelector("svg")?.remove();
        const a = createLogoIris(el, { gsap, base: "/iris/logo/", ext: "webp", variant, color: "currentColor", reduced: false, title });
        el.querySelector("svg")?.setAttribute("aria-hidden", "true");
        anim.current = { tl: a.tl, tocs: a.tocs };
      } else { jouerToc(); return; }
    }
    const { tl, tocs } = anim.current;
    tl.restart();
    tocs.forEach((t) => window.setTimeout(jouerToc, t * 1000));
  };
  return (
    <button ref={boite} type="button" className={["px-logo-iris-btn", className].filter(Boolean).join(" ")} onClick={rejouer}
      aria-label={`${title} · ${replay}`} data-testid="logo-iris" />
  );
}
