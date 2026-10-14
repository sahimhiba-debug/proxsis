"""Point-in-time feature panel ("vu à la date T").

For a cutoff T (a Monday), only information with ``available_at < T`` is
used. All counts are computed from weekly matrices (company × week) by
cumulative sums, which makes leakage structurally impossible: the value at
cutoff index ``w`` only reads weeks ``< w``.

The builder is generic: it takes plain tables (companies, signals,
postings), so it runs on the FICTIONAL world and on real data alike.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from proxsis.taxonomy import CONSTRUCTION_SECTORS, SECTOR_TRADES

# (family, subtype or None, windows in weeks)
_COUNT_SPECS: list[tuple[str, str, str | None, tuple[int, ...]]] = [
    ("award", "marche_attribue", None, (6, 13, 26, 52)),
    ("cpermit", "permis_construire", None, (26, 52, 78)),
    ("branch", "mutation_rc", "succursale", (13, 26)),
    ("capital", "mutation_rc", "augmentation_capital", (26,)),
    ("newreg", "mutation_rc", "nouvelle_inscription", (17, 52)),
    ("noise_mut", "mutation_rc", "changement_but", (26,)),
    ("move", "mutation_rc", "transfert_siege", (26,)),
    ("liquidation", "mutation_rc", "liquidation", (520,)),
]

FEATURE_GROUPS: dict[str, str] = {
    "award": "Projet — marché public attribué",
    "cpermit": "Projet — permis de construire de l'entreprise",
    "branch": "Entreprise — nouvelle succursale",
    "capital": "Entreprise — augmentation de capital",
    "newreg": "Entreprise — nouvelle inscription au RC",
    "noise_mut": "Entreprise — changement de but",
    "move": "Entreprise — transfert de siège",
    "liquidation": "Entreprise — liquidation",
    "post": "Recrutement — offres publiées",
    "region": "Région — permis de construire à moins de 25 km",
    "size": "Taille de l'entreprise",
    "season": "Saison",
    "sector": "Secteur",
}


def week_index(dates: pd.Series, weeks: list[date]) -> np.ndarray:
    """Index of the week (Monday-based) containing each date; -1 if before start."""
    w0 = np.datetime64(weeks[0])
    d = pd.to_datetime(dates).to_numpy(dtype="datetime64[D]")
    return np.floor((d - w0).astype(int) / 7).astype(int)


@dataclass
class Panel:
    weeks: list[date]
    company_ids: np.ndarray
    frame: pd.DataFrame  # one row per (company, cutoff week index)
    feature_cols: list[str]
    categorical_cols: list[str]


class PanelBuilder:
    def __init__(
        self,
        companies: pd.DataFrame,
        signals: pd.DataFrame,
        postings: pd.DataFrame,
        weeks: list[date],
        region_radius_km: float = 25.0,
    ) -> None:
        self.c = companies.reset_index(drop=True)
        self.s = signals
        self.p = postings
        self.weeks = weeks
        self.W = len(weeks)
        self.N = len(self.c)
        self.idx = {cid: i for i, cid in enumerate(self.c["company_id"])}
        self.radius = region_radius_km

    # -- weekly matrices --------------------------------------------------
    def _matrix(self, df: pd.DataFrame, value_col: str | None = None) -> np.ndarray:
        m = np.zeros((self.N, self.W + 1), dtype=np.float64)
        if df.empty:
            return m
        rows = df["company_id"].map(self.idx)
        wi = week_index(df["available_at"], self.weeks)
        ok = rows.notna().to_numpy() & (wi >= 0) & (wi < self.W)
        r = rows.to_numpy()[ok].astype(int)
        vals = df[value_col].fillna(0).to_numpy()[ok] if value_col else np.ones(ok.sum())
        np.add.at(m, (r, wi[ok]), vals)
        return m

    @staticmethod
    def _window(cs: np.ndarray, w: np.ndarray, k: int) -> np.ndarray:
        """Sum over weeks [w-k, w-1] given cumulative sums cs[:, j] = sum weeks < j."""
        lo = np.clip(w - k, 0, None)
        return np.asarray(cs[:, w] - cs[:, lo])

    @staticmethod
    def _cumsum0(m: np.ndarray) -> np.ndarray:
        return np.concatenate([np.zeros((m.shape[0], 1)), np.cumsum(m, axis=1)], axis=1)

    @staticmethod
    def _weeks_since_last(m: np.ndarray, cap: int = 520) -> np.ndarray:
        """ws[:, j] = weeks since the last non-zero week < j (cap if none)."""
        N, W1 = m.shape
        out = np.full((N, W1 + 1), cap, dtype=np.float64)
        last = np.full(N, -10_000)
        for j in range(W1 + 1):
            if j > 0:
                nz = m[:, j - 1] > 0
                last = np.where(nz, j - 1, last)
            out[:, j] = np.minimum(cap, j - last)
        return out

    def _regional(self) -> np.ndarray:
        perm = self.s[self.s["family"] == "permis_construire"]
        m = np.zeros((self.N, self.W + 1))
        if perm.empty:
            return m
        wi = week_index(perm["available_at"], self.weeks)
        ok = (wi >= 0) & (wi < self.W)
        plat = perm["lat"].to_numpy()[ok]
        plon = perm["lon"].to_numpy()[ok]
        clat = self.c["lat"].to_numpy()[:, None]
        clon = self.c["lon"].to_numpy()[:, None]
        d = np.hypot((clat - plat[None, :]) * 111.2, (clon - plon[None, :]) * 76.0)
        near = (d < self.radius).astype(np.float64)
        onehot = np.zeros((ok.sum(), self.W + 1))
        onehot[np.arange(ok.sum()), wi[ok]] = 1.0
        return np.asarray(near @ onehot)

    # -- panel -------------------------------------------------------------
    def build(self, cutoffs: list[int]) -> Panel:
        w = np.asarray(cutoffs, dtype=int)
        cols: dict[str, np.ndarray] = {}
        for name, fam, sub, wins in _COUNT_SPECS:
            sel = self.s[(self.s["family"] == fam) & (self.s["company_id"].notna())]
            if sub is not None:
                sel = sel[sel["subtype"] == sub]
            m = self._matrix(sel)
            cs = self._cumsum0(m)
            for k in wins:
                cols[f"{name}_{k}w"] = self._window(cs, w, k)
            if name in ("award", "cpermit"):
                v = self._cumsum0(self._matrix(sel, "value_chf"))
                cols[f"{name}_logvalue_{wins[1]}w"] = np.log1p(self._window(v, w, wins[1]))
                cols[f"{name}_weeks_since"] = self._weeks_since_last(m)[:, w]
        # Postings of the company (recent activity), in its sector trades.
        pm = self._matrix(self.p)
        pcs = self._cumsum0(pm)
        for k in (8, 26, 52):
            cols[f"post_{k}w"] = self._window(pcs, w, k)
        cols["post_weeks_since"] = self._weeks_since_last(pm)[:, w]
        # Regional permits.
        rcs = self._cumsum0(self._regional())
        cols["region_permits_13w"] = self._window(rcs, w, 13)
        cols["region_permits_52w"] = self._window(rcs, w, 52)

        n_cut = len(w)
        frame = pd.DataFrame({k: v.T.reshape(-1) for k, v in cols.items()})
        frame.insert(0, "company_id", np.tile(self.c["company_id"].to_numpy(), n_cut))
        frame.insert(1, "cutoff_idx", np.repeat(w, self.N))
        emp = self.c["employees_est"].fillna(self.c["employees_est"].median()).to_numpy(dtype=float)
        frame["size_log_employees"] = np.tile(np.log(emp), n_cut)
        woy = np.array([self.weeks[min(i, self.W - 1)].isocalendar()[1] for i in w])
        frame["season_sin"] = np.repeat(np.sin(2 * np.pi * woy / 52.0), self.N)
        frame["season_cos"] = np.repeat(np.cos(2 * np.pi * woy / 52.0), self.N)
        frame["sector"] = pd.Categorical(np.tile(self.c["sector"].to_numpy(), n_cut), categories=sorted(SECTOR_TRADES))
        frame["is_construction"] = np.tile(self.c["sector"].isin(list(CONSTRUCTION_SECTORS)).to_numpy(), n_cut).astype(
            int
        )
        feature_cols = [c for c in frame.columns if c not in ("company_id", "cutoff_idx")]
        for c in feature_cols:
            if frame[c].dtype == np.float64:
                frame[c] = frame[c].astype(np.float32)
        return Panel(self.weeks, self.c["company_id"].to_numpy(), frame, feature_cols, ["sector"])


def feature_group(col: str) -> str:
    return FEATURE_GROUPS.get(col.split("_")[0], col)
