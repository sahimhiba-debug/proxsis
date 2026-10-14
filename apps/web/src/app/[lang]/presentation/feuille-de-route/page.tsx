import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import { RoadmapPage } from "@/visite/InfoPages";
import { PAGES_COPY } from "@/visite/pages";

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation/feuille-de-route">) {
  const { lang } = await params;
  return { title: PAGES_COPY[isLang(lang) ? lang : "fr"].feuille.title };
}

export default async function Page({ params }: PageProps<"/[lang]/presentation/feuille-de-route">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  return <RoadmapPage lang={lang} />;
}
