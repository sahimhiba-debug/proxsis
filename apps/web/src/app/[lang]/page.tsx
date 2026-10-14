import curated from "@/data/presentation/dossiers.json";
import { calls, companies } from "@/lib/data";
import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import { Accueil } from "@/visite/Accueil";
import { visitDossier, type Curated } from "@/visite/dossier";
import { PAGES_COPY } from "@/visite/pages";

export async function generateMetadata({ params }: PageProps<"/[lang]">) {
  const { lang } = await params;
  // the layout's « · Proxsis » applies to the pages below this one, not to it: the name is written here
  return { title: `Proxsis — ${PAGES_COPY[isLang(lang) ? lang : "fr"].accueil.title}` };
}

// The first screen of Proxsis (brief « à distance », § 3): only the example dossier is built, to stay light.
export default async function FirstScreen({ params }: PageProps<"/[lang]">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  const id = curated.guides[0];
  const reading: Record<string, Curated> = curated.dossiers;
  return <Accueil lang={lang} d={visitDossier(id, companies[id], calls[id], reading[id], curated.rejeu)} />;
}
