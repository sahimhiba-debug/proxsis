import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { getDict } from "@/lib/i18n";
import { HomeRedirect } from "@/futur/HomeRedirect";

// The entrance of the application (/[lang]/application/; /[lang]/ is the first screen of Proxsis since the brief « à
// distance », § 3): the name, its signature, the promise, and the way to the week. The browser goes on at once to the
// week of the chosen demo role (HomeRedirect); without JavaScript, the link does it.
export default async function AppHome({ params }: PageProps<"/[lang]/application">) {
  const { lang } = await params;
  const t = getDict(lang);
  return (
    <div className="fx-col pb-8 pt-10 sm:pt-16">
      <h1 className="fx-display text-[52px] sm:text-[80px]">
        {t.app.name.slice(0, 3)}<span className="fx-copper">{t.app.name.slice(3, 4)}</span>{t.app.name.slice(4)}
      </h1>
      <p className="mt-2 text-[20px] sm:text-[24px]">{t.app.signature}</p>
      <p className="fx-caps fx-muted mt-2">{t.app.prototype}</p>
      <p className="mt-8 max-w-[52ch] text-[17px] leading-relaxed">{t.fx.promise}</p>
      <p className="mt-8"><Link className="fx-action" href={`/${lang}/semaine/M1/`}>{t.nav.semaine} <ArrowRight aria-hidden className="size-4" /></Link></p>
      <HomeRedirect lang={lang} />
    </div>
  );
}
