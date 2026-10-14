"""One-page sheet « à valider par les consultants » for a call list, and the integration of their answers.

For each company, three boxes: « connue » (already a client or known contact), « recrute en effet » (the
consultant knows it is hiring), « pas pertinente ». The answers become the first field ground truth
(RÉEL-TERRAIN): share of the list that is really hiring, share already known (novelty), share irrelevant,
and the agreement between consultants. Consultants are identified by a code (C1, SH…), never by name.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from proxsis.call_list import reason_text
from proxsis.taxonomy import TRADES

FIELDS = ("connue", "recrute_en_effet", "pas_pertinente")
CSV_COLUMNS = ["liste_id", "rang", "entreprise_id", "entreprise", "consultant", "agence", *FIELDS, "remarque"]
_CODE = re.compile(r"[A-Z]{1,2}\d{0,3}")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TXT: dict[str, dict[str, Any]] = {
    "fr": {"titre": "Liste d'appels {spec} — semaine du {date} — à valider par les consultants",
           "consigne": "Pour chaque entreprise, cochez ce que vous savez. Aucune case = vous ne savez pas. "
                       "Écrivez votre code (pas votre nom).",
           "cases": ("Connue", "Recrute en effet", "Pas pertinente"), "entreprise": "Entreprise",
           "pourquoi": "Pourquoi",
           "besoin": "Main-d'œuvre estimée (pers./semaine, pic sur 8 semaines, ordre de grandeur)",
           "conf": "Confiance", "src": "Source",
           "remarque": "Remarque", "pied": "Code consultant : ______  Agence : ______________  Date : __________",
           "conf_v": {"elevee": "élevée", "moyenne": "moyenne", "faible": "faible"},
           "surveiller": "À surveiller : surprises hors des dix premières (activité qui bondit ou nouveau venu)",
           "note": "Entreprises et marchés réels (simap.ch). Aucune donnée de Flexsis ni de particulier. "
                   "Le besoin chiffré est la main-d'œuvre mobilisée par le lot ; la part temporaire est inconnue."},
    "de": {"titre": "Anrufliste {spec} — Woche vom {date} — von den Beratenden zu prüfen",
           "consigne": "Kreuzen Sie pro Firma an, was Sie wissen. Kein Kreuz = unbekannt. "
                       "Bitte Ihr Kürzel eintragen (nicht Ihren Namen).",
           "cases": ("Bekannt", "Stellt tatsächlich ein", "Nicht relevant"), "entreprise": "Firma",
           "pourquoi": "Warum",
           "besoin": "Geschätzter Personaleinsatz (Pers./Woche, Spitze in 8 Wochen, Grössenordnung)",
           "conf": "Sicherheit", "src": "Quelle",
           "remarque": "Bemerkung", "pied": "Kürzel: ______  Filiale: ______________  Datum: __________",
           "conf_v": {"elevee": "hoch", "moyenne": "mittel", "faible": "tief"},
           "surveiller": "Auffällig: Überraschungen ausserhalb der ersten zehn "
                         "(sprunghafte Aktivität oder neu im Markt)",
           "note": "Reale Firmen und Aufträge (simap.ch). Keine Daten von Flexsis oder Privatpersonen. "
                   "Der Bedarf ist der Personaleinsatz des Loses; der Temporäranteil ist unbekannt."},
}
ORDER_TXT = {"frequence": ("ordre : nombre de marchés de la spécialité en 52 semaines, puis le plus récent",
                         "Reihenfolge: Anzahl Zuschläge im Fachbereich in 52 Wochen, dann der jüngste"),
             "combine": ("ordre : modèle combiné (probabilité d'un nouveau marché dans les 8 semaines)",
                         "Reihenfolge: kombiniertes Modell (Wahrscheinlichkeit eines neuen Zuschlags in 8 Wochen)")}
SPEC = {"batiment": ("Bâtiment", "Bau"), "electricite": ("Électricité", "Elektro"),
        "technique": ("Technique du bâtiment", "Gebäudetechnik"), "industrie": ("Industrie", "Industrie")}


def _entries(call_list: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """(rank label, company): the k companies of the list, then the surprises S1, S2…"""
    out = [(str(e.get("rang", "")), e) for e in call_list["entreprises"]]
    return out + [(f"S{i}", e) for i, e in enumerate(call_list.get("surprises") or [], 1)]


def freeze_list(call_list: dict[str, Any]) -> dict[str, Any]:
    key = json.dumps({"as_of": call_list["as_of"], "specialite": call_list["specialite"],
                      "ids": [e["id"] for e in call_list["entreprises"]],
                      "surprises": [e["id"] for e in call_list.get("surprises") or []]}, sort_keys=True)
    return call_list | {"liste_id": hashlib.sha256(key.encode()).hexdigest()[:12]}


def _need(e: dict[str, Any], lang: str) -> str:
    if not e.get("besoin"):
        return "—"
    weeks: dict[str, list[float]] = {}
    for r in e["besoin"]:
        w = weeks.setdefault(r["semaine"], [0.0, 0.0])
        w[0] += r["personnes_bas"]
        w[1] += r["personnes_haut"]
    low, high = max(v[0] for v in weeks.values()), max(v[1] for v in weeks.values())
    trades = sorted({r["metier"] for r in e["besoin"]})
    names = ", ".join(TRADES[t].label_fr if lang == "fr" else TRADES[t].label_de for t in trades if t in TRADES)
    rng = f"{low:.0f}–{high:.0f}" if high >= 1.5 else f"{low:.1f}–{high:.1f}"
    return f"{rng.replace('.', ',') if lang == 'fr' else rng} ({names})"


def _short(x: Any, n: int) -> Any:
    return x if not isinstance(x, str) or len(x) <= n else x[: n - 1].rstrip() + "…"


def render_html(call_list: dict[str, Any], lang: str = "fr", zoom: float = 1.0) -> str:
    t = TXT[lang]
    d = call_list["as_of"].split("-")
    spec = SPEC[call_list["specialite"]][0 if lang == "fr" else 1]
    title = t["titre"].format(spec=spec, date=f"{d[2]}.{d[1]}.{d[0]}")
    order_pair = ORDER_TXT.get(str(call_list.get("ordre_code", "frequence")), ORDER_TXT["frequence"])
    order = order_pair[0 if lang == "fr" else 1]

    def esc(x: str) -> str:
        return html.escape(x, quote=False)

    def row(rank: str, e: dict[str, Any]) -> str:
        reasons = sorted(e["raisons"], key=lambda r: r["code"] not in {"rythme_double", "nouveau_venu"}) \
            if rank.startswith("S") else e["raisons"]
        why = "<br>".join(esc(reason_text(r | {"titre": _short(r.get("titre"), 70),
                                                   "adjudicateur": _short(r.get("adjudicateur"), 45)}, lang))
                          for r in reasons[:2])
        src = e["sources"][0] if e.get("sources") else None
        when = ".".join(reversed(src["date"].split("-"))) if src else ""
        src_html = (f'<a href="{html.escape(src["url_simap"])}">simap.ch, {esc(when)}</a>' if src else "—")
        boxes = "".join('<td><span class="case"></span></td>' for _ in t["cases"])
        return (f"<tr><td>{rank}</td><td><b>{esc(e['nom'])}</b><br>{esc(str(e.get('ville') or ''))}</td>"
                f"<td class='small'>{why}</td><td class='small'>{esc(_need(e, lang))}</td>"
                f"<td>{t['conf_v'][e['confiance']]}</td><td class='small'>{src_html}</td>{boxes}"
                "<td class='rem'></td></tr>")

    entries = _entries(call_list)
    rows = [row(r, e) for r, e in entries if not r.startswith("S")]
    surprises = [row(r, e) for r, e in entries if r.startswith("S")]
    if surprises:
        span = 6 + len(t["cases"]) + 1
        rows.append(f"<tr class='sep'><td colspan='{span}'><b>{esc(t['surveiller'])}</b></td></tr>")
        rows += surprises
    head = "".join(f"<th>{h}</th>" for h in ("#", t["entreprise"], t["pourquoi"], t["besoin"], t["conf"], t["src"],
                                              *t["cases"], t["remarque"]))
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{esc(title)}</title>
<style>@page{{size:A4 landscape;margin:8mm}}
body{{zoom:{zoom};font:8.2pt/1.22 -apple-system,Helvetica,Arial,sans-serif;color:#111}}
h1{{font-size:12pt;margin:0 0 2mm}}p{{margin:0 0 2mm}}table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #999;padding:1.2mm;vertical-align:top}}th{{background:#eee;font-size:7.6pt}}
.small{{font-size:7.4pt}}.case{{display:inline-block;width:4mm;height:4mm;border:1.2px solid #000}}
.rem{{width:30mm}}
.sep td{{background:#f6f6f6}}footer{{margin-top:2mm;font-size:7pt;color:#333}}a{{color:#0645ad}}</style></head><body>
<h1>{esc(title)}</h1>
<p>{esc(t['consigne'])} <b>{t['pied']}</b></p>
<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>
<footer>{esc(t['note'])} {esc(call_list['mention_obligatoire'])}
· liste {html.escape(call_list['liste_id'])} · {esc(order)}</footer>
</body></html>"""


