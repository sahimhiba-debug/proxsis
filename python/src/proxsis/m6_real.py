"""M6 on REAL public series: regional / national labour demand.

Targets: KOF Job Tracker (weekly online job ads, national, 2018 →), FSO job vacancies by large region
(quarterly, 1997 →). Signals: the series' own past, the calendar, lagged weather (MeteoSwiss OGD) and simap
award volumes (only since late 2024). Simple first: seasonal naive, last value, 4-period mean; then gradient
boosting (LightGBM, direct model per horizon). Deep learning is not tried: a few hundred points do not
justify it (docs/adr/0009-m6-prevision.md).

No leakage: at origin ``o`` (first unknown period) every feature uses periods < o only — except the
calendar of the target period, which is known in advance. Models are trained only on targets < o.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

NAIVE = ("saisonnier_naif", "derniere_valeur", "moyenne_4")


def _feat(y: np.ndarray, ex: np.ndarray | None, t: int, h: int, period: int) -> list[float]:
    o = t - h + 1
    lags = [y[o - k] if o - k >= 0 else np.nan for k in (1, 2, 3, 4)]
    m4 = np.nanmean(y[max(0, o - 4):o]) if o > 0 else np.nan
    seas = y[t - period] if 0 <= t - period < o else np.nan
    prev_m4 = np.nanmean(y[max(0, o - 4 - period):max(0, o - period)]) if o - period > 0 else np.nan
    pos = 2 * np.pi * (t % period) / period
    f = [*(v / m4 - 1 if m4 else np.nan for v in lags), seas / m4 - 1 if m4 else np.nan,
         m4 / prev_m4 - 1 if prev_m4 else np.nan, np.sin(pos), np.cos(pos), float(h)]
    if ex is not None:
        for j in range(ex.shape[1]):
            last = ex[o - 1, j] if o - 1 >= 0 else np.nan
            before = ex[o - 5, j] if o - 5 >= 0 else np.nan
            f += [last, last - before]
    return f


def forecast_at(y: pd.Series, ex: pd.DataFrame | None, origin: Any, horizons: Iterable[int],
                period: int) -> dict[str, dict[int, float]]:
    """Forecasts for targets origin + h - 1 using information strictly before ``origin``."""
    import lightgbm as lgb

    idx = list(y.index)
    o = idx.index(origin)
    yv = y.to_numpy(float)
    exv = ex.reindex(y.index).to_numpy(float) if ex is not None else None
    out: dict[str, dict[int, float]] = {m: {} for m in (*NAIVE, "boosting")}
    m4 = float(np.nanmean(yv[max(0, o - 4):o]))
    known = yv[:o][~np.isnan(yv[:o])]
    last = float(known[-1]) if len(known) else float("nan")
    for h in horizons:
        t = o + h - 1
        seas = yv[t - period] if 0 <= t - period < o else np.nan
        out["saisonnier_naif"][h] = float(seas) if not np.isnan(seas) else last
        out["derniere_valeur"][h] = last
        out["moyenne_4"][h] = m4
        rows, target = [], []
        for tt in range(4 + h, o):  # labels known at the origin only
            if np.isnan(yv[tt]):
                continue
            f = _feat(yv, exv, tt, h, period)
            base = np.nanmean(yv[max(0, tt - h + 1 - 4):tt - h + 1])
            if not base:
                continue
            rows.append(f)
            target.append(yv[tt] / base - 1)
        if len(rows) < 30:
            out["boosting"][h] = out["moyenne_4"][h]
            continue
        model = lgb.train({"objective": "l2", "learning_rate": 0.05, "num_leaves": 7, "min_data_in_leaf": 10,
                           "verbose": -1, "seed": 0, "deterministic": True, "num_threads": 1},
                          lgb.Dataset(np.array(rows), label=np.array(target)), num_boost_round=200)
        pred = float(model.predict(np.array([_feat(yv, exv, t, h, period)]))[0])
        out["boosting"][h] = m4 * (1 + pred)
    return out


def _block_ci(x: np.ndarray, n_boot: int, block: int, rng: np.random.Generator) -> list[float]:
    n = len(x)
    if n == 0:
        return [float("nan"), float("nan")]
    nb = int(np.ceil(n / block))
    means = []
    for _ in range(n_boot):
        starts = rng.integers(0, max(n - block + 1, 1), nb)
        idx = np.concatenate([np.arange(s, min(s + block, n)) for s in starts])[:n]
        means.append(float(np.mean(x[idx])))
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def evaluate_series(y: pd.Series, ex: pd.DataFrame | None, first_origin: Any, step: int, horizons: Iterable[int],
                    period: int, n_boot: int = 1000, seed: int = 0) -> dict[str, Any]:
    hs = list(horizons)
    y = y.sort_index()
    idx = list(y.index)
    yv = y.to_numpy(float)
    start = idx.index(first_origin)
    origins = [o for o in range(start, len(idx)) if (o - start) % step == 0 and o + max(hs) - 1 < len(idx)
               and not np.isnan(yv[o + max(hs) - 1])]
    methods = (*NAIVE, "boosting")
    err: dict[str, list[float]] = {m: [] for m in methods}
    per_origin: dict[str, list[float]] = {m: [] for m in methods}
    act_origin: list[float] = []
    actual: list[float] = []
    for o in origins:
        f = forecast_at(y, ex, idx[o], hs, period)
        a_sum = 0.0
        e_sum = dict.fromkeys(methods, 0.0)
        for h in hs:
            a = yv[o + h - 1]
            if np.isnan(a):  # missing value in the real series: not scored
                continue
            actual.append(abs(a))
            a_sum += abs(a)
            for m in methods:
                e = abs(a - f[m][h])
                err[m].append(e)
                e_sum[m] += e
        act_origin.append(a_sum)
        for m in methods:
            per_origin[m].append(e_sum[m])
    total = float(np.sum(actual)) or 1.0
    wape = {m: float(np.sum(err[m]) / total) for m in methods}
    best = min(NAIVE, key=lambda m: wape[m])
    w_b = np.array(per_origin["boosting"]) / np.array(act_origin)
    w_n = np.array(per_origin[best]) / np.array(act_origin)
    rng = np.random.default_rng(seed)
    block = max(1, -(-max(hs) // step))
    diff = w_b - w_n
    return {"periode": [str(idx[origins[0]]), str(idx[origins[-1] + max(hs) - 1])], "n_origines": len(origins),
            "pas": step, "horizons": hs, "wape": wape, "meilleure_naive": best,
            "boosting_moins_meilleure_naive": {"moyenne": float(diff.mean()),
                                               "ic95": _block_ci(diff, n_boot, block, rng)}}


# ------------------------------------------------------------------ real data (allowed public sources)
def kof_jobtracker(client: Any) -> pd.Series:
    """Weekly KOF Job Tracker index (public series, tsdb-api.kof.ethz.ch)."""
    import io

    r = client.get("https://tsdb-api.kof.ethz.ch/v2/ts", source="KOF Swiss Economic Institute",
                   license="KOF, données publiques (citer la source)", store_raw=True,
                   params={"keys": "ch.kof.jobtracker.total.total.clean.idx", "mime": "csv", "access_type": "public"})
    df = pd.read_csv(io.StringIO(r.text()))
    s = pd.Series(df.iloc[:, 1].to_numpy(float), index=pd.to_datetime(df["date"]).dt.date)
    s.index = [d - pd.Timedelta(days=d.weekday()) for d in s.index]  # weeks keyed by Monday
    return s.groupby(level=0).mean().sort_index()


def bfs_vacancies(client: Any) -> pd.DataFrame:
    """Quarterly job vacancies by large region (FSO, STAT-TAB px-x-0602000000_104)."""
    url = "https://www.pxweb.bfs.admin.ch/api/v1/fr/px-x-0602000000_104/px-x-0602000000_104.px"
    q = {"query": [{"code": "Offene Stellen", "selection": {"filter": "item", "values": ["1"]}},
                   {"code": "Grossregion", "selection": {"filter": "all", "values": ["*"]}},
                   {"code": "Quartal", "selection": {"filter": "all", "values": ["*"]}}],
         "response": {"format": "json"}}
    r = client.post_json(url, q, source="OFS STAT-TAB", license="OFS (conditions d'utilisation de l'OFS)")
    data = r.json()
    cols = [c["code"] for c in data["columns"]]
    rows = [dict(zip(cols, [*d["key"], *d["values"]], strict=False)) for d in data["data"]]
    df = pd.DataFrame(rows)
    df["valeur"] = pd.to_numeric(df[cols[-1]], errors="coerce")  # « ... » (not available) → NaN
    return df.dropna(subset=["valeur"])


def meteo_weekly(client: Any, station: str = "sio") -> pd.DataFrame:
    """Weekly mean temperature and precipitation of a MeteoSwiss station (OGD, CC BY 4.0)."""
    import io

    frames = []
    for part in ("historical", "recent"):
        url = f"https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/{station}/ogd-smn_{station}_d_{part}.csv"
        r = client.get(url, source="MétéoSuisse OGD", license="CC BY 4.0 (source : MétéoSuisse)", store_raw=True)
        if r.status == 200:
            frames.append(pd.read_csv(io.StringIO(r.text()), sep=";"))
    df = pd.concat(frames).drop_duplicates()
    when = pd.to_datetime(df["reference_timestamp"], format="%d.%m.%Y %H:%M", errors="coerce").dt.date
    nan = pd.Series(np.nan, index=df.index)
    temp = df.get("tre200d0", nan)
    rain = df.get("rre150d0", nan)
    out = pd.DataFrame({"date": when, "temperature": pd.to_numeric(temp, errors="coerce"),
                        "precipitation": pd.to_numeric(rain, errors="coerce")}).dropna(subset=["date"])
    out["semaine"] = out["date"].map(lambda d: d - pd.Timedelta(days=d.weekday()))
    return out.groupby("semaine").agg(temperature=("temperature", "mean"), precipitation=("precipitation", "sum"))


def weekly_counts(dates: Iterable[date], index: Iterable[date]) -> pd.Series:
    s = pd.Series(1, index=[d - pd.Timedelta(days=d.weekday()) for d in dates]).groupby(level=0).sum()
    return s.reindex(list(index)).fillna(0.0)


def run_all(client: Any, simap_files: list[str], out_series: Any) -> dict[str, Any]:
    """Fetch the real series, evaluate naive vs boosting, return a report (data RÉEL)."""
    import json
    from pathlib import Path

    out_series = Path(out_series)
    out_series.mkdir(parents=True, exist_ok=True)
    kof = kof_jobtracker(client)
    kof.rename("kof_jobtracker").to_csv(out_series / "kof_jobtracker_hebdo.csv", index_label="semaine")
    met = [meteo_weekly(client, st) for st in ("sio", "gve", "ber", "sma")]
    weather = pd.concat(met).groupby(level=0).mean()
    weather.to_csv(out_series / "meteo_4_stations_hebdo.csv", index_label="semaine")
    idx = list(kof.index)
    ex_w = weather.reindex(idx)
    rep: dict[str, Any] = {"donnees": "RÉEL", "sources": {
        "kof": "KOF Job Tracker, ch.kof.jobtracker.total.total.clean.idx (tsdb-api.kof.ethz.ch), hebdomadaire",
        "meteo": "MétéoSuisse OGD, stations Sion, Genève, Berne, Zurich (CC BY 4.0), moyenne hebdomadaire",
        "ofs": "OFS STAT-TAB px-x-0602000000_104, places vacantes par grande région, trimestriel",
        "simap": "adjudications simap de construction collectées (Suisse romande et adjudicateurs valaisans)"}}
    first = next(d for d in idx if d >= date(2022, 1, 3))
    rep["kof_hebdo_sans_signal"] = evaluate_series(kof, None, first, 4, range(1, 9), 52, n_boot=1000)
    rep["kof_hebdo_avec_meteo"] = evaluate_series(kof, ex_w, first, 4, range(1, 9), 52, n_boot=1000)
    # simap volumes exist only since late 2024: short window, with and without the signal
    dates = []
    for f in simap_files:
        for line in Path(f).read_text("utf-8").splitlines():
            r = json.loads(line)
            if r.get("publication_date"):
                dates.append(date.fromisoformat(r["publication_date"][:10]))
    sim = weekly_counts(dates, idx).rolling(4, min_periods=1).sum()
    first_s = next(d for d in idx if d >= date(2025, 6, 2))
    rep["kof_hebdo_fenetre_simap_sans"] = evaluate_series(kof, ex_w, first_s, 2, range(1, 9), 52, n_boot=1000)
    rep["kof_hebdo_fenetre_simap_avec"] = evaluate_series(kof, ex_w.assign(simap_4s=sim.to_numpy()), first_s, 2,
                                                          range(1, 9), 52, n_boot=1000)
    vac = bfs_vacancies(client)
    vac.to_csv(out_series / "ofs_places_vacantes_trimestre.csv", index=False)
    region_col = next(c for c in vac.columns if c.lower().startswith("gross"))
    quarter_col = next(c for c in vac.columns if c.lower().startswith("quart"))
    names = {"0": "Suisse", "1": "Région lémanique", "2": "Espace Mittelland"}
    rep["ofs_trimestriel"] = {}
    for code, name in names.items():
        s = vac[vac[region_col] == code].set_index(quarter_col)["valeur"].sort_index()
        q0 = next(q for q in s.index if q >= "2015Q1")
        rep["ofs_trimestriel"][name] = evaluate_series(s, None, q0, 1, range(1, 5), 4, n_boot=1000)
    return rep
