"""La carte des sources (suite 10, § 3): what the catalogue of the sources (data/catalogue.csv, 68 lines read and tested
in October 2026, CLAIMS CAT-1) says, counted line by line, for the top of the page « Sources et mesures », the visit
and the A4 page (CLAIMS SOURCES-1).

One line of the catalogue is one source or one part of a source (the three lines of simap.ch share one access).
Four groups, without overlap:
- **en service**: the two sources of the list and of the application, simap.ch (awarded public contracts, official
  access) and the Bulletin officiel du Valais (building permit requests, consulted by a person);
- **couvertes par une demande d'accès envoyée**: the lines that the four requests of docs/demandes/ ask for, sent by
  Hiba in October 2026 (the Bulletin officiel, already consulted by hand, is counted in service);
- **écartées**: the lines the catalogue says « non », each with the short reason of its family;
- **les autres**: conditions still to be checked (« sous_conditions » without a request), or usable but of no use for
  the list today (« utilisable »).
A line that the catalogue says « non » without a family here, or a line named here that the catalogue no longer has, is
refused: the numbers can only change with this file and its test.
"""

from __future__ import annotations

from typing import Any

IN_SERVICE = ("simap_adjudications", "amtsblatt_vs_permis_construire")

# The four requests (suite 10, annex), sent by Hiba herself: the keys are those of the page « Sources et mesures »
REQUESTS: list[dict[str, Any]] = [
    {"cle": "portail", "lignes": ["amtsblatt_fosc_hr"], "fichier": "docs/demandes/seco_feuilles_officielles.md",
     "statut": "envoyee", "mois": "2026-10"},
    {"cle": "zefix", "lignes": ["zefix_publicrest"], "fichier": "docs/demandes/ofj_zefix.md",
     "statut": "envoyee", "mois": "2026-10"},
    {"cle": "jobroom", "lignes": ["jobroom_api"], "fichier": "docs/demandes/seco_job_room.md",
     "statut": "envoyee", "mois": "2026-10"},
    {"cle": "regbl", "lignes": ["regbl_madd_dump"], "fichier": "docs/demandes/ofs_regbl.md",
     "statut": "envoyee", "mois": "2026-10"},
]

# The lines set aside (verdict « non »), by family; the reason of each comes from its line of the catalogue
EXCLUDED: dict[str, list[str]] = {
    # personal data: bankruptcies, debt collection, successions, civil status; applicants' names and addresses
    "particuliers": ["amtsblatt_rubriques_personnes_exclues", "ge_sad_consult", "vs_econstruction"],
    # the site's own conditions forbid it (robots.txt, or an internal interface not offered for reuse)
    "conditions": ["zefix_rest_site_web", "zh_zefix_neugruendungen", "nager_date_feries"],
    # a private portal, without an agreement
    "prive": ["jobcloud_jobs_ch_jobup", "indeed_linkedin"],
    # a closed server, replaced by another address of the same institute (kof_tsdb_job_tracker)
    "injoignable": ["kof_datenservice"],
}

CLAIMS_ID = "SOURCES-1"


def source_map(rows: list[dict[str, str]]) -> dict[str, Any]:
    """The four groups of the catalogue and their numbers (``rows``: the lines of data/catalogue.csv)."""
    verdict = {r["id"]: r["verdict"] for r in rows}
    requested = [x for req in REQUESTS for x in req["lignes"]]
    excluded = [x for ids in EXCLUDED.values() for x in ids]
    missing = [x for x in (*IN_SERVICE, *requested, *excluded) if x not in verdict]
    if missing:
        raise ValueError(f"ligne absente du catalogue : {', '.join(missing)}")
    stray = sorted(i for i, v in verdict.items() if v == "non" and i not in excluded)
    if stray:
        raise ValueError(f"source écartée sans famille : {', '.join(stray)}")
    wrong = [x for x in excluded if verdict[x] != "non"] + [x for x in (*IN_SERVICE, *requested) if verdict[x] == "non"]
    if wrong:
        raise ValueError(f"verdict du catalogue contraire au groupe : {', '.join(wrong)}")
    named = {*IN_SERVICE, *requested, *excluded}
    others = [i for i in verdict if i not in named]
    to_check = [i for i in others if verdict[i] == "sous_conditions"]
    usable = [i for i in others if verdict[i] == "utilisable"]
    if len(to_check) + len(usable) != len(others):
        raise ValueError("verdict inconnu dans le catalogue")
    return {
        "schema": 1,
        "claims": CLAIMS_ID,
        "catalogue": "data/catalogue.csv",
        "etudiees": len(verdict),
        "en_service": {"nombre": len(IN_SERVICE), "lignes": list(IN_SERVICE)},
        "demandes": {"nombre": len(requested), "liste": REQUESTS},
        "ecartees": {"nombre": len(excluded), "familles": EXCLUDED},
        "autres": {"nombre": len(others), "conditions_a_verifier": len(to_check),
                   "sans_usage_pour_la_liste": len(usable)},
    }


def claim_matches(data: dict[str, Any], valeur: str) -> bool:
    """The CLAIMS line says the same numbers as the file."""
    wanted = [f"{data['etudiees']} sources", f"{data['en_service']['nombre']} en service",
              f"{data['demandes']['nombre']} couvertes", f"{data['ecartees']['nombre']} écartées",
              f"{data['autres']['nombre']} autres"]
    return all(w in valeur for w in wanted)
