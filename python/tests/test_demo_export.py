"""Demo export for apps/web (SYNTHETIC simap-like records, fictional candidates)."""

import json
from datetime import date

import pytest

from proxsis.demo_export import PiiFound, export_demo, parse_claims, pii_sweep
from proxsis.synth.candidates import generate_candidates
from test_call_list import _rec, _world

AS_OF = date(2026, 9, 28)
PLACES = [{"localite": "Sion", "commune": "Sion", "lat": 46.23, "lon": 7.36, "langue": "fr"},
          {"localite": "Martigny", "commune": "Martigny", "lat": 46.10, "lon": 7.07, "langue": "fr"},
          {"localite": "Lausanne", "commune": "Lausanne", "lat": 46.52, "lon": 6.63, "langue": "fr"}]
CLAIMS = """| ID | Affirmation | Valeur | Données | Commande | Fichier | Limite |
|---|---|---|---|---|---|---|
| REEL-SPEC-BAT | Liste Bâtiment P@10 | fréquence 65,6 % | RÉEL | `x` | `y` | z |
| REEL-SPEC-NOUVEAUX | Nouveaux | 35,1 % | RÉEL | `x` | `y` | z |
| REDEP-1 | Redéploiement | 21 sur 43 | FICTIF | `x` | `y` | z |
| CONF-1 | Conformité | 15 sur 49 | RÉEL | `x` | `y` | z |
| TAB-FICTIF-1 | Maquette | inventé | FICTIF | `x` | `y` | z |
"""


def _run(tmp_path, records=None):
    claims = tmp_path / "CLAIMS.md"
    claims.write_text(CLAIMS, "utf-8")
    cands = generate_candidates(PLACES[:2], today=AS_OF, n=60, seed=1)
    out = tmp_path / "demo"
    recs = records or [*_world(), _rec(88888, date(2026, 9, 21), "Bondit SA", auth=None)]
    export_demo(out, records=recs, as_of=AS_OF, places=PLACES, candidates=cands,
                claims_md=claims, specialties=("batiment",), seed=42, provider=None)
    return out, {p.stem: json.loads(p.read_text("utf-8")) for p in out.glob("*.json")}


def test_export_writes_every_screen_with_schema_and_mandatory_mention(tmp_path):
    _, d = _run(tmp_path)
    assert {"meta", "agences", "entreprises", "listes", "propositions", "candidats", "redeploiement", "conformite",
            "appels", "tableau", "claims"} <= set(d)
    assert d["meta"]["schema"] == 1 and "font foi" in d["meta"]["mention_simap"]
    assert d["meta"]["semaine"] == "2026-09-28"


def test_companies_have_bilingual_reasons_sources_coordinates_and_an_agency(tmp_path):
    _, d = _run(tmp_path)
    assert d["entreprises"]
    for e in d["entreprises"].values():
        assert all(r["fr"] and r["de"] for r in e["raisons"])
        assert e["sources"] and e["agence"] in {"martigny", "sion", "monthey"}
        assert e["chronologie"] and all(x["url_simap"].startswith("https://www.simap.ch/") for x in e["chronologie"])
    # lists: per specialty and per agency, only known companies
    lst = d["listes"]["batiment"]
    for ag in lst["par_agence"].values():
        assert set(ag["entreprises"]) <= set(d["entreprises"])


def test_fictional_things_are_flagged_and_numbers_point_to_claims(tmp_path):
    _, d = _run(tmp_path)
    assert all(c["fictif"] for c in d["candidats"].values())
    assert d["redeploiement"]["fictif"] is True
    assert all(a["consultants"] and all(c["fictif"] for c in a["consultants"]) for a in d["agences"].values())
    for k in d["tableau"]["indicateurs"]:
        assert k["type"] in {"RÉEL", "FICTIF"} and k["claim"] in d["claims"]


