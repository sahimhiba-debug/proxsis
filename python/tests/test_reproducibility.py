"""The files read by the web app come back byte for byte from the commands (review 1, B2): « every figure goes back to
a reproducible command » holds for the demo export, the presentation's map, its three stories and its dated
Mondays. Needs the filtered simap records of data/reel/ (kept outside git, see docs/DONNEES.md); skipped without
them."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from proxsis.cli import ROOT, main

REAL = ROOT / "data" / "reel" / "simap"
WEB = ROOT / "apps" / "web" / "src" / "data"
pytestmark = pytest.mark.skipif(not any(REAL.glob("*.jsonl")), reason="données réelles filtrées absentes (data/reel/)")


@pytest.fixture
def offline_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("PUBLICAI_API_KEY", "PUBLICAI_BASE_URL", "PROXSIS_LLM_PROVIDER"):
        monkeypatch.delenv(key, raising=False)  # the deterministic text model, as for the committed files
    made = json.loads((WEB / "demo" / "meta.json").read_text("utf-8"))["genere_le"]
    epoch = datetime.fromisoformat(f"{made}T12:00:00").replace(tzinfo=UTC).timestamp()
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(int(epoch)))


def test_the_snapshot_is_the_one_recorded() -> None:
    import hashlib

    lines = [x.split() for x in (ROOT / "data" / "reel.sha256").read_text("utf-8").splitlines() if x and x[0] != "#"]
    assert len(lines) >= 8
    for digest, rel in lines:
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel


def _same(produced: Path, committed: Path) -> list[str]:
    return [p.name for p in sorted(produced.glob("*.json")) if p.read_bytes() != (committed / p.name).read_bytes()]


@pytest.mark.usefixtures("offline_deterministic")
def test_the_demo_export_is_reproduced_byte_for_byte(tmp_path: Path) -> None:
    assert main(["export-demo", "--out", str(tmp_path)]) == 0
    assert len(list(tmp_path.glob("*.json"))) == 11
    assert _same(tmp_path, WEB / "demo") == []


@pytest.mark.usefixtures("offline_deterministic")
def test_the_presentation_data_is_reproduced_byte_for_byte(tmp_path: Path) -> None:
    assert main(["export-presentation", "--out", str(tmp_path / "presentation.json")]) == 0
    assert main(["histoires-presentation", "--out", str(tmp_path / "histoires.json")]) == 0
    assert main(["lundis-presentation", "--out", str(tmp_path / "lundis.json")]) == 0
    assert main(["territoire-presentation", "--out", str(tmp_path / "territoire.json")]) == 0
    assert main(["lundi-suivant-presentation", "--out", str(tmp_path / "lundi_suivant.json")]) == 0
    assert main(["moments-presentation", "--out-dir", str(tmp_path)]) == 0
    assert main(["matins-presentation", "--lundis", str(tmp_path / "lundis.json"),
                 "--out", str(tmp_path / "matins.json")]) == 0
    assert _same(tmp_path, WEB / "presentation") == []


def test_the_specialty_measure_is_reproduced_whatever_the_pandas_version(tmp_path: Path) -> None:
    """REEL-SPEC-BAT and its neighbours (CLAIMS.md) come back exactly from the locked environment: on 07.10.2026 the
    combined model of the measure differed in the environment of the lock (pandas 2.3.3) from the one of the original
    computation (pandas 3.0.6) until the count of adjudicators no longer depended on pandas (real_backtest.snapshot)."""
    out = tmp_path / "specialites.json"
    assert main(["backtest-specialites", "--specialites", "batiment", "--out", str(out)]) == 0
    committed = json.loads((ROOT / "docs" / "backtest" / "specialites_v1.json").read_text("utf-8"))
    produced = json.loads(out.read_text("utf-8"))
    assert produced["specialites"]["batiment"] == committed["specialites"]["batiment"]
