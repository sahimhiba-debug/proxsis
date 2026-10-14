"""« Préparer l'appel » — a call guide and an e-mail in French or German where every claim cites its source.

Facts are numbered: real (simap.ch), estimation (Proxsis method, linked to « Ce qu'on a mesuré »), house
arguments (only those verified on Flexsis' public pages, docs/recherche/flexsis_offre.md § 3) and fictional
(demo candidates). The guide is a deterministic template. The e-mail may be rewritten by Apertus when the
``PUBLICAI_API_KEY`` variable is present at export time; the rewrite is checked sentence by sentence
(``validate``): known source ids only, no number that is not in the cited facts, no unsourced claim (questions
and a closed list of short courtesy formulas excepted), no promise word (« garantir », « livrer », « disponible »,
« premier »…) unless the cited fact says it; the subject is checked too (``validate_email``). Any failure falls
back to the template, and the reason is shown.

Audit of week 2 (M2, M3): the arguments published for the Lausanne Bâtiment agency only stay out of the Valais
guide until they are confirmed internally; the estimated need gives the probable trades and the period, to be
confirmed, and never a number of people (no measured reliability for headcounts); the subject is neutral.

Design critique, round 1 (07.10.2026): the e-mail is the only text that leaves the application, so it carries the
published facts and a question, never the estimate nor the name of the tool, and ends with slots for the consultant's
name and agency. Each fact names its source and its scope in both languages (no French on a German page).
"""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any

from proxsis.llm.base import LLMProvider
from proxsis.taxonomy import TRADES
from proxsis.values import optional_text

TEMPLATE_NAME = "modèle de texte (faux fournisseur)"
PHASE_LABELS = {
    "gros_oeuvre": ("gros œuvre", "Rohbau"), "electricite": ("électricité", "Elektro"),
    "cvc": ("chauffage-ventilation", "HLK"), "sanitaire": ("sanitaire", "Sanitär"),
    "enveloppe": ("enveloppe", "Gebäudehülle"), "amenagement_int": ("aménagements intérieurs", "Innenausbau"),
    "finitions": ("finitions", "Endarbeiten"), "terrassement": ("terrassement", "Erdarbeiten"),
    "preparatoire": ("travaux préparatoires", "Vorbereitungsarbeiten"), "transport": ("ascenseurs", "Aufzüge"),
    "equipement": ("équipements", "Betriebseinrichtungen"), "exterieur": ("aménagements extérieurs", "Umgebung"),
    "genie_civil": ("génie civil", "Tiefbau"),
}

