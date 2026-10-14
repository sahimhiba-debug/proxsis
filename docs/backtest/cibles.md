# Cibles du backtest (vérité terrain mesurable avec des données publiques)

Code : `python/src/proxsis/targets.py`. Tests : `python/tests/test_features_targets.py`.

## Définitions

Pour une semaine de référence T (un lundi) et une entreprise e :

| Code | Définition | Pourquoi |
|---|---|---|
| `offre_8s` (cible A) | e publie au moins une offre d'emploi dans [T, T + 56 jours[ | Simple, observable ; mais une entreprise qui publie en continu est « facile » et le consultant la voit déjà. |
| `nouveau_besoin_8s` (cible B, **principale**) | A, **et** e n'a publié aucune offre dans les 56 jours avant T | C'est là que l'anticipation a de la valeur : le besoin n'est pas encore visible dans une annonce. Les entreprises qui ont une offre en cours sont exclues du classement pour cette cible. |
| `offre_batiment_8s` (cible C) | A, restreinte aux métiers du bâtiment (`taxonomy.TRADES[...].construction`) | Exemple du cahier des charges (« offre d'emploi dans le bâtiment dans les huit semaines »). |
| `besoin_temporaire_latent` | e a une vague d'embauche avec besoin de temporaires dans [T, T + 8 semaines[ | **Monde FICTIF seulement** : le besoin réel n'est pas observable dans les données publiques ; cette cible mesure l'écart entre l'indicateur public et le vrai besoin. |

## Mesures associées

- **P@10 liste agence (opérationnelle)** : chaque agence reçoit 10 entreprises par semaine ; une entreprise
  proposée n'est pas reproposée pendant 6 semaines (même nombre d'appels distincts pour toutes les méthodes).
- **P@20 liste globale**, **rappel** des listes d'agence, **taux de détection** des épisodes de besoin.
- **Jours d'avance** : pour un épisode détecté (entreprise, date de la première offre), nombre de jours entre la
  **première** apparition de l'entreprise dans la liste de son agence (dans les 8 semaines précédentes) et la
  publication de l'offre.
- **Calibration** (Brier, ECE, table de fiabilité) des modèles probabilistes ; taux de réalisation par niveau
  d'alerte pour M0.
- Intervalles de confiance à 95 % par **bootstrap par blocs de semaines** ; écarts appariés contre la meilleure
  méthode naïve.

## Limites (à garder en tête)

1. **Une offre publiée n'est qu'un indicateur du besoin.** Des besoins ne donnent jamais d'offre (réseau,
   bouche-à-oreille, agence déjà en place) ; certaines offres sont permanentes (« vivier »).
2. **Les offres d'agences doivent être exclues** (sinon on mesure l'activité des concurrents). Dans les données
   réelles, il faudra une règle fiable (raison sociale de l'annonceur = l'entreprise, pas une agence).
3. **Sources d'offres autorisées seulement** : pages carrières des entreprises (lecture ponctuelle, robots.txt),
   Job-Room / agrégateurs / x28 **avec accord écrit**. La couverture de la cible dépend de ces accords.
4. **Horizon de 8 semaines** : choix métier à confirmer avec Flexsis (délai entre un appel et une commande).
5. **Historique réel court** : simap.ch n'a pas repris les publications d'avant juillet 2024 ; le backtest réel
   couvrira environ deux ans.
6. **Le monde FICTIF reflète nos hypothèses** : les chiffres mesurés dessus valident la mécanique, pas la valeur
   commerciale. Le pilote randomisé (`docs/affaires/pilote.md`) mesure la valeur réelle.
