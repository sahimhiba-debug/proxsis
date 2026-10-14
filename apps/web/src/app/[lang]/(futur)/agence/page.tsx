import { agencies } from "@/lib/data";
import { getDict, type Lang } from "@/lib/i18n";
import { AgencyNav } from "@/futur/AgencyNav";
import { AgencyView } from "@/futur/AgencyView";

export async function generateMetadata({ params }: PageProps<"/[lang]/agence">) {
  const { lang } = await params;
  return { title: getDict(lang).agency.title };
}

// The direction's view: the three agencies side by side, then the radar's real measures.
export default async function AllAgencies({ params }: PageProps<"/[lang]/agence">) {
  const { lang: l } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{t.agency.title}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{t.agency.all}</span>
      </h1>
      <AgencyNav lang={lang} current={null} allLabel={t.agency.all} label={t.fx.agence.nav} />
      <AgencyView ids={Object.keys(agencies)} lang={lang} t={t} />
    </div>
  );
}
