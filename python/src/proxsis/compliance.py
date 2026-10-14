"""Job-reporting obligation 2026 (Stellenmeldepflicht): « poste soumis ou non », countdown, ready announcement.

Sources (read on 2026-10-05/06; details in docs/recherche/conformite_cct_annonce.md § b-d):
- art. 21a LEI (RS 142.20); art. 53a-53f OSE (RS 823.111);
- ordinance of the DEFR of 27.11.2025 on the 2026 list (RS 823.111.3), in force 1.1-31.12.2026, Fedlex:
  https://www.fedlex.admin.ch/eli/cc/2025/800/fr — official act, free of copyright (art. 5 LDA). Membership is
  coded from the ORDINANCE prefixes (the SECO XLSX does not list every grouped code);
- SECO directive « LSE SPE », part B (B8, B16-B17, B33, B36), state 1.7.2025;
- CH-ISCO-19 genres (OFS, file 36037208, published 4.7.2025): « probable » codes per trade, the ORP decides.

No call to Job-Room: the consultant announces on the platform himself; this module only checks, counts and drafts.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from proxsis.taxonomy import TRADES

ORDINANCE = ("Ordonnance du DEFR du 27 novembre 2025 concernant l'adaptation de la liste des genres de profession "
             "soumis à l'obligation d'annoncer les postes vacants (RS 823.111.3), en vigueur du 1.1 au 31.12.2026 — "
             "https://www.fedlex.admin.ch/eli/cc/2025/800/fr")
# Codes and prefixes of the 2026 ordinance (CH-ISCO-19); « 93 sans 93120 ».
SUBJECT_PREFIXES_2026 = ("1221", "21130", "21310", "21330", "21660", "24331", "24332", "26310", "26320", "26330",
                         "26550", "33320", "4222", "4223", "42240", "4225", "4226", "4227", "4228", "4229", "51200",
                         "51311", "51313", "71140", "71190", "71230", "71240", "71241", "71310", "72120", "72240",
                         "73112", "81570", "83440", "90", "93", "91120", "92110", "92140", "94", "962")
EXCLUDED_2026 = ("93120",)
LIST_VALID = (date(2026, 1, 1), date(2026, 12, 31))  # the ordinance's own period of validity


class ListOutOfDate(ValueError):
    """The list of occupations subject to the obligation is set each year by an ordinance: outside its year, the
    engine stops and asks for the new list instead of answering with the old one (review 1, I9)."""

# Probable CH-ISCO-19 genre per trade of the taxonomy (OFS file 36037208/36037209; labels FR/DE of the genre).
TRADE_CH_ISCO: dict[str, dict[str, str]] = {
    "macon": {"genre": "71121", "fr": "Maçons (sauf poêliers-fumistes)",
              "de": "Maurer und verwandte Berufe (ohne Ofenbau)", "statut": "probable"},
    "manoeuvre_construction": {"genre": "93131", "fr": "Manœuvres du bâtiment, domaine principal de la construction",
                               "de": "Hilfsarbeiter im Hochbau, Bauhauptgewerbe", "statut": "probable",
                               "genre_genie_civil": "93120"},
    "coffreur": {"genre": "71140", "fr": "Constructeurs en béton armé, maçons ragréeurs et assimilés",
                 "de": "Betonierer/Betonierinnen, Betonoberflächenfertiger/-innen und verwandte Berufe",
                 "statut": "probable"},
    "grutier": {"genre": "83431", "fr": "Conducteurs de grues, d'engins de levage divers et de matériels similaires "
                                        "(sans remontées mécaniques)",
                "de": "Kranführer, Aufzugmaschinisten und Bediener verwandter Hebeeinrichtungen (ohne Seilbahn)",
                "statut": "probable"},
    "machiniste": {"genre": "83422", "fr": "Conducteurs de machines de chantier qualifiés",
                   "de": "Führer von Erdbewegungs- und verwandten Maschinen, Baumaschinen", "statut": "probable"},
    "electricien": {"genre": "74110", "fr": "Électriciens du bâtiment et assimilés",
                    "de": "Bauelektriker und verwandte Berufe", "statut": "probable"},
    "installateur_sanitaire": {"genre": "71263", "fr": "Installateurs sanitaires", "de": "Sanitärinstallateure",
                               "statut": "probable"},
    "peintre": {"genre": "71310", "fr": "Peintres en bâtiment et poseurs de papiers peints",
                "de": "Maler/-innen und verwandte Berufe", "statut": "probable"},
    "platrier": {"genre": "71230", "fr": "Plâtriers, constructeurs à sec", "de": "Gipser/-innen, Trockenbauer/-innen",
                 "statut": "probable"},
    "charpentier": {"genre": "71151", "fr": "Charpentiers", "de": "Zimmerleute", "statut": "probable"},
    "soudeur": {"genre": "72120", "fr": "Soudeurs et oxycoupeurs",
                "de": "Schweisser/-innen und Brennschneider/-innen", "statut": "probable"},
    "polymecanicien": {"genre": "72001", "fr": "Polymécaniciens et mécaniciens de production",
                       "de": "Polymechaniker und Produktionsmechaniker", "statut": "probable"},
    "operateur_production": {"genre": "81000", "fr": "Conducteurs de machines et d'installations fixes, sip",
                             "de": "Bediener stationärer Anlagen und Maschinen, onA", "statut": "à confirmer"},
    "cariste": {"genre": "83440", "fr": "Conducteurs de chariots élévateurs",
                "de": "Gabelstaplerfahrer/-innen und verwandte Berufe", "statut": "probable"},
    "agent_logistique": {"genre": "43200", "fr": "Employés d'approvisionnement, d'ordonnancement et des transports, "
                                                "sip", "de": "Bürokräfte im Bereich Materialwirtschaft und Transport, "
                                                             "onA", "statut": "à confirmer"},
}

NO_SPLIT = ("Ne jamais découper une mission pour rester sous 14 jours : des missions successives de la même "
            "personne pour le même profil s'additionnent (directive SECO B33).")
NO_EARLY_CONTACT = ("Les candidats de la base de l'agence non inscrits à l'ORP ne peuvent être contactés et engagés "
                    "qu'après la date de publication libre (directive SECO B8).")


def is_subject_2026(genre: str) -> bool:
    g = str(genre).strip()
    if g in EXCLUDED_2026:
        return False
    return any(g.startswith(p) for p in SUBJECT_PREFIXES_2026)


def check(trade: str, site: str = "batiment", duration_days: int | None = None,
          orp_registered: bool = False, on: date | None = None) -> dict[str, Any]:
    """Is a vacancy for ``trade`` subject to the 2026 reporting obligation, and is an announcement required?
    ``on``: the day the vacancy is announced; outside the list's year, ListOutOfDate."""
    if on is not None and not LIST_VALID[0] <= on <= LIST_VALID[1]:
        raise ListOutOfDate(f"la liste des genres de profession soumis est celle de 2026 "
                            f"({ORDINANCE.split(' — ')[0]}) ; pour le {on:%d.%m.%Y}, la mettre à jour avec "
                            "l'ordonnance de l'année")
    m = TRADE_CH_ISCO.get(trade)
    if m is None:
        return {"metier": trade, "genre": None, "soumis": None, "annonce_requise": None, "exception": None,
                "raison": "métier sans correspondance CH-ISCO-19 vérifiée : demander à l'ORP",
                "avertissement": NO_SPLIT, "source": ORDINANCE}
    genre = m.get("genre_genie_civil", m["genre"]) if site == "genie_civil" else m["genre"]
    subject = is_subject_2026(genre)
    exception, exception_code = None, None
    if subject and duration_days is not None and duration_days <= 14:
        exception, exception_code = ("rapport de travail de 14 jours civils au plus (art. 53d al. 1 let. b OSE)",
                                     "mission_courte")
    elif subject and orp_registered:
        exception, exception_code = ("poste pourvu par une personne inscrite à l'ORP comme demandeur d'emploi "
                                     "(art. 21a al. 5 LEI)", "inscrit_orp")
    reason = (f"genre {genre} {'inscrit' if subject else 'absent'} de la liste 2026"
              + (" (« 93 sans 93120 » : manœuvres du génie civil exclus)" if genre == "93120" else ""))
    return {"metier": trade, "genre": genre, "libelle_fr": m["fr"], "libelle_de": m["de"],
            "correspondance": m["statut"], "soumis": subject, "annonce_requise": subject and exception is None,
            "exception": exception, "exception_code": exception_code, "raison": reason,
            "avertissement": NO_SPLIT + " " + NO_EARLY_CONTACT,
            "source": ORDINANCE, "orp_competent": "ORP du siège de l'entreprise locataire (directive SECO B14)"}


