import Link from "next/link";
import { agencies } from "@/lib/data";
import { getDict } from "@/lib/i18n";
import { consultantLabel } from "@/lib/roleLabel";
import { HomeRedirect } from "@/futur/HomeRedirect";

export async function generateMetadata({ params }: PageProps<"/[lang]/semaine">) {
  const { lang } = await params;
  return { title: getDict(lang).semaine.title };
}

// The weeks of every demo consultant (fictional), agency by agency; the browser goes on to the chosen role's week.
export default async function WeekIndex({ params }: PageProps<"/[lang]/semaine">) {
  const { lang } = await params;
  const t = getDict(lang);
  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{t.semaine.title}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{t.fx.weeks}</span>
      </h1>
      <div className="mt-8 grid gap-4 lg:grid-cols-3">
        {Object.values(agencies).map((a) => (
          <section key={a.id} className="fx-card p-5" aria-labelledby={`fx-weeks-${a.id}`}>
            {/* the agency is real; its consultants are fictional: the mention goes with them */}
            <h2 id={`fx-weeks-${a.id}`} className="fx-caps fx-muted">{a.nom.replace(/^Flexsis\s+/, "")}</h2>
            <p className="mt-2"><span className="fx-tag" data-kind="fictif">{t.fx.fictionalConsultants}</span></p>
            <ul className="mt-2">
              {a.consultants.map((c) => (
                <li key={c.code}>
                  <Link className="fx-link inline-flex min-h-11 min-w-11 items-center text-[16px]" href={`/${lang}/semaine/${c.code}/`}>
                    {consultantLabel(t, lang, c.specialite)}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
      <HomeRedirect lang={lang} />
    </div>
  );
}
