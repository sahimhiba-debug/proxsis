"""300 FICTIONAL candidates for the demo — invented, marked ``fictif=True`` and « FICTIF » in their label.

No names: each profile is « Candidat·e 042 (FICTIF) ». The distributions below are assumptions chosen to look
plausible for a Valais staffing agency; they are NOT measured (Flexsis' candidate pool is not available):
specialty shares, training, permits, languages, status. What is NOT random:
- the CCT wage category is computed by the rule of the CCT Location de services (``proxsis.cct``);
- the place is a real Valais locality (swisstopo directory) with its coordinates and language.

Protected attributes (``audit_*``) exist only for the fairness audit; the matcher never reads them.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from proxsis.cct import cct_category
from proxsis.specialty import SPECIALTIES

# Assumptions (FICTIF): share of the pool per agency specialty, then uniform trade within the specialty.
SPECIALTY_SHARE = {"batiment": 0.55, "electricite": 0.15, "technique": 0.10, "industrie": 0.20}
NO_TRAINING_TRADES = {"manoeuvre_construction"}  # assumption: no CFC/AFP for a site labourer
PERMITS = (("CH", 0.45), ("C", 0.27), ("B", 0.20), ("L", 0.08))
OTHER_LANGS = ("pt", "it", "es", "sq", "sr")
AGENCIES = {"Martigny": (46.102, 7.072), "Sion": (46.233, 7.360), "Monthey": (46.255, 6.954)}


def _nearest_agency(lat: float, lon: float) -> str:
    return min(AGENCIES, key=lambda a: (AGENCIES[a][0] - lat) ** 2 + (AGENCIES[a][1] - lon) ** 2)


def generate_candidates(places: list[dict[str, Any]], today: date, n: int = 300, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rng_orp = np.random.default_rng(seed + 7919)  # separate stream: adding this field leaves the pool unchanged
    weights = np.array([float(p.get("poids", 1.0)) for p in places])
    weights = weights / weights.sum()
    specs = list(SPECIALTY_SHARE)
    rows = []
    for i in range(1, n + 1):
        spec = specs[rng.choice(len(specs), p=list(SPECIALTY_SHARE.values()))]
        trades = SPECIALTIES[spec].trades
        trade = str(trades[rng.integers(len(trades))])
        place = places[rng.choice(len(places), p=weights)]
        age_band = str(rng.choice(["18-25", "26-35", "36-50", "51+"], p=[0.18, 0.32, 0.35, 0.15]))
        max_years = {"18-25": 6, "26-35": 15, "36-50": 28, "51+": 38}[age_band]
        practice = int(rng.integers(0, max_years + 1))
        training_exists = trade not in NO_TRAINING_TRADES
        training = str(rng.choice(["cfc", "afp", "etrangere_reconnue", "aucune"], p=[0.40, 0.10, 0.08, 0.42])) \
            if training_exists else "aucune"
        hours = [int(rng.integers(500, 2100)) for _ in range(min(practice, 4))]
        cat = cct_category(training, practice, [float(h) for h in hours], training_exists)
        permit = str(rng.choice([p for p, _ in PERMITS], p=[w for _, w in PERMITS]))
        nat = "CH" if permit == "CH" else str(rng.choice(["UE/AELE", "autre"], p=[0.8, 0.2]))
        langs = [place["langue"]]
        if rng.random() < 0.25:
            langs.append("de" if place["langue"] == "fr" else "fr")
        if nat != "CH" and rng.random() < 0.7:
            langs.append(str(rng.choice(OTHER_LANGS)))
        status = str(rng.choice(["en_mission", "disponible", "indisponible"], p=[0.55, 0.30, 0.15]))
        end = None
        if status == "en_mission":
            end = today + timedelta(days=int(rng.integers(0, 84)))
            avail = end + timedelta(days=1)
        elif status == "disponible":
            avail = today
        else:
            avail = today + timedelta(weeks=int(rng.integers(8, 21)))
        certs = []
        if trade == "grutier" and rng.random() < 0.9:
            certs.append("permis_grue")
        if spec in {"batiment", "electricite", "technique"} and rng.random() < 0.5:
            certs.append("sst_chantier")
        female_p = 0.08 if spec != "industrie" else 0.25
        rows.append({
            "candidate_id": f"cand-{i:03d}", "libelle": f"Candidat·e {i:03d} (FICTIF)", "fictif": True,
            "specialite": spec, "metier": trade, "trades": trade, "certifications": ";".join(certs),
            "formation": training, "formation_existe": training_exists, "annees_pratique": practice,
            "heures_par_annee": ";".join(str(h) for h in hours), "categorie_cct": cat.code, "regle_cct": cat.rule,
            "point_ouvert_cct": cat.open_point, "permis_travail": permit, "langues": ";".join(langs),
            "localite": place["localite"], "commune": place.get("commune", place["localite"]),
            "lat": float(place["lat"]), "lon": float(place["lon"]),
            "agence": _nearest_agency(float(place["lat"]), float(place["lon"])), "statut": status,
            "fin_mission": end.isoformat() if end else None, "available_from": avail.isoformat(),
            # assumption (FICTIF): 40 % of the available candidates are registered at the ORP as job seekers
            "inscrit_orp": bool(status == "disponible" and rng_orp.random() < 0.4),
            "driving_licence": bool(rng.random() < 0.75), "max_travel_km": float(rng.choice([15, 25, 40, 60])),
            "experience_years": practice,
            "audit_gender": "f" if rng.random() < female_p else "m", "audit_age_band": age_band,
            "audit_nationality_group": nat,
        })
    return pd.DataFrame(rows)
