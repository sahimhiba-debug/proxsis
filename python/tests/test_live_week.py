"""« Chaque matin, en direct de simap » (suite 10, § 2): on Monday the week that ended, from Tuesday to Friday the day
before; never the day of the reading; filtered, checked before any write."""

import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from proxsis.call_list import company_id
from proxsis.connectors import simap
from proxsis.entities import normalize_name
from proxsis.live_week import (
    build_live,
    check_corrections,
    check_live,
    frozen_mornings,
    frozen_projects,
    last_monday,
    previous_week,
    reading_period,
    update_corrections,
    write_if_valid,
)
from proxsis.morning_gate import should_read
from proxsis.pii import PRIVATE_PLACEHOLDER

MONDAY = date(2026, 10, 12)
TUESDAY = date(2026, 10, 13)
ZURICH = ZoneInfo("Europe/Zurich")


def _award(day: str, *, pub_type: str = "award", vendors: tuple[str, ...] = ("Bitz travaux publics SA",),
           authority: str | None = "Commune de Sion") -> dict:
    return {"pub_type": pub_type, "publication_date": day, "creation_language": "fr",
            "title": {"fr": f"Réfection d'une route ({day})", "de": "Strassensanierung"},
            "contracting_authority": authority, "order_city": "Sion",
            "vendors": [{"name": n, "uid": "CHE-123.456.789" if n.endswith("(IDE)") else None} for n in vendors],
            "project_id": f"projet-{day}"}


def _names(contract: dict) -> list[str]:
    return [w["nom"] for w in contract["laureats"]]


def test_monday_reads_the_week_that_ended_and_tuesday_to_friday_the_day_before():
    assert previous_week(MONDAY) == (date(2026, 10, 5), date(2026, 10, 11))
    assert last_monday(date(2026, 10, 14)) == MONDAY and last_monday(MONDAY) == MONDAY
    with pytest.raises(ValueError):
        previous_week(TUESDAY)
    assert reading_period(MONDAY) == ("semaine", date(2026, 10, 5), date(2026, 10, 11))
    assert reading_period(TUESDAY) == ("veille", date(2026, 10, 12), date(2026, 10, 12))
    assert reading_period(date(2026, 10, 16)) == ("veille", date(2026, 10, 15), date(2026, 10, 15))
    for weekend in (date(2026, 10, 17), date(2026, 10, 18)):  # no reading on Saturday or Sunday
        with pytest.raises(ValueError):
            reading_period(weekend)


def test_on_monday_nothing_changes_the_whole_week_is_shown_and_no_person_is_named():
    data = build_live([
        _award("2026-10-06", vendors=("Bitz travaux publics SA", PRIVATE_PLACEHOLDER)),
        _award("2026-10-09", authority=PRIVATE_PLACEHOLDER, pub_type="direct_award"),
        _award("2026-10-04"),  # the week before: not shown
        _award("2026-10-07", pub_type="tender"),  # a call for tenders is not an award
    ], MONDAY)
    assert data["mode"] == "semaine" and data["periode"] == {"du": "2026-10-05", "au": "2026-10-11"}
    assert data["mis_a_jour_le"] == "2026-10-12" and data["schema"] == 2
    assert [c["date"] for c in data["marches"]] == ["2026-10-09", "2026-10-06"]
    assert _names(data["marches"][1]) == ["Bitz travaux publics SA"]
    assert data["marches"][0]["adjudicateur"] is None
    assert data["mention"] == simap.MANDATORY_NOTICE
    assert check_live(data) == []


def test_from_tuesday_to_friday_only_the_day_before_is_shown():
    records = [_award("2026-10-12"), _award("2026-10-13"), _award("2026-10-14"), _award("2026-10-09")]
    data = build_live(records, date(2026, 10, 14))
    assert data["mode"] == "veille" and data["periode"] == {"du": "2026-10-13", "au": "2026-10-13"}
    assert [c["date"] for c in data["marches"]] == ["2026-10-13"]  # never the day of the reading itself
    assert check_live(data) == []
    empty = build_live(records, date(2026, 10, 16))  # nothing published on Thursday 15: an empty day, said as such
    assert empty["marches"] == [] and empty["total"] == 0 and check_live(empty) == []


