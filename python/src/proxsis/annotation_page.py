"""Self-contained HTML page to annotate the real test set (no server, no network).

``build_page(items)`` embeds the items and the trade list as JSON. Annotations
stay in the browser (localStorage, per annotator) and are exported as JSONL
by the annotator. The page never shows a model output or another annotator's
work.

``profile`` chooses the fields asked (see ``annotation_agreement.PROFILES``):
``simap`` (default) is the original page; ``bo_fr`` and ``bo_de_structure``
are the Bulletin officiel building permits (decision of 2026-10-06). Parcels
and coordinates are masked by the filter before any write: only their
PRESENCE is asked. The German lot asks the structured fields only (no trades,
no need, no amount), with a visible note; the interface stays in French.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from proxsis.annotation_agreement import DEFAULT_PROFILE, FIXED, NOT_COMPARED, compared_fields
from proxsis.connectors import simap
from proxsis.taxonomy import SECTOR_LABELS, SECTOR_TRADES, TRADES

DE_NOTE = ("Lot allemand : seuls les champs structurés sont annotés ; métiers non mesurés. Ne pas utiliser de "
           "traduction automatique. Glossaire : docs/annotation/glossaire_bo_de_fr.md")
_PARCEL = [{"value": "oui", "label": "oui (mentionnée, masquée)"}, {"value": "non", "label": "non (absente)"}]
_COORDS = [{"value": "oui", "label": "oui (mentionnées, masquées)"}, {"value": "non", "label": "non (absentes)"}]
_NEED = [{"value": v, "label": v} for v in ("oui", "non", "incertain")]
BO_FIELDS: dict[str, dict[str, Any]] = {
    "company_name": {"kind": "text", "label": "Entreprise requérante (vide si particulier)"},
    "private_person": {"kind": "check", "label": "Une personne physique est mentionnée"},
    "commune": {"kind": "text", "label": "Commune du projet"},
    "date_evenement": {"kind": "date", "label": "Date de publication"},
    "date_expiration": {"kind": "date", "label": "Expiration du délai"},
    "parcelle_mentionnee": {"kind": "choice", "label": "Parcelle mentionnée ? (présence seulement, jamais la valeur)",
                            "options": _PARCEL, "required": True},
    "coordonnees_mentionnees": {"kind": "choice",
                                "label": "Coordonnées mentionnées ? (présence seulement, jamais la valeur)",
                                "options": _COORDS, "required": True},
    "amount_chf": {"kind": "number", "label": "Montant CHF (coût des travaux ; vide si absent)"},
    "date_debut_travaux": {"kind": "date", "label": "Début des travaux (si écrit)"},
    "trades": {"kind": "multi", "label": "Métiers dont le projet fera probablement naître un besoin"},
    "besoin_temporaire": {"kind": "choice", "label": "Besoin de personnel temporaire possible (secteurs Flexsis) ?",
                          "options": _NEED, "required": True},
    "commentaire": {"kind": "textarea", "label": "Commentaire (jamais de donnée personnelle)"},
}


def _json_for_script(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")


def _trade_groups() -> list[dict[str, Any]]:
    groups = []
    seen: set[str] = set()
    for sector, trades in SECTOR_TRADES.items():
        codes = [t for t in trades if t not in seen]
        seen.update(codes)
        if codes:
            groups.append({"label": SECTOR_LABELS[sector][0],
                           "trades": [{"code": c, "fr": TRADES[c].label_fr, "de": TRADES[c].label_de} for c in codes]})
    rest = [c for c in TRADES if c not in seen]
    if rest:
        groups.append({"label": "Autres", "trades": [{"code": c, "fr": TRADES[c].label_fr, "de": TRADES[c].label_de}
                                                     for c in rest]})
    return groups


def build_page(items: list[dict[str, Any]], title: str = "Annotation — jeu réel v2",
               profile: str = DEFAULT_PROFILE) -> str:
    compared_fields(profile)  # unknown profile → error
    if profile != DEFAULT_PROFILE:
        return _build_bo_page(items, title, profile)
    return (_TEMPLATE.replace("__TITLE__", title).replace("__NOTICE__", html.escape(simap.MANDATORY_NOTICE, quote=False))
            .replace("__ITEMS__", _json_for_script(items))
            .replace("__TRADES__", _json_for_script(_trade_groups())))


def write_page(items_jsonl: Path, out_html: Path, title: str = "Annotation — jeu réel v2",
               profile: str = DEFAULT_PROFILE) -> int:
    items = [json.loads(line) for line in items_jsonl.read_text("utf-8").splitlines() if line.strip()]
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(build_page(items, title, profile=profile), "utf-8")
    return len(items)


# ---------------------------------------------------------------- Bulletin officiel profiles

def profile_config(profile: str) -> dict[str, Any]:
    """Fields asked by a Bulletin officiel page, in order: the compared fields of the profile, then the comment."""
    fields = []
    for f in (*compared_fields(profile), *NOT_COMPARED):
        spec = {"id": f, "required": False} | BO_FIELDS[f]
        if spec["kind"] == "multi":
            spec["groups"] = _trade_groups()
        fields.append(spec)
    return {"name": profile, "fields": fields, "fixed": FIXED.get(profile, {})}


def _field_html(f: dict[str, Any]) -> str:
    i, label, kind = f["id"], html.escape(f["label"]), f["kind"]
    if kind in ("text", "date", "number"):
        extra = ' step="0.01" min="0"' if kind == "number" else ""
        return f'<label for="{i}">{label}</label>\n      <input id="{i}" type="{kind}"{extra}>'
    if kind == "textarea":
        return f'<label for="{i}">{label}</label>\n      <textarea id="{i}"></textarea>'
    if kind == "check":
        return (f'<div class="inline" style="margin-top:10px"><label><input id="{i}" type="checkbox">\n'
                f'        {label}</label></div>')
    if kind == "choice":
        opts = "\n".join(f'        <label><input type="radio" name="{i}" value="{o["value"]}"> '
                         f'{html.escape(o["label"])}</label>' for o in f["options"])
        return f'<fieldset><legend>{label}</legend><div class="inline">\n{opts}</div></fieldset>'
    boxes = []
    for g in f["groups"]:
        checks = "".join(f'<label><input type="checkbox" name="{i}" value="{t["code"]}">'
                         f'{html.escape(t["fr"] + " / " + t["de"])}</label>' for t in g["trades"])
        boxes.append(f'<div><div class="hint">{html.escape(g["label"])}</div><div class="checks">{checks}</div></div>')
    return f'<fieldset><legend>{label}</legend>\n        ' + "\n        ".join(boxes) + "</fieldset>"


def _build_bo_page(items: list[dict[str, Any]], title: str, profile: str) -> str:
    cfg = profile_config(profile)
    note = f'<p class="lot-note" role="note">{html.escape(DE_NOTE)}</p>\n' if profile == "bo_de_structure" else ""
    head = _TEMPLATE[: _TEMPLATE.index("<body>")].replace("</style>", _BO_CSS + "</style>")
    form = "\n      ".join(_field_html(f) for f in cfg["fields"])
    page = (head + _BO_BODY).replace("__TITLE__", html.escape(title)).replace("__NOTE__", note)
    page = page.replace("__FORM__", form).replace("__PROFILE__", _json_for_script(cfg))
    return page.replace("__ITEMS__", _json_for_script(items))  # last: item texts are never searched for placeholders


_BO_CSS = """.lot-note { margin: 8px 16px 0; padding: 8px 12px; border: 2px solid var(--warn); border-radius: 6px;
            font-weight: 600; }
