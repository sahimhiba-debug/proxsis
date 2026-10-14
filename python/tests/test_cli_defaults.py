"""The commands' default paths point into the repository, whatever the working directory (review 1, B2: run from the
root, a command wrote outside the repository)."""

import contextlib
import io
import re
from pathlib import Path

import pytest

from proxsis.cli import ROOT, build_parser


def _commands() -> list[str]:
    usage = build_parser().format_usage()
    return re.findall(r"[a-z0-9][a-z0-9-]+", usage.split("{", 1)[1].split("}", 1)[0])


def test_every_default_path_is_anchored_in_the_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)  # anywhere but python/
    checked = 0
    for cmd in _commands():
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                ns = build_parser().parse_args([cmd])
        except SystemExit:
            continue  # a command with a required argument has no default to check
        for value in vars(ns).values():
            for v in value if isinstance(value, list) else [value]:
                if isinstance(v, str) and "/" in v and not v.startswith(("http", "simap")):
                    assert Path(v).is_absolute() and Path(v).resolve().is_relative_to(ROOT), (cmd, v)
                    checked += 1
    assert checked > 40  # the defaults are really examined
    assert (ROOT / "python" / "pyproject.toml").exists()