def test_regular_awards_are_kept_not_only_direct_awards():
    # simap's detail calls an award after a call for tenders « award » (the search filter says « award_tender »): the
    # Monday section of 07.10.2026 kept only « award_tender » and « direct_award », and so dropped every regular award
    # (on the week of 21.09.2026 replayed: 13 shown out of 25)
    data = build_live([_award("2026-10-12", pub_type="award"), _award("2026-10-12", pub_type="award_tender"),
                       _award("2026-10-12", pub_type="direct_award")], TUESDAY)
    assert data["total"] == 3


def test_each_laureate_carries_the_identifier_of_the_application_lists():
    # « dans votre liste » (suite 10, § 2): the screen compares this identifier with the companies of the list
    data = build_live([_award("2026-10-12", vendors=("Bitz travaux publics SA",))], TUESDAY)
    assert data["marches"][0]["laureats"] == [{"nom": "Bitz travaux publics SA",
                                              "id": company_id(normalize_name("Bitz travaux publics SA"))}]
    data["marches"][0]["laureats"][0]["id"] = "ent-0000000000"
    assert any("identifiant" in p for p in check_live(data))


def test_a_file_that_fails_a_check_is_not_written_and_the_previous_one_stays(tmp_path: Path):
    out = tmp_path / "matin.json"
    out.write_text('{"etat": "a_jour", "precedent": true}\n', "utf-8")
    bad = build_live([_award("2026-10-12")], TUESDAY)
    bad["marches"][0]["url"] = "https://example.org/x"
    bad["marches"][0]["laureats"] = [{"nom": "Jean Dupont", "id": company_id(normalize_name("Jean Dupont"))}]
    problems = write_if_valid(bad, out)
    assert any("simap.ch" in p for p in problems) and any("personne" in p for p in problems)
    assert json.loads(out.read_text("utf-8"))["precedent"] is True
    good = build_live([_award("2026-10-12")], TUESDAY)
    assert write_if_valid(good, out) == [] and json.loads(out.read_text("utf-8"))["total"] == 1


def test_nothing_published_on_the_day_of_the_reading_is_passed_on():
    # AGB API ch. 5 al. 2: a day's publications only from 8 a.m.; the reading ends the day before, and the check refuses
    # anything dated the day of the reading or later, whatever the path
    data = build_live([_award("2026-10-12"), _award("2026-10-13")], TUESDAY)
    assert [c["date"] for c in data["marches"]] == ["2026-10-12"]
    assert check_live(data) == []
    data["marches"][0]["date"] = "2026-10-13"
    data["periode"]["au"] = "2026-10-13"
    problems = check_live(data)
    assert any("8 h" in p for p in problems) and any("période" in p for p in problems)


def test_the_period_must_be_the_one_of_the_reading_day():
    data = build_live([_award("2026-10-12")], TUESDAY)
    data["mode"] = "semaine"  # a Tuesday never shows a whole week
    assert any("période" in p for p in check_live(data))
    data = build_live([_award("2026-10-12")], TUESDAY)
    data["mis_a_jour_le"] = "2026-10-17"  # a Saturday: no reading
    assert any("jour ouvrable" in p for p in check_live(data))


REAL = Path("../data/reel/simap/adjudications_emetteur_vs_construction_2024-07_2026-09.jsonl")


@pytest.mark.skipif(not REAL.exists(), reason="données réelles absentes (hors dépôt)")
def test_a_real_week_and_a_real_day_replayed_pass_every_check():
    records = [json.loads(line) for line in REAL.read_text("utf-8").splitlines() if line.strip()]
    week = build_live(records, date(2026, 9, 28))
    assert week["total"] == 25 and check_live(week) == []  # 12 awards and 13 direct awards (21 to 27.09.2026)
    day = build_live(records, date(2026, 9, 30))
    assert day["mode"] == "veille" and check_live(day) == []


