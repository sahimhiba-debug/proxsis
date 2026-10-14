"""Business taxonomy: sectors, trades (with ISCO-08 codes), cantons and languages.

ISCO-08 4-digit codes are given for orientation; the mapping to CH-ISCO-19
(the Swiss extension used by the SECO for the job-reporting obligation) is
to be verified before production use.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Trade:
    code: str
    label_fr: str
    label_de: str
    isco08: str
    construction: bool


TRADES: dict[str, Trade] = {
    t.code: t
    for t in [
        Trade("macon", "Maçon", "Maurer", "7112", True),
        Trade("manoeuvre_construction", "Manœuvre de chantier", "Bauhilfsarbeiter", "9313", True),
        Trade("coffreur", "Coffreur", "Schaler", "7114", True),
        Trade("grutier", "Grutier", "Kranführer", "8343", True),
        Trade("machiniste", "Machiniste", "Baumaschinenführer", "8342", True),
        Trade("electricien", "Électricien", "Elektroinstallateur", "7411", True),
        Trade("installateur_sanitaire", "Installateur sanitaire", "Sanitärinstallateur", "7126", True),
        Trade("peintre", "Peintre en bâtiment", "Maler", "7131", True),
        Trade("platrier", "Plâtrier", "Gipser", "7123", True),
        Trade("charpentier", "Charpentier", "Zimmermann", "7115", True),
        Trade("operateur_production", "Opérateur de production", "Produktionsmitarbeiter", "9329", False),
        Trade("polymecanicien", "Polymécanicien", "Polymechaniker", "7223", False),
        Trade("soudeur", "Soudeur", "Schweisser", "7212", False),
        Trade("horloger", "Horloger", "Uhrmacher", "7311", False),
        Trade("decolleteur", "Décolleteur", "Decolleteur", "7223", False),
        Trade("cariste", "Cariste", "Staplerfahrer", "8344", False),
        Trade("agent_logistique", "Agent de logistique", "Logistiker", "4321", False),
        Trade("chauffeur_pl", "Chauffeur poids lourd", "LKW-Chauffeur", "8332", False),
        Trade("operateur_pharma", "Opérateur de production pharma", "Pharma-Produktionsmitarbeiter", "8131", False),
        Trade("laborantin", "Laborantin", "Laborant", "3111", False),
    ]
}

SECTOR_LABELS: dict[str, tuple[str, str]] = {
    "construction_gros_oeuvre": ("Construction — gros œuvre", "Bau — Rohbau"),
    "construction_second_oeuvre": ("Construction — second œuvre", "Bau — Ausbau"),
    "genie_civil": ("Génie civil", "Tiefbau"),
    "industrie": ("Industrie", "Industrie"),
    "horlogerie": ("Horlogerie", "Uhrenindustrie"),
    "logistique": ("Logistique", "Logistik"),
    "pharma": ("Pharma", "Pharma"),
}

SECTOR_TRADES: dict[str, tuple[str, ...]] = {
    "construction_gros_oeuvre": ("macon", "manoeuvre_construction", "coffreur", "grutier"),
    "construction_second_oeuvre": ("electricien", "installateur_sanitaire", "peintre", "platrier", "charpentier"),
    "genie_civil": ("machiniste", "manoeuvre_construction", "macon"),
    "industrie": ("operateur_production", "polymecanicien", "soudeur"),
    "horlogerie": ("horloger", "decolleteur", "operateur_production"),
    "logistique": ("cariste", "agent_logistique", "chauffeur_pl"),
    "pharma": ("operateur_pharma", "laborantin", "agent_logistique"),
}

CONSTRUCTION_SECTORS = frozenset({"construction_gros_oeuvre", "construction_second_oeuvre", "genie_civil"})

SIGNAL_FAMILIES: dict[str, tuple[str, ...]] = {
    "marche_attribue": ("adjudication",),
    "appel_offres": ("publication",),
    "permis_construire": ("mise_a_l_enquete", "permis_delivre"),
    "mutation_rc": (
        "nouvelle_inscription",
        "succursale",
        "augmentation_capital",
        "changement_but",
        "transfert_siege",
        "fusion",
        "liquidation",
        "radiation",
    ),
    "offre_emploi": ("publication",),
    "macro": ("indice",),
}

# Official languages per canton (federal constitution / cantonal constitutions).
CANTON_LANGUAGES: dict[str, tuple[str, ...]] = {
    "ZH": ("de",),
    "BE": ("de", "fr"),
    "LU": ("de",),
    "UR": ("de",),
    "SZ": ("de",),
    "OW": ("de",),
    "NW": ("de",),
    "GL": ("de",),
    "ZG": ("de",),
    "FR": ("fr", "de"),
    "SO": ("de",),
    "BS": ("de",),
    "BL": ("de",),
    "SH": ("de",),
    "AR": ("de",),
    "AI": ("de",),
    "SG": ("de",),
    "GR": ("de", "rm", "it"),
    "AG": ("de",),
    "TG": ("de",),
    "TI": ("it",),
    "VD": ("fr",),
    "VS": ("fr", "de"),
    "NE": ("fr",),
    "GE": ("fr",),
    "JU": ("fr",),
}

# Communes whose language differs from the canton's first language (partial list,
# used by the fictional world and as a fallback; real data takes the language
# from the official commune register).
_MINORITY_COMMUNES: dict[str, dict[str, str]] = {
    "VS": {
        c: "de"
        for c in (
            "Visp",
            "Brig-Glis",
            "Naters",
            "Zermatt",
            "Saas-Fee",
            "Leuk",
            "Raron",
            "Steg-Hohtenn",
            "Gampel-Bratsch",
            "Fiesch",
            "Lalden",
            "Susten",
        )
    },
    "FR": {c: "de" for c in ("Düdingen", "Tafers", "Schmitten", "Wünnewil-Flamatt", "Murten")},
    "BE": {c: "fr" for c in ("Saint-Imier", "Tramelan", "Tavannes", "Reconvilier", "La Neuveville")},
}


def language_for(canton: str, commune: str | None = None) -> str:
    if commune and commune in _MINORITY_COMMUNES.get(canton, {}):
        return _MINORITY_COMMUNES[canton][commune]
    return CANTON_LANGUAGES[canton][0]


def trade_label(code: str, lang: str) -> str:
    t = TRADES[code]
    return t.label_de if lang == "de" else t.label_fr
