"""Entity resolution on real simap laureates (tests on SYNTHETIC names)."""

from proxsis.real_entities import doubtful_pairs, vendor_table


def _r(pid, *names, canton="VS"):
    return {"publication_id": pid, "order_canton": canton, "provenance": {"url": f"https://www.simap.ch/x/{pid}"},
            "vendors": [{"name": n} for n in names]}


def test_vendor_table_merges_exact_variants_and_ignores_masked():
    t = vendor_table([_r("1", "Exemple Bau AG"), _r("2", "EXEMPLE BAU A.G."), _r("3", "[particulier]"),
                      _r("4", "Autre Firma GmbH")])
    assert len(t) == 2
    row = t.set_index("cle").loc["exemple bau"]
    assert row["adjudications"] == 2 and row["variantes"] == 2


def test_doubtful_pairs_are_in_the_review_band_and_sorted():
    recs = [_r("1", "Exemple Bau AG"), _r("2", "Exempel Bau AG"), _r("3", "Exemple Bauunternehmung AG"),
            _r("4", "Zufall Holz AG"), _r("5", "Sanitaire Dupuis Sàrl"), _r("6", "Sanitaire Dupuy Sàrl")]
    pairs = doubtful_pairs(vendor_table(recs), low=80, high=97, n=10)
    assert len(pairs) >= 2
    assert all(80 <= p["score"] < 97 for p in pairs)
    assert pairs == sorted(pairs, key=lambda p: -p["score"])
    assert not any("Zufall" in p["nom_a"] + p["nom_b"] for p in pairs)
    assert {"nom_a", "nom_b", "score", "adjudications_a", "adjudications_b", "lien_a", "lien_b"} <= set(pairs[0])
