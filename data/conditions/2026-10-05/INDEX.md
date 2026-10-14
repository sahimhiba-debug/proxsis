# Archive des conditions — 2026-10-05

> Document antérieur au nom Proxsis (07.10.2026) ; le nom du produit y a été mis à jour le 14.10.2026.

| Fichier | Obtenu par | Remarque |
|---|---|---|
| `robots_<domaine>.txt` | `GET https://<domaine>/robots.txt`, User-Agent du projet (sous son ancien nom), 2026-10-05 ~17:50 UTC | copie brute |
| `robots_date.nager.at.txt` | même requête **en suivant la redirection** vers `https://nagerholidays.com/robots.txt` (HTTP 200) | contient `Disallow: /api/v` (audit m13 : l'archive initiale était vide) |
| `robots_opendata.swiss_page_404.html` | redirection vers `https://opendata.swiss/de/robots.txt` → page HTML « 404 » | **opendata.swiss n'a pas de robots.txt** ; ckan.opendata.swiss en a un (`Disallow: /api/`) |
| `robots_daten.statistik.zh.ch.txt` | HTTP 404, 0 octet | pas de robots.txt (aucune restriction) |
| `robots_www.pxweb.bfs.admin.ch.txt`, `robots_www.uid-wse.admin.ch.txt` | HTTP 404 (page HTML d'erreur enregistrée) | pas de robots.txt |

## Conditions générales lues (lecture humaine, non aspirées)

| Document | URL | Version / date | Empreinte SHA-256 de la copie lue |
|---|---|---|---|
| CG API simap.ch | https://www.simap.ch/fr/about/legal (section « CG pour l'utilisation de l'API ») | version du 30.09.2023, lue le 2026-10-05 dans le navigateur | non calculée (page JavaScript, texte lu à l'écran) |
| Spécification OpenAPI simap | https://www.simap.ch/api/specifications/simap.yaml | v1.5.1 | `514cf1df075badcdd7aac5dbfb66dda2811e06553fa30ca59c5f3d1504eb0d5e` |
| CG du Portail des feuilles officielles (SECO) | https://amtsblattportal.ch/static/agb_fr.pdf | lue le 2026-10-05, **avant** la décision « consultation manuelle uniquement » | `e8770a63beb1b9a6344e347023410c9ad4c3d287187a8efa88745ce237bf708e` |

Les copies des CG ne sont pas versionnées (droit d'auteur) ; l'empreinte
permet de vérifier qu'on parle du même texte.
