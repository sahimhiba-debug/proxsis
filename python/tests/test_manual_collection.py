"""Manual collection kit: people read the portals, paste the text; the filter runs BEFORE anything is saved."""

import json
import socket

import pytest

from proxsis import manual_collection as mc

TEXT_PERMIT = ("Commune de Sion. Mise à l'enquête publique. Requérant : M. Jean Exemple, rue du Rhône 1, Sion. "
               "Auteur du projet : Bureau Fictif Sàrl, Sion. Objet : construction d'une villa familiale. "
               "Coût : CHF 850'000.-")
TEXT_RC = ("Exemple Construction SA, à Martigny, CHE-123.456.789. Nouvelle inscription. But : travaux de "
           "maçonnerie. Capital : CHF 100'000. Personnes inscrites : Exemple, Jean, de Sion, à Sion, administrateur.")


def _sub(text=TEXT_PERMIT, **kw):
    base = {"text": text, "url": "https://amtsblattportal.ch/#!/search/publications/detail/abc", "date": "2026-09-04",
            "lang": "fr", "source": "bo_vs", "rubrique": "BA-VS05", "collecteur": "HS"}
    return base | kw


def test_preview_masks_private_persons_and_keeps_companies_without_writing(tmp_path):
    res = mc.preview(_sub())
    assert "Jean Exemple" not in res["texte_filtre"] and "rue du Rhône 1" not in res["texte_filtre"]
    assert "Bureau Fictif Sàrl" in res["texte_filtre"] and res["masquages"] >= 2
    assert not any(tmp_path.rglob("*"))


def test_save_writes_filtered_text_privately_and_only_hash_and_link_publicly(tmp_path):
    entry = mc.save(_sub(text=TEXT_RC, source="fosc", rubrique="HR01"), tmp_path)
    private = (tmp_path / "textes" / "HS.jsonl").read_text("utf-8")
    public = (tmp_path / "index" / "HS.jsonl").read_text("utf-8")
    assert "Exemple Construction SA" in private and "Exemple, Jean" not in private
    pub = json.loads(public)
    assert "text" not in pub and "texte" not in pub and pub["sha256_texte"] == entry["sha256_texte"]
    assert pub["url"].startswith("https://amtsblattportal.ch/") and pub["doc_type_indicatif"] == "registre_commerce"


def test_save_refilters_server_side_even_if_client_sends_raw_text(tmp_path):
    mc.save(_sub(), tmp_path)
    assert "Jean Exemple" not in (tmp_path / "textes" / "HS.jsonl").read_text("utf-8")


@pytest.mark.parametrize("bad", [
    "Avis de faillite. Le juge a prononcé la faillite de …",
    "Konkurseröffnung über …",
    "Betreibungsamt Sion : commandement de payer …",
    "Appel aux héritiers, succession de …",
])
def test_excluded_categories_are_refused_and_nothing_is_written(tmp_path, bad):
    with pytest.raises(mc.Refused):
        mc.save(_sub(text=bad + " " * 60), tmp_path)
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


@pytest.mark.parametrize("field, value", [("lang", "it"), ("source", "jobs"), ("rubrique", "KK01"),
                                          ("url", "https://www.jobs.ch/x"), ("date", "05.09.2026"),
                                          ("collecteur", "")])
def test_invalid_submissions_are_refused(tmp_path, field, value):
    with pytest.raises(mc.Refused):
        mc.save(_sub(**{field: value}), tmp_path)


def test_duplicates_are_refused(tmp_path):
    mc.save(_sub(), tmp_path)
    with pytest.raises(mc.Refused):
        mc.save(_sub(), tmp_path)
    with pytest.raises(mc.Refused):
        mc.save(_sub(url="https://amtsblattportal.ch/#!/x/other"), tmp_path)  # same text


def test_status_counts_against_quotas(tmp_path):
    mc.save(_sub(), tmp_path)
    mc.save(_sub(text=TEXT_RC, source="fosc", rubrique="HR01", url="https://amtsblattportal.ch/#!/y"), tmp_path)
    st = mc.status(tmp_path)
    assert st["total"] == 2 and st["par_strate"]["bo_vs/fr"]["n"] == 1 and st["par_strate"]["bo_vs/fr"]["quota"] == 50
    assert st["quotas_langue"] == {"fr": 100, "de": 50}