"""

_BO_BODY = r"""<body>
<header>
  <h1>__TITLE__</h1>
  <span><label for="who" style="display:inline;margin:0">Annotateur·rice :</label>
    <input id="who" type="text" placeholder="prénom" style="width:140px" autocomplete="off"></span>
  <span id="progress" class="pill"></span>
  <select id="filter" aria-label="Filtrer">
    <option value="all">Toutes</option><option value="todo">À faire</option><option value="done">Faites</option>
  </select>
  <button id="export">Exporter (JSONL)</button>
  <label class="pill" style="cursor:pointer;margin:0">Reprendre un export<input id="import" type="file"
    accept=".jsonl,.json" hidden></label>
</header>
__NOTE__<div class="notice">Bulletin officiel du Valais — seule la publication officielle fait foi. Textes filtrés
  avant tout enregistrement : particuliers, adresses, parcelles et coordonnées masqués. Pour la parcelle et les
  coordonnées, annotez seulement leur présence (mentionnée et masquée, ou absente), jamais leur valeur. Rien ne
  quitte ce navigateur tant que vous n'exportez pas. Guide (à lire avant de commencer) :
  docs/annotation/guide_annotation.md. Raccourci : Ctrl+Entrée (⌘+Entrée sur Mac) = enregistrer et suivant.</div>