def test_pii_sweep_blocks_the_export(tmp_path):
    assert pii_sweep({"a": ["Exemple SA", {"b": "Commune de Sion"}]}) == []
    found = pii_sweep({"x": "Contact : M. Jean Dupont, rue des Alpes 12"})
    assert found
    assert pii_sweep({"sources": [{"adjudicateur": "Gaston exemplaire"}]})
    bad = [*_world(), _rec(77777, AS_OF.replace(day=20), "Bondit SA", auth="M. Jean Dupont")]
    with pytest.raises(PiiFound):
        _run(tmp_path, records=bad)


def test_parse_claims_reads_the_registry(tmp_path):
    p = tmp_path / "C.md"
    p.write_text(CLAIMS, "utf-8")
    c = parse_claims(p)
    assert c["REEL-SPEC-BAT"]["donnees"] == "RÉEL" and c["REEL-SPEC-BAT"]["valeur"].startswith("fréquence")


def test_exported_json_is_strict_without_nan(tmp_path):
    out, _ = _run(tmp_path)

    def refuse(c):
        raise ValueError(f"constante JSON non standard : {c}")

    for p in out.glob("*.json"):
        json.loads(p.read_text("utf-8"), parse_constant=refuse)


def test_committed_measures_page_matches_the_claims_registry():
    """Audit week 2, B3: the « Mesures » page must say what CLAIMS.md says (re-export after each regeneration)."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    committed = json.loads((root / "apps/web/src/data/demo/claims.json").read_text("utf-8"))
    assert committed == json.loads(json.dumps(parse_claims(root / "CLAIMS.md"), ensure_ascii=False))


def test_pii_sweep_uses_the_gazette_person_markers():
    for text in ("Chalet, Domicile: Sion", "Bureau X SA c/o Exemple", "Gemeinde Visp z. Hd. Muster"):
        assert pii_sweep({"permis": [{"titre": text}]}), text
    assert not pii_sweep({"permis": [{"titre": "Construction d'un immeuble, Herr [masqué]"}]})
    for org in ("PPE Les Mélèzes c/o Gérance Exemple SA", "Ville de Sion, p.a. Direction générale de l'enseignement"):
        assert not pii_sweep({"marche": {"adjudicateur": org}}), org
    assert pii_sweep({"marche": {"adjudicateur": "Commune de Sion c/o Jean Exemple"}})


def _company_refs(obj, out=None):
    out = set() if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("entreprise", "entreprise_id", "company_id") and isinstance(v, str) and v.startswith("ent-"):
                out.add(v)
            _company_refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _company_refs(v, out)
    return out


def test_every_company_referenced_by_a_screen_has_its_page(tmp_path):
    """Audit week 2, M6: a redeployment target outside the exported companies gave a dead link (404)."""
    claims = tmp_path / "CLAIMS.md"
    claims.write_text(CLAIMS, "utf-8")
    cands = generate_candidates(PLACES[:2], today=AS_OF, n=60, seed=1)
    out = tmp_path / "demo"
    export_demo(out, records=[*_world(), _rec(88888, date(2026, 9, 21), "Bondit SA", auth=None)], as_of=AS_OF,
                places=PLACES, candidates=cands, claims_md=claims, specialties=("batiment",), seed=42, provider=None,
                k_per_agency=1)
    d = {p.stem: json.loads(p.read_text("utf-8")) for p in out.glob("*.json")}
    refs = set().union(*(_company_refs(d[k]) for k in ("redeploiement", "listes", "propositions", "conformite")))
    refs |= set(d["propositions"]) | set(d["conformite"]) | set(d["appels"])
    assert refs <= set(d["entreprises"])


def test_committed_demo_data_has_no_dead_company_link():
    from pathlib import Path

    demo = Path(__file__).resolve().parents[2] / "apps/web/src/data/demo"
    d = {k: json.loads((demo / f"{k}.json").read_text("utf-8"))
         for k in ("entreprises", "redeploiement", "listes", "propositions", "conformite", "appels")}
    refs = set().union(*(_company_refs(d[k]) for k in ("redeploiement", "listes", "propositions", "conformite")))
    assert refs <= set(d["entreprises"]), sorted(refs - set(d["entreprises"]))