# Verified house arguments (docs/recherche/flexsis_offre.md § 3, read on 2026-10-05). « portee » says where the
# fact was published: three of them describe one agency (Lausanne Bâtiment) and must be confirmed for Valais.
HOUSE_ARGUMENTS: list[dict[str, Any]] = [
    {"code": "try_hire", "portee": {"fr": "réseau Flexsis", "de": "Flexsis-Netz"},
     "fr": "Try & Hire : vous évaluez la personne en mission, sans frais supplémentaires si vous l'engagez "
           "définitivement.",
     "de": "Try & Hire: umfassender Einblick in Fach- und Sozialkompetenz der Person; keine Zusatzkosten bei "
           "definitiver Anstellung.",
     "sources": ["https://www.flexsis.ch/entreprise/", "https://www.flexsis.ch/de/unternehmen/"]},
    {"code": "securite", "portee": {"fr": "réseau Flexsis", "de": "Flexsis-Netz"},
     "fr": "Sécurité : Flexsis a adhéré à la charte de sécurité SUVA et fournit les équipements de protection "
           "individuelle.",
     "de": "Sicherheit: Flexsis hält sich an die SUVA-Sicherheitscharta und stellt eine persönliche "
           "Schutzausrüstung zur Verfügung.",
     "sources": ["https://www.flexsis.ch/secteurs-activites/construction/",
                 "https://www.flexsis.ch/de/branchen/bauwesen-handwerk/"]},
    {"code": "journee_test", "portee": {"fr": "agence Lausanne Bâtiment (à confirmer pour le Valais)",
                                     "de": "Filiale Lausanne Bâtiment (für das Wallis zu bestätigen)"},
     "fr": "Notre agence Lausanne Bâtiment peut organiser une première journée test ; si elle n'est pas "
           "concluante, elle n'est pas facturée.",
     "de": "Unsere Filiale Lausanne Bâtiment kann einen ersten Testtag organisieren; bleibt er ohne Ergebnis, "
           "wird er nicht in Rechnung gestellt.",
     "sources": ["https://www.flexsis.ch/un-accueil-chaleureux-une-equipe-investie-et-une-vraie-connaissance-du-"
                 "terrain-autant-delements-qui-definissent-lagence-flexsis-lausanne-batiment/",
                 "https://www.flexsis.ch/de/flexsis-lausanne-batiment-eine-agentur-die-fest-in-der-praxis-"
                 "verwurzelt-ist/"]},
    {"code": "suivi_administratif", "portee": {"fr": "agence Lausanne Bâtiment (à confirmer pour le Valais)",
                                            "de": "Filiale Lausanne Bâtiment (für das Wallis zu bestätigen)"},
     "fr": "Pour les collaborateurs venus de l'étranger, notre agence Lausanne Bâtiment aide pour les permis de "
           "travail et les allocations familiales.",
     "de": "Für Mitarbeitende aus dem Ausland unterstützt unsere Filiale Lausanne Bâtiment bei "
           "Arbeitsgenehmigungen und Kindergeld.",
     "sources": ["https://www.flexsis.ch/un-accueil-chaleureux-une-equipe-investie-et-une-vraie-connaissance-du-"
                 "terrain-autant-delements-qui-definissent-lagence-flexsis-lausanne-batiment/"]},
    {"code": "agences_valais",
     "portee": {"fr": "réseau Flexsis (liste des agences sur flexsis.ch, consultée le 05.10.2026)",
                "de": "Flexsis-Netz (Filialliste auf flexsis.ch, abgerufen am 05.10.2026)"},
     "fr": "Flexsis a trois agences en Valais : Martigny, Sion et Monthey.",
     "de": "Flexsis hat drei Filialen im Wallis: Martigny, Sitten und Monthey.",
     "sources": ["https://www.flexsis.ch/agences-de-placement/"]},
]

# Courtesy formulas: a CLOSED list of short phrases (whole phrase, not a prefix: « Merci de nous faire confiance :
# nous garantissons… » is not a formula).
_FORMULAS = {"bonjour", "madame, monsieur", "madame, monsieur,", "meilleures salutations", "meilleures salutations,",
             "cordialement", "cordialement,", "merci", "merci beaucoup", "merci d'avance", "guten tag",
             "sehr geehrte damen und herren", "sehr geehrte damen und herren,", "freundliche grüsse",
             "freundliche grüsse,", "mit freundlichen grüssen", "mit freundlichen grüssen,", "danke", "vielen dank"}
# Promise words: allowed only when the cited fact itself says it (audit M2).
_PROMISES = re.compile(r"garanti|livr|disponib|premier|première|leader|gratuit|meilleur|sans frais|immédiat|"
                       r"dès demain|garantier|liefer|verfügbar|erste[rns]?\b|führend|kostenlos|gratis|"
                       r"beste[rns]?\b|sofort|ab morgen", re.I)
# Arguments published for one agency outside Valais: to be confirmed internally before use (flexsis_offre.md § 3).
VALAIS_HOUSE_ARGUMENTS = [a for a in HOUSE_ARGUMENTS if "Lausanne" not in a["portee"]["fr"]]
# The house arguments the guide and the e-mail say; a source is listed only when a sentence cites it.
CITED_HOUSE_ARGUMENTS = ("try_hire", "securite")
# A line made of slots only (the consultant's name, « Flexsis [agency] »): to fill in, not a claim.
_SLOTS_ONLY = re.compile(r"^(Flexsis )?\[[^\]]+\]$")
_NUMBER = re.compile(r"\d+(?:[.,']\d+)*")


