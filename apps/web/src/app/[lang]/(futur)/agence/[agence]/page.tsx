import { notFound } from "next/navigation";
import { agencies } from "@/lib/data";
import { getDict, LANGS, type Lang } from "@/lib/i18n";
import { AgencyNav } from "@/futur/AgencyNav";
import { AgencyView } from "@/futur/AgencyView";

export const dynamicParams = false;

export function generateStaticParams() {
  return LANGS.flatMap((lang) => Object.keys(agencies).map((agence) => ({ lang, agence })));
}

export async function generateMetadata({ params }: PageProps<"/[lang]/agence/[agence]">) {
  const { lang, agence } = await params;
  return { title: `${getDict(lang).agency.title} · ${agencies[agence]?.nom ?? ""}` };
}

// The agency head's view: the agency's activity (fictional), its consultants (fictional), the radar's real measures.
export default async function AgencyPage({ params }: PageProps<"/[lang]/agence/[agence]">) {
  const { lang: l, agence } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const a = agencies[agence];
  if (!a) notFound();
  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{t.agency.title}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{a.nom.replace(/^Flexsis\s+/, "")}</span>
      </h1>
      <p className="fx-muted mt-3 text-[14px]">{a.nom} · {a.adresse}</p>
      <AgencyNav lang={lang} current={agence} allLabel={t.agency.all} label={t.fx.agence.nav} />
      <AgencyView ids={[agence]} lang={lang} t={t} />
    </div>
  );
}
