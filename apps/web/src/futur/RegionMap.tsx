import { CANTON, communesIn, labelSide, places, project, regionView } from "./region";

interface RegionMapLabels {
  title: string; recent: string; company: string; agency: string; source: string; aria: string; ariaRecent: string;
  ariaNone: string; companies: string; company1: string;
}

const pct = (v: number) => `${(v * 100).toFixed(2)}%`;

/**
 * The region of the week on wide screens: the commune boundaries (swisstopo), the agency, one dot per commune where a
 * company of the list is based, in copper where one of them won a contract less than 14 days ago. Server-rendered,
 * no script; the pulse is CSS and stops when motion is reduced.
 */
export function RegionMap({ items, agency, t }: {
  items: { ville: string; lat: number; lon: number; recent: boolean }[];
  agency: { name: string; lat: number; lon: number };
  t: RegionMapLabels;
}) {
  const home = project(agency.lat, agency.lon);
  const ps = places(items);
  const v = regionView([home, ...ps]);
  const at = (p: { x: number; y: number }) => ({ left: pct((p.x - v.x) / v.w), top: pct((p.y - v.y) / v.h) });
  const recentPlaces = ps.filter((p) => p.recent > 0).map((p) => p.ville);
  const aria = t.aria.replace("{agence}", agency.name)
    + " " + (recentPlaces.length ? t.ariaRecent.replace("{lieux}", recentPlaces.join(", ")) : t.ariaNone);
  // a label goes on the side where it has room and covers no other dot (frame of 440 × 330 px on wide screens)
  const W = 440;
  const H = 330;
  const px = (p: { x: number; y: number }) => ({ x: ((p.x - v.x) / v.w) * W, y: ((p.y - v.y) / v.h) * H });
  const side = (p: { x: number; y: number }, text: string) =>
    labelSide(px(p), text, [home, ...ps].filter((o) => o !== p).map(px), W, H);
  const homeLabel = `${agency.name} · ${t.agency}`;
  return (
    <figure className="fx-map hidden lg:block" data-testid="region-map">
      <p className="fx-caps fx-muted mb-3">{t.title}</p>
      <div className="fx-map-frame" role="img" aria-label={aria}>
        <svg viewBox={`${v.x} ${v.y} ${v.w} ${v.h}`} preserveAspectRatio="xMidYMid meet" aria-hidden focusable="false">
          <path d={CANTON} className="fx-map-canton" />
          {communesIn(v).map((c) => <path key={c.bfs} d={c.d} className="fx-map-commune" />)}
        </svg>
        <span className="fx-map-home" style={at(home)} aria-hidden>
          <span className="fx-caps fx-map-label" data-side={side(home, homeLabel)}>{homeLabel}</span>
        </span>
        {ps.map((p) => (
          <span key={p.ville} className="fx-map-dot" data-recent={p.recent > 0} aria-hidden
            style={{ ...at(p), ["--s" as string]: `${6 + 2 * (Math.min(p.n, 4) - 1)}px` }}
            title={`${p.ville} · ${p.n === 1 ? t.company1 : t.companies.replace("{n}", String(p.n))}`}>
            {p.recent > 0 ? <span className="fx-map-pulse" /> : null}
            {/* the agency's own commune is already named by the agency's label */}
            {p.recent > 0 && p.ville !== agency.name ? (
              <span className="fx-caps fx-copper fx-map-label" data-side={side(p, p.ville)}>{p.ville}</span>
            ) : null}
          </span>
        ))}
      </div>
      <figcaption className="mt-3 space-y-1">
        {/* no count here: the list's own figure (« 10 entreprises à appeler ») stays the only one in the header */}
        <p className="flex flex-wrap gap-x-5 gap-y-1 text-[13px]">
          {recentPlaces.length ? (
            <span className="inline-flex items-center gap-2"><i className="fx-map-key" data-recent="true" aria-hidden />{t.recent}</span>
          ) : <span className="fx-muted">{t.ariaNone}</span>}
          <span className="inline-flex items-center gap-2"><i className="fx-map-key" aria-hidden />{t.company}</span>
        </p>
        <p className="fx-muted text-[12px]">{t.source}</p>
      </figcaption>
    </figure>
  );
}
