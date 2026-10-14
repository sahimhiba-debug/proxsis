"""Week-1 reports generated from the JSON written by the commands (audit of week 1, M9: every figure of a document
comes out of a reproducible command). ``proxsis docs-semaine1`` rewrites the four documents."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

SIMAP_NOTE = ("*Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font "
              "foi.*")
FICTIF = "> **Monde fictif : prouve que le code fonctionne, pas sa performance réelle.**"


def pc(x: float | None, d: int = 1) -> str:
    return "—" if x is None else f"{x * 100:.{d}f}".replace(".", ",")


def num(x: float | None, d: int = 1) -> str:
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def pts(x: float) -> str:
    return f"{x * 100:+.1f}".replace(".", ",").replace("-", "−")


def ci(v: list[float]) -> str:
    return f"{pc(v[0])} à {pc(v[1])}"


def ci_pts(v: list[float]) -> str:
    return f"{pts(v[0])} à {pts(v[1])}"


def chf(n: int) -> str:
    return f"{n:,}".replace(",", " ")


# ------------------------------------------------------------------ backtest per specialty

LAB = {"batiment": "Bâtiment", "electricite": "Électricité", "technique": "Technique du bâtiment"}


def specialites_md(r: dict[str, Any]) -> str:
    rows, rowsp, flags = [], [], []
    for s, v in r["specialites"].items():
        if "erreur" in v:
            continue
        t, p = v["cibles"]["t0"], v["cibles"]["pic"]
        rows.append(f"| {LAB[s]} | {num(v['region']['entreprises_classees_moyenne'])} | {pc(t['taux_de_base'])} % | "
                    f"{pc(t['p_at_k']['recence']['moyenne'])} % | **{pc(t['p_at_k']['frequence_52s']['moyenne'])} %** "
                    f"({ci(t['p_at_k']['frequence_52s']['ic95'])}) | {pc(t['p_at_k']['combine']['moyenne'])} % | "
                    f"{pts(t['combine_moins_frequence']['moyenne'])} ({ci_pts(t['combine_moins_frequence']['ic95'])}) "
                    f"| {v['ordre_retenu']} |")
        rowsp.append(f"| {LAB[s]} | {pc(p['taux_de_base'])} % | {pc(p['p_at_k']['frequence_52s']['moyenne'])} % | "
                     f"{pc(p['p_at_k']['m0_marches']['moyenne'])} % | {pc(p['p_at_k']['combine']['moyenne'])} % | "
                     f"{pts(p['combine_moins_frequence']['moyenne'])} ({ci_pts(p['combine_moins_frequence']['ic95'])}) |")
        f = v["drapeaux_surprise"]
        rd, nv = f["rythme_double"], f["nouveau_venu"]
        sr = v["surprises_retenues"]
        flags.append(f"| {LAB[s]} | {rd['hors_top_k']['signalements']} | {pc(rd['hors_top_k']['taux_t0'])} % | "
                     f"{nv['hors_top_k']['signalements']} | {pc(nv['hors_top_k']['taux_t0'])} % | "
                     f"{pc(rd['hors_top_k']['taux_de_base_t0'])} % | {sr['signalements']} | {pc(sr['taux_t0'])} % |")
    b = r["specialites"]["batiment"]
    bt = b["cibles"]["t0"]
    rd = b["drapeaux_surprise"]["rythme_double"]["hors_top_k"]
    nv = b["drapeaux_surprise"]["nouveau_venu"]["hors_top_k"]
    lift = rd["taux_t0"] / rd["taux_de_base_t0"] if rd["taux_t0"] and rd["taux_de_base_t0"] else None
    return f"""# Backtest réel par spécialité d'agence : classement et détecteur de surprises (livrable 2.7)

Données **RÉELLES** : {chf(r['adjudications'])} adjudications de travaux simap (Suisse romande et adjudicateurs
valaisans, juillet 2024 à septembre 2026). {SIMAP_NOTE}

Commandes : `proxsis backtest-specialites` → `docs/backtest/specialites_v1.json` (bootstrap par blocs de
8 semaines, 2 000 tirages, graine 0) ; ce document : `proxsis docs-semaine1`. Mesuré le {r['mesure_le']}.

## Protocole

