import { getDict, type Lang } from "@/lib/i18n";
import { RoiCalculator } from "@/futur/RoiCalculator";

export async function generateMetadata({ params }: PageProps<"/[lang]/roi">) {
  const { lang } = await params;
  return { title: getDict(lang).roi.title };
}

// « Retour sur investissement », futurisme suisse: the director's hypotheses and what they give, with the same model and
// the same example values as the presentation (act 5); every figure is a hypothesis, nothing is measured here.
export default async function RoiPage({ params }: PageProps<"/[lang]/roi">) {
  const { lang } = await params;
  const t = getDict(lang);
  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{t.roi.title}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{t.roi.display}</span>
      </h1>
      <p className="fx-muted mt-4 max-w-[62ch] text-[16px] leading-relaxed">{t.roi.intro}</p>
      <div className="mt-8"><RoiCalculator lang={lang as Lang} tags={{ hypothesis: t.roi.hypothesis, example: t.roi.example }} /></div>
    </div>
  );
}
