# Guide d'annotation — extraction des publications (M3)

But : mesurer honnêtement l'extraction automatique (règles, Apertus, modèle spécialisé) sur
des publications officielles en français et en allemand.

## Champs annotés (`gold`)

| Champ | Valeur | Règle |
|---|---|---|
| `doc_type` | `permis_construire` · `adjudication` · `registre_commerce` | Type de publication. |
| `company_name` | texte ou `null` | La **personne morale** concernée : requérant (permis), adjudicataire (marché ; s'il y a plusieurs lots, le premier mentionné), société inscrite (RC). **`null` si le requérant est une personne physique** : on n'annote jamais un nom de particulier. Forme juridique incluse, telle qu'écrite. |
| `uid` | `CHE#########` ou `null` | IDE de l'entreprise concernée s'il figure dans le texte, normalisé sans ponctuation. |
| `commune` | texte ou `null` | Commune **du projet** (permis, marché) — à défaut celle de l'autorité ; pour le RC, le **siège** (le nouveau siège en cas de transfert). |
| `amount_chf` | nombre ou `null` | Coût estimé (permis), prix adjugé (premier lot), capital (RC : nouveau capital). « 11,5 millions » → 11500000. |
| `rc_subtype` | `nouvelle_inscription` · `succursale` · `augmentation_capital` · `changement_but` · `transfert_siege` · `liquidation` · `radiation` · `null` | RC seulement. |
| `trades` | liste de codes métier (`proxsis.taxonomy.TRADES`) | Métiers dont le projet fera probablement naître un besoin : construction neuve de bâtiment → `macon`, `manoeuvre_construction` ; routes, terrassements, conduites → `machiniste`, `manoeuvre_construction` ; CFC/BKP 23 → `electricien` ; 25 → `installateur_sanitaire` ; 285 → `peintre` ; charpente/Holzbau → `charpentier` ; grue/Kran → `grutier`. RC : liste vide. |
| `private_person` | booléen | Vrai si le texte mentionne une personne physique (requérant privé, propriétaire, associé, liquidateur…). Sert à mesurer le filtre de données personnelles : l'extraction ne doit **jamais** recopier ces noms. |

## Métriques

- Exactitude par champ (comparaison normalisée : casse, accents, espaces ; montants à 1 % près).
- F1 sur l'ensemble des métiers (`trades`).
- Taux de remplissage à tort (champ rempli alors que la référence est `null`).
- **Fuites de données personnelles** : nombre de sorties contenant un nom de particulier (objectif : 0).

## Protocole pour le jeu réel (à faire par l'équipe)

1. Tirer au hasard ≥ 200 publications réelles (≈ 1/3 par type, ≈ 1/2 FR et 1/2 DE, plusieurs cantons),
   depuis les sources autorisées (amtsblattportal, simap), en conservant le lien et la date.
2. Deux annotateurs indépendants par publication ; mesurer l'accord (kappa de Cohen par champ) ;
   arbitrage par une troisième personne.
3. Geler le fichier (empreinte SHA-256 dans `data/annotations/FROZEN.md`) **avant** tout essai.
4. Les textes réels contiennent des noms de particuliers : le fichier annoté est stocké hors du dépôt
   public (accès restreint), seule l'empreinte est versionnée.