- Chaque lundi T de {b['semaines'][0]} à {b['semaines'][1]} (**{b['n_semaines']} semaines**), on classe les
  entreprises **valaisannes à la date T** : canton le plus fréquent de leurs lots publiés **avant T** (même
  définition que la liste d'appels ; audit m1). Seul ce qui était publié avant T est utilisé.
- On regarde les **10 premières** (P@10) sur deux cibles : **T0** (au moins un nouveau marché de la spécialité dans les
  8 semaines) et **pic** (au moins deux marchés dans les 8 semaines et le double du rythme habituel).
- Classements : hasard (espérance exacte = taux de base), récence, **fréquence sur 52 semaines**, M0, **modèle
  combiné** (régression logistique, apprise sur les semaines dont l'issue était connue avant T).
- Règle fixée **avant** la mesure : le combiné n'est retenu que si la borne basse de l'IC 95 % de (combiné −
  fréquence) sur T0 est positive ; sinon, fréquence puis récence.

## Résultats sur T0

| Spécialité | Entreprises classées (moyenne) | Hasard | Récence | Fréquence 52 sem. (IC 95 %) | Combiné | Combiné − fréquence (IC 95 %, points) | Ordre retenu |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

## Résultats sur « pic »

| Spécialité | Hasard | Fréquence | M0 | Combiné | Combiné − fréquence (IC 95 %, points) |
|---|---|---|---|---|---|
{chr(10).join(rowsp)}

## Détecteur de surprises, là où l'appli le montre : hors des 10 premières (audit M2)

Taux de réussite sur T0 des entreprises signalées **hors du top 10 par fréquence**, et des **3 surprises retenues**
chaque semaine (signalées hors top 10, triées par le score « pic »). Les signalements ne sont pas indépendants
(une entreprise peut l'être plusieurs semaines de suite) : taux descriptifs.

| Spécialité | « Activité qui bondit » hors top 10 | Réussite T0 | « Nouveau venu » hors top 10 | Réussite T0 | Base hors top 10 | Surprises retenues | Réussite T0 |
|---|---|---|---|---|---|---|---|
{chr(10).join(flags)}

## Ce qu'on en conclut (honnêtement)

1. **Bâtiment** : les dix entreprises valaisannes les plus fréquentes gagnent un nouveau marché dans les 8 semaines
   dans **{pc(bt['p_at_k']['frequence_52s']['moyenne'])} %** des cas, contre {pc(bt['taux_de_base'])} % au hasard :
   un fort indicateur d'**activité**. Le combiné ne fait pas mieux ({pts(bt['combine_moins_frequence']['moyenne'])}
   point) : la liste reste ordonnée par fréquence puis récence (ADR-0013).
2. **« Activité qui bondit »**, hors des dix premières : **{pc(rd['taux_t0'])} %** de réussite contre
   {pc(rd['taux_de_base_t0'])} % ({num(lift)} fois la base). Le drapeau mérite sa section « à surveiller ».
3. **« Nouveau venu »** : {pc(nv['taux_t0'])} % hors top 10. Il **ne prédit pas** un nouveau marché ; l'appli le dit
   dans la raison même (« indice de prospection »).
4. **Électricité et Technique** : trop peu d'entreprises valaisannes ({num(r['specialites']['electricite']['region']['entreprises_classees_moyenne'])}
   et {num(r['specialites']['technique']['region']['entreprises_classees_moyenne'])} classées en moyenne). En
   Électricité, le top 10 couvre la quasi-totalité de la population : P@10 ≈ taux de base **par construction**
   (audit m2). La liste publique y est un appoint, pas un moteur.
5. **{pc(b['part_premiers_gagnants'], 0)} % des lauréats** d'une fenêtre de 8 semaines (toutes entreprises de la
   spécialité, Valais ou non, fenêtres glissantes qui se chevauchent) n'avaient jamais gagné de marché de la
   spécialité avant : aucun classement fondé sur l'historique des marchés ne peut les voir venir.

## Ce qui exige l'historique des commandes de Flexsis

Le backtest mesure une **activité publique** (un nouveau marché gagné). Il ne mesure pas la commande de personnel
temporaire, la part du besoin confiée à des temporaires, le délai entre adjudication et commande, ni le taux appel →
rendez-vous → mission. La demande de données est prête : `docs/affaires/demande-donnees-pilote.md`. En attendant,
la première vérité terrain viendra des consultants (`proxsis integrer-validation`).
"""


# ------------------------------------------------------------------ candidates, redeployment, compliance

def semaine1_md(w: dict[str, Any], cands_csv: Path) -> str:
    c = list(csv.DictReader(cands_csv.open(encoding="utf-8")))
    cat = Counter(r["categorie_cct"] for r in c)
    stat = Counter(r["statut"] for r in c)
    spec = Counter(r["specialite"] for r in c)
    openpt = sum(r["point_ouvert_cct"] == "True" for r in c)
    orp = sum(r["inscrit_orp"] == "True" for r in c)
    eq = w["equite"]
    e15, e5, rnd = eq["plafond_15_ans_actuel"], eq["plafond_5_ans_adr_0012"], eq["reference_tirage_au_hasard"]
    pr, red, conf = w["propositions"], w["redeploiement"], w["conformite"]

    def di(e: dict[str, Any], a: str) -> str:
        return num(e["di_ratio"][a]["moyenne"], 2)

    def perm(e: dict[str, Any], a: str) -> str:
        p = e["test_permutation"][a]
        n = round((p["part_p_inf_0_05"] or 0) * p["viviers"])
        return f"{n} sur {p['viviers']} (p médiane {num(p['p_mediane'], 2)})"

    def verdict(e: dict[str, Any], a: str) -> str:
        p = e["test_permutation"][a]
        n = round((p["part_p_inf_0_05"] or 0) * p["viviers"])
        if n >= 4:
            return f"**écart réel** ({n} viviers sur {p['viviers']} avec p < 0,05)."
        if n >= 2:
            return f"**signal faible, non concluant** ({n} viviers sur {p['viviers']} avec p < 0,05)."
        return f"**pas d'écart au-delà du hasard** ({n} vivier(s) sur {p['viviers']} avec p < 0,05)."

    age_n = round((e15["test_permutation"]["audit_age_band"]["part_p_inf_0_05"] or 0)
                  * e15["test_permutation"]["audit_age_band"]["viviers"])
    age_note = ("Il tient à l'expérience (20 % du score) : les 18-25 ans sont moins sélectionnés. Le plafond à 5 ans "
                "le réduit un peu ; c'est le compromis de l'ADR-0012, en attente de décision. Le code reste à 15 ans."
                if age_n >= 2 else "")

    def rates(e: dict[str, Any], a: str) -> str:
        return " ; ".join(f"{g} {pc(v)} %" for g, v in e["test_permutation"][a]["taux_selection_moyens"].items())

    motifs = ", ".join(f"{k} : {v}" for k, v in red["motifs_non_redeploye"].items())
    return f"""# Semaine 1 : candidats FICTIFS, propositions, redéploiement, conformité (livrables 2.4, 2.5, 2.6)

