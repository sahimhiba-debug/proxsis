# Provenance des composants tiers du téléphone (C2)

## Maquette d'iPhone : Magic UI « iphone »

| | |
|---|---|
| Composant | `iphone` (registre Magic UI, type `registry:ui`, composant **gratuit**, pas « Pro ») |
| Récupéré par | le registre shadcn de Magic UI : `https://magicui.design/r/iphone.json` (lu le 06.10.2026) |
| Source | `apps/www/registry/magicui/iphone.tsx` du dépôt `github.com/magicuidesign/magicui` |
| Version | branche `main` au commit `cdb348cb4c72a9b54b554d8617801e479fbc8714` (05.10.2026) ; dernière modification du fichier : commit `913eef524678a22810eaa904192ec6b196520206` (25.09.2025, « fix: rename iphone 15 to iphone ») |
| Vérification | le contenu servi par le registre est identique, octet pour octet, au fichier du dépôt (SHA-256 `64aa5f8f05c2444d2f0f791328a6bc5c0cc73624eb53dde2c5d29cd710c20124`) |
| Licence | **MIT**, fichier `LICENSE.md` à la racine du dépôt : <https://github.com/magicuidesign/magicui/blob/main/LICENSE.md> (lu le 06.10.2026 ; l'API GitHub le reconnaît comme `MIT`) |
| Fichier adapté | `PhoneFrame.tsx` (en-tête de provenance en tête du fichier) |

**Modifications** : l'écran reçoit un contenu quelconque (ici l'application réelle dans une iframe) au lieu d'une image
ou d'une vidéo ; couleurs de la direction « Votre prochain lundi » (corps graphite `--g-2`, filet fin `--rule-strong`,
touches `--rule`, bord de verre et îlot presque noirs), sans variantes clair / sombre ; le SVG laisse passer le
pointeur vers l'écran ; identifiants de masque uniques par instance ; chemin `clipPath` inutilisé retiré ; l'ombre
portée sobre du papier (`0 22px 44px -22px`, décalage et flou) placée sous le corps (`phone.css`). Le fichier
d'origine ne contenait ni dégradé, ni lueur, ni reflet, ni flou ; aucun n'a été ajouté. Les tracés du cadre, des
touches, de l'îlot et de l'objectif sont repris tels quels.

### Texte de la licence (reproduit comme l'exige la licence)

```
MIT License

Copyright (c) Magic UI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Le reste

Le doigt, l'onde, la barre d'état, le pilote (`pilot.ts`), le script (`script.ts`) et les pages sont écrits pour
Proxsis ; ils n'utilisent que des bibliothèques déjà présentes dans le projet (Motion, base-ui via `ui.tsx`,
lucide-react). Polices : Urbanist et Sora (SIL OFL 1.1), servies par le site lui-même (`public/fonts`, `src/app/fonts.css`) comme dans la présentation.
Réseau, pour ce composant seulement (06.10.2026) : registre `magicui.design` (2 requêtes, dont `iphone-15-pro.json`,
ancien nom, en 404), `raw.githubusercontent.com` (`LICENSE.md`, `LICENSE` en 404, `iphone.tsx`), API GitHub (commit de
`main`, licence, historique du fichier) ; aucune clé, aucun compte. La démo elle-même n'appelle que des pages de
l'application, de même origine.
