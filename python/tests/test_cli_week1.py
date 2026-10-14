"""Week-1 commands on SYNTHETIC simap-like files: call list + sheet, answers integration, specialty backtest."""

import csv
import json
from datetime import date

from proxsis.cli import main
from test_call_list import _world


def _write(tmp_path):
    f = tmp_path / "simap.jsonl"
    f.write_text("\n".join(json.dumps(r, default=str) for r in _world()) + "\n", "utf-8")
    return f


def test_dix_entreprises_writes_frozen_list_sheet_and_csv(tmp_path):
    f = _write(tmp_path)
    out = tmp_path / "terrain"
    rc = main(["dix-entreprises", "--fichiers", str(f), "--date", "2026-09-28", "--k", "5", "--out-dir", str(out),
               "--sans-pdf"])
    assert rc == 0
    lst = json.loads((out / "liste_2026-09-28_batiment.json").read_text("utf-8"))
    assert len(lst["entreprises"]) == 5 and len(lst["liste_id"]) == 12
    assert (out / "liste_2026-09-28_batiment_fr.html").exists()
    assert (out / "liste_2026-09-28_batiment_de.html").exists()
    rows = list(csv.DictReader((out / "reponses_2026-09-28_batiment.csv").open(encoding="utf-8")))
    assert len(rows) == 5 + len(lst["surprises"])


def test_integrer_validation_reads_the_filled_csv(tmp_path):
    f = _write(tmp_path)
    out = tmp_path / "terrain"
    main(["dix-entreprises", "--fichiers", str(f), "--date", "2026-09-28", "--k", "3", "--out-dir", str(out),
          "--sans-pdf"])
    tpl = out / "reponses_2026-09-28_batiment.csv"
    rows = list(csv.DictReader(tpl.open(encoding="utf-8")))
    for r in rows:
        r.update(consultant="C1", agence="Martigny", connue="0", recrute_en_effet="1", pas_pertinente="0")
    with tpl.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    rc = main(["integrer-validation", "--liste", str(out / "liste_2026-09-28_batiment.json"), "--reponses", str(tpl),
               "--out-dir", str(out)])
    assert rc == 0
    rep = json.loads(next(out.glob("validation_*.json")).read_text("utf-8"))
    assert rep["recrute_en_effet"]["part"] == 1.0


def test_backtest_specialites_reports_each_specialty_and_the_chosen_order(tmp_path):
    f = _write(tmp_path)
    out = tmp_path / "bt.json"
    rc = main(["backtest-specialites", "--fichiers", str(f), "--specialites", "batiment", "--premiere-semaine",
               "2025-06-02", "--derniere-semaine", "2026-07-27", "--apprentissage-depuis", "2025-01-06",
               "--fin-donnees", "2026-09-28", "--k", "3", "--n-boot", "50", "--out", str(out)])
    assert rc == 0
    rep = json.loads(out.read_text("utf-8"))
    b = rep["specialites"]["batiment"]
    assert b["ordre_retenu"] in {"frequence", "combine"}
    assert "drapeaux_surprise" in b and date.fromisoformat(rep["mesure_le"])