{FICTIF} Les candidats sont inventés. Les besoins auxquels ils sont proposés sont **réels** : listes d'appels du
{w['date']} (Bâtiment, Électricité, Technique), bâties sur les marchés publics simap. {SIMAP_NOTE}

Commandes, depuis `python/` : `proxsis candidats` (vivier, graine 42) → `proxsis moteur-semaine1` →
`docs/modeles/semaine1_v1.json` ; ce document : `proxsis docs-semaine1`. Localités : copie versionnée du
répertoire swisstopo `{w['localites']['fichier']}` (sha256 `{w['localites']['sha256'][:16]}…`, audit M10).

## 2.4 Les 300 candidats FICTIFS

- Aucun nom (« Candidat·e 042 (FICTIF) »). Les attributs protégés (`audit_*`) ne servent qu'à l'audit.
- **Inventé** (hypothèses, `proxsis/synth/candidates.py`) : parts par spécialité, formation, permis, langues,
  statut, inscription à l'ORP (40 % des disponibles).
- **Calculé par la règle** : la catégorie CCT (art. 20 al. 4 et 5 CCT Location de services 2026, `proxsis/cct.py`).
  « Quatre ans de pratique et 1 000 heures par année civile » donne **spécialisé** (22.76 CHF/h), pas qualifié ;
  {openpt} profils relèvent du point ouvert (heures insuffisantes ou non renseignées), lu de façon prudente.
- **Composition** : qualifié {cat['qualifie']}, non qualifié {cat['non_qualifie']}, spécialisé {cat['specialise']} ;
  en mission {stat['en_mission']}, disponible {stat['disponible']}, indisponible {stat['indisponible']} ; Bâtiment
  {spec['batiment']}, Industrie {spec['industrie']}, Électricité {spec['electricite']}, Technique {spec['technique']} ;
  inscrits à l'ORP {orp}.
- **Salaire affiché** (audit M7) : pour le gros œuvre, le second œuvre, l'électricité et la technique du bâtiment,
  la CCT étendue de l'entreprise de mission prime (CN, second-œuvre romand, CCT valaisannes) : l'appli affiche la CCT
  probable et renvoie à tempdata.ch. Le minimum CCT LS n'est affiché que pour les métiers sans CCT étendue probable.
  Le Valais relève des montants standard de la CCT LS d'après l'annexe 3 (déduction de lecture, à confirmer).

### Propositions : critères stricts, puis proximité

- **{pr['besoins']} besoins réels** (une entreprise × un métier) ; tous ont au moins une proposition.
- Entonnoir moyen : {num(pr['entonnoir_moyen']['tous'], 0)} → métier {num(pr['entonnoir_moyen']['metier'], 0)} →
  permis {num(pr['entonnoir_moyen']['certificat'], 0)} → disponibles {num(pr['entonnoir_moyen']['disponible'], 0)}
  → dans le rayon **{num(pr['entonnoir_moyen']['distance'], 0)}**.
- Poste soumis à l'obligation d'annonce : chaque candidat non inscrit à l'ORP porte « contact possible dès le … »
  (directive SECO B8) ; {conf['contact_differe_propositions']} propositions concernées.

### Audit d'équité reproductible

