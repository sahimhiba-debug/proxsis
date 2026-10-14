"""FICTIONAL world generator — the test bench of the backtest.

Everything produced here is invented and marked ``fictif=True``. The world
is a *simulation* with explicit, documented parameters (``WorldConfig``):

* companies (sector, size, location, language);
* latent processes, NOT observable by models: sector business cycle,
  private construction projects, per-project effect sizes;
* observable public signals with a publication lag: public-procurement
  awards (simap-like), building-permit publications (company applicants and
  masked private applicants), commercial-register mutations;
* hiring waves (truth) and the public job postings they produce (target).

``signal_effect`` scales the causal link between signals and hiring. With
``signal_effect=0`` (the *null world*) signals are generated identically but
have no effect: any model that beats the naive baselines there reveals a
leak or a bug. Measured performance on this world validates the mechanics
of the pipeline, NOT the commercial value of the method.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from proxsis.calendar import weeks_between
from proxsis.entities import uid_check_digit
from proxsis.synth.geo import AGENCY_TOWNS, COMMUNES, SECTOR_CANTON_AFFINITY, haversine_km
from proxsis.taxonomy import CONSTRUCTION_SECTORS, SECTOR_TRADES, TRADES, language_for

SECTOR_SHARES: dict[str, float] = {
    "construction_gros_oeuvre": 0.18,
    "construction_second_oeuvre": 0.22,
    "genie_civil": 0.08,
    "industrie": 0.18,
    "horlogerie": 0.10,
    "logistique": 0.14,
    "pharma": 0.10,
}


@dataclass(frozen=True)
class WorldConfig:
    seed: int = 42
    n_companies: int = 4000
    start: date = date(2023, 1, 2)
    end: date = date(2026, 9, 28)  # last Monday with complete data (as of 2026-10-04)
    signal_effect: float = 1.0  # 0 = null world
    hidden_project_ratio: float = 2.0  # private (unobservable) projects per public award
    p_post: float = 0.65  # probability that a hiring wave produces a public posting
    base_wave_rate: float = 0.010  # weekly rate for a 20-employee company
    award_rate_per_year: float = 0.6
    company_permit_rate_per_year: float = 0.15
    branch_rate_per_year: float = 0.05
    capital_rate_per_year: float = 0.08
    noise_mutation_rate_per_year: float = 0.15
    liquidation_rate_per_year: float = 0.01
    new_company_share: float = 0.06
    private_permits_per_weight_per_year: float = 6.0
    n_candidates: int = 700
    size_noise_sigma: float = 0.5  # observed headcount = true x lognormal noise (size is not public)

    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), default=str, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:16]


@dataclass
class World:
    config: WorldConfig
    weeks: list[date]
    companies: pd.DataFrame
    signals: pd.DataFrame
    postings: pd.DataFrame
    waves: pd.DataFrame  # truth (latent, fictional)
    agencies: pd.DataFrame
    consultants: pd.DataFrame
    candidates: pd.DataFrame


_PREFIX = [
    "Alpar",
    "Rhodan",
    "Valmor",
    "Berglin",
    "Lacus",
    "Montal",
    "Sorev",
    "Tavel",
    "Orsan",
    "Brevin",
    "Kaltor",
    "Riedan",
    "Seelan",
    "Waldis",
    "Fluhar",
    "Arvel",
    "Lemar",
    "Jurel",
    "Vignol",
    "Corbel",
    "Dravon",
    "Ermin",
    "Faulor",
    "Gristal",
    "Hellar",
    "Isern",
    "Lorvan",
    "Mirant",
    "Novel",
    "Pradel",
    "Quarel",
    "Ronsel",
    "Silvan",
    "Tormel",
    "Ulmar",
    "Vercor",
    "Zinal",
    "Abrel",
    "Bovan",
    "Celtis",
]
_SUFFIX_FR = {
    "construction_gros_oeuvre": ["Construction", "Bâtiment", "Maçonnerie"],
    "construction_second_oeuvre": ["Électricité", "Sanitaire", "Peinture", "Plâtrerie", "Charpente"],
    "genie_civil": ["Génie Civil", "Terrassements", "Travaux Publics"],
    "industrie": ["Industrie", "Mécanique", "Métal"],
    "horlogerie": ["Horlogerie", "Microtechnique", "Précision"],
    "logistique": ["Logistique", "Transports", "Distribution"],
    "pharma": ["Pharma", "Life Sciences", "Biotech"],
}
_SUFFIX_DE = {
    "construction_gros_oeuvre": ["Bau", "Hochbau", "Baugeschäft"],
    "construction_second_oeuvre": ["Elektro", "Haustechnik", "Malerei", "Gipserei", "Holzbau"],
    "genie_civil": ["Tiefbau", "Strassenbau", "Erdbau"],
    "industrie": ["Industrie", "Maschinenbau", "Metallbau"],
    "horlogerie": ["Uhren", "Mikrotechnik", "Präzision"],
    "logistique": ["Logistik", "Transporte", "Distribution"],
    "pharma": ["Pharma", "Life Sciences", "Biotech"],
}

_FIRST = [
    "Camille",
    "Luca",
    "Noa",
    "Sasha",
    "Alix",
    "Robin",
    "Elia",
    "Jessy",
    "Lou",
    "Morgan",
    "Andrea",
    "Kim",
    "Yannick",
    "Dominique",
    "Charlie",
    "Maxime",
    "Lio",
    "Sam",
]


def _fictional_uid(rng: np.random.Generator, used: set[str]) -> str:
    while True:
        first8 = "".join(str(d) for d in rng.integers(0, 10, size=8))
        chk = uid_check_digit(first8)
        if chk is None:
            continue
        uid = f"CHE{first8}{chk}"
        if uid not in used:
            used.add(uid)
            return uid


def _season(sector: str, woy: np.ndarray) -> np.ndarray:
    if sector in CONSTRUCTION_SECTORS:
        s = 1.0 + 0.35 * np.sin(2 * np.pi * (woy - 8) / 52.0)
        s = np.where((woy >= 51) | (woy <= 1), s * 0.3, s)  # winter break
        return np.asarray(s)
    if sector == "logistique":
        return np.asarray(1.0 + 0.45 * np.exp(-((woy - 42) ** 2) / (2 * 4.0**2)))
    return np.asarray(1.0 + 0.08 * np.sin(2 * np.pi * (woy - 2) / 52.0))


class _Builder:
    def __init__(self, cfg: WorldConfig) -> None:
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.weeks = weeks_between(cfg.start, cfg.end)
        self.W = len(self.weeks)
        self.signals: list[dict[str, Any]] = []
        self._sig_n = 0
        self.emp: np.ndarray = np.zeros(0)

    # -- helpers -------------------------------------------------------
    def week_index(self, d: date) -> int:
        return (d - self.weeks[0]).days // 7

    def date_of(self, wi: float, jitter_days: int = 6) -> date:
        return self.weeks[0] + timedelta(days=int(wi * 7) + int(self.rng.integers(0, jitter_days + 1)))

    def add_signal(self, **kw: object) -> str:
        self._sig_n += 1
        sid = f"sig{self._sig_n:06d}"
        rec = {
            "signal_id": sid,
            "fictif": True,
            "source": "FICTIF:monde-simule",
            "license": "FICTIF — données inventées",
            "url": f"fictif://signal/{sid}",
        }
        rec.update(kw)
        self.signals.append(rec)
        return sid

    # -- companies -----------------------------------------------------
    def companies(self) -> pd.DataFrame:
        cfg, rng = self.cfg, self.rng
        sectors = list(SECTOR_SHARES)
        sec = rng.choice(sectors, size=cfg.n_companies, p=np.array(list(SECTOR_SHARES.values())))
        used_uids: set[str] = set()
        used_names: set[str] = set()
        rows = []
        cw = np.array([c[4] for c in COMMUNES])
        for i, s in enumerate(sec):
            aff = np.array([SECTOR_CANTON_AFFINITY.get(s, {}).get(c[1], 1.0) for c in COMMUNES])
            p = cw * aff
            ci = int(rng.choice(len(COMMUNES), p=p / p.sum()))
            commune, canton, lat, lon, _ = COMMUNES[ci]
            lang = language_for(canton, commune)
            if commune == "Biel/Bienne":
                lang = "de" if rng.random() < 0.6 else "fr"
            med = 18 if s in CONSTRUCTION_SECTORS else 35
            emp = int(np.clip(rng.lognormal(np.log(med), 1.05), 3, 3000))
            for _ in range(50):
                stem = rng.choice(_PREFIX) + rng.choice(["", "ex", "ia", "on", "is", "a"])
                word = rng.choice((_SUFFIX_DE if lang == "de" else _SUFFIX_FR)[s])
                form = rng.choice(["AG", "GmbH"] if lang == "de" else ["SA", "Sàrl"], p=[0.6, 0.4])
                name = f"{stem} {word} {form}"
                if name not in used_names:
                    used_names.add(name)
                    break
            created_wi = -1
            if rng.random() < cfg.new_company_share:
                created_wi = int(rng.integers(8, self.W - 4))
            rows.append(
                {
                    "company_id": f"c{i:05d}",
                    "uid": _fictional_uid(rng, used_uids),
                    "name": name,
                    "canton": canton,
                    "commune": commune,
                    "lat": lat + rng.normal(0, 0.01),
                    "lon": lon + rng.normal(0, 0.01),
                    "language": lang,
                    "sector": s,
                    "employees_est": emp,
                    "created_week": created_wi,
                    "liquidated_week": -1,
                    "fictif": True,
                    "source": "FICTIF:monde-simule",
                    "license": "FICTIF — données inventées",
                    "url": f"fictif://company/c{i:05d}",
                }
            )
        return pd.DataFrame(rows)

    # -- main simulation ----------------------------------------------
    def build(self) -> World:
        cfg, rng, W = self.cfg, self.rng, self.W
        comp = self.companies()
        N = len(comp)
        woy = np.array([w.isocalendar()[1] for w in self.weeks])
        emp = comp["employees_est"].to_numpy(dtype=float)
        self.emp = emp
        # Models only see a noisy headcount estimate; the simulation uses the true size.
        comp["employees_true"] = comp["employees_est"]
        noise = rng.lognormal(0.0, cfg.size_noise_sigma, size=N) if cfg.size_noise_sigma > 0 else np.ones(N)
        comp["employees_est"] = np.maximum(1, np.round(emp * noise)).astype(int)

        # Base hazard (turnover + growth), independent of signals.
        size_factor = (emp / 20.0) ** 0.6
        logh = np.zeros((N, W))
        for s in SECTOR_SHARES:
            idx = np.where(comp["sector"].to_numpy() == s)[0]
            cyc = np.zeros(W)
            for t in range(1, W):
                cyc[t] = 0.95 * cyc[t - 1] + rng.normal(0, 0.05)
            logh[idx, :] = np.log(_season(s, woy))[None, :] + cyc[None, :]
        logh += np.log(cfg.base_wave_rate * size_factor)[:, None]
        # Construction-trade boost (projects) and operations boost (expansions).
        boost_constr = np.zeros((N, W))
        boost_ops = np.zeros((N, W))
        beta = cfg.signal_effect

        def add_window(arr: np.ndarray, ci: int, a: int, b: int, strength: float) -> None:
            a, b = max(a, 0), min(b, W)
            if a < b:
                arr[ci, a:b] += strength

        is_constr = comp["sector"].isin(list(CONSTRUCTION_SECTORS)).to_numpy()
        lat = comp["lat"].to_numpy()
        lon = comp["lon"].to_numpy()
        created = comp["created_week"].to_numpy()

        def alive_from(ci: int) -> int:
            return max(0, int(created[ci]) + 1) if created[ci] >= 0 else 0

        # 1) Public awards (observable) + hidden private projects for construction firms.
        for ci in map(int, np.where(is_constr)[0]):
            sec = str(comp.at[ci, "sector"])
            rate = (
                cfg.award_rate_per_year
                * (emp[ci] / 20.0) ** 0.6
                * (0.6 if sec == "construction_second_oeuvre" else 1.0)
            )
            for public in (True, False):
                lam = rate * (1.0 if public else cfg.hidden_project_ratio) * W / 52.0
                for _ in range(rng.poisson(lam)):
                    d_wi = int(rng.integers(alive_from(ci), W))
                    value = float(np.clip(rng.lognormal(np.log(350_000 * (emp[ci] / 20) ** 0.5), 1.0), 30_000, 60e6))
                    start_wi = d_wi + int(rng.integers(3, 15))
                    lead = int(rng.integers(2, 9))
                    effect = rng.gamma(1.0, 1.0)  # many projects need no extra hires
                    rel = min(3.0, value / (emp[ci] * 15_000))
                    add_window(boost_constr, ci, start_wi - lead, start_wi + 2, beta * 1.6 * effect * rel)
                    if public:
                        pub = self.date_of(d_wi) + timedelta(days=int(rng.integers(3, 26)))
                        ev = self.date_of(d_wi)
                        pub = max(pub, ev)
                        trades = list(SECTOR_TRADES[sec][:2])
                        self.add_signal(
                            company_id=comp.at[ci, "company_id"],
                            family="marche_attribue",
                            subtype="adjudication",
                            event_date=ev,
                            available_at=pub,
                            canton=comp.at[ci, "canton"],
                            commune=comp.at[ci, "commune"],
                            lat=lat[ci],
                            lon=lon[ci],
                            value_chf=round(value, -2),
                            trades=";".join(trades),
                            expected_start=self.weeks[min(start_wi, W - 1)]
                            if start_wi < W
                            else self.weeks[-1] + timedelta(days=7 * (start_wi - W + 1)),
                        )

        # 2) Company permits (expansions) for non-construction firms + local construction demand.
        constr_idx = np.where(is_constr)[0]
        for ci in map(int, np.where(~is_constr)[0]):
            lam = cfg.company_permit_rate_per_year * (emp[ci] / 50.0) ** 0.5 * W / 52.0
            for _ in range(rng.poisson(lam)):
                d_wi = int(rng.integers(alive_from(ci), W))
                value = float(np.clip(rng.lognormal(np.log(2_500_000), 1.0), 200_000, 150e6))
                ev = self.date_of(d_wi)
                pub = ev + timedelta(days=int(rng.integers(1, 8)))
                self.add_signal(
                    company_id=comp.at[ci, "company_id"],
                    family="permis_construire",
                    subtype="mise_a_l_enquete",
                    event_date=ev,
                    available_at=pub,
                    canton=comp.at[ci, "canton"],
                    commune=comp.at[ci, "commune"],
                    lat=lat[ci],
                    lon=lon[ci],
                    value_chf=round(value, -3),
                    trades=";".join(SECTOR_TRADES[str(comp.at[ci, "sector"])][:2]),
                )
                if rng.random() < 0.3:
                    continue  # abandoned project
                build_start = d_wi + int(rng.integers(8, 30))
                done = build_start + int(rng.integers(26, 61))
                add_window(boost_ops, ci, done - 8, done + 4, beta * 1.5 * rng.gamma(1.5, 1 / 1.5))
                self._assign_local_construction(ci, build_start, value, constr_idx, lat, lon, boost_constr, beta)

        # 3) Private residential permits (applicant masked) -> hidden demand for local builders.
        cw = np.array([c[4] for c in COMMUNES])
        for k, (commune, canton, clat, clon, _wgt) in enumerate(COMMUNES):
            lam = cfg.private_permits_per_weight_per_year * cw[k] * W / 52.0
            for _ in range(rng.poisson(lam)):
                d_wi = int(rng.integers(0, W))
                value = float(np.clip(rng.lognormal(np.log(900_000), 0.9), 150_000, 30e6))
                ev = self.date_of(d_wi)
                self.add_signal(
                    company_id=None,
                    family="permis_construire",
                    subtype="mise_a_l_enquete",
                    event_date=ev,
                    available_at=ev + timedelta(days=int(rng.integers(1, 8))),
                    canton=canton,
                    commune=commune,
                    lat=clat,
                    lon=clon,
                    value_chf=round(value, -3),
                    trades="macon;manoeuvre_construction",
                    applicant_private=True,
                )
                if rng.random() < 0.25:
                    continue
                start = d_wi + int(rng.integers(10, 35))
                self._assign_local_construction(
                    None, start, value, constr_idx, lat, lon, boost_constr, beta, at=(clat, clon)
                )

        # 4) Commercial-register mutations.
        for ci in range(N):
            cid = comp.at[ci, "company_id"]
            base = dict(
                company_id=cid,
                canton=comp.at[ci, "canton"],
                commune=comp.at[ci, "commune"],
                lat=lat[ci],
                lon=lon[ci],
                family="mutation_rc",
            )
            a0 = alive_from(ci)
            if created[ci] >= 0:
                ev = self.date_of(created[ci])
                self.add_signal(
                    **base,
                    subtype="nouvelle_inscription",
                    event_date=ev,
                    available_at=ev + timedelta(days=int(rng.integers(3, 11))),
                )
                add_window(
                    boost_ops if not is_constr[ci] else boost_constr, ci, created[ci] + 1, created[ci] + 17, beta * 2.0
                )
            for subtype, rate, strength, win in (
                ("succursale", cfg.branch_rate_per_year * (emp[ci] / 20) ** 0.3, 2.0, (2, 12)),
                ("augmentation_capital", cfg.capital_rate_per_year, 0.6, (0, 26)),
                ("changement_but", cfg.noise_mutation_rate_per_year / 2, 0.0, (0, 1)),
                ("transfert_siege", cfg.noise_mutation_rate_per_year / 2, 0.0, (0, 1)),
            ):
                for _ in range(rng.poisson(rate * W / 52.0)):
                    d_wi = int(rng.integers(a0, W))
                    ev = self.date_of(d_wi)
                    self.add_signal(
                        **base,
                        subtype=subtype,
                        event_date=ev,
                        available_at=ev + timedelta(days=int(rng.integers(3, 11))),
                    )
                    target = boost_constr if is_constr[ci] else boost_ops
                    if strength > 0:
                        add_window(target, ci, d_wi + win[0], d_wi + win[1], beta * strength * rng.gamma(2.0, 0.5))
            if rng.random() < cfg.liquidation_rate_per_year * W / 52.0:
                d_wi = int(rng.integers(a0 + 4, W)) if a0 + 4 < W else W - 1
                ev = self.date_of(d_wi)
                self.add_signal(
                    **base,
                    subtype="liquidation",
                    event_date=ev,
                    available_at=ev + timedelta(days=int(rng.integers(3, 11))),
                )
                comp.at[ci, "liquidated_week"] = d_wi
                # Liquidation is a real-world fact: hiring stops whatever the signal_effect.
                logh[ci, d_wi:] -= 3.0

        # Companies do not exist before creation.
        for ci in map(int, np.where(created >= 0)[0]):
            logh[ci, : created[ci] + 1] = -50.0

        # Hazards and waves.
        h_constr = np.exp(logh) * (1.0 + boost_constr) * np.where(is_constr, 1.0, 0.0)[:, None]
        h_ops = np.exp(logh) * (1.0 + boost_ops) * np.where(is_constr, 0.0, 1.0)[:, None]
        h = np.clip(h_constr + h_ops, 0, 0.9)
        draws = rng.random((N, W)) < h
        waves, postings = [], []
        pn = 0
        for wn, (ci_, wi_) in enumerate(zip(*np.nonzero(draws), strict=True)):
            ci, wi = int(ci_), int(wi_)
            sec = str(comp.at[ci, "sector"])
            sector_trades = SECTOR_TRADES[sec]
            n_trades = 1 + int(rng.random() < 0.35)
            chosen = list(rng.choice(sector_trades, size=min(n_trades, len(sector_trades)), replace=False))
            n_pos = 1 + int(rng.poisson(0.6 + 0.4 * np.log1p(emp[ci] / 20)))
            boosted = (boost_constr[ci, wi] + boost_ops[ci, wi]) > 0
            temp_need = bool(rng.random() < (0.55 if boosted else 0.35))
            wave_date = self.date_of(wi)
            waves.append(
                {
                    "wave_id": f"w{wn:06d}",
                    "company_id": comp.at[ci, "company_id"],
                    "week": self.weeks[wi],
                    "date": wave_date,
                    "trades": ";".join(chosen),
                    "n_positions": n_pos,
                    "signal_driven": boosted,
                    "temp_need": temp_need,
                    "fictif": True,
                }
            )
            if rng.random() < cfg.p_post:
                for t in chosen:
                    pn += 1
                    pdate = wave_date + timedelta(days=int(rng.integers(0, 15)))
                    postings.append(
                        {
                            "posting_id": f"p{pn:06d}",
                            "company_id": comp.at[ci, "company_id"],
                            "trade": t,
                            "available_at": pdate,
                            "construction": TRADES[t].construction,
                            "fictif": True,
                            "source": "FICTIF:offres-simulees",
                            "url": f"fictif://posting/p{pn:06d}",
                        }
                    )

        sig = pd.DataFrame(self.signals)
        for col in ("event_date", "available_at"):
            sig[col] = pd.to_datetime(sig[col]).dt.date
        post = pd.DataFrame(postings)
        post["available_at"] = pd.to_datetime(post["available_at"]).dt.date
        post = post[post["available_at"] <= cfg.end + timedelta(days=6)].reset_index(drop=True)
        sig = sig[sig["available_at"] <= cfg.end + timedelta(days=6)].reset_index(drop=True)
        agencies, consultants = self._agencies(comp)
        candidates = self._candidates()
        return World(cfg, self.weeks, comp, sig, post, pd.DataFrame(waves), agencies, consultants, candidates)

    def _assign_local_construction(
        self,
        owner_ci: int | None,
        start_wi: int,
        value: float,
        constr_idx: np.ndarray,
        lat: np.ndarray,
        lon: np.ndarray,
        boost: np.ndarray,
        beta: float,
        at: tuple[float, float] | None = None,
    ) -> None:
        """A built project hires a nearby construction firm (hidden from models)."""
        rng = self.rng
        olat, olon = at if at is not None else (lat[owner_ci], lon[owner_ci])
        d = np.hypot((lat[constr_idx] - olat) * 111.0, (lon[constr_idx] - olon) * 76.0)
        near = constr_idx[d < 30.0]
        if len(near) == 0:
            return
        ci = int(rng.choice(near))
        lead = int(rng.integers(2, 8))
        rel = min(3.0, value / (max(1.0, float(self.emp[ci])) * 15_000))
        a, b = max(start_wi - lead, 0), min(start_wi + 2, self.W)
        if a < b:
            boost[ci, a:b] += beta * 1.2 * rng.gamma(1.0, 1.0) * rel

    def _agencies(self, comp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        lookup = {c[0]: c for c in COMMUNES}
        ag_rows, cons_rows = [], []
        for k, town in enumerate(AGENCY_TOWNS):
            _, canton, la, lo, _ = lookup[town]
            lang = language_for(canton, town)
            aid = f"a{k:02d}"
            brand = "Flexsis (FICTIF)" if k < 9 else "Flexsis Deutschschweiz (FICTIF)"
            ag_rows.append(
                {
                    "agency_id": aid,
                    "name": f"Agence {town} (FICTIF)",
                    "brand": brand,
                    "canton": canton,
                    "town": town,
                    "lat": la,
                    "lon": lo,
                    "language": lang,
                    "fictif": True,
                }
            )
            for j in range(2 if k % 3 else 3):
                first = _FIRST[(k * 3 + j) % len(_FIRST)]
                cons_rows.append(
                    {
                        "consultant_id": f"u{k:02d}{j}",
                        "agency_id": aid,
                        "display_name": f"{first} {chr(65 + (k + j) % 26)}. (FICTIF)",
                        "role": "consultant",
                        "fictif": True,
                    }
                )
            cons_rows.append(
                {
                    "consultant_id": f"u{k:02d}m",
                    "agency_id": aid,
                    "display_name": f"Chef·fe d'agence {town} (FICTIF)",
                    "role": "chef_agence",
                    "fictif": True,
                }
            )
        cons_rows.append(
            {
                "consultant_id": "g0",
                "agency_id": "groupe",
                "display_name": "Direction groupe (FICTIF)",
                "role": "groupe",
                "fictif": True,
            }
        )
        ag = pd.DataFrame(ag_rows)
        # Territory: nearest agency.
        c_lat, c_lon = comp["lat"].to_numpy(float), comp["lon"].to_numpy(float)
        a_lat, a_lon = ag["lat"].to_numpy(float), ag["lon"].to_numpy(float)
        dist = np.array([[haversine_km(cy, cx, ay, ax) for ay, ax in zip(a_lat, a_lon, strict=True)]
                         for cy, cx in zip(c_lat, c_lon, strict=True)])
        comp["agency_id"] = ag["agency_id"].to_numpy()[dist.argmin(axis=1)]
        return ag, pd.DataFrame(cons_rows)

    def _candidates(self) -> pd.DataFrame:
        rng, cfg = self.rng, self.cfg
        rows = []
        all_trades = list(TRADES)
        cw = np.array([c[4] for c in COMMUNES])
        for i in range(cfg.n_candidates):
            ci = int(rng.choice(len(COMMUNES), p=cw / cw.sum()))
            commune, canton, la, lo, _ = COMMUNES[ci]
            main = str(rng.choice(all_trades))
            trades = [main]
            if rng.random() < 0.3:
                trades.append(str(rng.choice(all_trades)))
            lang = language_for(canton, commune)
            langs = [lang] + (["fr" if lang == "de" else "de"] if rng.random() < 0.25 else [])
            certs = []
            if main in ("grutier",) or rng.random() < 0.1:
                certs.append("permis_grue")
            if main == "cariste" or rng.random() < 0.15:
                certs.append("permis_cariste")
            if TRADES[main].construction and rng.random() < 0.5:
                certs.append("sst_chantier")
            age_band = str(rng.choice(["18-29", "30-44", "45-54", "55+"], p=[0.3, 0.35, 0.2, 0.15]))
            max_exp = {"18-29": 8, "30-44": 20, "45-54": 30, "55+": 40}[age_band]
            rows.append(
                {
                    "candidate_id": f"k{i:04d}",
                    "trades": ";".join(trades),
                    # Experience depends on age: a realistic proxy that the fairness audit must detect.
                    "experience_years": int(rng.integers(0, max_exp + 1)),
                    "commune": commune,
                    "canton": canton,
                    "lat": la + rng.normal(0, 0.02),
                    "lon": lo + rng.normal(0, 0.02),
                    "languages": ";".join(langs),
                    "certifications": ";".join(certs),
                    "driving_licence": bool(rng.random() < 0.7),
                    "max_travel_km": float(rng.choice([15, 25, 40, 60])),
                    "available_from": self.weeks[-1] + timedelta(days=int(rng.integers(-30, 60))),
                    # Audit attributes: FICTIONAL, never used as features (fairness audit only).
                    "audit_gender": str(rng.choice(["F", "M"], p=[0.3, 0.7])),
                    "audit_age_band": age_band,
                    "audit_nationality_group": str(rng.choice(["CH", "UE/AELE", "autre"], p=[0.45, 0.45, 0.10])),
                    "fictif": True,
                }
            )
        return pd.DataFrame(rows)


def generate_world(cfg: WorldConfig | None = None) -> World:
    return _Builder(cfg or WorldConfig()).build()
