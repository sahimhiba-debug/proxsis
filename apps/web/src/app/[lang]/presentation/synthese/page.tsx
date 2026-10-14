import { preloadFonts } from "@/lib/fonts";
import { isLang, type Lang } from "@/lib/i18n";
import { VISIT_COPY } from "@/visite/copy";
import { visitData } from "@/visite/data";
import { SyntheseVisite } from "@/visite/Synthese";

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation/synthese">) {
  const { lang } = await params;
  return { title: VISIT_COPY[isLang(lang) ? lang : "fr"].synthese.title };
}

// « Télécharger ma synthèse »: the visit's choices on one A4 page, read on this device, saved as PDF by the browser.
export default async function VisitSummaryPage({ params }: PageProps<"/[lang]/presentation/synthese">) {
  const { lang: l } = await params;
  const lang = (isLang(l) ? l : "fr") as Lang;
  preloadFonts("presentation");
  const d = visitData(lang);
  return <SyntheseVisite inputs={{ lang, dossiers: d.dossiers, exampleCompany: d.territory.exemple.entreprise, mondays: d.mondays }} />;
}