20 viviers (le vivier publié, puis les graines 1001 à 1019), les mêmes {pr['besoins']} besoins réels, 5 propositions
par besoin. Ratio d'impact = taux le plus bas / taux le plus haut (groupes d'au moins 20 éligibles), référence au
hasard (5 tirées au hasard parmi les éligibles), et **test de permutation** (audit M8) : choix du moteur gardés,
attribut permuté entre candidats, khi-deux des sélections par groupe ; sous indépendance, 5 % des viviers ont
p < 0,05.

| Réglage | Ratio genre | Ratio âge | Ratio nationalité | Expérience moyenne des proposés |
|---|---|---|---|---|
| Plafond d'expérience 15 ans (actuel) | {di(e15, 'audit_gender')} | {di(e15, 'audit_age_band')} | {di(e15, 'audit_nationality_group')} | {num(e15['experience_moyenne_proposes_ans'])} ans |
| Plafond 5 ans (ADR-0012, proposé) | {di(e5, 'audit_gender')} | {di(e5, 'audit_age_band')} | {di(e5, 'audit_nationality_group')} | {num(e5['experience_moyenne_proposes_ans'])} ans |
| Référence : tirage au hasard | {di(rnd, 'audit_gender')} | {di(rnd, 'audit_age_band')} | {di(rnd, 'audit_nationality_group')} | {num(rnd['experience_moyenne_proposes_ans'])} ans |

Test de permutation, viviers avec p < 0,05 :

- plafond 15 ans : genre {perm(e15, 'audit_gender')} ; âge {perm(e15, 'audit_age_band')} ; nationalité {perm(e15, 'audit_nationality_group')} ;
- plafond 5 ans : genre {perm(e5, 'audit_gender')} ; âge {perm(e5, 'audit_age_band')} ; nationalité {perm(e5, 'audit_nationality_group')}.

Taux moyens de sélection (plafond 15 ans) : âge {rates(e15, 'audit_age_band')} ; nationalité {rates(e15, 'audit_nationality_group')} ;
genre {rates(e15, 'audit_gender')}.

Lecture (conclusions calculées à partir des comptes ci-dessus ; sous indépendance, 1 vivier sur 20 environ a
p < 0,05 par hasard) :