def _d(s: str) -> str:
    return date.fromisoformat(s).strftime("%d.%m.%Y")


def _chf(x: float) -> str:
    return f"{x:,.0f}".replace(",", "'")


def facts_for(company: dict[str, Any], proposals: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []

    def add(kind: str, fr: str, de: str, url: str, source: str | dict[str, str], **extra: Any) -> None:
        both = source if isinstance(source, dict) else {"fr": source, "de": source}
        facts.append({"id": len(facts) + 1, "type": kind, "fr": fr, "de": de, "url": url, "source": both} | extra)

    src = (company.get("sources") or [None])[0]
    if src:
        amount = src.get("montant_chf")
        fr_amt = f" (montant publié : CHF {_chf(amount)})" if amount else ""
        de_amt = f" (publizierter Betrag: CHF {_chf(amount)})" if amount else ""
        # a masked or missing authority is left out of the sentence, never written as « nan » or « None »
        who = optional_text(src.get("adjudicateur"))
        fr_who, de_who = (f" attribué par {who}", f" durch {who}") if who else ("", "")
        add("reel", f"Marché « {src['titre']} »{fr_who}, publié le {_d(src['date'])} sur simap.ch{fr_amt}.",
            f"Zuschlag «{src['titre']}»{de_who}, publiziert am {_d(src['date'])} auf simap.ch{de_amt}.",
            src["url_simap"], "simap.ch", code="adjudication")
    n = int(company.get("n_52s") or 0)
    if n:
        # a total leads to the dated contracts of the dossier, not to one of them
        add("reel", f"{n} marchés publics gagnés dans la spécialité en 52 semaines (simap.ch).",
            f"{n} öffentliche Aufträge im Fachbereich in 52 Wochen gewonnen (simap.ch).",
            f"app:/entreprise/{company['id']}#fx-timeline", "simap.ch", code="frequence")
    need = company.get("besoin") or []
    if need:
        # trades and period only: a headcount has no measured reliability (audit M3, CLAIMS BESOIN-1)
        first = min(r["semaine"] for r in need)
        trades = sorted({r["metier"] for r in need})
        fr_tr = ", ".join(TRADES[t].label_fr.lower() for t in trades)
        de_tr = ", ".join(TRADES[t].label_de for t in trades)
        add("estimation",
            f"Métiers probables : {fr_tr}, à partir de la semaine du {_d(first)} ; nombre de personnes non estimé "
            "(à confirmer avec l'entreprise).",
            f"Wahrscheinliche Berufe: {de_tr}, ab der Woche vom {_d(first)}; Anzahl Personen nicht geschätzt "
            "(mit dem Unternehmen zu prüfen).",
            "app:/mesures#BESOIN-1",
            {"fr": "Proxsis (lots publiés et phasage mesuré sur simap, hypothèses déclarées)",
             "de": "Proxsis (publizierte Lose und auf simap gemessene Phasenfolge, offengelegte Annahmen)"},
            code="besoin")
    lots = company.get("lots_attendus") or []
    if lots:
        p10 = min(x["date_p10"] for x in lots)
        p90 = max(x["date_p90"] for x in lots)
        fr_ph = ", ".join(PHASE_LABELS.get(x["phase"], (x["phase"], x["phase"]))[0] for x in lots)
        de_ph = ", ".join(PHASE_LABELS.get(x["phase"], (x["phase"], x["phase"]))[1] for x in lots)
        add("estimation", f"Lots encore attendus sur ce chantier selon le phasage mesuré : {fr_ph} (entre le "
                          f"{_d(p10)} et le {_d(p90)}).",
            f"Laut gemessener Phasenfolge noch erwartete Lose: {de_ph} (zwischen {_d(p10)} und {_d(p90)}).",
            "app:/mesures#PHAS-2",
            {"fr": "Proxsis (phasage mesuré sur simap)", "de": "Proxsis (auf simap gemessene Phasenfolge)"},
            code="lots")
    for a in VALAIS_HOUSE_ARGUMENTS:
        if a["code"] in CITED_HOUSE_ARGUMENTS:
            add("maison", a["fr"], a["de"], a["sources"][0], "flexsis.ch", portee=a["portee"], code=a["code"])
    if proposals and proposals.get("n_proposes"):
        t = TRADES[proposals["metier"]]
        add("fictif", f"{proposals['n_proposes']} profils de {t.label_fr.lower()} proposés par Proxsis (fictifs, pour "
                      "la démonstration).",
            f"{proposals['n_proposes']} Profile ({t.label_de}) von Proxsis vorgeschlagen (fiktiv, für die Demo).",
            f"app:/entreprise/{company['id']}/candidats",
            {"fr": "Proxsis (candidats fictifs)", "de": "Proxsis (fiktive Kandidaten)"}, code="candidats")
    return facts


def _fid(facts: list[dict[str, Any]], kind: str, code: str | None = None, contains: str = "") -> list[int]:
    for f in facts:
        if f["type"] == kind and (code is None or f.get("code") == code) and contains in f["fr"]:
            return [f["id"]]
    return []


# Stable codes of the guide's sections, in the order of the call: the screen styles each part by its code (opening and
# question in front, the estimate marked as a hypothesis), never by its translated title.
GUIDE_SECTIONS = ("ouverture", "pourquoi", "estimation", "questions", "apport", "proposition", "suite")


def _guide(company: dict[str, Any], facts: list[dict[str, Any]], lang: str) -> list[dict[str, Any]]:
    fr = lang == "fr"
    by = {f["id"]: f for f in facts}

    def say(ids: list[int]) -> dict[str, Any]:
        return {"texte": " ".join(by[i][lang] for i in ids), "sources": ids}

    award, freq = _fid(facts, "reel", "adjudication"), _fid(facts, "reel", "frequence")
    need, lots = _fid(facts, "estimation", "besoin"), _fid(facts, "estimation", "lots")
    sections: list[dict[str, Any]] = [
        {"code": "ouverture", "titre": "Ouverture" if fr else "Einstieg", "phrases": [
            {"texte": ("Bonjour, je suis [votre nom], de l'agence Flexsis de [votre agence]." if fr else
                       "Guten Tag, hier ist [Ihr Name] von der Flexsis-Filiale [Ihre Filiale]."), "sources": []}]},
        {"code": "pourquoi", "titre": "Pourquoi j'appelle" if fr else "Warum ich anrufe",
         "phrases": [say(x) for x in (award, freq) if x]},
        {"code": "estimation",
         "titre": "Notre estimation, à confirmer" if fr else "Unsere Schätzung, zu prüfen",
         "phrases": [say(x) for x in (need, lots) if x]},
        {"code": "questions", "titre": "Questions à poser" if fr else "Fragen", "phrases": [
            {"texte": t, "sources": []} for t in (
                ["Quand le chantier démarre-t-il ?", "De quels métiers aurez-vous besoin, et combien de personnes ?",
                 "Travaillez-vous déjà avec une agence pour ce chantier ?"] if fr else
                ["Wann beginnt die Baustelle?", "Welche Berufe brauchen Sie, und wie viele Personen?",
                 "Arbeiten Sie für diese Baustelle bereits mit einer Agentur?"])]},
        {"code": "apport", "titre": "Ce que Flexsis apporte" if fr else "Was Flexsis bietet",
         "phrases": [say(_fid(facts, "maison", c)) for c in CITED_HOUSE_ARGUMENTS if _fid(facts, "maison", c)]},
        {"code": "proposition", "titre": "Ce que je peux proposer" if fr else "Was ich anbieten kann",
         "phrases": [say(x) for x in (_fid(facts, "fictif"),) if x]},
        {"code": "suite", "titre": "Prochaine étape" if fr else "Nächster Schritt", "phrases": [
            {"texte": "Puis-je passer vous voir cette semaine ?" if fr else "Darf ich Sie diese Woche besuchen?",
             "sources": []}]},
    ]
    return [s for s in sections if s["phrases"]]


def _email(company: dict[str, Any], facts: list[dict[str, Any]], lang: str) -> dict[str, Any]:
    """What a consultant would write himself: the published award, Flexsis's published arguments, two questions, his
    signature to fill in. The estimate stays in the application (it is a hypothesis, not something to tell a client),
    and so does the name of the tool."""
    fr = lang == "fr"
    src = (company.get("sources") or [{}])[0]
    title = _cut(str(src.get("titre", "")).strip(), 60)
    award = _fid(facts, "reel", "adjudication")
    phrases: list[dict[str, Any]] = [{"texte": "Madame, Monsieur," if fr else "Sehr geehrte Damen und Herren",
                                      "sources": []}]
    if award and src.get("date"):
        full = _cut(str(src.get("titre", "")).strip(), 90)
        phrases.append({"texte": (f"Félicitations pour le marché « {full} », publié sur simap.ch le {_d(src['date'])}."
                                  if fr else
                                  f"Herzliche Gratulation zum Zuschlag «{full}», publiziert auf simap.ch am "
                                  f"{_d(src['date'])}."), "sources": award})
    phrases.append({"texte": "Aurez-vous besoin de renfort sur ce chantier ces prochaines semaines ?" if fr else
                    "Brauchen Sie auf dieser Baustelle in den nächsten Wochen Verstärkung?", "sources": []})
    for code in CITED_HOUSE_ARGUMENTS:
        ids = _fid(facts, "maison", code)
        if ids:
            phrases.append({"texte": facts[ids[0] - 1][lang], "sources": ids})
    phrases += [{"texte": "Seriez-vous disponible pour un court échange cette semaine ?" if fr else
                 "Hätten Sie diese Woche Zeit für ein kurzes Gespräch?", "sources": []},
                {"texte": "Meilleures salutations," if fr else "Freundliche Grüsse", "sources": []},
                {"texte": "[votre nom]" if fr else "[Ihr Name]", "sources": []},
                {"texte": "Flexsis [votre agence]" if fr else "Flexsis [Ihre Filiale]", "sources": []}]
    # neutral subject (audit M2): the published title, cut between two words, and a question; no promise
    if title:
        subject = (f"Votre marché « {title} » : un échange sur vos besoins en personnel ?" if fr else
                   f"Ihr Auftrag «{title}»: ein Gespräch über Ihren Personalbedarf?")
    else:
        subject = "Un échange sur vos besoins en personnel ?" if fr else "Ein Gespräch über Ihren Personalbedarf?"
    return {"objet": subject, "objet_sources": award, "phrases": phrases}


def _cut(text: str, limit: int) -> str:
    """At most ``limit`` characters, cut between two words, with « … » when something was cut."""
    if len(text) <= limit:
        return text
    head = text[:limit + 1].rsplit(" ", 1)[0].rstrip(" ,;:-–/")
    return f"{head}…"


def validate(phrases: list[dict[str, Any]], facts: list[dict[str, Any]], lang: str) -> tuple[bool, str]:
    known = {f["id"]: f for f in facts}
    if not phrases:
        return False, "texte vide"
    for p in phrases:
        text, ids = str(p.get("texte", "")).strip(), list(p.get("sources") or [])
        unknown = [i for i in ids if i not in known]
        if unknown:
            return False, f"source inconnue {unknown} dans « {text[:60]} »"
        allowed = set()
        for i in ids:
            allowed |= set(_NUMBER.findall(known[i]["fr"])) | set(_NUMBER.findall(known[i]["de"]))
        extra = [x for x in _NUMBER.findall(text) if x not in allowed]
        if extra:
            return False, f"chiffre sans source {extra} dans « {text[:60]} »"
        if not ids and (text.lower() in _FORMULAS or _SLOTS_ONLY.match(text)):
            continue
        if not ids and not text.endswith("?"):
            return False, f"affirmation sans source : « {text[:60]} »"
        cited = " ".join(known[i][lang] for i in ids)
        promises = [m.group(0) for m in _PROMISES.finditer(text) if m.group(0).lower() not in cited.lower()]
        if promises and not (not ids and text.endswith("?") and _is_plain_question(text)):
            return False, f"promesse sans source {promises} dans « {text[:60]} »"
    return True, ""


def _is_plain_question(text: str) -> bool:
    """A question to the client about him (« Seriez-vous disponible… ? »), not a claim about us in question form."""
    return re.match(r"^(seriez|êtes|avez|pourriez|auriez|wären|sind|haben|hätten|könnten)\b", text.strip(),
                    re.I) is not None


def validate_email(email: dict[str, Any], facts: list[dict[str, Any]], lang: str) -> tuple[bool, str]:
    """The phrases AND the subject: the subject is checked as a phrase citing the award it names."""
    text = str(email.get("objet", ""))
    if not text.strip():
        return False, "objet vide"
    ok, why = validate([{"texte": text, "sources": list(email.get("objet_sources") or [])}], facts, lang)
    if not ok:
        return False, f"objet : {why}"
    return validate(list(email.get("phrases") or []), facts, lang)


SCHEMA = {"type": "object", "additionalProperties": False, "required": ["phrases"],
          "properties": {"phrases": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["texte", "sources"],
              "properties": {"texte": {"type": "string"},
                             "sources": {"type": "array", "items": {"type": "integer"}}}}}}}


