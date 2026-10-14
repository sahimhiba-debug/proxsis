import { agencies, companies, meta } from "@/lib/data";
import { getDict, type Lang } from "@/lib/i18n";
import { usageName } from "@/futur/display";
import { CANTON, communesIn, project, VALAIS_VIEW } from "@/futur/region";
import { WeekMap, type MapContract, type MapPlace, type MapWeek } from "@/futur/WeekMap";

export async function generateMetadata({ params }: PageProps<"/[lang]/carte">) {
  const { lang } = await params;
  return { title: getDict(lang).fx.carte.title };
}

const WEEKS = 12; // the periods the slider shows, one week apart (about a quarter)
const WINDOW_DAYS = 14; // a contract is « recent » for 14 days, as in « Ma semaine » (DESIGN.md § 4 bis)
const DAY = 86_400_000;
const iso = (t: number) => new Date(t).toISOString().slice(0, 10);

// « Carte », futurisme suisse: the dark Valais of the swisstopo commune boundaries (embedded, offline, no map tiles),
// the three agencies, the companies of the lists at their commune, and the public contracts published week by week.
export default async function MapPage({ params }: PageProps<"/[lang]/carte">) {
  const { lang: l } = await params;
  const lang = l as Lang;
  const t = getDict(lang);
  const v = VALAIS_VIEW;
  const at = (lat: number, lon: number) => {
    const p = project(lat, lon);
    return { left: (p.x - v.x) / v.w, top: (p.y - v.y) / v.h };
  };
  const monday = Date.parse(`${meta.semaine}T12:00:00Z`);
  // each period: the 14 days that end on a Sunday, the last one just before the list's Monday
  const weeks: MapWeek[] = Array.from({ length: WEEKS }, (_, k) => {
    const to = monday - (WEEKS - 1 - k) * 7 * DAY - DAY;
    return { from: iso(to - (WINDOW_DAYS - 1) * DAY), to: iso(to) };
  });
  const byPlace = new Map<string, MapPlace>();
  const contracts: MapContract[] = [];
  for (const c of Object.values(companies)) {
    const place = byPlace.get(c.ville) ?? { ville: c.ville, ...at(c.lat, c.lon), companies: [] };
    place.companies.push(usageName(c.nom));
    byPlace.set(c.ville, place);
    for (const s of c.chronologie) {
      if (s.date >= weeks[0].from && s.date <= weeks[WEEKS - 1].to) {
        contracts.push({ company: c.id, name: usageName(c.nom), ville: c.ville, date: s.date, titre: s.titre });
      }
    }
  }
  const m = t.fx.carte;
  return (
    <div className="fx-col pb-8 pt-6 sm:pt-10">
      <h1>
        <span className="fx-caps fx-muted block">{t.nav.carte}</span>
        <span className="fx-display mt-3 block text-[34px] sm:text-[52px]">{m.title}</span>
      </h1>
      <p className="fx-muted mt-4 max-w-[60ch] text-[16px] leading-relaxed">{m.lead}</p>
      <div className="mt-8">
        <WeekMap ratio={v.w / v.h} places={[...byPlace.values()]} contracts={contracts} weeks={weeks} lang={lang}
          agencies={Object.values(agencies).map((a) => ({ name: a.nom.replace(/^Flexsis\s+/, ""), ...at(a.lat, a.lon) }))}
          t={{ week: m.week, prev: m.prev, next: m.next, slider: m.slider, signals: m.signals, signal1: m.signal1, none: m.none,
            listTitle: m.listTitle, recent: m.recent, company: m.company, agency: m.agency, colon: t.label.colon }}>
          <svg viewBox={`${v.x} ${v.y} ${v.w} ${v.h}`} preserveAspectRatio="xMidYMid meet" aria-hidden focusable="false">
            <path d={CANTON} className="fx-map-canton" />
            {communesIn(v).map((c) => <path key={c.bfs} d={c.d} className="fx-map-commune" />)}
          </svg>
        </WeekMap>
      </div>
      <p className="fx-muted mt-6 text-[12px]">{m.source}</p>
    </div>
  );
}
