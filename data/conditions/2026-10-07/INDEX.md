# Archive des conditions — 2026-10-07 (simap.ch)

Relecture des conditions de simap.ch, demandée par le brief « à distance » (§ 7) : la version du dépôt (lue le
05.10.2026, `../2026-10-05/INDEX.md`) est-elle toujours en vigueur, et que disent-elles exactement sur l'heure de
transmission, la séparation du contenu publié, les corrections et les pièces jointes ? Passages cités et conséquences :
[`docs/DONNEES.md`](../../../docs/DONNEES.md), § « Conditions de simap.ch ».

## Ce qui a été lu, et comment

Trois requêtes, à plus de 2 s d'intervalle, User-Agent du projet sous son ancien nom (`…/0.1 (prototype de recherche Hack VS 2026)`),
le **07.10.2026 vers 09:54 UTC** : `robots.txt`, puis les pages publiques `/fr/about/legal` et `/de/about/legal`
(non interdites par robots.txt ; pages servies avec leur texte, sans exécuter de script). Aucune page interdite,
aucun appel à l'API pour cette relecture.

| Fichier ou document | URL | Version affichée | Empreinte SHA-256 |
|---|---|---|---|
| `robots_www.simap.ch.txt` (copie brute) | https://www.simap.ch/robots.txt | — | `795f770781ef096296906dd6d05bfe96652912a58f71474d24cb806b9457cf07` (**identique** à la copie du 05.10.2026) |
| Page HTML allemande, telle que reçue (non versionnée) | https://www.simap.ch/de/about/legal | — | `eb5ec20299172caeb0d9c04482cfab3c61b2fb39ba9d9dbca8831797b8eabacb` |
| Page HTML française, telle que reçue (non versionnée) | https://www.simap.ch/fr/about/legal | — | `4c8b5cca2b11d7d41692552773801f59a358d830aacbf05d057952d3b7bfd476` |
| « AGB der Nutzung des Application Programming Interfaces (API) von simap.ch » (texte de la section, **version qui fait foi**, ch. 13) | page allemande | « Version vom 29.09.2009 », modifiée le 30.03.2017 et le 13.11.2023 | `61ea8a2f4e902787a0cc316cac597c96ac39111366c093ecdbf2f146023357c7` |
| « Conditions générales (CG) pour l'utilisation de l'Application Programming Interface (API) de simap.ch » (texte de la section) | page française | « Version du 30 septembre 2023 », mêmes modifications (30.3.2017, 13.11.2023) | `d393424d2a0291d4e619a1f2cffbff558ed30f60ddd01d06c4ece680212778d5` |
| « Allgemeine Geschäftsbedingungen (AGB) zur Nutzung von www.simap.ch » (texte de la section ; elles s'appliquent à l'API pour tout ce que les AGB API ne règlent pas, ch. 2) | page allemande | « Version vom 29.09.2009 », dernière modification le **01.07.2026** | `ca288797e65efed6f9a8addf4e81b432465dcee3b9b70b73f6877da826592ff4` |
| Même texte en français (titre affiché par erreur : « … de l'interface de programmation de www.simap.ch ») | page française | « Version du 30 septembre 2023 », dernière modification le 01.07.2026 | `59606bde5bb00b7ba92488ea469270848352e636042d3feedcdf7d1e78074e24` |

**Version** : les AGB API n'ont pas changé depuis la lecture du 05.10.2026 ; leur dernière modification date du
13.11.2023 (« Anpassung an neue Plattform »). La « version du 30.09.2023 » du dépôt est le titre de la page
française ; la page allemande, qui fait foi, titre « Version vom 29.09.2009 » avec les mêmes modifications. Les AGB
générales ont été modifiées le 01.07.2026 (« Div. redaktionelle Anpassungen, Löschen Abschnitte Parallelbetrieb …
und Datenspeicherung / Aufbewahrung / Archivierung, Anpassung Abschnitt Datenschutz ») ; la déclaration de
confidentialité de simap est en « Version 4.0 vom 01.07.2026 ».

**Copies** : comme le 05.10.2026, le texte des conditions n'est pas versionné (droit d'auteur) ; seuls les passages
utiles sont cités dans `docs/DONNEES.md`. Les empreintes ci-dessus permettent de vérifier qu'une copie est bien le
texte lu ce jour-là.

## Calcul des empreintes des sections

Texte de la page = contenu HTML hors balises `script` et `style`, un saut de ligne à chaque balise `p`, `div`, `li`,
`h1` à `h4`, `br`, `tr`, puis lignes vides fusionnées ; section = du titre (inclus) au titre suivant (exclu) ;
empreinte du texte encodé en UTF-8.

```python
import hashlib, re
from html.parser import HTMLParser

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.out, self.skip = [], 0
    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "br", "tr"): self.out.append("\n")
    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style")
    def handle_data(self, data):
        if not self.skip: self.out.append(data)

def section(html: str, start: str, end: str) -> str:
    p = Text(); p.feed(html); text = re.sub(r"\n\s*\n+", "\n", "".join(p.out))
    i = text.index(start); return text[i:text.index(end, i + len(start))]

# AGB API (DE) : section(page_de, "AGB der Nutzung des Application Programming Interfaces (API) von simap.ch",
#                        "Datenschutzerklärung des Vereins simap.ch")
# CG API (FR) : section(page_fr, "Conditions générales (CG) pour l'utilisation de l'Application Programming Interface (API) de simap.ch",
#                       "Déclaration de confidentialité de l'association simap.ch") ; on garde le saut de ligne final
# AGB générales (DE) : section(page_de, "Allgemeine Geschäftsbedingungen (AGB) zur Nutzung von www.simap.ch",
#                              "AGB Online Abonnent simap.ch")
# CG générales (FR) : section(page_fr, "Conditions générales (CG) pour l'utilisation de l'interface de programmation de www.simap.ch",
#                             "Conditions générales (CG) pour les abonnés en ligne de simap.ch")
# hashlib.sha256(s.encode("utf-8")).hexdigest()
```
