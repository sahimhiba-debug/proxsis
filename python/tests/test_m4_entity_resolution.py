import pandas as pd
import pytest

from proxsis.models.m4_entity_resolution import (
    EntityResolver,
    ExactNameResolver,
    benchmark,
    make_mentions,
)
from proxsis.synth.world import WorldConfig, generate_world


@pytest.fixture(scope="module")
def companies():
    return generate_world(WorldConfig(seed=4, n_companies=800, n_candidates=5)).companies


def test_uid_match_is_decisive(companies):
    r = EntityResolver(companies)
    c = companies.iloc[10]
    m = r.resolve("nom complètement différent", uid=c["uid"], canton="ZH")
    assert m.company_id == c["company_id"] and m.method == "uid"


def test_variants_resolve(companies):
    r = EntityResolver(companies)
    c = companies.iloc[3]
    variant = c["name"].upper().replace(" SA", " S.A.").replace(" AG", " A.G.")
    m = r.resolve(variant, canton=c["canton"], commune=c["commune"])
    assert m.company_id == c["company_id"]


def test_unknown_company_not_linked():
    comp = pd.DataFrame(
        {"company_id": ["a"], "uid": [None], "name": ["Alpar Construction SA"], "canton": ["VS"], "commune": ["Sion"]}
    )
    r = EntityResolver(comp)
    assert r.resolve("Zinal Horlogerie SA", canton="VS").company_id is None


def test_fuzzy_beats_exact_baseline_on_recall_without_losing_precision(companies):
    mentions = make_mentions(companies, 600, seed=1)
    fuzzy = benchmark(EntityResolver(companies), mentions)
    exact = benchmark(ExactNameResolver(companies), mentions)
    assert fuzzy["recall"] > exact["recall"]
    assert fuzzy["precision"] >= 0.95


def test_an_unknown_company_left_unlinked_is_not_a_missed_company():
    # B10 (questionnaire of Hiba, 07.10.2026): an unknown company has no truth; whether pandas keeps it as None or reads
    # it as NaN, leaving it unlinked is right, not a miss (the first M4-1 counted it as missed under pandas 3)
    from types import SimpleNamespace

    class Known:  # links the known company by its name, leaves everything else unlinked
        def resolve(self, name, *_):
            return SimpleNamespace(company_id="c-1" if name == "Connue SA" else None,
                                   method="name" if name == "Connue SA" else "none")

    mentions = pd.DataFrame({"name": ["Connue SA", "Inconnue Sàrl"], "uid": [None, None], "canton": [None, None],
                             "commune": [None, None], "truth": ["c-1", None]})
    mentions["truth"] = mentions["truth"].astype(object).where(mentions["truth"].notna(), float("nan"))  # pandas 3
    r = benchmark(Known(), mentions)  # type: ignore[arg-type]
    assert r["recall"] == 1.0 and r["precision"] == 1.0
