"use client";

// Le geste d'Iris sur une carte (suite 8, § 3) : quand un fait mérite l'attention (« Repéré »), toc, et le point se pose
// sur la carte, au coin haut droit, avec un léger rebond. Pour retrouver un rappel, le point est déjà posé sur
// l'étiquette « Rappel du jour ». Le point est la petite diagonale de Proxsis ; l'étiquette ne désigne que sa carte.
// Les cibles portent data-lumiere="…" ; le point se pose dans la scène (il défile avec elle), sans capter le pointeur.
// Mouvement réduit : le point est déjà là, sans chute ni son. (Remplace la visée et le balayage de l'ancienne Iris.)
import { useEffect, useRef, useState } from "react";
import { jouerToc } from "@/iris/sons";
import { GUIDE_COPY } from "./guide";

export interface PlanLumiere {
  visee?: { cible: string; theme: "p" | "c"; tag?: "spotted" | "recall" }; // p : sur le papier ; c : sur le graphite
}

type Boite = [number, number, number, number];

function mesurer(hote: HTMLElement, cible: string): Boite | null {
  const el = hote.querySelector<HTMLElement>(`[data-lumiere="${cible}"]`);
  if (!el) return null;
  const a = el.getBoundingClientRect(), h = hote.getBoundingClientRect();
  if (a.width === 0 && a.height === 0) return null;
  return [a.left - h.left + hote.scrollLeft, a.top - h.top + hote.scrollTop, a.width, a.height];
}

const egal = (a: Boite | null, b: Boite | null) => (a === b) || (!!a && !!b && a.every((v, i) => Math.abs(v - b[i]) < 0.5));

export function Lumiere({ plan, lang, immobile, cle }: { plan: PlanLumiere; lang: "fr" | "de"; immobile: boolean; cle: string }) {
  const g = GUIDE_COPY[lang];
  const ref = useRef<HTMLDivElement>(null);
  const [boite, setBoite] = useState<Boite | null>(null);
  const cv = plan.visee?.cible;
  const tagKind = plan.visee?.tag;

  // la cible : mesurée tant que la scène se pose (ses entrées bougent), puis à chaque redimensionnement
  useEffect(() => {
    const hote = ref.current?.parentElement;
    if (!hote || !cv) return;
    let raf = 0;
    const debut = performance.now();
    const suivre = () => {
      const b = mesurer(hote, cv);
      setBoite((v) => (egal(v, b) ? v : b));
      if (performance.now() - debut < 1400) raf = requestAnimationFrame(suivre);
    };
    raf = requestAnimationFrame(suivre);
    const resize = () => setBoite(mesurer(hote, cv));
    window.addEventListener("resize", resize);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", resize); };
  }, [cv, cle]);

  // le toc, au moment où le point touche la carte (la chute dure 0,42 s) ; pas pour un rappel, déjà posé
  useEffect(() => {
    if (!cv || immobile || tagKind === "recall") return;
    const t = window.setTimeout(jouerToc, 420);
    return () => window.clearTimeout(t);
  }, [cv, cle, immobile, tagKind]);

  const tag = tagKind ? (tagKind === "spotted" ? g.spotted : g.recall) : "";
  return (
    <div ref={ref} className="v-lumiere" aria-hidden data-testid="lumiere">
      {boite && plan.visee ? (
        <div key={`${cv}-${cle}`} className="v-visee" data-theme={plan.visee.theme} data-immobile={immobile || undefined}
          data-pose={tagKind === "recall" || immobile ? "" : undefined} data-testid="visee" data-cible={plan.visee.cible}
          style={{ left: boite[0] + boite[2], top: boite[1] }}>
          <i className="v-point" />
          {tag ? <span className="v-visee-tag">{tag}</span> : null}
        </div>
      ) : null}
    </div>
  );
}
