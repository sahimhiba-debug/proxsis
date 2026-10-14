"""A missing text cell never reaches the screen as « nan » or « None »."""

import math

from proxsis.call_list import reason_text
from proxsis.call_prep import facts_for
from proxsis.values import optional_text


def test_optional_text_turns_every_kind_of_empty_cell_into_none():
    assert optional_text(math.nan) is None
    assert optional_text(None) is None
    assert optional_text("   ") is None
    assert optional_text(" Commune de Sion ") == "Commune de Sion"


def test_latest_contract_without_authority_reads_without_it():
    for missing in (math.nan, None, ""):
        r = {"code": "dernier_marche", "jours": 209, "titre": "Ateliers", "adjudicateur": missing}
        for lang in ("fr", "de"):
            text = reason_text(r, lang)
            assert "nan" not in text and "None" not in text and "()" not in text
            assert text.rstrip().endswith(("»", "«Ateliers»"))


def test_call_fact_without_authority_leaves_the_clause_out():
    company = {"id": "ent-x", "n_52s": 0, "besoin": [], "sources": [
        {"date": "2026-03-10", "titre": "Ateliers", "adjudicateur": math.nan, "montant_chf": 683472.0,
         "url_simap": "https://www.simap.ch/fr/project-detail/x"}]}
    award = facts_for(company)[0]
    assert award["fr"] == "Marché « Ateliers », publié le 10.03.2026 sur simap.ch (montant publié : CHF 683'472)."
    assert award["de"] == ("Zuschlag «Ateliers», publiziert am 10.03.2026 auf simap.ch "
                           "(publizierter Betrag: CHF 683'472).")