<main>
  <section aria-labelledby="pubtitle">
    <div class="meta"><strong id="pubtitle"></strong><span id="pubmeta"></span><a id="publink" target="_blank"
      rel="noopener">voir la publication (Bulletin officiel)</a></div>
    <div id="text" class="text"></div>
  </section>
  <section>
    <form id="form" autocomplete="off">
      __FORM__
      <div class="nav">
        <button type="button" id="prev">← Précédente</button>
        <button type="submit" class="primary">Enregistrer et suivante →</button>
        <span id="status" class="hint" role="status"></span>
      </div>
    </form>
  </section>
</main>
<script id="profile" type="application/json">__PROFILE__</script>
<script id="items" type="application/json">__ITEMS__</script>
<script>
(function () {
  "use strict";
  const ITEMS = JSON.parse(document.getElementById("items").textContent);
  const PROFILE = JSON.parse(document.getElementById("profile").textContent);
  const FIELDS = PROFILE.fields;
  const NS = "proxsis-annot-" + PROFILE.name;
  const $ = (id) => document.getElementById(id);
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } },
  };
  let who = store.get(NS + ":who") || "";
  let annotations = {};
  let order = ITEMS.map((_, i) => i);
  let pos = 0;

  function key() { return NS + ":" + who.trim().toLowerCase(); }
  function load() { annotations = (who && store.get(key())) || {}; }
  function save() { if (who && !store.set(key(), annotations)) $("status").textContent =
    "Stockage du navigateur indisponible : exportez souvent."; }
  function inputs(f) { return [...document.querySelectorAll('input[name="' + f.id + '"]')]; }

  function applyFilter() {
    const f = $("filter").value;
    order = ITEMS.map((_, i) => i).filter((i) => {
      const done = !!annotations[ITEMS[i].id];
      return f === "all" || (f === "todo" && !done) || (f === "done" && done);
    });
    if (!order.length) order = ITEMS.map((_, i) => i);
    pos = Math.min(pos, order.length - 1);
  }

  function render() {
    const it = ITEMS[order[pos]];
    const n = ITEMS.filter((x) => annotations[x.id]).length;
    $("progress").textContent = n + " / " + ITEMS.length + " annotées";
    $("progress").className = "pill " + (n === ITEMS.length ? "done" : "todo");
    $("pubtitle").textContent = (pos + 1) + " / " + order.length + " — " + it.id;
    $("pubmeta").textContent = [it.lang && it.lang.toUpperCase(), it.order_type, it.publication_date]
      .filter(Boolean).join(" · ");
    $("publink").href = it.source_url || "#";
    $("text").textContent = it.text;
    const a = (annotations[it.id] || {}).gold || {};
    FIELDS.forEach((f) => {
      if (f.kind === "check") $(f.id).checked = !!a[f.id];
      else if (f.kind === "choice") inputs(f).forEach((r) => { r.checked = r.value === a[f.id]; });
      else if (f.kind === "multi") inputs(f).forEach((c) => { c.checked = (a[f.id] || []).includes(c.value); });
      else $(f.id).value = a[f.id] == null ? "" : a[f.id];
    });
    $("status").textContent = annotations[it.id] ? "déjà annotée (" + annotations[it.id].annotated_at + ")" : "";
  }

  function current() {
    const g = Object.assign({}, PROFILE.fixed);
    FIELDS.forEach((f) => {
      if (f.kind === "check") g[f.id] = $(f.id).checked;
      else if (f.kind === "choice") { const r = inputs(f).find((x) => x.checked); g[f.id] = r ? r.value : null; }
      else if (f.kind === "multi") g[f.id] = inputs(f).filter((c) => c.checked).map((c) => c.value).sort();
      else if (f.kind === "number") { const v = $(f.id).value.trim(); g[f.id] = v === "" ? null : Number(v); }
      else g[f.id] = $(f.id).value.trim() || null;
    });
    return g;
  }

  $("form").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!who.trim()) { $("who").focus(); $("status").textContent = "Saisissez d'abord votre prénom."; return; }
    const g = current();
    const missing = FIELDS.find((f) => f.required && g[f.id] == null);
    if (missing) { inputs(missing)[0].focus(); $("status").textContent = "Répondez d'abord : " + missing.label;
      return; }
    const it = ITEMS[order[pos]];
    annotations[it.id] = { id: it.id, lang: it.lang, annotateur: who.trim(),
                           annotated_at: new Date().toISOString(), gold: g };
    save();
    if (pos < order.length - 1) pos += 1;
    render();
  });
  $("prev").addEventListener("click", () => { if (pos > 0) { pos -= 1; render(); } });
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); $("form").requestSubmit(); }
  });
  $("who").value = who;
  $("who").addEventListener("change", () => {
    who = $("who").value; store.set(NS + ":who", who); load(); applyFilter(); render();
  });
  $("filter").addEventListener("change", () => { pos = 0; applyFilter(); render(); });
  $("export").addEventListener("click", () => {
    if (!who.trim()) { $("who").focus(); return; }
    const lines = ITEMS.filter((it) => annotations[it.id]).map((it) => JSON.stringify(annotations[it.id]));
    const blob = new Blob([lines.join("\n") + "\n"], { type: "application/x-ndjson" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "annotations_" + who.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-") + "_" + PROFILE.name + "_" +
      new Date().toISOString().slice(0, 10) + ".jsonl";
    a.click(); URL.revokeObjectURL(a.href);
  });
  $("import").addEventListener("change", async (e) => {
    const f = e.target.files[0]; if (!f) return;
    const known = new Set(ITEMS.map((it) => it.id));
    let n = 0;
    for (const line of (await f.text()).split("\n")) {
      if (!line.trim()) continue;
      try { const r = JSON.parse(line);
        if (!who && r.annotateur) { who = r.annotateur; $("who").value = who; load(); }
        // audit m8: never load someone else's work into this session (blind double annotation)
        if (known.has(r.id) && r.gold && (r.annotateur || "").trim().toLowerCase() === who.trim().toLowerCase()) {
          annotations[r.id] = r; n += 1; } } catch (err) { /* ignore */ }
    }
    save(); applyFilter(); render(); $("status").textContent = n + " annotations reprises.";
  });
  load(); applyFilter(); render();
})();
</script>
</body>
</html>
"""


_TEMPLATE = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root {
  --bg: #f7f7f5; --panel: #ffffff; --ink: #1c1c1a; --muted: #5f5f5a; --line: #deded8;
  --accent: #1f5f8b; --accent-ink: #ffffff; --ok: #2e7d4f; --warn: #9a5b00; --focus: #f2b632;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #161615; --panel: #20201e; --ink: #ecece6; --muted: #a5a59c; --line: #3a3a36;
          --accent: #6fb3e0; --accent-ink: #0d1b24; --ok: #6cc28f; --warn: #e0a548; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
       font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
header { padding: 12px 16px; border-bottom: 1px solid var(--line); background: var(--panel);
         display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; position: sticky; top: 0; z-index: 2; }
header h1 { font-size: 16px; margin: 0; flex: 1 1 260px; }
header select { width: auto; }
@media (max-width: 860px) { header { position: static; } }
.notice { font-size: 12px; color: var(--muted); padding: 6px 16px; }
main { max-width: 1180px; margin: 0 auto; padding: 16px; display: grid; gap: 16px;
       grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); }
@media (max-width: 860px) { main { grid-template-columns: 1fr; } }
section { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; min-width: 0; }
.text { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 14px; }
.meta { color: var(--muted); font-size: 13px; margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 6px 14px; }
label { display: block; font-weight: 600; margin: 10px 0 4px; }
input[type=text], input[type=number], select, textarea { width: 100%; padding: 7px 9px; border: 1px solid var(--line);
  border-radius: 6px; background: var(--bg); color: var(--ink); font: inherit; }
textarea { min-height: 56px; }
fieldset { border: 1px solid var(--line); border-radius: 6px; margin: 8px 0 0; padding: 6px 10px 10px; }
legend { font-size: 13px; color: var(--muted); padding: 0 4px; }
.checks { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 2px 10px; }
.checks label, .inline label { font-weight: 400; margin: 2px 0; display: flex; gap: 6px; align-items: baseline; }
.inline { display: flex; flex-wrap: wrap; gap: 4px 16px; }
button { font: inherit; padding: 7px 12px; border-radius: 6px; border: 1px solid var(--line); background: var(--panel);
         color: var(--ink); cursor: pointer; }
button.primary { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, a:focus-visible {
  outline: 3px solid var(--focus); outline-offset: 1px; }
.nav { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; align-items: center; }
.pill { font-size: 12px; padding: 2px 8px; border-radius: 99px; border: 1px solid var(--line); }
.done { color: var(--ok); border-color: var(--ok); }
.todo { color: var(--warn); border-color: var(--warn); }
a { color: var(--accent); }
.hint { font-size: 12px; color: var(--muted); }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <span><label for="who" style="display:inline;margin:0">Annotateur·rice :</label>
    <input id="who" type="text" placeholder="prénom" style="width:140px" autocomplete="off"></span>
  <span id="progress" class="pill"></span>
  <select id="filter" aria-label="Filtrer">
    <option value="all">Toutes</option><option value="todo">À faire</option><option value="done">Faites</option>
    <option value="fr">FR</option><option value="de">DE</option>
  </select>
  <button id="export">Exporter (JSONL)</button>
  <label class="pill" style="cursor:pointer;margin:0">Reprendre un export<input id="import" type="file"
    accept=".jsonl,.json" hidden></label>
</header>
<div class="notice">__NOTICE__ Textes filtrés (personnes de contact retirées). Rien ne quitte ce navigateur tant que vous n'exportez
  pas. Guide (à lire avant de commencer) : docs/annotation/guide_annotation.md.
  Raccourci : Ctrl+Entrée (⌘+Entrée sur Mac) = enregistrer et suivant.</div>
<main>
  <section aria-labelledby="pubtitle">
    <div class="meta"><strong id="pubtitle"></strong><span id="pubmeta"></span><a id="publink" target="_blank"
      rel="noopener">voir sur simap.ch</a></div>
    <div id="text" class="text"></div>
  </section>
  <section>
    <form id="form" autocomplete="off">
      <label for="doc_type">Type</label>
      <select id="doc_type"><option value="permis_construire">permis de construire</option>
        <option value="adjudication">adjudication (marché attribué)</option>
        <option value="registre_commerce">registre du commerce</option>
        <option value="autre">autre (préciser en commentaire)</option></select>
      <div id="rcbox"><label for="rc_subtype">Sous-type RC</label>
      <select id="rc_subtype"><option value="">—</option><option value="nouvelle_inscription">nouvelle inscription</option>
        <option value="succursale">succursale</option><option value="augmentation_capital">augmentation de capital</option>
        <option value="changement_but">changement de but</option><option value="transfert_siege">transfert de siège</option>
        <option value="liquidation">liquidation</option><option value="radiation">radiation</option></select></div>
      <label for="company_name">Entreprise (requérant, adjudicataire ou société ; vide si particulier)</label>
      <input id="company_name" type="text">
      <label for="uid">IDE (si présent dans le texte)</label>
      <input id="uid" type="text" placeholder="CHE-123.456.789">
      <label for="commune">Commune (du projet ; siège pour le RC)</label>
      <input id="commune" type="text">
      <label for="amount_chf">Montant CHF (coût, prix adjugé ou capital ; vide si absent)</label>
      <input id="amount_chf" type="number" step="0.01" min="0">
      <div class="inline" style="gap:4px 12px">
        <span style="flex:1 1 160px"><label for="date_evenement">Date de l'événement</label>
          <input id="date_evenement" type="date"></span>
        <span style="flex:1 1 160px"><label for="date_debut_travaux">Début des travaux (si écrit)</label>
          <input id="date_debut_travaux" type="date"></span>
      </div>
      <fieldset><legend>Métiers dont le marché fera probablement naître un besoin</legend>
        <div id="trades"></div></fieldset>
      <div class="inline" style="margin-top:10px"><label><input id="private_person" type="checkbox">
        Une personne physique est mentionnée</label></div>
      <fieldset><legend>Besoin de personnel temporaire possible (secteurs Flexsis) ?</legend><div class="inline">
        <label><input type="radio" name="besoin" value="oui"> oui</label>
        <label><input type="radio" name="besoin" value="non"> non</label>
        <label><input type="radio" name="besoin" value="incertain"> incertain</label></div></fieldset>
      <label for="commentaire">Commentaire (jamais de donnée personnelle)</label>
      <textarea id="commentaire"></textarea>
      <div class="nav">
        <button type="button" id="prev">← Précédente</button>
        <button type="submit" class="primary">Enregistrer et suivante →</button>
        <span id="status" class="hint" role="status"></span>
      </div>
    </form>
  </section>
</main>
<script id="items" type="application/json">__ITEMS__</script>
<script id="tradegroups" type="application/json">__TRADES__</script>
<script>
(function () {
  "use strict";
  const ITEMS = JSON.parse(document.getElementById("items").textContent);
  const GROUPS = JSON.parse(document.getElementById("tradegroups").textContent);
  const $ = (id) => document.getElementById(id);
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } },
  };
  let who = store.get("proxsis-annot-v2:who") || "";
  let annotations = {};
  let order = ITEMS.map((_, i) => i);
  let pos = 0;

  function key() { return "proxsis-annot-v2:" + who.trim().toLowerCase(); }
  function load() { annotations = (who && store.get(key())) || {}; }
  function save() { if (who && !store.set(key(), annotations)) $("status").textContent =
    "Stockage du navigateur indisponible : exportez souvent."; }

  const tradesBox = $("trades");
  GROUPS.forEach((g) => {
    const fs = document.createElement("div");
    const h = document.createElement("div"); h.className = "hint"; h.textContent = g.label; fs.appendChild(h);
    const box = document.createElement("div"); box.className = "checks";
    g.trades.forEach((t) => {
      const l = document.createElement("label");
      const c = document.createElement("input"); c.type = "checkbox"; c.value = t.code; c.name = "trade";
      l.appendChild(c); l.appendChild(document.createTextNode(t.fr + " / " + t.de));
      box.appendChild(l);
    });
    fs.appendChild(box); tradesBox.appendChild(fs);
  });

  function applyFilter() {
    const f = $("filter").value;
    order = ITEMS.map((_, i) => i).filter((i) => {
      const it = ITEMS[i], done = !!annotations[it.id];
      return f === "all" || (f === "todo" && !done) || (f === "done" && done) || it.lang === f;
    });
    if (!order.length) order = ITEMS.map((_, i) => i);
    pos = Math.min(pos, order.length - 1);
  }

  function render() {
    const it = ITEMS[order[pos]];
    const n = Object.keys(annotations).length;
    $("progress").textContent = n + " / " + ITEMS.length + " annotées";
    $("progress").className = "pill " + (n === ITEMS.length ? "done" : "todo");
    $("pubtitle").textContent = (pos + 1) + " / " + order.length + " — " + it.id;
    $("pubmeta").textContent = [it.lang && it.lang.toUpperCase(), it.order_type, it.publication_date]
      .filter(Boolean).join(" · ");
    $("publink").href = it.source_url || "#";
    $("text").textContent = it.text;
    const a = (annotations[it.id] || {}).gold || {};
    $("doc_type").value = a.doc_type || it.doc_type_indicatif || "adjudication";
    $("rc_subtype").value = a.rc_subtype || "";
    $("date_evenement").value = a.date_evenement || "";
    $("date_debut_travaux").value = a.date_debut_travaux || "";
    $("rcbox").style.display = $("doc_type").value === "registre_commerce" ? "" : "none";
    $("company_name").value = a.company_name || "";
    $("uid").value = a.uid || "";
    $("commune").value = a.commune || "";
    $("amount_chf").value = a.amount_chf == null ? "" : a.amount_chf;
    document.querySelectorAll("input[name=trade]").forEach((c) => { c.checked = (a.trades || []).includes(c.value); });
    $("private_person").checked = !!a.private_person;
    document.querySelectorAll("input[name=besoin]").forEach((r) => { r.checked = r.value === a.besoin_temporaire; });
    $("commentaire").value = a.commentaire || "";
    $("status").textContent = annotations[it.id] ? "déjà annotée (" + annotations[it.id].annotated_at + ")" : "";
  }

  function current() {
    const val = (id) => $(id).value.trim();
    const besoin = document.querySelector("input[name=besoin]:checked");
    const amount = val("amount_chf");
    return {
      doc_type: $("doc_type").value, company_name: val("company_name") || null, uid: val("uid") || null,
      commune: val("commune") || null, amount_chf: amount === "" ? null : Number(amount),
      rc_subtype: $("doc_type").value === "registre_commerce" ? (val("rc_subtype") || null) : null,
      date_evenement: val("date_evenement") || null, date_debut_travaux: val("date_debut_travaux") || null,
      trades: [...document.querySelectorAll("input[name=trade]:checked")].map((c) => c.value).sort(),
      private_person: $("private_person").checked, besoin_temporaire: besoin ? besoin.value : null,
      commentaire: val("commentaire") || null,
    };
  }

  $("form").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!who.trim()) { $("who").focus(); $("status").textContent = "Saisissez d'abord votre prénom."; return; }
    const g = current();
    if (!g.besoin_temporaire) { $("status").textContent = "Choisissez oui / non / incertain pour le besoin."; return; }
    const it = ITEMS[order[pos]];
    annotations[it.id] = { id: it.id, lang: it.lang, annotateur: who.trim(),
                           annotated_at: new Date().toISOString(), gold: g };
    save();
    if (pos < order.length - 1) pos += 1;
    render();
  });
  $("doc_type").addEventListener("change", () => {
    $("rcbox").style.display = $("doc_type").value === "registre_commerce" ? "" : "none"; });
  $("prev").addEventListener("click", () => { if (pos > 0) { pos -= 1; render(); } });
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); $("form").requestSubmit(); }
  });
  $("who").value = who;
  $("who").addEventListener("change", () => {
    who = $("who").value; store.set("proxsis-annot-v2:who", who); load(); applyFilter(); render();
  });
  $("filter").addEventListener("change", () => { pos = 0; applyFilter(); render(); });
  $("export").addEventListener("click", () => {
    if (!who.trim()) { $("who").focus(); return; }
    const lines = ITEMS.filter((it) => annotations[it.id]).map((it) => JSON.stringify(annotations[it.id]));
    const blob = new Blob([lines.join("\n") + "\n"], { type: "application/x-ndjson" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "annotations_" + who.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-") + "_" +
      new Date().toISOString().slice(0, 10) + ".jsonl";
    a.click(); URL.revokeObjectURL(a.href);
  });
  $("import").addEventListener("change", async (e) => {
    const f = e.target.files[0]; if (!f) return;
    const known = new Set(ITEMS.map((it) => it.id));
    let n = 0;
    for (const line of (await f.text()).split("\n")) {
      if (!line.trim()) continue;
      try { const r = JSON.parse(line);
        if (!who && r.annotateur) { who = r.annotateur; $("who").value = who; load(); }
        // audit m8: never load someone else's work into this session (blind double annotation)
        if (known.has(r.id) && r.gold && (r.annotateur || "").trim().toLowerCase() === who.trim().toLowerCase()) {
          annotations[r.id] = r; n += 1; } } catch (err) { /* ignore */ }
    }
    save(); applyFilter(); render(); $("status").textContent = n + " annotations reprises.";
  });
  load(); applyFilter(); render();
})();
</script>
</body>
</html>
"""
