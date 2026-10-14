# ADR-0013 — Liste d'appels par spécialité : fréquence d'abord, signaux du radar par-dessus

- Statut : **accepté** (règle « simple d'abord », CONTRIBUTING.md n° 8) ; à revoir après la première vérité terrain des consultants
- Date : 2026-10-06
- Couloir : modèles et évaluation (session Mac)
- Complète : ADR-0003 (protocole de backtest), ADR-0004 (M0)

## Contexte

La mission « Lundi 8 h à Martigny » demande un classement « fréquence et récence comme base, les signaux du radar par-dessus, et un détecteur de surprises », avec un mode par spécialité d'agence (Bâtiment, Industrie, Électricité). Le backtest réel par spécialité (`docs/backtest/specialites.md`, CLAIMS REEL-SPEC-*) compare, sur 57 semaines et les entreprises valaisannes, la fréquence sur 52 semaines et un modèle combiné (régression logistique sur fréquence, récence, montants, adjudicateurs, tendance).

## Décision

1. **Ordre de la liste** : nombre de marchés de la spécialité sur 52 semaines, puis le plus récent. Le modèle combiné reste disponible (`--ordre combine`). Il ne devient l'ordre par défaut d'une spécialité que si la borne basse de l'IC 95 % de (combiné − fréquence) sur T0 est positive. C'est la règle écrite dans `proxsis backtest-specialites`, fixée avant la mesure.
2. **Signaux du radar par-dessus**, affichés comme raisons, sans réordonner la liste :
   - main-d'œuvre mobilisée estimée par le phasage ;
   - lots attendus sur ses chantiers ;
   - demandes d'autorisation de construire dans la commune ;
   - citation de l'entreprise dans une demande d'autorisation.

   Ils n'entreront dans l'ordre qu'après un backtest qui les valide : les permis importés à la main n'ont pas encore d'historique.
3. **Détecteur de surprises** : drapeaux « activité qui bondit » et « nouveau venu ». Les surprises hors des k premières sont listées à part, trois au plus, et validées par les consultants comme les autres.

## Conséquences

- **Mesuré (Bâtiment)** :
  - fréquence 65,6 % contre combiné 67,0 % (+1,4 point, IC −0,5 à +3,2) : le combiné n'est pas retenu ;
  - « activité qui bondit » : 47,7 % de réussite contre 20,5 % de base ;
  - « nouveau venu » : 9,6 %. Il ne prédit pas un nouveau marché et reste un indice de prospection, dit tel quel.
- **Électricité et Technique** : 18 et 43 entreprises valaisannes. La liste y est un appoint.
- **Industrie** : aucun signal public suffisant à ce jour. La collecte des marchés de fournitures simap est en cours ; le mode Industrie sera évalué de la même façon avant d'être montré.
- Les besoins chiffrés ne sont affichés que si le montant du lot est publié, ou estimable par le phasage mesuré sur le même chantier. Sinon : « non chiffré ».
