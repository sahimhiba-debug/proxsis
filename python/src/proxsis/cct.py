"""CCT Location de services (CCT LS 2024-2027, extended by the Federal Council on 11.12.2025, in force
1.1.2026-31.12.2027): wage category of a temporary worker and 2026 minimum wages.

Sources (read on 2026-10-05, details in docs/recherche/conformite_cct_annonce.md § a):
- art. 20 al. 1 and 5 CCT LS, 2026 version (tempservice.ch brochure of 11.12.2025; FF 2025 3547);
- art. 20 al. 4: « avec formation professionnelle » = CFC of the branch, or a completed vocational training of
  at least three years suited to the activity, or an AFP with at least three years of practice in the activity;
- art. 20 al. 5: « employé spécialisé » (Angelernte) = at least four years of practice in the activity, for
  which a vocational training exists, with at least 1 000 hours of work per calendar year.

Open point (to validate with tempcontrol): the text does not say whether the 1 000 hours are required for each
of the four years. The prudent reading (each year) is applied and flagged.

Caution: when the client company is bound by an extended CCT (CN for the main construction sector, second-œuvre
romand, Valais CCTs of electricity, building technology, metal construction, tiling), its wages and working
time apply (art. 20 LSE, art. 3 CCT LS). These minimums are then not the reference.
"""

from __future__ import annotations

from dataclasses import dataclass

CATEGORIES: dict[str, dict[str, str]] = {
    "non_qualifie": {"fr": "non qualifié (sans formation professionnelle)", "de": "ungelernt"},
    "specialise": {"fr": "spécialisé (art. 20 al. 5)", "de": "angelernt (Art. 20 Abs. 5)"},
    "qualifie": {"fr": "qualifié (avec formation professionnelle)", "de": "gelernt"},
}
# Art. 20 al. 1 and 5, 2026, outside Ticino, Geneva and high-wage regions (no Valais postcode in annex 3).
MIN_WAGE_2026: dict[str, dict[str, float]] = {
    "non_qualifie": {"annee": 50277.0, "mois": 3867.45, "heure": 21.22},
    "specialise": {"annee": 53920.0, "mois": 4147.70, "heure": 22.76},
    "qualifie": {"annee": 61273.0, "mois": 4713.29, "heure": 25.86},
}
SOURCE = ("CCT Location de services, art. 20 (version 2026 étendue par l'arrêté du Conseil fédéral du 11.12.2025, "
          "FF 2025 3547) — https://www.tempservice.ch")


@dataclass(frozen=True)
class Category:
    code: str
    rule: str
    open_point: bool = False


def cct_category(training: str, practice_years: float, hours_by_year: list[float],
                 training_exists: bool) -> Category:
    """``training`` in {cfc, formation_3ans, afp, etrangere_reconnue, aucune}; ``hours_by_year``: hours worked in
    the activity per calendar year, most recent last."""
    if training in {"cfc", "formation_3ans", "etrangere_reconnue"}:
        return Category("qualifie", "art. 20 al. 4 : CFC de la branche ou formation d'au moins trois ans")
    if training == "afp" and practice_years >= 3:
        return Category("qualifie", "art. 20 al. 4 : AFP et au moins trois ans de pratique")
    if training_exists and practice_years >= 4:
        last4 = hours_by_year[-4:]
        if len(last4) == 4 and min(last4) >= 1000:
            return Category("specialise", "art. 20 al. 5 : quatre ans de pratique, au moins 1 000 heures par année "
                                          "civile, formation existante")
        if len(last4) < 4:
            return Category("non_qualifie", "art. 20 al. 5 non vérifiable : heures non renseignées pour quatre années "
                                            "civiles", open_point=True)
        return Category("non_qualifie", "art. 20 al. 5 non rempli : une année sous 1 000 heures (lecture prudente, "
                                        "à valider par tempcontrol)", open_point=True)
    return Category("non_qualifie", "ni art. 20 al. 4 ni al. 5")


# Which wage rules are probable for a temporary worker of this trade placed in Valais (art. 20 LSE, art. 3 CCT LS):
# the extended CCT of the client company prevails. Research note docs/recherche/conformite_cct_annonce.md § a.
_CCT_BY_TRADE: dict[str, tuple[str, str]] = {
    **{t: ("CN — Convention nationale du secteur principal de la construction (probable)",
           "LMV — Landesmantelvertrag für das Bauhauptgewerbe (wahrscheinlich)")
       for t in ("macon", "coffreur", "manoeuvre_construction", "grutier", "machiniste")},
    **{t: ("CCT du second-œuvre romand (probable)", "GAV Westschweizer Ausbaugewerbe (wahrscheinlich)")
       for t in ("platrier", "peintre")},
    "charpentier": ("CCT de l'entreprise locataire à vérifier (la CCT nationale de la construction en bois exclut "
                    "le Valais)", "GAV des Einsatzbetriebs zu prüfen (der Holzbau-GAV schliesst das Wallis aus)"),
    "electricien": ("CCT valaisanne des métiers de l'électricité (probable)",
                    "Walliser GAV Elektrogewerbe (wahrscheinlich)"),
    "installateur_sanitaire": ("CCT valaisanne des métiers de la technique du bâtiment (probable)",
                               "Walliser GAV Gebäudetechnik (wahrscheinlich)"),
}


def applicable_cct(trade: str) -> dict[str, object]:
    """Probable applicable CCT; the CCT LS minimum is shown only when no extended CCT of the client is likely."""
    if trade in _CCT_BY_TRADE:
        fr, de = _CCT_BY_TRADE[trade]
        return {"cct": fr, "cct_de": de, "minimum_cct_ls": False,
                "note": "montant à lire dans la CCT de l'entreprise de mission (tempdata.ch)"}
    return {"cct": "CCT Location de services (sauf CCT étendue de l'entreprise de mission)",
            "cct_de": "GAV Personalverleih (ausser allgemeinverbindlicher GAV des Einsatzbetriebs)",
            "minimum_cct_ls": True, "note": "minimum de l'art. 20 CCT LS 2026"}
