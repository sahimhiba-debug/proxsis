import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import { VISIT_COPY } from "@/visite/copy";
import { visitData } from "@/visite/data";
import { Visit } from "@/visite/Visit";

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation">) {
  const { lang } = await params;
  return { title: VISIT_COPY[isLang(lang) ? lang : "fr"].title };
}

// The visit in five times (brief « à distance »): the presentation of Proxsis, at its address since 07.10.2026.
export default async function VisitPage({ params }: PageProps<"/[lang]/presentation">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  return <Visit data={visitData(lang)} />;
}
