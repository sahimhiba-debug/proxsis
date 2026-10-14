import hashlib
import json

import pytest

from proxsis.compare_extractors import NotFrozenError, compare
from proxsis.llm.base import FakeLLM
from proxsis.models.m3_extraction import LLMExtractor, RulesExtractor

ROW = {"id": "simap:x", "lang": "fr",
       "text": "Adjudication — simap.ch\nObjet : Travaux de maçonnerie CFC 211\nLieu d'exécution : 1950 Sion (VS)\n"
               "Adjudicataire : Exemple Construction SA — prix : CHF 1'250'000.–",
       "gold": {"doc_type": "adjudication", "company_name": "Exemple Construction SA", "uid": None, "commune": "Sion",
                "amount_chf": 1250000, "rc_subtype": None, "trades": ["macon", "manoeuvre_construction"],
                "private_person": False, "besoin_temporaire": "oui"}}


def _frozen(tmp_path, register=True):
    path = tmp_path / "reel_v2.jsonl"
    payload = (json.dumps(ROW, ensure_ascii=False) + "\n").encode()
    path.write_bytes(payload)
    md = tmp_path / "FROZEN.md"
    md.write_text(f"| `reel_v2.jsonl` | `{hashlib.sha256(payload).hexdigest()}` | x | y |\n" if register else "vide\n")
    return path, md


def test_refuses_a_set_that_is_not_frozen(tmp_path):
    path, md = _frozen(tmp_path, register=False)
    with pytest.raises(NotFrozenError):
        compare(path, md, [RulesExtractor()])


def test_compares_rules_and_llm_on_frozen_set(tmp_path):
    path, md = _frozen(tmp_path)
    fake = LLMExtractor(FakeLLM(lambda user, name: RulesExtractor().extract(user)))
    rep = compare(path, md, [RulesExtractor(), fake])
    assert set(rep["extracteurs"]) == {"regles", "llm:fake:fake-deterministic"}
    r = rep["extracteurs"]["regles"]
    assert r["n"] == 1 and "field_accuracy" in r and "pii_leaks" in r
    assert rep["jeu"]["sha256"] and rep["jeu"]["n"] == 1
    assert "avertissement" not in rep  # real data: no fictional warning…
    assert rep["donnees"] == "RÉEL"


def test_leak_detector_flags_placeholders_copied_into_company_name(tmp_path):
    path, md = _frozen(tmp_path)

    class Leaky:
        name = "fuite"

        def extract(self, text):
            return {"doc_type": "adjudication", "company_name": "[masqué] SA", "uid": None, "commune": None,
                    "amount_chf": None, "rc_subtype": None, "trades": [], "private_person": False}

    rep = compare(path, md, [Leaky()])
    assert rep["extracteurs"]["fuite"]["pii_leaks"] == 1


def test_agent_written_set_is_marked(tmp_path):
    path, md = _frozen(tmp_path)
    rep = compare(path, md, [RulesExtractor()], donnees="FICTIF-AGENT")
    assert "optimistes" in rep["avertissement_jeu_de_test"] and rep["avertissement"].startswith("monde fictif")


def test_fields_where_humans_disagree_are_flagged_in_the_comparison(tmp_path):
    path, md = _frozen(tmp_path)
    rel = {"commune": {"fiable": False, "mesure": "accord_exact", "valeur": 0.5, "n": 20},
           "company_name": {"fiable": True, "mesure": "accord_exact", "valeur": 0.95, "n": 20},
           "trades": {"fiable": False, "mesure": "jaccard_moyen", "valeur": 0.6, "n": 20}}
    rep = compare(path, md, [RulesExtractor()], reliability=rel)
    r = rep["extracteurs"]["regles"]
    assert set(r["champs_a_prendre_avec_precaution"]) == {"commune", "trades"}
    assert rep["fiabilite_humaine"] == rel
