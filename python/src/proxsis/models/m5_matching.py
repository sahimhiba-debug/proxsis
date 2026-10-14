"""M5 — candidate suggestions for an estimated need (FICTIONAL candidates).

1. Strict criteria (all must hold): the candidate has the trade or a close
   trade; holds the certification the trade legally requires; is available
   within 14 days of the need; lives within his/her travel radius (25 km max
   without a driving licence).
2. Soft score: skill proximity, experience, distance, availability.
3. Every suggestion carries its reasons. The consultant decides.

Protected attributes (gender, age, nationality — ``audit_*`` columns, present
only in the fictional data for the audit) are NEVER read by the matcher. The
working language is shown to the consultant but not used in the score, to
avoid a nationality proxy (docs/adr/0008-m5-candidats-equite.md).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
import pandas as pd

from proxsis.synth.geo import haversine_km
from proxsis.taxonomy import trade_label

# Skill proximity between trades (symmetric); 1.0 = same trade.
TRADE_NEIGHBOURS: dict[tuple[str, str], float] = {
    ("macon", "coffreur"): 0.7,
    ("macon", "manoeuvre_construction"): 0.5,
    ("coffreur", "manoeuvre_construction"): 0.5,
    ("peintre", "platrier"): 0.7,
    ("machiniste", "grutier"): 0.4,
    ("charpentier", "coffreur"): 0.4,
    ("polymecanicien", "decolleteur"): 0.7,
    ("decolleteur", "horloger"): 0.4,
    ("operateur_production", "decolleteur"): 0.5,
    ("operateur_production", "operateur_pharma"): 0.6,
    ("operateur_production", "polymecanicien"): 0.4,
    ("cariste", "agent_logistique"): 0.7,
    ("agent_logistique", "chauffeur_pl"): 0.3,
    ("soudeur", "polymecanicien"): 0.4,
    ("operateur_pharma", "laborantin"): 0.3,
}
REQUIRED_CERT: dict[str, str] = {"grutier": "permis_grue", "cariste": "permis_cariste"}
CERT_LABELS = {
    "permis_grue": ("permis de grutier", "Kranführerausweis"),
    "permis_cariste": ("permis de cariste", "Staplerausweis"),
    "sst_chantier": ("formation sécurité chantier", "Baustellen-Sicherheitskurs"),
}
MIN_SKILL = 0.5
# Years beyond which experience no longer raises the score. v1 = 15 years; lower caps are a *proposal*
# (docs/adr/0012-m5-plafond-experience.md, status « proposé »): the default stays 15 until it is accepted.
DEFAULT_EXP_CAP_YEARS = 15.0


def experience_component(years: np.ndarray, cap_years: float = DEFAULT_EXP_CAP_YEARS) -> np.ndarray:
    """log1p(years) scaled so that ``cap_years`` and above give 1.0."""
    return np.minimum(1.0, np.log1p(np.asarray(years, dtype=float)) / math.log1p(cap_years))


def skill_proximity(need: str, trades: list[str]) -> float:
    best = 0.0
    for t in trades:
        if t == need:
            return 1.0
        best = max(best, TRADE_NEIGHBOURS.get((need, t), TRADE_NEIGHBOURS.get((t, need), 0.0)))
    return best


@dataclass
class Need:
    company_id: str
    trade: str
    lat: float
    lon: float
    start: date
    n: int = 1


@dataclass
class Suggestion:
    candidate_id: str
    score: float
    reasons_fr: list[str] = field(default_factory=list)
    reasons_de: list[str] = field(default_factory=list)
    distance_km: float = 0.0


_FORBIDDEN = ("audit_gender", "audit_age_band", "audit_nationality_group")


class CandidateMatcher:
    name = "M5_candidats"

    def __init__(self, candidates: pd.DataFrame, exp_cap_years: float = DEFAULT_EXP_CAP_YEARS,
                 exp_weight: float = 0.20) -> None:
        self.exp_cap_years = exp_cap_years
        self.exp_weight = exp_weight
        # The matcher only keeps the columns it is allowed to use.
        allowed = [c for c in candidates.columns if c not in _FORBIDDEN]
        self.c = candidates[allowed].reset_index(drop=True).copy()
        self.c["m_trades"] = self.c["trades"].fillna("").map(lambda s: [t for t in s.split(";") if t])
        self.c["m_certs"] = self.c["certifications"].fillna("").map(lambda s: [t for t in s.split(";") if t])
        self.c["m_avail"] = pd.to_datetime(self.c["available_from"]).dt.date

    def eligible(self, need: Need) -> pd.DataFrame:
        c = self.c
        skill = c["m_trades"].map(lambda ts: skill_proximity(need.trade, ts))
        dist = np.array([haversine_km(need.lat, need.lon, a, b) for a, b in zip(c["lat"], c["lon"], strict=True)])
        radius = np.where(c["driving_licence"], c["max_travel_km"], np.minimum(c["max_travel_km"], 25.0))
        cert = REQUIRED_CERT.get(need.trade)
        has_cert = c["m_certs"].map(lambda cs: cert is None or cert in cs)
        avail = c["m_avail"].map(lambda d: d <= need.start + timedelta(days=14))
        mask = (skill >= MIN_SKILL) & (dist <= radius) & has_cert & avail
        out = c[mask].copy()
        out["m_skill"] = skill[mask]
        out["m_dist"] = dist[mask.to_numpy()]
        out["m_radius"] = radius[mask.to_numpy()]
        return out

    def funnel(self, need: Need) -> dict[str, int]:
        """How many candidates pass each strict criterion, in order (shown to the consultant)."""
        c = self.c
        skill = c["m_trades"].map(lambda ts: skill_proximity(need.trade, ts)) >= MIN_SKILL
        cert = REQUIRED_CERT.get(need.trade)
        has_cert = c["m_certs"].map(lambda cs: cert is None or cert in cs)
        avail = c["m_avail"].map(lambda d: d <= need.start + timedelta(days=14))
        dist = np.array([haversine_km(need.lat, need.lon, a, b) for a, b in zip(c["lat"], c["lon"], strict=True)])
        radius = np.where(c["driving_licence"], c["max_travel_km"], np.minimum(c["max_travel_km"], 25.0))
        near = pd.Series(dist <= radius, index=c.index)
        return {"tous": len(c), "metier": int(skill.sum()), "certificat": int((skill & has_cert).sum()),
                "disponible": int((skill & has_cert & avail).sum()),
                "distance": int((skill & has_cert & avail & near).sum())}

    def score_frame(self, need: Need, e: pd.DataFrame) -> np.ndarray:
        exp = experience_component(e["experience_years"].to_numpy(float), self.exp_cap_years)
        dist = 1.0 - e["m_dist"].to_numpy() / np.maximum(e["m_radius"].to_numpy(), 1.0)
        days = np.array([(d - need.start).days for d in e["m_avail"]])
        avail = np.clip(1.0 - np.maximum(days, 0) / 14.0, 0, 1)
        return np.asarray(0.55 * e["m_skill"].to_numpy() + self.exp_weight * exp + 0.15 * dist + 0.10 * avail)

    def suggest(self, need: Need, k: int = 5) -> list[Suggestion]:
        e = self.eligible(need)
        if e.empty:
            return []
        e = e.assign(m_score=self.score_frame(need, e)).sort_values(
            ["m_score", "candidate_id"], ascending=[False, True]
        )
        out = []
        for r in e.head(k).to_dict("records"):
            fr: list[str] = []
            de: list[str] = []
            if r["m_skill"] == 1.0:
                fr.append(f"Métier : {trade_label(need.trade, 'fr')}")
                de.append(f"Beruf: {trade_label(need.trade, 'de')}")
            else:
                near = next(t for t in r["m_trades"] if skill_proximity(need.trade, [t]) == r["m_skill"])
                fr.append(f"Métier proche : {trade_label(near, 'fr')}")
                de.append(f"Verwandter Beruf: {trade_label(near, 'de')}")
            fr.append(f"À {r['m_dist']:.0f} km (rayon accepté {r['m_radius']:.0f} km)")
            de.append(f"{r['m_dist']:.0f} km entfernt (akzeptierter Radius {r['m_radius']:.0f} km)")
            fr.append(f"{r['experience_years']} ans d'expérience")
            de.append(f"{r['experience_years']} Jahre Erfahrung")
            fr.append(f"Disponible dès le {r['m_avail']:%d.%m.%Y}")
            de.append(f"Verfügbar ab {r['m_avail']:%d.%m.%Y}")
            for cert in r["m_certs"]:
                if cert in CERT_LABELS:
                    fr.append(CERT_LABELS[cert][0].capitalize())
                    de.append(CERT_LABELS[cert][1])
            out.append(Suggestion(str(r["candidate_id"]), float(r["m_score"]), fr, de, float(r["m_dist"])))
        return out