1. **Le ratio min/max est très bruité** sur ces volumes (même au hasard, il vaut {di(rnd, 'audit_age_band')} pour
   l'âge) : le seuil de 0,8 seul ne prouve rien ; le test de permutation est le test retenu.
2. **Âge** : {verdict(e15, 'audit_age_band')} {age_note}
3. **Nationalité** : {verdict(e15, 'audit_nationality_group')} Ni la langue ni le permis n'entrent dans le score ; à
   surveiller sur les vrais candidats.
4. **Genre** : {verdict(e15, 'audit_gender')}

## 2.5 « Fin de mission, prochaine mission » (FICTIF)

Travailleurs dont la mission finit dans les **trois semaines**, rapprochés des besoins **réels** prévus : métier
identique ou proche, **permis légalement requis** (audit M6), rayon, besoin actif dans les 21 jours ; capacité =
pic de l'estimation médiane ; pour un poste soumis à l'obligation d'annonce, un candidat non inscrit à l'ORP
n'est placé qu'après la date de publication libre (audit M4).

- {red['fins_de_mission']} fins de mission ; **{red['redeployes']} redéployés ({pc(red['taux_redeploiement'])} %)**.
- Motifs de non-redéploiement : {motifs}. Le premier tient surtout aux travailleurs de l'**Industrie** : aucune liste
  Industrie (signal public insuffisant, `docs/recherche/apercu_simap.md`).

## 2.6 Conformité : obligation d'annonce 2026

Sources : art. 21a LEI ; art. 53a à 53f OSE ; ordonnance du DEFR du 27.11.2025 (RS 823.111.3, Fedlex) ; directive
SECO B8, B14, B16-B17, B33, B36 ; CH-ISCO-19 (OFS).

- Liste 2026 codée depuis les **préfixes de l'ordonnance** (« 93 sans 93120 »).
- **Site de chaque besoin** déduit des phases de ses propres lots ; « génie civil » seulement si **tous** sont du
  génie civil, sinon bâtiment par prudence (audit M4) : **{conf['besoins_soumis']} besoins soumis sur {conf['besoins']}**,
  comptés besoin par besoin.
- Exceptions (mission de 14 jours au plus ; personne inscrite à l'ORP), règles fermes (ne jamais découper une mission,
  B33 ; pas de contact avant la publication libre, B8).
- Compte à rebours de cinq jours ouvrés, testé sur l'exemple officiel (5.7.2021 → 13.7.2021) ; jours fériés
  valaisans à confirmer avec la loi cantonale (fêtes communales non traitées).
- Texte d'annonce FR et DE avec le contenu de l'art. 53b al. 2 OSE, **adresse comprise** (audit M5).
- Aucun appel à Job-Room.
"""


# ------------------------------------------------------------------ simap overview and phasing (figures only)

def apercu_fix(md: str, o: dict[str, Any]) -> str:
    """Replace the unsourced « 47 % » by the share measured on these awards (audit M9)."""
    share = o["sans_canton_des_travaux"] / o["n_adjudications"]
    return md.replace("47 % des projets simap n'indiquent pas le canton d'exécution",
                      f"{pc(share)} % de ces {chf(o['n_adjudications'])} adjudications "
                      f"({chf(o['sans_canton_des_travaux'])}) n'indiquent pas le canton des travaux")


PHASE_LAB = {"preparatoire": "Travaux préparatoires (CFC 1)", "terrassement": "Terrassement (CFC 20)",
             "enveloppe": "Enveloppe (CFC 22)", "electricite": "Électricité (CFC 23)",
             "cvc": "Chauffage, ventilation, climatisation (CFC 24)", "sanitaire": "Sanitaire (CFC 25)",
             "transport": "Installations de transport (CFC 26)", "amenagement_int": "Aménagements intérieurs 1 (CFC 27)",
             "finitions": "Aménagements intérieurs 2 (CFC 28)", "equipement": "Équipements d'exploitation (CFC 3)",
             "exterieur": "Aménagements extérieurs (CFC 4)"}


def _days(x: float) -> str:
    return f"{x:.0f}".replace("-", "−")


def phasage_md(p: dict[str, Any]) -> str:
    d = p["delais"]
    rows = []
    for k, lab in PHASE_LAB.items():
        v = d.get(k)
        if not v:
            continue
        r = v["rapport_montant_median"]
        rows.append(f"| {lab} | {v['n']} | {pc(v['presence'], 0)} % | {_days(v['mediane_jours'])} | "
                    f"{_days(v['ic95_mediane'][0])} à {_days(v['ic95_mediane'][1])} | {_days(v['p10_jours'])} à "
                    f"{_days(v['p90_jours'])} | {num(r, 2) if r else '—'} |")
    val = [f"| {v['coupure']} | {v['n_chantiers_apprentissage']} | {v['n_chantiers_test']} | {v['n_lots_test']} | "
           f"{pc(v['couverture_p10_p90'], 0)} % | {num(v['mae_mediane_jours'], 0)} j | "
           f"{num(v['mae_reference_jours'], 0)} j |" for v in p["validation"]]
    covs = [v["couverture_p10_p90"] for v in p["validation"]]
    maes = [v["mae_mediane_jours"] for v in p["validation"]]
    refs = [v["mae_reference_jours"] for v in p["validation"]]
    beats = all(m < r for m, r in zip(maes, refs, strict=True))
    verdict = ("le délai **par phase bat un délai unique**" if beats else
               "le délai **par phase ne bat pas un délai unique**")
    return f"""# Phasage réel appris sur les lots simap (livrable 2.3)

Données **RÉELLES** : adjudications de travaux simap (Suisse romande et adjudicateurs valaisans, juillet 2024 à
septembre 2026). {SIMAP_NOTE}

Commandes : `proxsis phasage-reel` → `docs/modeles/phasage_reel_v1.json` (bootstrap 2 000 tirages, graine 0) ;
ce document : `proxsis docs-semaine1`. Module : `proxsis.phasing` (testé).

## Ce qui est mesuré

1. **Chantiers** : lots d'un même bâtiment regroupés (même adjudicateur et même lieu, titres proches : au moins deux
   mots communs, Jaccard ≥ 0,5, moins de trois ans d'écart). **{p['chantiers']} chantiers**, dont
   **{p['chantiers_2_lots_ou_plus']} avec au moins deux lots** ; **{d['_chantiers_avec_ancre']} ont un lot de gros
   œuvre (CFC 21)**, qui sert d'ancre.
2. Pour chaque phase, le **délai entre l'adjudication du gros œuvre et celle de la phase**, avec l'IC 95 % de la
   médiane (bootstrap) et l'étendue p10–p90.
3. Le **montant de la phase rapporté au montant du gros œuvre** (médiane).

| Phase (CFC) | Chantiers | Présence | Délai médian (jours) | IC 95 % de la médiane | p10 à p90 (jours) | Montant / gros œuvre |
|---|---|---|---|---|---|---|
{chr(10).join(rows)}

Un délai négatif : la phase est adjugée **avant** le gros œuvre. « Présence » : part des chantiers avec gros œuvre
où la phase est adjugée séparément sur simap.

## Confrontation avec les références publiques du métier

- **SIA 112:2014** (sommaire gratuit ; `docs/recherche/conformite_cct_annonce.md` § e) : l'adjudication clôt la
  phase partielle **41** ; le besoin de main-d'œuvre arrive en **52** « Exécution de l'ouvrage ». La norme donne
  l'ordre des phases, pas leurs durées.
- **Données** : électricité, CVC et sanitaire sont adjugés en général **le même jour que le gros œuvre** (une vague
  41) ; les aménagements intérieurs et les finitions forment une **seconde vague**, deux à trois mois plus tard.
- **CFC (SN 506 500:2017, CRB)** : l'ordre des groupes 20 à 28 suit l'ordre d'exécution ; libellés livrés par simap ;
  norme détaillée payante, non lue.
- **Conséquence** : la date d'adjudication **ne révèle pas le calendrier des travaux** des installations. Le
  calendrier du besoin repose sur des **hypothèses déclarées** (début quatre semaines après l'adjudication, durées
  par phase, taille d'équipe plafonnée), à calibrer avec l'historique de Flexsis.

## Validation sur des chantiers plus récents

Apprentissage sur les chantiers dont le gros œuvre est adjugé avant la coupure, test sur les suivants. Référence :
un seul délai (médiane de toutes les phases).

| Coupure | Chantiers d'apprentissage | Chantiers de test | Lots de test | Couverture p10–p90 (attendu ≈ 80 %) | Erreur absolue moyenne du délai médian par phase | Erreur absolue moyenne d'un délai unique |
|---|---|---|---|---|---|---|
{chr(10).join(val)}

**Résultat honnête** : intervalles p10–p90 **bien calibrés** ({pc(min(covs), 0)} à {pc(max(covs), 0)} % de couverture) ;
{verdict}. Le produit affiche donc des **fenêtres** (« lots attendus entre telle et telle date »), jamais une date
ponctuelle par phase : la médiane reste dans les données pour l'analyse, l'appli ne l'affiche pas.

## Ce que le phasage apporte au produit, et ce qu'il n'apporte pas

- **Apporte** : les lots encore attendus sur un chantier (fenêtre p10–p90) ; l'estimation d'un montant non publié par
  le rapport mesuré au gros œuvre du même chantier ; l'ordre des vagues d'adjudication.
- **N'apporte pas** : les durées de travaux, la part de main-d'œuvre, le coût hebdomadaire, la part confiée à des
  temporaires — hypothèses listées dans `PhasingModel.assumptions` et dans chaque liste d'appels.
"""


def claims_lines(root: Path) -> dict[str, str]:
    """CLAIMS.md lines of week 1, rebuilt from the JSON of the commands."""
    docs = root / "docs"
    r = json.loads((docs / "backtest/specialites_v1.json").read_text("utf-8"))
    w = json.loads((docs / "modeles/semaine1_v1.json").read_text("utf-8"))
    o = json.loads((docs / "recherche/apercu_simap.json").read_text("utf-8"))
    ph = json.loads((docs / "modeles/phasage_reel_v1.json").read_text("utf-8"))
    c = list(csv.DictReader((root / "data/fictif/candidats_300.csv").open(encoding="utf-8")))
    b, el, te = (r["specialites"][k] for k in ("batiment", "electricite", "technique"))
    bt, bp = b["cibles"]["t0"], b["cibles"]["pic"]
    rd = b["drapeaux_surprise"]["rythme_double"]["hors_top_k"]
    nv = b["drapeaux_surprise"]["nouveau_venu"]["hors_top_k"]
    sr = b["surprises_retenues"]
    v = o["valais"]
    v1, v2 = ph["validation"]
    d = ph["delais"]
    eq = w["equite"]
    e15, e5, rnd = eq["plafond_15_ans_actuel"], eq["plafond_5_ans_adr_0012"], eq["reference_tirage_au_hasard"]
    cat = Counter(x["categorie_cct"] for x in c)
    red, pr, conf = w["redeploiement"], w["propositions"], w["conformite"]

    def di3(a: str) -> str:
        return " / ".join(num(e["di_ratio"][a]["moyenne"], 2) for e in (e15, e5, rnd))

    def perm(e: dict[str, Any], a: str) -> str:
        p = e["test_permutation"][a]
        return f"{round((p['part_p_inf_0_05'] or 0) * p['viviers'])}/{p['viviers']}"

    bw = f"{b['semaines'][0]} à {b['semaines'][1]}"
    cmd_bt, f_bt = "`proxsis backtest-specialites`", "`docs/backtest/specialites_v1.json`, `docs/backtest/specialites.md`"
    cmd_w, f_w = "`proxsis moteur-semaine1`", "`docs/modeles/semaine1_v1.json`, `docs/modeles/semaine1_candidats.md`"
    return {
        "SIMAP-3": f"| SIMAP-3 | Adjudications de construction collectées (Romandie et adjudicateurs valaisans, {o['periode'][0]} à {o['periode'][1]}) ; part valaisanne (au moins un des trois critères) ; sans canton des travaux | {chf(o['n_adjudications'])} adjudications ; Valais {chf(v['au_moins_un_critere'])} ({pc(v['part'])} %) ; sans canton {chf(o['sans_canton_des_travaux'])} ({pc(o['sans_canton_des_travaux'] / o['n_adjudications'])} %) ; lauréats masqués {o['masquage']['laureats_masques']} sur {chf(o['masquage']['laureats_total'])} | RÉEL | `proxsis apercu-simap` | `docs/recherche/apercu_simap.json`, `docs/recherche/apercu_simap.md` | collecte après masquage des adjudicateurs ressemblant à des personnes (audit semaine 1, B1) |",
        "PHAS-1": f"| PHAS-1 | Délai médian d'adjudication après le gros œuvre ({d['_chantiers_avec_ancre']} chantiers avec gros œuvre sur {ph['chantiers']}) | électricité {_days(d['electricite']['mediane_jours'])} j ; CVC {_days(d['cvc']['mediane_jours'])} j ; sanitaire {_days(d['sanitaire']['mediane_jours'])} j ; enveloppe {_days(d['enveloppe']['mediane_jours'])} j ; aménagements intérieurs {_days(d['amenagement_int']['mediane_jours'])} j ; finitions {_days(d['finitions']['mediane_jours'])} j | RÉEL | `proxsis phasage-reel` | `docs/modeles/phasage_reel_v1.json`, `docs/modeles/phasage_reel.md` | délai d'adjudication, **pas** calendrier des travaux |",
        "PHAS-2": f"| PHAS-2 | Validation temporelle du phasage (coupures {v1['coupure']} et {v2['coupure']}) | couverture p10–p90 {pc(v1['couverture_p10_p90'], 0)} % et {pc(v2['couverture_p10_p90'], 0)} % ; erreur absolue moyenne par phase {num(v1['mae_mediane_jours'], 0)} et {num(v2['mae_mediane_jours'], 0)} j contre {num(v1['mae_reference_jours'], 0)} et {num(v2['mae_reference_jours'], 0)} j pour un délai unique | RÉEL | idem | idem | fenêtres affichées, pas de date ponctuelle |",
        "REEL-SPEC-BAT": f"| REEL-SPEC-BAT | Liste Bâtiment, entreprises valaisannes à la date T, P@10 sur T0, {b['n_semaines']} semaines ({bw}) | hasard {pc(bt['taux_de_base'])} % ; récence {pc(bt['p_at_k']['recence']['moyenne'])} % ; fréquence 52 sem. {pc(bt['p_at_k']['frequence_52s']['moyenne'])} % (IC 95 % {ci(bt['p_at_k']['frequence_52s']['ic95'])}) ; combiné {pc(bt['p_at_k']['combine']['moyenne'])} % ; combiné − fréquence {pts(bt['combine_moins_frequence']['moyenne'])} point (IC {ci_pts(bt['combine_moins_frequence']['ic95'])}) → ordre par fréquence | RÉEL | {cmd_bt} | {f_bt} | activité publique, pas commande à Flexsis |",
        "REEL-SPEC-PIC": f"| REEL-SPEC-PIC | Liste Bâtiment, cible « pic », P@10 | hasard {pc(bp['taux_de_base'])} % ; fréquence {pc(bp['p_at_k']['frequence_52s']['moyenne'])} % ; combiné {pc(bp['p_at_k']['combine']['moyenne'])} % ; {pts(bp['combine_moins_frequence']['moyenne'])} points (IC {ci_pts(bp['combine_moins_frequence']['ic95'])}), non significatif | RÉEL | idem | idem | — |",
        "REEL-SURPRISE": f"| REEL-SURPRISE | Détecteur de surprises, Bâtiment, hors du top 10 (là où l'appli le montre) : réussite sur T0 | « activité qui bondit » {pc(rd['taux_t0'])} % ({rd['signalements']} signalements) contre {pc(rd['taux_de_base_t0'])} % de base hors top 10 ; « nouveau venu » {pc(nv['taux_t0'])} % ; 3 surprises retenues par semaine : {pc(sr['taux_t0'])} % | RÉEL | idem | idem | signalements non indépendants : taux descriptifs |",
        "REEL-SPEC-AUTRES": f"| REEL-SPEC-AUTRES | Électricité et Technique, entreprises valaisannes, P@10 sur T0 | Électricité ({num(el['region']['entreprises_classees_moyenne'])} entreprises classées en moyenne) : base {pc(el['cibles']['t0']['taux_de_base'])} %, fréquence {pc(el['cibles']['t0']['p_at_k']['frequence_52s']['moyenne'])} %, combiné {pc(el['cibles']['t0']['p_at_k']['combine']['moyenne'])} % ; Technique ({num(te['region']['entreprises_classees_moyenne'])}) : base {pc(te['cibles']['t0']['taux_de_base'])} %, fréquence {pc(te['cibles']['t0']['p_at_k']['frequence_52s']['moyenne'])} %, combiné {pc(te['cibles']['t0']['p_at_k']['combine']['moyenne'])} % | RÉEL | idem | idem | top 10 ≈ toute la population en Électricité : P@10 ≈ base par construction |",
        "REEL-SPEC-NOUVEAUX": f"| REEL-SPEC-NOUVEAUX | Part des lauréats Bâtiment d'une fenêtre de 8 semaines jamais vus avant dans la spécialité (toutes entreprises, fenêtres glissantes) | {pc(b['part_premiers_gagnants'])} % | RÉEL | idem | idem | fenêtres qui se chevauchent ; pas seulement les entreprises valaisannes |",
        "CAND-1": f"| CAND-1 | Vivier de 300 candidats FICTIFS (graine 42) : catégories CCT calculées par la règle (art. 20 al. 4-5 CCT LS) | qualifié {cat['qualifie']} ; non qualifié {cat['non_qualifie']} ; spécialisé {cat['specialise']} ; point ouvert CCT {sum(x['point_ouvert_cct'] == 'True' for x in c)} ; en mission {sum(x['statut'] == 'en_mission' for x in c)} ; inscrits ORP {sum(x['inscrit_orp'] == 'True' for x in c)} | FICTIF | `proxsis candidats` | `data/fictif/candidats_300.csv` | répartition inventée ; seule la catégorie suit la règle |",
        "PROP-1": f"| PROP-1 | Propositions pour les {pr['besoins']} besoins réels de la semaine du {w['date']} (entonnoir moyen des critères stricts) | {num(pr['entonnoir_moyen']['tous'], 0)} → métier {num(pr['entonnoir_moyen']['metier'], 0)} → permis {num(pr['entonnoir_moyen']['certificat'], 0)} → disponibles {num(pr['entonnoir_moyen']['disponible'], 0)} → dans le rayon {num(pr['entonnoir_moyen']['distance'], 0)} ; {pr['besoins_avec_au_moins_une']} besoins sur {pr['besoins']} avec au moins une proposition | FICTIF | {cmd_w} | {f_w} | candidats inventés, besoins réels (simap) |",
        "REDEP-1": f"| REDEP-1 | Redéploiement des fins de mission à trois semaines vers les besoins prévus réels (permis requis et délai d'annonce respectés) | {red['redeployes']} sur {red['fins_de_mission']} ({pc(red['taux_redeploiement'])} %) | FICTIF | idem | idem | prouve le mécanisme, pas le taux de Flexsis |",
        "EQ-1": f"| EQ-1 | Audit d'équité, 20 viviers, {pr['besoins']} besoins réels : ratio d'impact moyen (plafond 15 ans / 5 ans / hasard) et test de permutation (viviers avec p < 0,05, plafond 15 ans) | ratio genre {di3('audit_gender')} ; âge {di3('audit_age_band')} ; nationalité {di3('audit_nationality_group')} ; permutation : genre {perm(e15, 'audit_gender')}, âge {perm(e15, 'audit_age_band')}, nationalité {perm(e15, 'audit_nationality_group')} (5 % attendus sous indépendance) | FICTIF | idem | idem | âge : écart réel lié à l'expérience ; nationalité : signal faible, non concluant |",
        "CONF-1": f"| CONF-1 | Besoins réels de la semaine soumis à l'obligation d'annonce 2026 (ordonnance du DEFR, RS 823.111.3), site déduit des lots de chaque besoin, bâtiment par prudence | {conf['besoins_soumis']} sur {conf['besoins']} | RÉEL | idem | idem | correspondance CH-ISCO-19 « probable », l'ORP tranche |",
    }


def update_claims(root: Path) -> list[str]:
    path = root / "CLAIMS.md"
    lines = path.read_text("utf-8").splitlines()
    new = claims_lines(root)
    done = []
    for i, line in enumerate(lines):
        cid = line.strip("| ").split(" |")[0] if line.startswith("| ") else ""
        if cid in new:
            lines[i] = new[cid]
            done.append(cid)
    path.write_text("\n".join(lines) + "\n", "utf-8")
    return done


def write_all(root: Path) -> list[Path]:
    docs = root / "docs"
    out = []
    spec = json.loads((docs / "backtest/specialites_v1.json").read_text("utf-8"))
    (docs / "backtest/specialites.md").write_text(specialites_md(spec), "utf-8")
    out.append(docs / "backtest/specialites.md")
    w = json.loads((docs / "modeles/semaine1_v1.json").read_text("utf-8"))
    (docs / "modeles/semaine1_candidats.md").write_text(semaine1_md(w, root / "data/fictif/candidats_300.csv"),
                                                        "utf-8")
    out.append(docs / "modeles/semaine1_candidats.md")
    ph = json.loads((docs / "modeles/phasage_reel_v1.json").read_text("utf-8"))
    (docs / "modeles/phasage_reel.md").write_text(phasage_md(ph), "utf-8")
    out.append(docs / "modeles/phasage_reel.md")
    ap = docs / "recherche/apercu_simap.md"
    o = json.loads((docs / "recherche/apercu_simap.json").read_text("utf-8"))
    ap.write_text(apercu_fix(ap.read_text("utf-8"), o), "utf-8")
    out.append(ap)
    for p in out:
        p.write_text(p.read_text("utf-8").replace("— %", "—"), "utf-8")
    update_claims(root)
    out.append(root / "CLAIMS.md")
    return out
