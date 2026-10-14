"""Overview of the collected simap awards (tests on SYNTHETIC records)."""

from proxsis.simap_overview import overview


def _r(pid, day, canton=None, city=None, title="Travaux", codes=("211",), vendor="Exemple SA", auth="Commune X"):
    return {"publication_id": pid, "project_id": "p" + pid, "publication_date": day, "order_canton": canton,
            "order_city": city, "title": {"fr": title}, "description": {}, "bkp_codes": list(codes),
            "vendors": [{"name": vendor}], "contracting_authority": auth, "pub_type": "award"}


def test_valais_share_crosses_three_criteria_and_dedupes():
    romandie = [_r("1", "2025-01-10", canton="VS", city="Sion"), _r("2", "2025-04-02", canton="VD", city="Lausanne"),
                _r("3", "2025-05-02", canton=None, city=None, title="Ecole primaire de Bagnes - CFC 23", codes=("23",))]
    vs_issuer = [_r("4", "2025-06-02", canton=None, city=None, title="Route cantonale"), _r("1", "2025-01-10",
                                                                                         canton="VS", city="Sion")]
    places = {"sion", "bagnes"}
    o = overview(romandie, vs_issuer, places, sample=20, seed=0)
    assert o["n_adjudications"] == 4
    v = o["valais"]
    assert v["par_canton_des_travaux"] == 1 and v["par_adjudicateur_valaisan"] == 2 and v["par_lieu_cite"] == 2
    assert v["au_moins_un_critere"] == 3 and abs(v["part"] - 0.75) < 1e-9
    assert o["par_trimestre"]["2025-T1"] == 1 and o["par_trimestre"]["2025-T2"] == 3
    assert o["par_metier"]["electricien"] == 1 and o["par_metier"]["macon"] >= 2
    assert o["metiers_par_trimestre"]["2025-T2"]["electricien"] == 1
    assert o["metiers_par_trimestre"]["2025-T1"]["macon"] == 1


def test_masking_counts_and_sample_with_links():
    recs = [_r(str(i), "2025-01-10", vendor="[particulier]" if i % 3 == 0 else "Firma AG") for i in range(30)]
    o = overview(recs, [], set(), sample=5, seed=1)
    m = o["masquage"]
    assert m["laureats_masques"] == 10 and m["laureats_total"] == 30
    assert len(m["echantillon_a_verifier"]) == 5
    assert m["echantillon_a_verifier"][0]["lien_simap"].startswith("https://www.simap.ch/fr/project-detail/")
