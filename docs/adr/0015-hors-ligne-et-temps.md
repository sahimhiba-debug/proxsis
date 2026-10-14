# ADR-0015 — Hors ligne par copie statique versionnée, rien à l'exécution hors du site, une seule date

- Statut : accepté
- Date : 2026-10-07
- Couloir : produit

## Contexte
La démonstration a lieu dans une salle dont le réseau n'est pas garanti, et doit montrer la même chose quel que soit
le jour où on la joue. Trois sources de dérive existaient : l'horloge de l'ordinateur (huit écrans changeaient avec la
date), les polices téléchargées chez Google Fonts à chaque construction, et un éventuel cache du navigateur.

## Décision
- **Aucun appel hors du site pendant la démonstration** : données, polices (`public/fonts`, SIL OFL) et scripts sont
  dans la construction ; la politique de contenu le confirme ; `e2e/reseau.spec.ts` le prouve sur chaque page et
  chaque étape. Seule exception facultative : l'envoi d'un retour d'appel à Supabase, si l'agence le configure.
- **Une seule date de démonstration**, le lundi de la liste (`meta.semaine`) ; aucun écran ne lit l'horloge
  (`src/lib/clock.test.ts`) ; les 60 captures restent identiques à J+2, J+30 et J+90.
- **Hors ligne = copie statique versionnée**, pas de service worker : `scripts/copie-hors-ligne.sh` construit l'export
  d'un commit depuis une extraction propre, l'essaie, le nomme par sa date et son commit, avec l'empreinte de chaque
  fichier ; il s'ouvre avec un petit serveur local (trois lignes dans son `LISEZMOI.txt`).

## Alternatives considérées
Un service worker (application installable hors ligne) : il garde dans le navigateur une version qui peut être
périmée des semaines plus tard, sans que la personne qui présente le sache ; pas de bénéfice pour une démonstration
jouée depuis un ordinateur préparé. `next/font/google` : pratique, mais il dépend du réseau et du contenu de Google
Fonts au moment de la construction.

## Conséquences
La section « Cette semaine, en direct de simap » est la seule qui change avec le temps : elle est réécrite chaque lundi
par une tâche automatique, seulement si tous les contrôles passent, et masquée dans les captures de référence.
(Depuis l'ADR-0016, 13.10.2026 : « Chaque matin, en direct de simap », réécrite chaque jour ouvrable ; même règle.)
Raison de revenir dessus : un usage quotidien par les consultants sur leur téléphone, où une application installable
hors ligne aurait du sens (avec un cache dont le nom suit la version).

## Mesures liées
Aucune.
