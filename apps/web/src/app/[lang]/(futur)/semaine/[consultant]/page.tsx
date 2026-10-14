import { notFound } from "next/navigation";
import cetteSemaine from "@/data/presentation/cette_semaine.json";
import lundis from "@/data/presentation/lundis.json";
import { allConsultants, candidates, consultant, lists, meta, redeploy, weekList } from "@/lib/data";
import { getDict, LANGS, type Lang } from "@/lib/i18n";
import type { Company, Worker } from "@/lib/types";
import { TrialBar } from "@/futur/CarnetPanel";
import { CardList, type CardData } from "@/futur/CompanyCard";
import { EndingMissions } from "@/futur/EndingMissions";
import { ChaqueMatin } from "@/futur/ChaqueMatin";
import { callLine, consortiumMembers, longDay, shortWhy, timelinePoints, usageName, whyNow } from "@/futur/display";
import { fmtDate } from "@/lib/dates";
import { Em } from "@/futur/Em";
import { MethodSheet } from "@/futur/MethodSheet";
import { RegionMap } from "@/futur/RegionMap";

export const dynamicParams = false;

export function generateStaticParams() {
  return LANGS.flatMap((lang) => allConsultants().map((c) => ({ lang, consultant: c.code })));
}

export async function generateMetadata({ params }: PageProps<"/[lang]/semaine/[consultant]">) {
  const { lang } = await params;
  return { title: getDict(lang).semaine.title };
}

const pad = (n: number) => String(n).padStart(2, "0");
const num = (x: number | null, lang: Lang) => (x === null ? "—" : String(x).replace(".", lang === "fr" ? "," : "."));

