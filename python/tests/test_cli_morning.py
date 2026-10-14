"""The commands of « Chaque matin, en direct de simap » (suite 10, § 2): the morning reading (replayed from a filtered
file here, never the network) and the frozen mornings of « Choisissez une date »."""

import json
from pathlib import Path

from proxsis.cli import ROOT, build_parser, main
from proxsis.connectors import simap


def _award(day: str, pub_type: str = "award", name: str = "Bitz travaux publics SA") -> dict:
    return {"pub_type": pub_type, "publication_date": day, "creation_language": "fr", "title": {"fr": f"Route ({day})"},
            "contracting_authority": "Commune de Sion", "order_city": "Sion", "vendors": [{"name": name, "uid": None}],
            "project_id": f"95465d92-7be7-46b7-862a-a376ca08{day[-2:]}00"}


def _replay(tmp_path: Path, records: list[dict]) -> Path:
    path = tmp_path / "rejeu.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), "utf-8")
    return path


def _args(tmp_path: Path, day: str, replay: Path) -> list[str]:
    (tmp_path / "figees").mkdir(exist_ok=True)
    return ["matin-en-direct", "--jour", day, "--rejeu", str(replay), "--out", str(tmp_path / "matin.json"),
            "--corrections", str(tmp_path / "corrections.json"), "--figees", str(tmp_path / "figees")]


def test_the_morning_reading_writes_the_day_before_on_a_tuesday(tmp_path: Path) -> None:
    replay = _replay(tmp_path, [_award("2026-10-09"), _award("2026-10-12"), _award("2026-10-13")])
    assert main(_args(tmp_path, "2026-10-13", replay)) == 0
    data = json.loads((tmp_path / "matin.json").read_text("utf-8"))
    assert (data["mode"], data["periode"], data["total"]) == ("veille", {"du": "2026-10-12", "au": "2026-10-12"}, 1)
    assert data["mention"] == simap.MANDATORY_NOTICE
    corrections = json.loads((tmp_path / "corrections.json").read_text("utf-8"))
    assert corrections["mis_a_jour_le"] == "2026-10-13" and corrections["avis"] == []


def test_a_day_without_new_award_is_written_as_an_empty_day(tmp_path: Path) -> None:
    replay = _replay(tmp_path, [_award("2026-10-12")])
    assert main(_args(tmp_path, "2026-10-14", replay)) == 0
    data = json.loads((tmp_path / "matin.json").read_text("utf-8"))
    assert data["marches"] == [] and data["total"] == 0 and data["etat"] == "a_jour"


def test_no_reading_on_a_saturday_and_nothing_is_written(tmp_path: Path) -> None:
    replay = _replay(tmp_path, [_award("2026-10-16")])
    assert main(_args(tmp_path, "2026-10-17", replay)) == 2
    assert not (tmp_path / "matin.json").exists()


def test_a_failed_check_writes_nothing(tmp_path: Path) -> None:
    replay = _replay(tmp_path, [_award("2026-10-12", name="Garage Exemple SA, c/o Jean Exemple")])
    assert main(_args(tmp_path, "2026-10-13", replay)) == 1
    assert not (tmp_path / "matin.json").exists() and not (tmp_path / "corrections.json").exists()


def test_the_frozen_mornings_follow_the_chosen_mondays(tmp_path: Path) -> None:
    mondays = {"lundis": [{"lundi": "2026-10-12", "choisissable": True, "dix": []}]}
    (tmp_path / "lundis.json").write_text(json.dumps(mondays), "utf-8")
    replay = _replay(tmp_path, [_award("2026-10-06"), _award("2026-10-12")])
    out = tmp_path / "matins.json"
    assert main(["matins-presentation", "--fichiers", str(replay), "--lundis", str(tmp_path / "lundis.json"),
                 "--out", str(out)]) == 0
    data = json.loads(out.read_text("utf-8"))
    assert [c["date"] for c in data["lundis"]["2026-10-12"]["marches"]] == ["2026-10-06"]


def test_the_defaults_point_at_the_files_of_the_section() -> None:
    ns = build_parser().parse_args(["matin-en-direct"])
    assert Path(ns.out) == ROOT / "apps/web/src/data/direct/matin.json" and ns.jour is None
    ns = build_parser().parse_args(["matins-presentation"])
    assert Path(ns.out) == ROOT / "apps/web/src/data/presentation/matins.json"
    assert Path(ns.lundis) == ROOT / "apps/web/src/data/presentation/lundis.json"
    # the frozen mornings read the Valais authorities' construction awards, the perimeter of the live reading
    assert [Path(f).name for f in ns.fichiers] == ["adjudications_emetteur_vs_construction_2024-07_2026-09.jsonl"]