def _system(lang: str) -> str:
    if lang == "fr":
        return ("Tu rédiges un court e-mail commercial d'une agence de placement à une entreprise de construction. "
                "Utilise UNIQUEMENT les faits fournis, cite leurs numéros dans « sources », n'ajoute aucun chiffre, "
                "aucune promesse ni aucun fait. Les questions et les formules de politesse n'ont pas de source. "
                "Réponds en français, en JSON.")
    return ("Du schreibst eine kurze Geschäfts-E-Mail einer Personalagentur an ein Bauunternehmen. Verwende NUR die "
            "gelieferten Fakten, nenne ihre Nummern in « sources », füge keine Zahl, kein Versprechen und keine "
            "Tatsache hinzu. Fragen und Höflichkeitsformeln haben keine Quelle. Antworte auf Deutsch, als JSON.")


def build_call_prep(company: dict[str, Any], proposals: dict[str, Any] | None,
                    provider: LLMProvider | None = None) -> dict[str, Any]:
    facts = facts_for(company, proposals)
    out: dict[str, Any] = {"entreprise": company["id"], "faits": facts}
    for lang in ("fr", "de"):
        out[lang] = {"guide": _guide(company, facts, lang), "email": _email(company, facts, lang)}
    out["redaction"] = {"type": "modele", "fournisseur": TEMPLATE_NAME,
                        "note": "texte déterministe, chaque affirmation citée"}
    if provider is None or provider.name == "fake":
        return out
    rewritten: dict[str, list[dict[str, Any]]] = {}
    reasons: list[str] = []
    for lang in ("fr", "de"):
        user = json.dumps({"faits": [{"id": f["id"], "texte": f[lang]} for f in facts],
                           "brouillon": out[lang]["email"]["phrases"]}, ensure_ascii=False)
        try:
            res = provider.extract(_system(lang), user, SCHEMA, "redaction_email")
            phrases = res.data.get("phrases") or []
        except Exception as exc:  # network, quota, malformed JSON: the template stays
            phrases, reasons = [], [*reasons, f"{lang} : erreur du fournisseur ({type(exc).__name__})"]
            continue
        ok, why = validate_email({**out[lang]["email"], "phrases": phrases}, facts, lang)
        if ok:
            rewritten[lang] = phrases
        else:
            reasons.append(f"{lang} : {why}")
    if len(rewritten) == 2:
        for lang in ("fr", "de"):
            out[lang]["email"]["phrases"] = rewritten[lang]
        out["redaction"] = {"type": "apertus", "fournisseur": f"Apertus ({provider.model})",
                            "note": "e-mail reformulé par Apertus, contrôlé phrase par phrase contre les sources"}
    else:
        out["redaction"]["note"] = ("texte d'Apertus rejeté par le contrôle des sources (" + " ; ".join(reasons)
                                    + ") : modèle de texte utilisé")
    return out
