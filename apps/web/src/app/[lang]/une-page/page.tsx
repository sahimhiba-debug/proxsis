import lundis from "@/data/presentation/lundis.json";
import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import type { MondaysData } from "@/presentation/mondayData";
import { visitData } from "@/visite/data";
import { PAGES_COPY } from "@/visite/pages";
import { UnePage } from "@/visite/UnePage";

export async function generateMetadata({ params }: PageProps<"/[lang]/une-page">) {
  const { lang } = await params;
  return { title: PAGES_COPY[isLang(lang) ? lang : "fr"].unePage.title };
}

// « Proxsis en une page », FR or DE, printable on one A4 page.
export default async function OnePage({ params }: PageProps<"/[lang]/une-page">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  // checked against its schema, and the schema against this type (src/lib/schema.test.ts)
  const data = visitData(lang);
  return <UnePage lang={lang} mondays={lundis as unknown as MondaysData} example={data.dossiers[data.territory.exemple.entreprise]} />;
}
