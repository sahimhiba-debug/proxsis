import lundis from "@/data/presentation/lundis.json";
import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import type { MondaysData } from "@/presentation/mondayData";
import { PAGES_COPY } from "@/visite/pages";
import { PourDirection } from "@/visite/PourDirection";

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation/direction">) {
  const { lang } = await params;
  return { title: PAGES_COPY[isLang(lang) ? lang : "fr"].direction.title };
}

// « Pour votre direction » (brief of 07.10.2026, suite 2, § 8), FR or DE, printable: a page to pass on to the group.
export default async function DirectionPage({ params }: PageProps<"/[lang]/presentation/direction">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  return <PourDirection lang={lang} mondays={lundis as unknown as MondaysData} />;
}
