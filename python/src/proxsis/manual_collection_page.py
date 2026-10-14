"""HTML of the local collection page (served by ``proxsis collecte-manuelle`` on 127.0.0.1 only).

The pasted text stays in the browser until « Enregistrer »; it is never put in
browser storage. Saving sends it to the local server, which filters it before
writing (proxsis.manual_collection.save).
"""

from __future__ import annotations

import json
from datetime import date


def build_collection_page(token: str, sources: dict[str, str], rubrics: dict[str, dict[str, str]],
                          period: tuple[date, date], quotas: dict[str, int]) -> str:
    cfg = {"token": token, "sources": sources, "rubrics": rubrics, "period": [str(period[0]), str(period[1])],
           "quotas": quotas}
    return _PAGE.replace("__CFG__", json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/"))


_PAGE = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Collecte manuelle</title>
<style>
:root { --bg:#f7f7f5; --panel:#fff; --ink:#1c1c1a; --muted:#5f5f5a; --line:#deded8; --accent:#1f5f8b;
        --accent-ink:#fff; --ok:#2e7d4f; --bad:#a3271f; --mask:#f6e3a1; --focus:#f2b632; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#161615; --panel:#20201e; --ink:#ecece6; --muted:#a5a59c; --line:#3a3a36; --accent:#6fb3e0;
          --accent-ink:#0d1b24; --ok:#6cc28f; --bad:#ef8a80; --mask:#6b5a1e; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
header { padding:12px 16px; background:var(--panel); border-bottom:1px solid var(--line); }
header h1 { margin:0; font-size:17px; }
.hint { color:var(--muted); font-size:13px; }
main { max-width:1100px; margin:0 auto; padding:16px; display:grid; gap:16px; grid-template-columns:minmax(0,1.4fr) minmax(0,1fr); }
@media (max-width:860px) { main { grid-template-columns:1fr; } }
section { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px; min-width:0; }
label { display:block; font-weight:600; margin:10px 0 4px; }
input, select, textarea { width:100%; padding:7px 9px; border:1px solid var(--line); border-radius:6px;
  background:var(--bg); color:var(--ink); font:inherit; }
textarea { min-height:220px; }
.row { display:grid; grid-template-columns:repeat(auto-fit, minmax(150px,1fr)); gap:0 12px; }
button { font:inherit; padding:7px 12px; border-radius:6px; border:1px solid var(--line); background:var(--panel);
  color:var(--ink); cursor:pointer; }
button.primary { background:var(--accent); color:var(--accent-ink); border-color:var(--accent); }
button:disabled { opacity:.5; cursor:not-allowed; }
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible { outline:3px solid var(--focus); outline-offset:1px; }
.actions { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
#apercu { white-space:pre-wrap; overflow-wrap:anywhere; font-size:14px; min-height:60px; }
mark { background:var(--mask); color:inherit; padding:0 2px; border-radius:3px; }
.msg { margin-top:10px; font-size:14px; }
.ok { color:var(--ok); } .bad { color:var(--bad); }
.drop { margin-top:12px; padding:12px; border:2px dashed var(--line); border-radius:8px; font-size:14px; }
.drop.over { border-color:var(--accent); background:var(--bg); }
table { width:100%; border-collapse:collapse; font-size:14px; font-variant-numeric:tabular-nums; }
td, th { text-align:left; padding:4px 6px; border-bottom:1px solid var(--line); }
</style>
</head>
<body>
<header>
  <h1>Collecte manuelle — jeu de test réel (BO VS, FOSC)</h1>
  <div class="hint">Lisez la consigne (docs/annotation/consigne_collecte_manuelle.md). Vous consultez le portail
    vous-même ; cette page ne visite aucun site. Les noms de particuliers sont masqués <strong>avant</strong>
    l'enregistrement ; seul votre poste garde le texte (dossier exclu de git).</div>
</header>
<main>
  <section>
    <div class="row">
      <div><label for="collecteur">Vos initiales</label><input id="collecteur" maxlength="4" autocomplete="off"></div>
      <div><label for="source">Source</label><select id="source"></select></div>
      <div><label for="rubrique">Rubrique</label><select id="rubrique"></select></div>
    </div>
    <div class="row">
      <div><label for="lang">Langue du texte</label><select id="lang"><option value="fr">français</option>
        <option value="de">allemand</option></select></div>
      <div><label for="date">Date de publication</label><input id="date" type="date"></div>
    </div>
    <div id="drop" class="drop" tabindex="0">
      <strong>Importer les exports XML</strong> (lien « Exporter au format XML » du portail) : glissez ici
      <strong>1 à 10 fichiers XML</strong> ou <strong>une archive ZIP</strong> qui les contient tous, ou
      <label for="xmlfile" style="display:inline;font-weight:600;cursor:pointer;text-decoration:underline">choisissez-les</label>.
      Les particuliers sont masqués d'après le fichier lui-même ; vous vérifiez, puis vous enregistrez.
      <input id="xmlfile" type="file" accept=".xml,.zip,text/xml,application/xml,application/zip" multiple hidden>
    </div>
    <label for="url">Lien de la publication (copié depuis le portail)</label>
    <input id="url" type="url" placeholder="https://amtsblattportal.ch/…">
    <label for="text">Texte de la publication (collez-le en entier)</label>
    <textarea id="text" spellcheck="false"></textarea>
    <div class="actions">
      <button id="mask" type="button" title="Sélectionnez un nom dans le texte ci-dessus, puis cliquez">Masquer la sélection</button>
      <button id="preview" type="button">Aperçu filtré</button>
      <button id="save" type="button" class="primary" disabled>Enregistrer</button>
    </div>
    <div id="msg" class="msg" role="status"></div>
  </section>
  <section>
    <h2 style="font-size:15px;margin:0 0 6px">Aperçu de ce qui sera enregistré</h2>
    <div class="hint">Vérifiez qu'aucun nom de particulier ne reste visible. Sinon : sélectionnez-le à gauche,
      « Masquer la sélection », puis « Aperçu filtré ». Les noms d'entreprises restent.</div>
    <div id="apercu" class="hint" style="margin-top:8px">—</div>
    <h2 style="font-size:15px;margin:16px 0 6px">Avancement de l'équipe (sur ce poste)</h2>
    <table><thead><tr><th>Strate</th><th>Collectées</th><th>Objectif</th></tr></thead><tbody id="etat"></tbody></table>
    <div id="periode" class="hint" style="margin-top:6px"></div>
  </section>
</main>
<section id="lot" hidden style="max-width:1100px;margin:0 auto 24px;">
  <h2 style="font-size:15px;margin:0 0 6px">Lot importé — vérifiez chaque texte filtré, puis enregistrez</h2>
  <div class="hint">Ouvrez « voir le texte filtré » pour chaque publication : aucun nom de particulier ne doit rester.
    Une publication refusée (doublon, date hors période, rubrique exclue…) n'est pas enregistrée.</div>
  <div id="lotresume" class="hint" style="margin-top:6px"></div>
  <table style="margin-top:8px"><thead><tr><th>Fichier</th><th>Publication</th><th>Date</th><th>Langue</th>
    <th>Masqués</th><th>Jour tiré</th><th>État</th></tr></thead><tbody id="lotrows"></tbody></table>
  <div class="actions"><button id="savelot" type="button" class="primary">Enregistrer les publications prêtes</button>
    <button id="droplate" type="button">Écarter les publications hors des jours tirés</button>
    <button id="clearlot" type="button">Vider le lot</button></div>
</section>
<script id="cfg" type="application/json">__CFG__</script>
<script>
(function () {
  "use strict";
  const CFG = JSON.parse(document.getElementById("cfg").textContent);
  const $ = (id) => document.getElementById(id);
  let previewed = null;
  const opt = (sel, value, label) => { const o = document.createElement("option"); o.value = value; o.textContent = label; sel.appendChild(o); };
  Object.entries(CFG.sources).forEach(([k, v]) => opt($("source"), k, v));
  function fillRubrics() { $("rubrique").innerHTML = ""; Object.entries(CFG.rubrics[$("source").value]).forEach(([k, v]) => opt($("rubrique"), k, k + " — " + v)); }
  $("source").addEventListener("change", () => { fillRubrics(); invalidate(); });
  fillRubrics();
  $("date").min = CFG.period[0]; $("date").max = CFG.period[1];
  $("periode").textContent = "Période : du " + CFG.period[0] + " au " + CFG.period[1] + ".";
  try { $("collecteur").value = localStorage.getItem("proxsis-collecteur") || ""; } catch (e) { /* ignore */ }
  $("collecteur").addEventListener("change", () => { try { localStorage.setItem("proxsis-collecteur", $("collecteur").value); } catch (e) { /* ignore */ } });

  function payload() {
    return { text: $("text").value, url: $("url").value.trim(), date: $("date").value, lang: $("lang").value,
             source: $("source").value, rubrique: $("rubrique").value, collecteur: $("collecteur").value.trim(),
             masquages_import: importMasks };
  }
  function invalidate() { previewed = null; $("save").disabled = true; }
  ["text", "url", "date", "lang", "rubrique", "collecteur"].forEach((id) => $(id).addEventListener("input", () => { importMasks = 0; invalidate(); }));
  async function call(path, body) {
    const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json", "X-Jeton": CFG.token },
                                  body: JSON.stringify(body) });
    const data = await r.json();
    if (!r.ok) throw new Error(data.erreur || ("erreur " + r.status));
    return data;
  }
  function show(msg, ok) { $("msg").textContent = msg; $("msg").className = "msg " + (ok ? "ok" : "bad"); }
  function renderPreview(t) {
    const box = $("apercu"); box.className = ""; box.textContent = "";
    t.split(/(\[masqué\]|\[particulier\])/).forEach((part) => {
      if (part === "[masqué]" || part === "[particulier]") { const m = document.createElement("mark"); m.textContent = part; box.appendChild(m); }
      else box.appendChild(document.createTextNode(part));
    });
  }
  $("mask").addEventListener("click", () => {
    const t = $("text"), a = t.selectionStart, b = t.selectionEnd;
    if (a === b) { show("Sélectionnez d'abord le nom à masquer dans le texte.", false); return; }
    t.value = t.value.slice(0, a) + "[masqué]" + t.value.slice(b); invalidate(); show("Masqué. Refaites l'aperçu.", true);
  });
  let importMasks = 0;
  async function doPreview() {
    try { const r = await call("/api/apercu", payload()); previewed = JSON.stringify(payload()); renderPreview(r.texte_filtre);
          $("save").disabled = false;
          show((r.masquages + importMasks) + " élément(s) masqué(s). Vérifiez l'aperçu, puis enregistrez.", true); }
    catch (e) { invalidate(); show(e.message, false); }
  }
  $("preview").addEventListener("click", doPreview);
  $("save").addEventListener("click", async () => {
    if (previewed !== JSON.stringify(payload())) { invalidate(); show("Le texte a changé : refaites l'aperçu.", false); return; }
    try { const r = await call("/api/enregistrer", payload()); renderEtat(r.etat);
          $("text").value = ""; $("url").value = ""; invalidate(); $("apercu").textContent = "—"; importMasks = 0;
          show("Enregistrée : " + r.enregistre.id + ". Publication suivante.", true); }
    catch (e) { show(e.message, false); }
  });
  function renderEtat(st) {
    const tb = $("etat"); tb.innerHTML = "";
    Object.entries(st.par_strate).forEach(([k, v]) => { const tr = document.createElement("tr");
      [k.replace("bo_vs", "BO VS").replace("fosc", "FOSC").replace("/", " · "), v.n, v.quota].forEach((x) => {
        const td = document.createElement("td"); td.textContent = x; tr.appendChild(td); }); tb.appendChild(tr); });
  }
  async function importXml(file) {
    if (!file) return;
    try {
      const r = await call("/api/xml", { xml: await file.text() });
      $("source").value = r.source; fillRubrics(); $("rubrique").value = r.rubrique; $("lang").value = r.lang;
      $("date").value = r.date; $("url").value = r.url; $("text").value = r.text; invalidate();
      importMasks = r.masquages;
      await doPreview();
      if (previewed) show("Export " + r.numero + " lu : " + r.masquages + " élément(s) masqué(s). Vérifiez l'aperçu, "
           + "puis enregistrez. Supprimez ensuite le fichier XML téléchargé (il contient des noms).", true);
    } catch (e) { show(e.message, false); }
  }
  // ---- lots de 1 à 10 fichiers
  const MAX_LOT = 10;
  let lot = [];
  function renderLot() {
    $("lot").hidden = lot.length === 0;
    const tb = $("lotrows"); tb.innerHTML = "";
    lot.forEach((it) => {
      const tr = document.createElement("tr");
      [it.file, it.numero || "—", it.sub ? it.sub.date : "—", it.sub ? it.sub.lang : "—",
       it.sub ? String(it.sub.masquages_import + (it.extra || 0)) : "—",
       it.jour === undefined ? "—" : (it.jour ? "oui" : "NON (hors tirage)")].forEach((x) => {
        const td = document.createElement("td"); td.textContent = x; tr.appendChild(td); });
      const st = document.createElement("td");
      st.textContent = it.status; st.className = it.status === "enregistrée" || it.status === "prête" ? "ok" : (it.status === "…" ? "" : "bad");
      tr.appendChild(st); tb.appendChild(tr);
      if (it.preview) {
        const tr2 = document.createElement("tr"); const td = document.createElement("td"); td.colSpan = 7;
        const det = document.createElement("details"); const sm = document.createElement("summary");
        sm.textContent = "voir le texte filtré"; det.appendChild(sm);
        const box = document.createElement("div"); box.style.whiteSpace = "pre-wrap"; box.style.fontSize = "13px";
        it.preview.split(/(\[masqué\]|\[particulier\])/).forEach((part) => {
          if (part === "[masqué]" || part === "[particulier]") { const m = document.createElement("mark"); m.textContent = part; box.appendChild(m); }
          else box.appendChild(document.createTextNode(part)); });
        det.appendChild(box); td.appendChild(det); tr2.appendChild(td); tb.appendChild(tr2);
      }
    });
    $("savelot").disabled = !lot.some((it) => it.status === "prête");
    const c = (f) => lot.filter(f).length;
    $("lotresume").textContent = lot.length ? (c((it) => it.status === "prête") + " prête(s), "
      + c((it) => it.status === "enregistrée") + " enregistrée(s), " + c((it) => it.status.startsWith("refusée"))
      + " refusée(s), " + c((it) => it.jour === false) + " hors des jours tirés, sur " + lot.length + ".") : "";
  }
  async function importZip(file) {
    const r = await fetch("/api/zip", { method: "POST", headers: { "Content-Type": "application/zip", "X-Jeton": CFG.token },
                                        body: file });
    const data = await r.json();
    if (!r.ok) { show(data.erreur || ("erreur " + r.status), false); return; }
    lot = data.fichiers.map((f) => ({ file: f.fichier, status: f.ok ? "…" : "refusée : " + f.erreur, numero: f.numero,
      jour: f.ok ? f.jour_tire : undefined,
      sub: f.ok ? { text: f.text, url: f.url, date: f.date, lang: f.lang, source: f.source, rubrique: f.rubrique,
                    collecteur: $("collecteur").value.trim(), masquages_import: f.masquages } : null }));
    renderLot();
    for (const it of lot) {
      if (!it.sub) continue;
      try { const p = await call("/api/apercu", it.sub); it.preview = p.texte_filtre; it.extra = p.masquages; it.status = "prête"; }
      catch (e) { it.status = "refusée : " + e.message; }
    }
    renderLot();
    show(lot.filter((it) => it.status === "prête").length + " publication(s) prête(s) sur " + lot.length
         + " fichier(s). Vérifiez les textes filtrés, puis « Enregistrer les publications prêtes ». Supprimez ensuite "
         + "l'archive et les fichiers XML (ils contiennent des noms).", true);
    $("lot").scrollIntoView({ behavior: "smooth" });
  }
  async function importLot(files) {
    files = Array.from(files || []);
    if (!files.length) return;
    if (!$("collecteur").value.trim()) { show("Saisissez d'abord vos initiales.", false); $("collecteur").focus(); return; }
    const zip = files.find((f) => f.name.toLowerCase().endsWith(".zip"));
    if (zip) { await importZip(zip); return; }
    if (files.length === 1 && lot.length === 0) { importXml(files[0]); return; }
    if (files.length > MAX_LOT) { show("10 fichiers au maximum par lot : seuls les 10 premiers sont importés.", false); files = files.slice(0, MAX_LOT); }
    lot = files.map((f) => ({ file: f.name, status: "…" })); renderLot();
    for (let i = 0; i < files.length; i++) {
      const it = lot[i];
      try {
        const r = await call("/api/xml", { xml: await files[i].text() });
        it.numero = r.numero;
        it.sub = { text: r.text, url: r.url, date: r.date, lang: r.lang, source: r.source, rubrique: r.rubrique,
                   collecteur: $("collecteur").value.trim(), masquages_import: r.masquages };
        const p = await call("/api/apercu", it.sub);
        it.preview = p.texte_filtre; it.extra = p.masquages; it.status = "prête";
      } catch (e) { it.status = "refusée : " + e.message; }
      renderLot();
    }
    const ok = lot.filter((it) => it.status === "prête").length;
    show(ok + " publication(s) prête(s) sur " + lot.length + ". Vérifiez les textes filtrés, puis « Enregistrer les publications prêtes ». "
         + "Supprimez ensuite les fichiers XML téléchargés (ils contiennent des noms).", ok > 0);
    $("lot").scrollIntoView({ behavior: "smooth" });
  }
  $("savelot").addEventListener("click", async () => {
    $("savelot").disabled = true;
    for (const it of lot) {
      if (it.status !== "prête") continue;
      try { const r = await call("/api/enregistrer", it.sub); it.status = "enregistrée"; renderEtat(r.etat); }
      catch (e) { it.status = "refusée : " + e.message; }
      renderLot();
    }
    const n = lot.filter((it) => it.status === "enregistrée").length;
    show(n + " publication(s) enregistrée(s). Lot suivant : glissez les 10 fichiers suivants.", n > 0);
  });
  $("clearlot").addEventListener("click", () => { lot = []; renderLot(); });
  $("droplate").addEventListener("click", () => {
    lot.forEach((it) => { if (it.jour === false && it.status === "prête") it.status = "écartée (hors des jours tirés)"; });
    renderLot(); });
  $("xmlfile").addEventListener("change", (e) => { importLot(e.target.files); e.target.value = ""; });
  const drop = $("drop");
  ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", (e) => importLot(e.dataTransfer.files));
  fetch("/api/etat").then((r) => r.json()).then(renderEtat).catch(() => {});
})();
</script>
</body>
</html>
"""