def test_a_laureate_is_named_only_with_a_legal_form_or_an_ide():
    # published every day without anyone reading it: fail closed (review 1, I2) — « Hans Baumann », « Kevin Rossier »
    # or a firm without its legal form are not named; the award itself (title, date, authority) is still shown
    data = build_live([_award("2026-10-12", vendors=("Bitz travaux publics SA", "Hans Baumann", "Kevin Rossier",
                                                     "Exemple Holzbau", "Muster Holz (IDE)"))], TUESDAY)
    assert _names(data["marches"][0]) == ["Bitz travaux publics SA", "Muster Holz (IDE)"]
    assert check_live(data) == []


def _correction(day: str, project: str, kind: str = "correction") -> dict:
    return {"pub_type": kind, "publication_date": day, "creation_language": "fr",
            "title": {"fr": f"Rectification ({day})"}, "project_id": project, "vendors": []}


P1 = "95465d92-7be7-46b7-862a-a376ca087134"  # a project cited by the frozen data
P2 = "11111111-2222-4333-8444-555555555555"


def test_the_corrections_revocations_and_abandonments_of_the_period_are_passed_on():
    data = build_live([_award("2026-10-06"), _correction("2026-10-08", P2),
                       _correction("2026-10-09", P1, "revocation"), _correction("2026-10-03", P1)], MONDAY)
    assert [(r["date"], r["type"]) for r in data["rectifications"]] == [("2026-10-09", "revocation"),
                                                                       ("2026-10-08", "correction")]
    assert data["rectifications"][0]["url"] == f"https://www.simap.ch/fr/project-detail/{P1}"
    assert "projet" not in data["rectifications"][0]
    assert check_live(data) == []
    data["rectifications"][0]["type"] = "commentaire"
    assert any("type inconnu" in p for p in check_live(data))
    tuesday = build_live([_correction("2026-10-09", P1), _correction("2026-10-12", P2)], TUESDAY)
    assert [r["date"] for r in tuesday["rectifications"]] == ["2026-10-12"]


def test_a_correction_of_a_frozen_notice_is_kept_from_one_morning_to_the_next(tmp_path: Path):
    frozen_file = tmp_path / "appels.json"
    frozen_file.write_text(json.dumps({"url": f"https://www.simap.ch/fr/project-detail/{P1}"}), "utf-8")
    frozen = frozen_projects([frozen_file])
    assert frozen == {P1}
    first = update_corrections(None, [_correction("2026-10-08", P1), _correction("2026-10-08", P2)], MONDAY, frozen)
    assert [(n["projet"], n["date"]) for n in first["avis"]] == [(P1, "2026-10-08")]  # P2 is not in the frozen data
    assert check_corrections(first) == []
    later = update_corrections(first, [_correction("2026-10-14", P1, "abandonment")], date(2026, 10, 15), frozen)
    assert [(n["date"], n["type"]) for n in later["avis"]] == [("2026-10-08", "correction"),
                                                                ("2026-10-14", "abandonment")]
    assert later["mis_a_jour_le"] == "2026-10-15" and check_corrections(later) == []
    bad = json.loads(json.dumps(later))
    bad["avis"][0]["url"] = "https://example.org/x"
    bad["avis"][1]["date"] = "2026-10-15"
    problems = check_corrections(bad)
    assert any("page simap.ch" in p for p in problems) and any("8 h" in p for p in problems)


def test_both_files_are_written_together_or_not_at_all(tmp_path: Path):
    morning, corr = tmp_path / "matin.json", tmp_path / "corrections.json"
    corr.write_text('{"precedent": true}\n', "utf-8")
    data = build_live([_award("2026-10-12")], TUESDAY)
    bad = update_corrections(None, [], TUESDAY, set()) | {"mention": "autre"}
    assert write_if_valid(data, morning, bad, corr) and not morning.exists()
    assert json.loads(corr.read_text("utf-8"))["precedent"] is True
    good = update_corrections(None, [], TUESDAY, set())
    assert write_if_valid(data, morning, good, corr) == []
    assert json.loads(corr.read_text("utf-8"))["avis"] == [] and json.loads(morning.read_text("utf-8"))["total"] == 1


