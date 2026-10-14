import type { MetadataRoute } from "next";
import { getDict } from "@/lib/i18n";

// The installable application: the name, its signature, the dark ground of the app. Same name in every language.
// Installed on a phone, it opens on the consultant's application (its entrance goes on to the week of the chosen
// role), full screen; /fr/ is the director's first screen since the brief « à distance », § 3.
export const dynamic = "force-static";

const fr = getDict("fr").app;
const de = getDict("de").app;

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Proxsis",
    short_name: "Proxsis",
    description: `${fr.signature} · ${de.signature} · ${fr.prototype}`,
    start_url: "/fr/application/",
    scope: "/",
    display: "standalone",
    background_color: "#121212",
    theme_color: "#121212",
    lang: "fr-CH",
    // la tête d'Iris de face (suite 8, § 3) ; les anciennes icônes (le « P » et la diagonale) sont dans l'historique Git
    // (working notes, not published)
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
      { src: "/icon-512-maskable.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
