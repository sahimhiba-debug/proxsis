# Contribuer à Proxsis

Merci de votre intérêt. Proxsis est un prototype : avant un changement important, ouvrez d'abord une issue pour en
parler. Ce qu'on construit est dans [PRODUCT.md](PRODUCT.md), le glossaire dans [CONTEXT.md](CONTEXT.md) et chaque
chiffre public dans [CLAIMS.md](CLAIMS.md).

## Installer

Versions exactes, celles que la CI vérifie :

- **Node.js 22** (`apps/web/.nvmrc`), dépendances à version exacte (`npm ci`) ;
- **[uv](https://docs.astral.sh/uv/)**, qui installe lui-même **Python 3.12.13** (`python/.python-version`) et les
  paquets exacts du verrou (`python/uv.lock`) ;
- sur macOS, `brew install libomp` (LightGBM) ; PostgreSQL pour les tests de la base (`make db-test`).

```bash
make install   # moteur Python (python/.venv) et application web (npm ci)
make dev       # l'application sur http://localhost:3000
make check     # tout ce que la CI vérifie, sauf les parcours dans le navigateur
```

Parcours dans le navigateur (comme en CI) :

```bash
cd apps/web && npm run e2e:prepare && npx playwright test
cd apps/web && npm run build:static && npm run moteurs
```

## Les règles qui ne se discutent pas

1. **Test rouge d'abord.** Tout code commence par un test qui échoue (pytest pour le moteur, vitest pour la logique
   web, Playwright pour les parcours).
2. **Chaque chiffre a sa source.** Un chiffre affiché (application, README, documents) renvoie à une ligne de
   [CLAIMS.md](CLAIMS.md), reliée à une commande qui le refait. Si vous ne savez pas, écrivez « inconnu ».
3. **Des entreprises, jamais des particuliers.** Le filtre `proxsis.pii` passe avant toute écriture (rubriques
   faillites, poursuites, successions et état civil exclues ; aucun nom de propriétaire privé) ; aucune donnée
   personnelle dans le dépôt, les tests, les captures ou les messages. L'outil aide, le consultant décide, et chaque
   proposition montre sa logique (nLPD, art. 21).
4. **Provenance et dates.** Chaque ligne de donnée porte `source`, `url`, `retrieved_at` et `license` ; toute donnée
   datée a une `event_date` et une `available_at`, et un modèle « vu à la date T » n'utilise que `available_at <= T`.
5. **Fictif marqué comme tel.** Client, candidat, mission ou commande : `fictif: true` dans les données, mention à
   l'écran.
6. **Sources respectées.** Conditions d'utilisation, `robots.txt` et limites de débit ; ni portails d'emploi privés,
   ni réseaux sociaux ; mention de la source à chaque affichage.
7. **Deux langues.** Interface en français et en allemand de Suisse (« ss », jamais « ß ») ; aucun texte français sur
   une page allemande.
8. **Le simple d'abord.** Un modèle plus complexe n'est gardé que s'il bat le simple sur le backtest sans fuite ;
   chaque choix a son ADR dans [docs/adr/](docs/adr/).
9. **Aucun secret** dans le dépôt : seul `.env.example` est versionné.
10. **Le code des autres** : aucune ligne copiée d'un dépôt sans licence compatible ; une idée reprise se dit dans
    l'ADR qui la retient.
11. **Parité IA.** Tout marche avec le faux fournisseur (`FakeLLM`) ; Apertus (Public AI, API compatible OpenAI) se
    branche derrière l'interface `proxsis.llm.LLMProvider`.
12. **Démo hors ligne et en ligne** : la démonstration se rejoue depuis le cache, réseau coupé.

## Proposer un changement

1. Créez une branche depuis `main`.
2. Écrivez le test, puis le code ; lancez `make check` (et les parcours si l'interface change).
3. Ouvrez une pull request avec le modèle proposé. Elle est fusionnée (en squash) quand les cinq contrôles de la CI
   sont verts : `python`, `web`, `e2e`, `moteurs`, `database`.

La branche `main` est protégée (règles dans [.github/rulesets/main.json](.github/rulesets/main.json)) : ni poussée
forcée ni suppression, historique linéaire, fusion par pull request seulement, les cinq contrôles exigés.

Un test instable se corrige à sa cause : pas de `skip`, pas de seuil abaissé, pas de référence visuelle régénérée sans
expliquer l'écart. Les références visuelles au pixel sont faites sur macOS (`apps/web/e2e/visuel/references/darwin/`)
et se rejouent sur macOS.

## Messages de commit

En français, au présent ou au nominatif, qui disent **ce qui change et pourquoi** : « Carte : contours des communes
embarqués hors ligne (swisstopo) ». Un commit = un changement cohérent. Ajoutez les fichiers un par un plutôt que
`git add -A`, et relisez `git diff --cached --name-only` avant de valider.

## Signaler une faille

Pas d'issue publique : voir [SECURITY.md](SECURITY.md).