def test_module_never_opens_an_outbound_connection(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("connexion sortante interdite")

    monkeypatch.setattr(socket, "create_connection", boom)
    mc.preview(_sub())
    mc.save(_sub(), tmp_path)
    with open(mc.__file__, encoding="utf-8") as fh:
        src = fh.read()
    assert "import httpx" not in src and "urllib.request" not in src and "requests" not in src.split("\n")[0:40]


def test_gitignore_excludes_private_texts():
    from pathlib import Path

    gi = (Path(mc.__file__).resolve().parents[3] / ".gitignore").read_text("utf-8")
    assert "data/manuel/textes/" in gi


def test_local_server_requires_token_and_refuses_foreign_origins(tmp_path):
    import threading
    import urllib.error
    import urllib.request

    httpd, token = mc.make_server(tmp_path, port=0)
    port = httpd.server_address[1]
    assert httpd.server_address[0] == "127.0.0.1"
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        def post(path, headers):
            req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(_sub()).encode(),
                                         headers={"Content-Type": "application/json", **headers}, method="POST")
            try:
                with urllib.request.urlopen(req) as r:
                    return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read())

        assert post("/api/enregistrer", {})[0] == 403
        assert post("/api/enregistrer", {"X-Jeton": token, "Origin": "https://evil.example"})[0] == 403
        code, body = post("/api/apercu", {"X-Jeton": token, "Origin": f"http://127.0.0.1:{port}"})
        assert code == 200 and "Jean Exemple" not in body["texte_filtre"]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as r:
            assert token in r.read().decode()
    finally:
        httpd.shutdown()
        httpd.server_close()
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_collection_plan_is_reproducible_and_meets_quotas():
    a, b = mc.collection_plan(seed=20261005), mc.collection_plan(seed=20261005)
    assert a == b
    totals: dict[str, int] = {}
    for row in a:
        totals[row["strate"]] = totals.get(row["strate"], 0) + row["quota"]
        assert len(row["jours"]) * mc.PER_DAY >= row["quota"] and len(row["reserve"]) == 3
        assert set(row["jours"]).isdisjoint(row["reserve"])
        assert all(mc.PERIOD[0].isoformat() <= d <= mc.PERIOD[1].isoformat() for d in row["jours"] + row["reserve"])
    assert totals == mc.QUOTAS
    per_person: dict[str, int] = {}
    for row in a:
        per_person[row["personne"]] = per_person.get(row["personne"], 0) + row["quota"]
    assert set(per_person.values()) == {30}


def test_duplicate_detected_by_publication_id_whatever_the_link_form(tmp_path):
    uid = "72e1f809-0483-4602-8259-85cbcef99cf4"
    mc.save(_sub(url=f"https://bulletin-officiel.vs.ch/#!/search/publications/detail/{uid}"), tmp_path)
    with pytest.raises(mc.Refused, match="déjà"):
        mc.save(_sub(text=TEXT_PERMIT + " (autre rendu)",
                     url=f"https://bulletin-officiel.vs.ch/api/v1/publications/{uid}/pdf"), tmp_path)


def test_xml_import_endpoint_returns_masked_fields_and_writes_nothing(tmp_path):
    import threading
    import urllib.request
    from pathlib import Path

    xml = (Path(__file__).parent / "fixtures" / "manuel" / "ba_vs05_fictif.xml").read_text("utf-8")
    httpd, token = mc.make_server(tmp_path, port=0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/xml", data=json.dumps({"xml": xml}).encode(),
                                     headers={"Content-Type": "application/json", "X-Jeton": token}, method="POST")
        with urllib.request.urlopen(req) as r:
            body = json.loads(r.read())
    finally:
        httpd.shutdown()
        httpd.server_close()
    assert body["source"] == "bo_vs" and body["date"] == "2026-09-25" and "Exempleton" not in body["text"]
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_masks_done_at_xml_import_are_recorded_separately(tmp_path):
    e = mc.save(_sub(masquages_import=3), tmp_path)
    assert e["masquages_import"] == 3 and e["masquages"] >= 1
    e2 = mc.save(_sub(text=TEXT_RC, source="fosc", rubrique="HR01", url="https://amtsblattportal.ch/#!/z",
                      masquages_import="beaucoup"), tmp_path)
    assert e2["masquages_import"] == 0
