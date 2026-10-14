import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import { TeamPage } from "@/visite/InfoPages";
import { PAGES_COPY } from "@/visite/pages";

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation/equipe">) {
  const { lang } = await params;
  return { title: PAGES_COPY[isLang(lang) ? lang : "fr"].equipe.title };
}

export default async function Page({ params }: PageProps<"/[lang]/presentation/equipe">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  return <TeamPage lang={lang} />;
}
