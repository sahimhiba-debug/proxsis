# Règles contre Apertus sur le jeu réel — protocole et statut

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

**Statut au 2026-10-05 : pas encore mesuré.** Deux préalables manquent :

1. le jeu réel v2 doit être **annoté par l'équipe puis gelé**
   (`docs/annotation/guide_reel_v2.md`) ;
2. la **clé Public AI** n'est pas disponible dans la session du Mac.

Aucun texte du jeu réel n'a été soumis aux règles ni à Apertus avant le gel :
la commande refuse un fichier dont l'empreinte n'est pas inscrite dans
`data/annotations/FROZEN.md` (`proxsis.compare_extractors.NotFrozenError`,
testé).

## Passerelle Public AI (vérifié le 2026-10-05)

| Élément | Valeur | Source |
|---|---|---|
| Base | `https://api.publicai.co/v1` (compatible OpenAI) | [documentation Public AI](https://platform.publicai.co/docs), lue le 2026-10-05 ; le domaine répond (`docs/recherche/reseau.md`) |
| En-têtes | `Authorization: Bearer <clé>` **et `User-Agent` obligatoire** (« prevent bot spamming ») | idem ; envoyé par `OpenAICompatibleProvider` (test `test_user_agent_header_is_sent_public_ai_requires_it`) |
| Modèle | `swiss-ai/apertus-v1.5-8b` (identifiant de l'exemple de la documentation) ; liste complète via `GET /v1/models` avec la clé | idem ; **l'ancien défaut `swiss-ai/apertus-70b-instruct` n'était pas vérifié** |
| Sortie structurée | `response_format: json_schema`, repli sur un appel d'outil forcé si refusé | non documenté sur la page lue : **à vérifier au premier appel** |
| Limites de débit | selon l'offre (Free, Plus, Pro, Enterprise) | page « Plans & Rate Limits », non lue |
| Conditions, conservation des données | non lues (« Terms & Privacy ») | **à lire avant d'envoyer des textes** ; on n'envoie que des publications officielles filtrées, jamais de données de candidats ni de données internes Flexsis |

## La clé : jamais dans un fichier ni dans un journal

`proxsis.llm.secrets.publicai_api_key()` lit `PUBLICAI_API_KEY`, sinon (macOS)
le trousseau, service `proxsis-publicai`. Pour l'y ranger une fois (la valeur
est demandée de façon masquée et ne passe pas par l'historique du terminal) :

```bash
security add-generic-password -a "$USER" -s proxsis-publicai -w
```

Le fournisseur n'affiche jamais la clé (`repr`, messages d'erreur : testé).

## Mesure, une fois le jeu gelé

```bash
cd python && . .venv/bin/activate
proxsis comparer-extraction --apertus --accord <accord.json>
```

`--accord` signale, pour chaque extracteur, les champs sur lesquels les
annotateurs humains ne s'accordent pas (`champs_a_prendre_avec_precaution`).

Sortie : `docs/modeles/m3_comparaison_reel_v2.json` (données `RÉEL`) :
exactitude par champ, F1 des métiers, taux de remplissage à tort, fuites de
données personnelles (motifs : `[masqué]`, `[particulier]`, civilité + nom,
e-mail, téléphone recopiés dans une sortie), latence, par langue. 150 appels
Apertus (un par texte, mis en cache pendant la mesure).

**Lecture attendue, à confirmer** : les règles ont été écrites sur des textes
fictifs de l'agent ; sur de vraies adjudications simap, dont la mise en forme
est différente (`Adjudicataire : …` produit par notre rendu), leurs scores
réels peuvent être très différents des 0,92–1,00 mesurés sur le jeu v1
(`CLAIMS.md` M3-1, optimiste ; **monde fictif : prouve que le code fonctionne,
pas sa performance réelle**). C'est précisément ce que la mesure dira.

**Biais connu du jeu simap (audit M3)** : le texte annoté est un rendu
Proxsis des champs de l'API, avec des étiquettes (« Adjudicataire : ») que
les règles reconnaissent déjà. Le jeu manuel BO VS / FOSC (texte officiel
collé tel quel) est la mesure de référence.
