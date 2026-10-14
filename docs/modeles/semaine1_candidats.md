# Semaine 1 : candidats FICTIFS, propositions, redéploiement, conformité (livrables 2.4, 2.5, 2.6)

> **Monde fictif : prouve que le code fonctionne, pas sa performance réelle.** Les candidats sont inventés. Les besoins auxquels ils sont proposés sont **réels** : listes d'appels du
2026-10-05 (Bâtiment, Électricité, Technique), bâties sur les marchés publics simap. *Ceci n'est pas une publication officielle. Les données publiées sur la plateforme www.simap.ch font foi.*

Commandes, depuis `python/` : `proxsis candidats` (vivier, graine 42) → `proxsis moteur-semaine1` →
`docs/modeles/semaine1_v1.json` ; ce document : `proxsis docs-semaine1`. Localités : copie versionnée du
répertoire swisstopo `../data/referentiels/localites_vs.csv` (sha256 `8e7eaf479c217794…`, audit M10).

## 2.4 Les 300 candidats FICTIFS

- Aucun nom (« Candidat·e 042 (FICTIF) »). Les attributs protégés (`audit_*`) ne servent qu'à l'audit.
- **Inventé** (hypothèses, `proxsis/synth/candidates.py`) : parts par spécialité, formation, permis, langues,
  statut, inscription à l'ORP (40 % des disponibles).
- **Calculé par la règle** : la catégorie CCT (art. 20 al. 4 et 5 CCT Location de services 2026, `proxsis/cct.py`).
  « Quatre ans de pratique et 1 000 heures par année civile » donne **spécialisé** (22.76 CHF/h), pas qualifié ;
  63 profils relèvent du point ouvert (heures insuffisantes ou non renseignées), lu de façon prudente.
- **Composition** : qualifié 173, non qualifié 114, spécialisé 13 ;
  en mission 171, disponible 81, indisponible 48 ; Bâtiment
  166, Industrie 59, Électricité 46, Technique 29 ;
  inscrits à l'ORP 34.
- **Salaire affiché** (audit M7) : pour le gros œuvre, le second œuvre, l'électricité et la technique du bâtiment,
  la CCT étendue de l'entreprise de mission prime (CN, second-œuvre romand, CCT valaisannes) : l'appli affiche la CCT
  probable et renvoie à tempdata.ch. Le minimum CCT LS n'est affiché que pour les métiers sans CCT étendue probable.
  Le Valais relève des montants standard de la CCT LS d'après l'annexe 3 (déduction de lecture, à confirmer).

### Propositions : critères stricts, puis proximité

- **60 besoins réels** (une entreprise × un métier) ; tous ont au moins une proposition.
- Entonnoir moyen : 300 → métier 46 →
  permis 46 → disponibles 17
  → dans le rayon **8**.
- Poste soumis à l'obligation d'annonce : chaque candidat non inscrit à l'ORP porte « contact possible dès le … »
  (directive SECO B8) ; 83 propositions concernées.

### Audit d'équité reproductible

20 viviers (le vivier publié, puis les graines 1001 à 1019), les mêmes 60 besoins réels, 5 propositions
par besoin. Ratio d'impact = taux le plus bas / taux le plus haut (groupes d'au moins 20 éligibles), référence au
hasard (5 tirées au hasard parmi les éligibles), et **test de permutation** (audit M8) : choix du moteur gardés,
attribut permuté entre candidats, khi-deux des sélections par groupe ; sous indépendance, 5 % des viviers ont
p < 0,05.

| Réglage | Ratio genre | Ratio âge | Ratio nationalité | Expérience moyenne des proposés |
|---|---|---|---|---|
| Plafond d'expérience 15 ans (actuel) | 0,80 | 0,61 | 0,73 | 12,5 ans |
| Plafond 5 ans (ADR-0012, proposé) | 0,78 | 0,63 | 0,73 | 11,8 ans |
| Référence : tirage au hasard | 0,87 | 0,73 | 0,81 | 10,4 ans |

