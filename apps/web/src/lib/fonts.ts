import { preload } from "react-dom";

// The fonts are declared once (src/app/fonts.css) and served by the site itself (public/fonts): a build needs no
// network and always gives the same pages. Each screen asks early for the Latin files of the faces it shows first; the
// other subsets load only when a character needs them. The presentation shows its statements in Sora (light, one word
// strong) from the first screen on; the application only uses Urbanist.
const LATIN = {
  urbanist: "/fonts/urbanist-latin.woff2",
  soraLight: "/fonts/sora-latin-300-normal.woff2",
  soraStrong: "/fonts/sora-latin-600-normal.woff2",
};

/** The application (« Ma semaine » and the other pages) or the presentation (the first screen and the visit). */
export function preloadFonts(direction: "app" | "presentation"): void {
  const files = direction === "app" ? [LATIN.urbanist] : [LATIN.urbanist, LATIN.soraLight, LATIN.soraStrong];
  for (const href of files) preload(href, { as: "font", type: "font/woff2", crossOrigin: "" });
}
