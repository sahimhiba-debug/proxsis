"""Should the automatic job « Chaque matin en direct » read simap now? (suite 10, § 2)

Every working day from 6 a.m., Swiss time, even late (GitHub's planner often starts scheduled jobs hours after their
time), and never twice the same day. Standard library only: the job runs it with the runner's own Python, before
installing anything (``python3 python/src/proxsis/morning_gate.py apps/web/src/data/direct/matin.json``), and prints
« go=true » or « go=false » for ``$GITHUB_OUTPUT``.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ZURICH = ZoneInfo("Europe/Zurich")
FIRST_HOUR = 6


def should_read(now: datetime, data: dict[str, Any]) -> bool:
    """``now``: the time in Zurich; ``data``: the section's current file."""
    if now.weekday() > 4 or now.hour < FIRST_HOUR:
        return False
    return not (data.get("etat") == "a_jour" and data.get("mis_a_jour_le") == now.date().isoformat())


def main(argv: list[str]) -> int:
    data = json.loads(Path(argv[1]).read_text("utf-8"))
    print("go=" + ("true" if should_read(datetime.now(ZURICH), data) else "false"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
