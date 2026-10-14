from datetime import date

import pandas as pd
import pytest
from pydantic import ValidationError

from proxsis.schema import (
    CallOutcome,
    Candidate,
    Company,
    NeedEstimate,
    Signal,
    validate_frame,
)
from proxsis.taxonomy import CANTON_LANGUAGES, SECTOR_TRADES, TRADES, language_for


def _prov():
    return dict(source="simap.ch", url="https://www.simap.ch/x", retrieved_at="2026-10-04T12:00:00+00:00", license="x")


def test_company_valid_and_uid_normalized():
    c = Company(
        company_id="c1",
        uid="CHE-123.456.788",
        name="Constructions Rhône SA",
        canton="VS",
        language="fr",
        sector="construction_gros_oeuvre",
        **_prov(),
    )
    assert c.uid == "CHE123456788"


def test_company_bad_uid_rejected():
    with pytest.raises(ValidationError):
        Company(
            company_id="c1",
            uid="CHE-123.456.789",
            name="X SA",
            canton="VS",
            language="fr",
            sector="industrie",
            **_prov(),
        )


def test_company_unknown_canton_rejected():
    with pytest.raises(ValidationError):
        Company(company_id="c1", name="X SA", canton="XX", language="fr", sector="industrie", **_prov())


def test_signal_available_before_event_rejected():
    with pytest.raises(ValidationError):
        Signal(
            signal_id="s1",
            company_id="c1",
            family="marche_attribue",
            subtype="adjudication",
            event_date=date(2026, 5, 10),
            available_at=date(2026, 5, 1),
            canton="VS",
            **_prov(),
        )


def test_signal_trades_must_exist():
    with pytest.raises(ValidationError):
        Signal(
            signal_id="s1",
            company_id="c1",
            family="marche_attribue",
            subtype="adjudication",
            event_date=date(2026, 5, 1),
            available_at=date(2026, 5, 3),
            canton="VS",
            trades=["astronaute"],
            **_prov(),
        )


def test_need_estimate_bounds():
    NeedEstimate(
        company_id="c1",
        week_start=date(2026, 10, 5),
        trade="macon",
        n_low=1,
        n_mid=2,
        n_high=4,
        confidence=0.6,
        method="M0",
        assumptions=["hypothèse"],
    )
    with pytest.raises(ValidationError):
        NeedEstimate(
            company_id="c1",
            week_start=date(2026, 10, 5),
            trade="macon",
            n_low=3,
            n_mid=2,
            n_high=4,
            confidence=0.6,
            method="M0",
            assumptions=[],
        )


def test_need_estimate_week_must_be_monday():
    with pytest.raises(ValidationError):
        NeedEstimate(
            company_id="c1",
            week_start=date(2026, 10, 6),
            trade="macon",
            n_low=1,
            n_mid=2,
            n_high=4,
            confidence=0.6,
            method="M0",
            assumptions=[],
        )


def test_candidate_must_be_fictional():
    with pytest.raises(ValidationError):
        Candidate(candidate_id="k1", trades=["macon"], canton="VS", lat=46.2, lon=7.3, fictif=False)
    Candidate(candidate_id="k1", trades=["macon"], canton="VS", lat=46.2, lon=7.3, fictif=True)


def test_call_outcome_enum():
    CallOutcome(
        outcome_id="o1", company_id="c1", consultant_id="u1", alert_week=date(2026, 10, 5), outcome="rendez_vous"
    )
    with pytest.raises(ValidationError):
        CallOutcome(
            outcome_id="o1", company_id="c1", consultant_id="u1", alert_week=date(2026, 10, 5), outcome="peut-etre"
        )


def test_taxonomy_consistency():
    for sector, trades in SECTOR_TRADES.items():
        assert trades, sector
        for t in trades:
            assert t in TRADES
    assert CANTON_LANGUAGES["GE"] == ("fr",)
    assert CANTON_LANGUAGES["ZH"] == ("de",)
    assert set(CANTON_LANGUAGES["VS"]) == {"fr", "de"}
    assert len(CANTON_LANGUAGES) == 26
    assert language_for("VS", "Visp") == "de"
    assert language_for("VS", "Sion") == "fr"
    for t in TRADES.values():
        assert t.label_fr and t.label_de


def test_validate_frame_reports_missing_columns():
    df = pd.DataFrame({"company_id": ["c1"]})
    errors = validate_frame(df, Company)
    assert any("name" in e for e in errors)
