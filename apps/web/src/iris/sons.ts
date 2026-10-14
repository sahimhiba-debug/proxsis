"use client";

// Le son de la visite (suite 8, § 5) : le toc, quand le marteau touche la planche. Rien ne joue tout seul : le son s'arme au premier geste du visiteur (un clic, une
// touche, « Commencer ») ; un bouton le coupe à tout moment, et ce choix reste sur l'appareil. Sans le son, tout se
// comprend. Les fichiers viennent du site (public/iris/sons/), jamais d'ailleurs.
import { readStored } from "@/lib/useStored";

export const PREF_SON = "proxsis.visite.son"; // « off » : le son est coupé (sur cet appareil)
const TOC_VOLUME = 0.55; // discret dans la visite

let arme = false;
let toc: HTMLAudioElement | null = null;

export const sonCoupe = () => readStored(PREF_SON) === "off";

/** Au premier geste du visiteur : prépare le toc (le navigateur n'autorise le son qu'après un geste). */
export function armerSon() {
  if (arme || typeof Audio === "undefined") return;
  arme = true;
  toc = new Audio("/iris/sons/toc-court.mp3");
  toc.preload = "auto";
  toc.volume = TOC_VOLUME;
}

/** Un toc, au moment exact où la tête touche la planche (ou où le point se pose). */
export function jouerToc() {
  if (!arme || !toc || sonCoupe()) return;
  try {
    const t = toc.cloneNode(true) as HTMLAudioElement;
    t.volume = TOC_VOLUME;
    void t.play().catch(() => {});
  } catch {
    /* le son n'est qu'un plus */
  }
}