def to_pdf(html_path: Path, pdf_path: Path, chrome: str = CHROME) -> bool:
    """Print the sheet with headless Chrome; False when Chrome is missing or fails (the HTML stays usable)."""
    exe = chrome if Path(chrome).exists() else shutil.which("google-chrome") or shutil.which("chromium")
    if not exe:
        return False
    pdf_path.unlink(missing_ok=True)  # a stale PDF must never be counted as the new one
    try:
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], check=True,
                       capture_output=True, timeout=120)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return False
    return pdf_path.exists() and pdf_path.stat().st_size > 0


def pdf_pages(pdf_path: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(pdf_path)).pages)


def write_one_page_pdf(call_list: dict[str, Any], lang: str, html_path: Path, pdf_path: Path,
                       chrome: str | None = None) -> int | None:
    """Write the sheet, shrinking it until the PDF fits on one page. Returns the number of pages of the last try
    (more than 1 means it does not fit: the caller must fail), or None when no PDF could be printed."""
    n = None
    for zoom in (1.0, 0.94, 0.88, 0.82, 0.76):
        html_path.write_text(render_html(call_list, lang, zoom), "utf-8")
        if not to_pdf(html_path, pdf_path, chrome or CHROME):
            return None
        n = pdf_pages(pdf_path)
        if n == 1:
            return 1
    return n