// « Ma semaine », futurisme suisse: the Monday, the agency, one line on what is real and what is fictional, then the
// ranked companies (real), each with why now and its 52 weeks of public contracts. No label, no confidence level,
// no estimate on the cards: the dossier carries the detail.
export default async function WeekPage({ params }: PageProps<"/[lang]/semaine/[consultant]">) {
  const { lang: l, consultant: code } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const who = consultant(code);
  const wl = weekList(code);
  if (!who || !wl) notFound();
  const spec = t.specialty[who.specialite as keyof typeof t.specialty] ?? who.specialite;
  const agency = who.agence.nom.replace(/^Flexsis\s+/, ""); // shown (« Martigny »); the joins use who.agence.id
  const bt = lists[who.specialite]?.backtest;
  const seen = new Set<string>();
  const fresh = (list: Company[]) => list.filter((c) => !seen.has(c.id) && seen.add(c.id));
  const week = { ranked: fresh(wl.ranked), newcomers: fresh(wl.surprises) };
  // a consortium is said, with its members when the published name separates them (brief « à distance », § 6)
  const consortiumLine = (name: string) => {
    const members = consortiumMembers(name);
    return members === null ? null : members.length ? t.fx.consortiumMembers.replace("{members}", members.join(", ")) : t.fx.consortiumUnnamed;
  };
  const start = fmtDate(lundis.source.debut_des_donnees); // the first day of our data (« Premier marché dans nos données depuis… »)
  const toCards = (list: Company[], ranked: boolean): CardData[] =>
    list.map((c, i) => ({
      id: c.id, rank: ranked ? pad(i + 1) : null, commune: c.ville, name: usageName(c.nom), legal: c.nom,
      // a newcomer's « new » is said by its section: the card gives its latest contract instead
      why: shortWhy(whyNow(c.raisons, ranked ? [] : ["nouveau_venu"]), lang), phone: callLine(c, lang),
      points: timelinePoints(c, meta.semaine), n52: c.n_52s, consortium: consortiumLine(c.nom),
    }));
  const ranked = toCards(week.ranked, true);
  const newcomers = toCards(week.newcomers, false);
  // the region of the week (wide screens): each company of the week at its commune, copper if a contract is < 14 days old
  const mapItems = [...week.ranked, ...week.newcomers].map((c) => ({ ville: c.ville, lat: c.lat, lon: c.lon,
    recent: timelinePoints(c, meta.semaine).some((p) => p.recent) }));
  // the consultant's own temps (same agency, same specialty) whose mission ends in the coming weeks (fictional)
  const ENDING_SHOWN = 5;
  const ending = redeploy.travailleurs
    .filter((w) => candidates[w.candidate_id]?.agence === who.agence.id && candidates[w.candidate_id]?.specialite === who.specialite)
    .sort((a, b) => a.fin_mission.localeCompare(b.fin_mission)).slice(0, ENDING_SHOWN);
  const trade = (w: Worker) => (w.metier ? meta.metiers[w.metier]?.[lang] ?? w.metier : "—");
  const labels = { call: t.semaine.call, dossier: t.fx.dossier, markets: t.fx.markets, market1: t.fx.market1, marketsAria: t.fx.marketsAria,
    recent: t.fx.recent, newcomer: t.fx.newcomer, recent1: t.fx.recent1, recentN: t.fx.recentN, phone: t.fx.phone,
    phoneFact: t.fx.phoneFact, phoneReview: t.fx.phoneReview, rankReason: t.fx.rankReason, rankReason1: t.fx.rankReason1, more: t.fx.more };
  return (
    <div className="fx-col">
      <section className="pb-8 pt-6 sm:pt-10 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,440px)] lg:items-end lg:gap-x-16">
        <div>
          <h1>
            <span className="fx-caps fx-muted block">{t.semaine.title}</span>
            <span className="fx-display mt-3 block text-[clamp(34px,11vw,44px)] sm:text-[64px] lg:text-[80px]">{longDay(meta.semaine, lang)}</span>
          </h1>
          <p className="fx-caps mt-3">{agency} · {spec}</p>
          {ranked.length ? (
            <p className="mt-6 text-[20px] leading-snug sm:text-[24px]">
              <Em text={(ranked.length === 1 ? t.fx.lead1 : t.fx.lead).replace("{n}", String(ranked.length))} />
            </p>
          ) : null}
          {/* the promise stays at the top (brief « à distance », § 6), quietly: on Monday morning the first calls come first */}
          <p className="fx-muted mt-4 max-w-[60ch] text-[14px] leading-relaxed" data-testid="promise">{t.fx.promise}</p>
          {/* suite 10, § 2: where the Monday is spoken of, Hiba's sentence (the section « Chaque matin » is at the end) */}
          <p className="mt-2 max-w-[60ch] text-[14px] leading-relaxed" data-testid="chaque-matin-phrase">{t.fx.live.morning}</p>
          <p className="fx-muted mt-2 text-[14px]" data-testid="demo-banner">{t.fx.demoLine}</p>
          {/* how fresh each source is, said every Monday (Q19): the dates of the week this list was made from */}
          {cetteSemaine.lundi === meta.semaine ? (
            <p className="fx-muted mt-2 max-w-[60ch] text-[14px] leading-relaxed" data-testid="sources-a-jour">
              {t.fx.upToDate.replace("{simap}", fmtDate(cetteSemaine.fin_des_donnees.simap))
                .replace("{bo}", fmtDate(cetteSemaine.fin_des_donnees.bulletin_officiel))
                .replace("{boNote}", cetteSemaine.sources.bulletin_officiel.mention[lang])}
            </p>
          ) : null}
          {bt ? (
            <MethodSheet label={t.fx.how} title={t.fx.how} close={t.fx.close} measureLabel={t.fx.howMeasure}
              measureHref={`/${lang}/mesures/#${bt.claim}`}
              body={t.fx.howBody.map((p) => p.replace("{semaines}", String(bt.semaines ?? "—"))
                .replace("{p}", num(bt.p_at_10, lang)).replace("{base}", num(bt.taux_de_base, lang)))}
              sources={t.fx.howSources} mention={`${t.banner.simap} « ${meta.mention_simap} »`} />
          ) : (
            <p className="fx-muted mt-3 text-[15px]" data-testid="no-industry">{t.semaine.noIndustry}</p>
          )}
        </div>
        {mapItems.length ? (
          <RegionMap items={mapItems} agency={{ name: agency, lat: who.agence.lat, lon: who.agence.lon }} t={t.fx.map} />
        ) : null}
      </section>
      {bt && ranked.length === 0 ? <p className="fx-muted text-[15px]">{t.semaine.empty}</p> : null}
      {/* « Vos trois premiers appels », then the seven others in the same ranking (brief « à distance », § 6); on a phone,
          the seven others and the newcomers keep their call sentence under « En savoir plus » (suite 9, § 10) */}
      {ranked.length ? (
        <section aria-labelledby="fx-first">
          <h2 id="fx-first" className="fx-display text-[26px]">{t.fx.firstThree}</h2>
          <div className="mt-4"><CardList cards={ranked.slice(0, 3)} lang={lang} t={labels} label={t.fx.firstThree} level={3} lead /></div>
        </section>
      ) : null}
      {ranked.length > 3 ? (
        <section className="mt-10" aria-labelledby="fx-others">
          <h2 id="fx-others" className="fx-display text-[22px]">{t.fx.others}</h2>
          <div className="mt-4"><CardList cards={ranked.slice(3)} lang={lang} t={labels} label={t.fx.others} level={3} compact /></div>
        </section>
      ) : null}
      {/* the trial week (semaine témoin): under the list, once the list has been read */}
      <div className="mt-8"><TrialBar lang={lang} week={meta.semaine} consultant={code} ranked={week.ranked.map((c) => c.id)} /></div>
      {newcomers.length ? (
        <section className="mt-14" aria-labelledby="fx-newcomers">
          <h2 id="fx-newcomers" className="fx-display text-[26px]">{t.fx.newcomers.replace("{date}", start)}</h2>
          <p className="fx-muted mb-5 mt-2 text-[15px]">{t.fx.newcomersLine.replace("{date}", start)}</p>
          <CardList cards={newcomers} lang={lang} t={labels} label={t.fx.newcomers.replace("{date}", start)} level={3} compact />
        </section>
      ) : null}
      <EndingMissions workers={ending} from={meta.semaine} lang={lang} t={t} trade={trade} />
      {/* « Chaque matin, en direct de simap » (suite 10, § 2): « dans votre liste » for a company of this week's list */}
      <ChaqueMatin t={t} list={[...week.ranked, ...week.newcomers].map((c) => c.id)} />
    </div>
  );
}
