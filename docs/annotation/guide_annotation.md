# Guide d'annotation — à lire avant de commencer (une page)

On annote de **vraies** publications officielles pour mesurer honnêtement
l'extraction automatique. Annotez **ce que dit le texte**, pas ce que vous
savez par ailleurs. Ne regardez ni les annotations des autres ni une sortie
de modèle. En cas de doute : **laissez vide** et écrivez pourquoi dans
« commentaire ».

## Les champs

| Champ | Définition | Si c'est ambigu |
|---|---|---|
| **Type** | `permis_construire` (demande d'autorisation de construire), `adjudication` (marché attribué) ou `registre_commerce` (inscription ou mutation au RC). | Pré-rempli d'après la rubrique ; ne le changez que s'il est faux. |
| **Entreprise** | La **personne morale** concernée, avec sa forme juridique, telle qu'écrite : le requérant (permis), l'adjudicataire (marché ; s'il y en a plusieurs, le premier), la société inscrite (RC). | **Vide** si c'est un particulier, `[masqué]` ou `[particulier]`. Plusieurs requérants : la première personne morale citée. Commune, canton ou bourgeoisie requérant : on l'annote (c'est une personne morale). Ne jamais recopier un nom de particulier. |
| **IDE** | `CHE-123.456.789` s'il figure dans le texte. | Vide sinon ; ne le cherchez pas ailleurs. |
| **Commune** | Permis et marché : commune **du projet**. RC : **siège** (le nouveau en cas de transfert). Nom seul, sans NPA ni canton. | Projet sur plusieurs communes : la première citée. Lieu-dit ou village : la commune politique si le texte la donne, sinon le nom écrit. |
| **Montant (CHF)** | Permis : coût des travaux. Marché : prix adjugé (premier lauréat). RC : capital (nouveau capital si augmentation). En francs, chiffres seuls : « 1,2 Mio » → `1200000`. | Fourchette « de 1 à 2 Mio » : la borne haute. HT ou TTC : tel qu'écrit. Pas de montant : vide. |
| **Sous-type RC** | `nouvelle_inscription`, `succursale`, `augmentation_capital`, `changement_but`, `transfert_siege`, `liquidation`, `radiation`. | Plusieurs mutations : la plus importante pour l'emploi, dans cet ordre : nouvelle inscription > succursale > transfert > augmentation > but > liquidation > radiation. |
| **Métiers** | Métiers dont le projet fera **probablement** naître un besoin de personnel : bâtiment neuf ou transformation lourde → maçon et manœuvre ; routes, conduites, terrassement → machiniste et manœuvre ; électricité (CFC 23) → électricien ; sanitaire (CFC 25) → installateur sanitaire ; peinture (CFC 285) → peintre ; charpente, bois → charpentier ; grue → grutier. RC : selon le **but** (ex. « travaux de maçonnerie » → maçon). | Petits travaux (pose d'un velux, cabane de jardin) : aucun métier. Études, conseil, informatique, simple fourniture : aucun métier. |
| **Date de l'événement** | Marché : date de la **décision** d'adjudication. RC : date d'**inscription au journal du registre** (« journal n° … du … », « Tagesregister Nr. … vom … ») si elle figure. Permis : **fin du délai d'opposition** (« jusqu'au … »). Format `AAAA-MM-JJ`. | Pas écrite : vide (ne mettez pas la date de publication, elle est déjà connue). |
| **Début des travaux** | Seulement si le texte annonce une date ou un mois de début (« début des travaux : mars 2027 » → `2027-03-01`). | Sinon vide. |
| **Personne physique mentionnée** | Cochée si le texte mentionne un particulier, y compris masqué (`[masqué]`, `[particulier]`). | En cas de doute : cochée. |
| **Besoin temporaire** | Jugement métier : ce texte peut-il créer un besoin de personnel **temporaire** dans les secteurs de Flexsis (construction, industrie, horlogerie, logistique, pharma) ? `oui` / `non` / `incertain`. | Villa, petit commerce, changement d'adresse : souvent `non` ou `incertain`. |

## Deux exemples annotés (textes FICTIFS)

**Exemple 1 — permis, français.** « Commune de Sion. Mise à l'enquête
publique. Requérant : Exemple Immobilier SA, Sion. Auteur du projet : Bureau
Fictif Sàrl. Objet : construction d'un immeuble de 12 logements avec parking
souterrain, parcelle n° 1234. Coût : CHF 4'800'000.–. Délai d'opposition :
jusqu'au 2 octobre 2026. »

→ Type `permis_construire` · Entreprise `Exemple Immobilier SA` · IDE vide ·
Commune `Sion` · Montant `4800000` · Sous-type RC vide · Métiers `macon`,
`manoeuvre_construction` (pas `grutier` : aucune grue n'est mentionnée) ·
Date de l'événement `2026-10-02` · Début des travaux vide · Personne physique
non · Besoin temporaire `oui`.

**Exemple 2 — registre du commerce, allemand.** « Muster Gebäudetechnik AG,
in Visp, CHE-000.000.001. Statutenänderung. Neuer Sitz: Brig-Glis. Zweck neu:
Ausführung von Sanitär- und Heizungsinstallationen. Eingetragene Personen:
[masqué], Mitglied, mit Einzelunterschrift. Tagesregister Nr. 4321 vom 15.09.2026. »

→ Type `registre_commerce` · Entreprise `Muster Gebäudetechnik AG` · IDE
`CHE-000.000.001` (format d'exemple, invalide exprès) · Commune `Brig-Glis`
(nouveau siège) · Montant vide · Sous-type RC `transfert_siege` (plus important
que le changement de but) · Métiers `installateur_sanitaire` · Date de
l'événement `2026-09-15` · Début des travaux vide · Personne physique **oui**
(`[masqué]`) · Besoin temporaire `incertain`.

## Double annotation

**20 publications** (environ 15 %), tirées au sort, sont annotées par
**deux personnes** qui ne voient pas le travail de l'autre. On calcule
l'accord champ par champ (kappa de Cohen pour les catégories, accord exact
pour les montants, les dates et les noms). **Un champ sur lequel les humains
ne s'accordent pas ne sert pas à juger un modèle sans précaution** : le
rapport de comparaison le signale.
