import { isLang } from "@/lib/i18n";
import { PHONE_COPY } from "@/presentation/phone/copy";
import { PhoneReview } from "@/presentation/phone/PhoneReview";
import { preloadFonts } from "@/lib/fonts";

// Same faces as the presentation (served with the app, so the offline copy needs no network).

export async function generateMetadata({ params }: PageProps<"/[lang]/presentation/telephone">) {
  const { lang } = await params;
  return { title: PHONE_COPY[isLang(lang) ? lang : "fr"].review.title, robots: { index: false } };
}

export default async function TelephonePage({ params }: PageProps<"/[lang]/presentation/telephone">) {
  const { lang } = await params;
  preloadFonts("presentation");
  return (
    <div>
      <PhoneReview lang={isLang(lang) ? lang : "fr"} />
    </div>
  );
}