def test_the_files_of_the_site_are_valid_waiting_or_published_and_the_frozen_data_cite_simap_projects():
    # the morning job runs these tests AFTER writing the files: they hold for the waiting files of the repository and
    # for a reading just written (found by the local run of the job on 13.10.2026: an « en_attente » assertion would
    # have stopped every publication)
    web = Path("../apps/web/src/data")
    corrections = json.loads((web / "direct/corrections.json").read_text("utf-8"))
    assert corrections["mention"] == simap.MANDATORY_NOTICE
    assert check_corrections(corrections | {"mis_a_jour_le": corrections["mis_a_jour_le"] or "2026-10-12"}) == []
    assert len(frozen_projects(sorted(web.glob("demo/*.json")) + sorted(web.glob("presentation/*.json")))) > 10
    morning = json.loads((web / "direct/matin.json").read_text("utf-8"))
    assert morning["schema"] == 2 and morning["mention"] == simap.MANDATORY_NOTICE
    if morning["etat"] == "en_attente":
        assert morning["mis_a_jour_le"] is None and morning["marches"] == []
    else:
        assert check_live(morning) == []
    assert not (web / "direct/semaine.json").exists()  # one file for the section, read every working day


# ------------------------------------------------------------------------------------------- the morning gate
def _at(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=ZURICH)


def test_the_automatic_job_reads_every_working_day_from_6_am_and_never_twice_the_same_day():
    waiting = {"etat": "en_attente", "mis_a_jour_le": None}
    assert not should_read(_at(TUESDAY, 5, 59), waiting)  # before 6 a.m. in Zurich: wait for the next start
    assert should_read(_at(TUESDAY, 6, 0), waiting)
    assert should_read(_at(TUESDAY, 13, 40), waiting)  # late (GitHub's planner): still read
    assert not should_read(_at(date(2026, 10, 17), 9), waiting)  # Saturday
    assert not should_read(_at(date(2026, 10, 18), 9), waiting)  # Sunday
    done_today = {"etat": "a_jour", "mis_a_jour_le": "2026-10-13"}
    assert not should_read(_at(TUESDAY, 7, 10), done_today)  # already read this morning
    assert should_read(_at(date(2026, 10, 14), 6, 5), done_today)  # a new day
    assert should_read(_at(MONDAY, 6, 1), {"etat": "a_jour", "mis_a_jour_le": "2026-10-09"})


# ------------------------------------------------------------------- « Choisissez une date »: the same section, frozen
def test_the_frozen_morning_of_a_chosen_monday_shows_only_what_was_published_before_it():
    mondays = [{"lundi": "2026-10-12", "choisissable": True, "dix": []},
               {"lundi": "2026-10-05", "choisissable": False, "dix": []}]  # not offered: not in the file
    records = [_award("2026-10-06"), _award("2026-10-11", pub_type="direct_award"), _award("2026-10-12"),
               _award("2026-10-04")]
    data = frozen_mornings(records, mondays)
    assert list(data["lundis"]) == ["2026-10-12"]
    shown = data["lundis"]["2026-10-12"]
    assert shown["periode"] == {"du": "2026-10-05", "au": "2026-10-11"}
    assert [c["date"] for c in shown["marches"]] == ["2026-10-11", "2026-10-06"]
    assert all(c["date"] < "2026-10-12" for c in shown["marches"])
    assert data["mention"] == simap.MANDATORY_NOTICE and data["source"] == simap.SOURCE


def test_a_corrected_award_is_passed_on_as_a_correction_not_as_a_new_award():
    corrected = _award("2026-10-12") | {"corrected": True, "project_id": P1}
    data = build_live([corrected, _award("2026-10-12", pub_type="direct_award")], TUESDAY)
    assert data["total"] == 1  # the award was shown on the day it was first published
    assert [(r["date"], r["type"]) for r in data["rectifications"]] == [("2026-10-12", "correction")]
    assert check_live(data) == []
    later = update_corrections(None, [corrected], TUESDAY, {P1})
    assert [(n["projet"], n["type"]) for n in later["avis"]] == [(P1, "correction")]