def csv_template(call_list: dict[str, Any]) -> str:
    import csv
    import io

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_COLUMNS)
    w.writeheader()
    for rank, e in _entries(call_list):
        w.writerow({"liste_id": call_list["liste_id"], "rang": rank, "entreprise_id": e["id"], "entreprise": e["nom"]})
    return buf.getvalue()


def integrate(call_list: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    """An unchecked box means « je ne sais pas » (sheet instructions). Per company and consultant: « recrute » if
    that box is checked, « pas pertinente » if that one is, unknown otherwise. Shares are computed on the
    companies with an opinion; the share on the whole list is a lower bound."""
    ids = {e["id"] for _, e in _entries(call_list)}
    answers: dict[str, dict[str, dict[str, int]]] = {}
    incoherent = []
    for r in rows:
        if r.get("liste_id") != call_list["liste_id"]:
            raise ValueError(f"réponse pour une autre liste ({r.get('liste_id')}) que {call_list['liste_id']}")
        if r.get("entreprise_id") not in ids:
            raise ValueError(f"entreprise inconnue dans la liste : {r.get('entreprise_id')}")
        who = (r.get("consultant") or "").strip()
        if not _CODE.fullmatch(who):
            raise ValueError(f"consultant : écrire un code (C1, SH…), pas un nom : {who!r}")
        vals = {}
        for f in FIELDS:
            v = (r.get(f) or "").strip()
            if v not in {"", "0", "1"}:
                raise ValueError(f"{f} doit valoir 0 ou 1 (reçu {v!r})")
            vals[f] = int(v == "1")
        if vals["recrute_en_effet"] and vals["pas_pertinente"]:
            incoherent.append({"consultant": who, "entreprise_id": r["entreprise_id"],
                               "motif": "recrute en effet et pas pertinente"})
        if who in answers.get(r["entreprise_id"], {}):
            incoherent.append({"consultant": who, "entreprise_id": r["entreprise_id"],
                               "motif": "doublon (dernière ligne retenue)"})
        answers.setdefault(r["entreprise_id"], {})[who] = vals

    def opinion(v: dict[str, int]) -> str:
        if v["recrute_en_effet"] and not v["pas_pertinente"]:
            return "R"
        if v["pas_pertinente"] and not v["recrute_en_effet"]:
            return "P"
        return "U"

    status = {}
    for cid, a in answers.items():
        ops = [opinion(v) for v in a.values()]
        r_, p_ = ops.count("R"), ops.count("P")
        status[cid] = "R" if r_ > p_ else ("P" if p_ > r_ else "U")
    n = len(answers)
    n_r = sum(v == "R" for v in status.values())
    n_p = sum(v == "P" for v in status.values())
    expressed = n_r + n_p
    both = [a for a in answers.values() if sum(opinion(v) != "U" for v in a.values()) >= 2]
    agree = [len({opinion(v) for v in a.values() if opinion(v) != "U"}) == 1 for a in both]
    known = sum(sum(v["connue"] for v in a.values()) * 2 > len(a) for a in answers.values())
    who_all = sorted({w for a in answers.values() for w in a})
    return {"liste_id": call_list["liste_id"], "as_of": call_list["as_of"], "specialite": call_list["specialite"],
            "type_de_donnee": "RÉEL-TERRAIN", "consultants": len(who_all), "entreprises_evaluees": n,
            "couverture": expressed / n if n else None,
            "recrute_en_effet": {"n": n_r, "part": n_r / expressed if expressed else None,
                                 "borne_basse": n_r / n if n else None},
            "pas_pertinente": {"n": n_p, "part": n_p / expressed if expressed else None},
            "connue": {"n": known, "borne_basse": known / n if n else None},
            "accord": {"avis_exprimes": {"entreprises": len(both),
                                         "accord_observe": sum(agree) / len(agree) if agree else None}},
            "incoherences": incoherent,
            "note": ("case vide = « je ne sais pas » ; « recrute en effet » : majorité des avis exprimés par "
                     "entreprise ; part sur les entreprises avec un avis (borne basse sur toute la liste) ; accord "
                     "calculé seulement là où deux consultants ont donné un avis")}
