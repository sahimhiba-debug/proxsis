"""Values read from tables. A missing cell is ``None`` in every output, whatever the library version: pandas gives NaN
or None for an empty text column depending on its version, and either would otherwise be written out as « nan » or
« None » (found in the call guide: « attribué par nan »)."""

from __future__ import annotations


def optional_text(value: object) -> str | None:
    """The text of a cell, or None when the cell is empty (NaN, None, or blank)."""
    if isinstance(value, str):
        return value.strip() or None
    return None
