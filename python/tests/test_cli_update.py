"""`proxsis update`: a source that could not be read makes the update fail (never a green run with nothing read)."""

from proxsis.cli import main


def test_update_fails_and_writes_nothing_when_the_source_is_missing(tmp_path, capsys):
    out = tmp_path / "reel"
    rc = main(["update", "--offline", "--cache", str(tmp_path / "cache"), "--out", str(out), "--until", "2026-10-05"])
    assert rc != 0
    assert not out.exists() or not any(out.iterdir())  # no empty table written as if the day were done
    assert "simap" in capsys.readouterr().out


def test_the_daily_update_reads_up_to_the_day_before_in_zurich():
    # suite 10, § 2: the rules of simap stay those of the morning section, never a publication of the day itself (AGB
    # API ch. 5 al. 2: a day's publications only from 8 a.m.; the job is planned at 7:17 in Zurich in summer)
    from datetime import date, datetime
    from zoneinfo import ZoneInfo

    from proxsis.commands.demo import update_window

    zurich = ZoneInfo("Europe/Zurich")
    window = (date(2026, 10, 10), date(2026, 10, 12))
    assert update_window(None, 2, datetime(2026, 10, 13, 7, 17, tzinfo=zurich)) == window
    # 00:30 in Zurich is still the previous evening in UTC: the day of Zurich counts
    assert update_window(None, 2, datetime(2026, 10, 13, 0, 30, tzinfo=zurich)) == window
    assert update_window("2026-10-05", 2, datetime(2026, 10, 13, 9, 0, tzinfo=zurich)) == (date(2026, 10, 3),
                                                                                           date(2026, 10, 5))
