from datetime import UTC, datetime

import pytest

from proxsis.provenance import Provenance, content_hash


def test_provenance_requires_source_url_date_license():
    p = Provenance(
        source="simap.ch",
        url="https://www.simap.ch/api/publications/v2/project/project-search?lang=fr",
        retrieved_at=datetime(2026, 10, 4, 12, 0, tzinfo=UTC),
        license="CGU simap.ch (à vérifier)",
    )
    assert p.source == "simap.ch"
    assert p.fictif is False
    d = p.as_dict()
    assert set(d) >= {"source", "url", "retrieved_at", "license", "fictif"}
    assert d["retrieved_at"] == "2026-10-04T12:00:00+00:00"


def test_provenance_rejects_empty_fields():
    with pytest.raises(ValueError):
        Provenance(source="", url="https://x.ch", retrieved_at=datetime.now(UTC), license="x")
    with pytest.raises(ValueError):
        Provenance(source="x", url="", retrieved_at=datetime.now(UTC), license="x")
    with pytest.raises(ValueError):
        Provenance(source="x", url="https://x.ch", retrieved_at=datetime.now(UTC), license="")


def test_provenance_rejects_naive_datetime():
    with pytest.raises(ValueError):
        Provenance(source="x", url="https://x.ch", retrieved_at=datetime(2026, 1, 1), license="x")


def test_fictional_provenance_is_marked():
    p = Provenance.fictional("monde-fictif", seed=42)
    assert p.fictif is True
    assert "FICTIF" in p.license
    assert p.url.startswith("fictif://")


def test_content_hash_is_stable():
    assert content_hash(b"abc") == content_hash(b"abc")
    assert content_hash(b"abc") != content_hash(b"abd")
    assert len(content_hash(b"abc")) == 64