def _easter(year: int) -> date:
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    month = (h + m - 7 * n + 114) // 31
    day = (h + m - 7 * n + 114) % 31 + 1
    return date(year, month, day)


def valais_holidays(year: int) -> set[date]:
    """Public holidays of the canton of Valais (list to confirm with the cantonal law before production):
    1.1, Saint-Joseph 19.3, Ascension, Fête-Dieu, 1.8, Assomption 15.8, Toussaint 1.11, Immaculée Conception 8.12,
    Noël 25.12."""
    e = _easter(year)
    return {date(year, 1, 1), date(year, 3, 19), e + timedelta(days=39), e + timedelta(days=60), date(year, 8, 1),
            date(year, 8, 15), date(year, 11, 1), date(year, 12, 8), date(year, 12, 25)}


def free_publication_date(online: date, holidays: set[date] | None = None, n: int = 5) -> date:
    """Day from which the job may be published elsewhere: the restriction runs over the ``n`` working days that
    follow the day it went online on the public employment service platform (art. 53b al. 5-6 OSE; B16-B17:
    Saturdays, Sundays and public holidays do not count)."""
    hol = holidays if holidays is not None else valais_holidays(online.year) | valais_holidays(online.year + 1)
    d, counted = online, 0
    while counted < n:
        d += timedelta(days=1)
        if d.weekday() < 5 and d not in hol:
            counted += 1
    return d + timedelta(days=1)


