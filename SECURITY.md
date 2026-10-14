# Sécurité

## Signaler une faille

N'ouvrez **pas** d'issue publique. Utilisez le signalement privé de GitHub : onglet **Security** du dépôt →
**Report a vulnerability**. Décrivez ce que vous avez trouvé, comment le reproduire et ce qui est exposé ; ne joignez
aucune donnée personnelle réelle.

Vous recevrez un accusé de réception, puis la suite donnée : correction, mesure d'atténuation ou explication.

## Ce qui compte particulièrement ici

- **Données personnelles** : Proxsis ne doit contenir ni afficher aucun nom de particulier (filtre `proxsis.pii`).
  Un nom de personne privée visible dans l'application, un export ou le dépôt est traité comme une faille.
- **Secrets** : aucune clé dans le dépôt ni dans l'application ; seule la clé publique `anon` de Supabase peut être
  servie au navigateur, et la clé `service_role` jamais.
- **Sources** : aucun accès automatisé aux portails qui l'interdisent (`proxsis.http.MANUAL_ONLY_HOSTS`).

## Contrôles en place

- CI à chaque pull request : tests du moteur, de l'application, des parcours (aucune requête hors du site) et des droits
  de la base (`supabase/tests/run.sh`).
- `scripts/securite/audit.sh` : failles connues des dépendances, recherche de secrets dans les fichiers et dans tout
  l'historique, licences des dépendances livrées.
- Dependabot : mises à jour des dépendances npm, Python et des actions GitHub.

## Versions prises en charge

Seule la branche `main` (la version en ligne) reçoit des corrections.
