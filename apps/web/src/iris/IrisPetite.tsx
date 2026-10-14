"use client";

// La petite Iris (suite 8, § 3) : debout sur son manche, tournée vers l'information, dans un coin de l'écran. Ses gestes :
// - elle veille : les yeux calmes, un clignement de temps en temps ;
// - elle regarde une information : ses yeux se tournent vers elle (`regard`) ;
// - elle repère (« Repéré ») : un petit toc, elle frappe l'air d'un coup de tête (`toc` change) ;
// - elle accompagne un choix : ses yeux deviennent contents (`humeur` = « contente ») ;
// - une source se tait : ses yeux deviennent inquiets (`humeur` = « inquiete »).
// Les images viennent de vues.jpg (scripts/mascotte/petite.py, web.py). Mouvement réduit : immobile, les humeurs changent
// sans transition. Elle ne choisit jamais : elle prévient et se pose pendant la lecture.
import { useEffect, useState } from "react";
import meta from "./iris-meta.json";

const P = meta.petite; // 183 × 240 (repère des images)
const GLOW = "#FFF4D8";

export type Humeur = "calme" | "contente" | "inquiete";

export function IrisPetite({ hauteur, humeur = "calme", regard = [-1.5, 1], toc = 0, immobile = false, label }: {
  hauteur: number; // en pixels CSS
  humeur?: Humeur;
  regard?: [number, number]; // déplacement des yeux, en pixels du repère (183 × 240) : vers l'information
  toc?: number; // change à chaque « Repéré » : un coup de tête
  immobile?: boolean;
  label?: string; // le nom de l'image (sinon elle est décorative)
}) {
  const [cligne, setCligne] = useState(false);
  const frappe = immobile ? 0 : toc; // chaque nouveau « Repéré » rejoue le coup de tête (la clé change)

  // un clignement toutes les 3 à 6 secondes, jamais quand le mouvement est réduit ni quand l'onglet est caché
  useEffect(() => {
    if (immobile) return;
    let t = 0, u = 0;
    const prochain = () => {
      t = window.setTimeout(() => {
        if (!document.hidden) { setCligne(true); u = window.setTimeout(() => setCligne(false), 140); }
        prochain();
      }, 3000 + Math.random() * 3000);
    };
    prochain();
    return () => { window.clearTimeout(t); window.clearTimeout(u); };
  }, [immobile]);

  const largeur = (hauteur * P.w) / P.h;
  const pct = (v: number, total: number) => `${(v / total) * 100}%`;
  const [dx, dy] = regard;
  const calme = humeur === "calme";
  return (
    <span className="v-iris" role={label ? "img" : undefined} aria-label={label} aria-hidden={label ? undefined : true}
      data-testid="iris-petite" data-humeur={humeur} data-immobile={immobile || undefined} style={{ width: largeur, height: hauteur }}>
      <span key={frappe} className="v-iris-corps" data-frappe={frappe ? "" : undefined}>
        {/* eslint-disable-next-line @next/next/no-img-element -- une image fixe déjà à la bonne taille (site exporté en statique) */}
        <img src="/iris/petite/face.webp" alt="" draggable={false} width={P.w} height={P.h} />
        {P.eyes.map((e, i) => (
          // eslint-disable-next-line @next/next/no-img-element -- les yeux, petites images animées par-dessus la tête
          <img key={i} className="v-iris-oeil" src={`/iris/petite/oeil-${i === 0 ? "g" : "d"}.webp`} alt="" draggable={false}
            style={{ left: pct(e.x, P.w), top: pct(e.y, P.h), width: pct(e.w, P.w), height: pct(e.h, P.h),
              transformOrigin: `${((e.cx - e.x) / e.w) * 100}% ${((e.cy - e.y) / e.h) * 100}%`,
              transform: `translate(${(dx / e.w) * 100}%, ${(dy / e.h) * 100}%) scaleY(${cligne ? 0.08 : 1})`, opacity: calme ? 1 : 0 }} />
        ))}
        <svg className="v-iris-humeurs" viewBox={`0 0 ${P.w} ${P.h}`} aria-hidden>
          <defs>
            <filter id="v-iris-halo" x="-80%" y="-80%" width="260%" height="260%">
              <feGaussianBlur stdDeviation="1.6" result="b" />
              <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>
          {P.eyes.map((e, i) => (
            <g key={i} transform={`translate(${e.cx + dx} ${e.cy + dy})`} filter="url(#v-iris-halo)">
              <path className="v-iris-contente" d="M -7.5 3.5 Q 0 -8.5 7.5 3.5" fill="none" stroke={GLOW} strokeWidth={4.2} strokeLinecap="round"
                style={{ opacity: humeur === "contente" ? 1 : 0 }} />
              <path className="v-iris-inquiete" fill={GLOW} style={{ opacity: humeur === "inquiete" ? 1 : 0 }}
                d={i === 0 ? "M -6.5 -5.5 L 4.5 -12 Q 6.5 -12.5 6.5 -10.5 L 6.5 6.5 Q 6.5 13.5 0 13.5 Q -6.5 13.5 -6.5 6.5 Z"
                  : "M 6.5 -5.5 L -4.5 -12 Q -6.5 -12.5 -6.5 -10.5 L -6.5 6.5 Q -6.5 13.5 0 13.5 Q 6.5 13.5 6.5 6.5 Z"} />
            </g>
          ))}
        </svg>
      </span>
    </span>
  );
}