def announcement_text(trade: str, client: str, place: str, start: date | None, duration: str, rate: int | None,
                      agency: str, lang: str = "fr", requirements: str = "", address: str = "",
                      draft: bool = False) -> str:
    """Draft with the mandatory content of art. 53b al. 2 OSE (for a staffing agency: name of the client, let. i).

    ``draft``: the need is an estimate (design critique, round 2): the text says so first, and what only the company
    can say (start date, rate) is a slot to fill in, never a value we would invent."""
    label = TRADES[trade].label_fr if lang == "fr" else TRADES[trade].label_de
    if lang == "fr":
        req = requirements or "expérience du métier ; équipements de sécurité de chantier ; permis de travail valable"
        head = "Brouillon : besoin estimé, à confirmer avec l'entreprise avant de saisir l'annonce.\n" if draft else ""
        rate_s = f"{rate} %" if rate is not None else "[à confirmer avec l'entreprise]"
        start_s = f"{start:%d.%m.%Y}" if start is not None else "[à confirmer avec l'entreprise]"
        return (f"{head}Profession : {label}\nActivité et exigences : {req}\nLieu de travail : {place}\n"
                f"Taux d'occupation : {rate_s}\nDate d'entrée : {start_s}\nDurée : {duration}\n"
                f"Employeur (location de services) : {agency}\nAdresse : {address or '[adresse de l’agence]'}\n"
                f"Entreprise locataire : {client}\n"
                "Annonce à saisir par le consultant sur la plateforme du service public de l'emploi ; "
                "publication ailleurs seulement après la date indiquée sur l'attestation.")
    req = requirements or "Berufserfahrung; Baustellen-Sicherheitsausrüstung; gültige Arbeitsbewilligung"
    head = "Entwurf: geschätzter Bedarf, vor der Erfassung mit dem Unternehmen zu bestätigen.\n" if draft else ""
    rate_s = f"{rate} %" if rate is not None else "[mit dem Unternehmen zu bestätigen]"
    start_s = f"{start:%d.%m.%Y}" if start is not None else "[mit dem Unternehmen zu bestätigen]"
    return (f"{head}Beruf: {label}\nTätigkeit und Anforderungen: {req}\nArbeitsort: {place}\nPensum: {rate_s}\n"
            f"Stellenantritt: {start_s}\nDauer: {duration}\nArbeitgeber (Personalverleih): {agency}\n"
            f"Adresse: {address or '[Adresse der Filiale]'}\n"
            f"Einsatzbetrieb: {client}\nDie Beraterin oder der Berater erfasst die Stelle auf der Plattform der "
            "öffentlichen Arbeitsvermittlung; anderswo erst ab dem Datum auf der Bestätigung publizieren.")
