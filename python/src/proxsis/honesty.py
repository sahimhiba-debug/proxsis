"""Mandatory warnings on every number measured on invented data.

Any result computed on the FICTIONAL world, or on a test set written by the
development agent, carries these sentences in the result file itself, so a
number can never travel without its caveat.
"""

from __future__ import annotations

from typing import Any

FICTIF_WARNING = "monde fictif : prouve que le code fonctionne, pas sa performance réelle"
AGENT_SET_WARNING = (
    "jeu de test écrit et annoté par l'agent de développement (Claude), pas par l'équipe, et sur des textes "
    "qu'il a lui-même inventés : les scores sont optimistes"
)


def mark(result: dict[str, Any], *, fictif: bool, agent_written_set: bool = False) -> dict[str, Any]:
    """Return a copy of ``result`` with the warnings first (so they are read first)."""
    head: dict[str, Any] = {}
    if fictif:
        head["avertissement"] = FICTIF_WARNING
    if agent_written_set:
        head["avertissement_jeu_de_test"] = AGENT_SET_WARNING
    return head | {k: v for k, v in result.items() if k not in head}