Test de permutation, viviers avec p < 0,05 :

- plafond 15 ans : genre 1 sur 20 (p médiane 0,50) ; âge 6 sur 20 (p médiane 0,15) ; nationalité 1 sur 20 (p médiane 0,39) ;
- plafond 5 ans : genre 0 sur 20 (p médiane 0,53) ; âge 4 sur 20 (p médiane 0,25) ; nationalité 2 sur 20 (p médiane 0,46).

Taux moyens de sélection (plafond 15 ans) : âge 18-25 37,2 % ; 26-35 48,1 % ; 36-50 54,2 % ; 51+ 54,4 % ; nationalité CH 48,7 % ; UE/AELE 50,1 % ; autre 50,3 % ;
genre f 53,3 % ; m 48,8 %.

Lecture (conclusions calculées à partir des comptes ci-dessus ; sous indépendance, 1 vivier sur 20 environ a
p < 0,05 par hasard) :

1. **Le ratio min/max est très bruité** sur ces volumes (même au hasard, il vaut 0,73 pour
   l'âge) : le seuil de 0,8 seul ne prouve rien ; le test de permutation est le test retenu.
2. **Âge** : **écart réel** (6 viviers sur 20 avec p < 0,05). Il tient à l'expérience (20 % du score) : les 18-25 ans sont moins sélectionnés. Le plafond à 5 ans le réduit un peu ; c'est le compromis de l'ADR-0012, en attente de décision. Le code reste à 15 ans.
3. **Nationalité** : **pas d'écart au-delà du hasard** (1 vivier(s) sur 20 avec p < 0,05). Ni la langue ni le permis n'entrent dans le score ; à
   surveiller sur les vrais candidats.
4. **Genre** : **pas d'écart au-delà du hasard** (1 vivier(s) sur 20 avec p < 0,05).

## 2.5 « Fin de mission, prochaine mission » (FICTIF)

Travailleurs dont la mission finit dans les **trois semaines**, rapprochés des besoins **réels** prévus : métier
identique ou proche, **permis légalement requis** (audit M6), rayon, besoin actif dans les 21 jours ; capacité =
pic de l'estimation médiane ; pour un poste soumis à l'obligation d'annonce, un candidat non inscrit à l'ORP
n'est placé qu'après la date de publication libre (audit M4).

- 43 fins de mission ; **26 redéployés (60,5 %)**.
- Motifs de non-redéploiement : aucun besoin prévu compatible (métier) : 11, besoins compatibles déjà pourvus par d'autres fins de mission : 4, besoins compatibles hors de son rayon de déplacement : 2. Le premier tient surtout aux travailleurs de l'**Industrie** : aucune liste
  Industrie (signal public insuffisant, `docs/recherche/apercu_simap.md`).

## 2.6 Conformité : obligation d'annonce 2026

Sources : art. 21a LEI ; art. 53a à 53f OSE ; ordonnance du DEFR du 27.11.2025 (RS 823.111.3, Fedlex) ; directive
SECO B8, B14, B16-B17, B33, B36 ; CH-ISCO-19 (OFS).

- Liste 2026 codée depuis les **préfixes de l'ordonnance** (« 93 sans 93120 »).
- **Site de chaque besoin** déduit des phases de ses propres lots ; « génie civil » seulement si **tous** sont du
  génie civil, sinon bâtiment par prudence (audit M4) : **22 besoins soumis sur 60**,
  comptés besoin par besoin.
- Exceptions (mission de 14 jours au plus ; personne inscrite à l'ORP), règles fermes (ne jamais découper une mission,
  B33 ; pas de contact avant la publication libre, B8).
- Compte à rebours de cinq jours ouvrés, testé sur l'exemple officiel (5.7.2021 → 13.7.2021) ; jours fériés
  valaisans à confirmer avec la loi cantonale (fêtes communales non traitées).
- Texte d'annonce FR et DE avec le contenu de l'art. 53b al. 2 OSE, **adresse comprise** (audit M5).
- Aucun appel à Job-Room.
