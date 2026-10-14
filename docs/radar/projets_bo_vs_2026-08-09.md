# Projets du Bulletin officiel qui comptent pour le radar (août–septembre 2026)

Données **RÉELLES** : 818 demandes d'autorisation de construire du Bulletin officiel du Valais
(531 en français, 287 en allemand dont 277 au contenu complet), publiées du 07.08.2026 au 29.09.2026,
importées depuis les PDF exportés par Hiba et reliées à l'index du portail (`proxsis import-bo-pdf`, rapports :
`data/manuel/import_pdf/RAPPORT_IMPORT.md` et `RAPPORT_IMPORT_DE.md`). *Seule la publication officielle fait foi.*

Toute personne physique est masquée (requérant, propriétaire, maître d'ouvrage, auteur des plans, titre), selon une
règle prudente : un mot de titre qui pourrait être un nom est masqué. Les entreprises et les organismes publics
restent nommés.

Commande : `proxsis projets-radar` → `data/manuel/import_pdf/projets_radar.json` et cette page.

## Ce qui est retenu

Projets qui annoncent un besoin de main-d'œuvre de chantier au-delà d'une maison individuelle :

- **logements collectifs** (immeubles, logements, appartements, Mehrfamilienhaus, Wohnungen) :
  71 ;
- **halles, ateliers, entrepôts** (Halle, Lager, Werkstatt, industriel, artisanal) : 21 ;
- **projets publics** (école, EMS, crèche, ou requérant public) : 41.

Total : **131 projets**, dont **42** avec un requérant entreprise.

Le tri se fait sur des mots du titre : c'est un repérage, pas une classification vérifiée.

## Pour la démo « Lundi 8 h à Martigny » : région de Martigny et Bas-Valais central

| Date | Commune | Type | Titre (masqué) | Requérant entreprise ou organisme public | Lien |
|---|---|---|---|---|---|
| 07.08.2026 | Martigny | halle / atelier | Construction d'une halle avec création de 68 places de parc, installation de panneaux sola | Novadrive sàrl, Novadrive sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/63401de9-b7c5-47f6-b25d-783c8f945d3e/pdf) |
| 07.08.2026 | Saxon | halle / atelier | POSE DE PANNEAUX SOLAIRES ET CHANGEMENT DE LA COUVERTURE SUR LE DEPOT, Saxon | EGG RAYMOND SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/e400ce71-661d-4f57-9956-3f2de99ec4e1/pdf) |
| 07.08.2026 | Salvan | logements collectifs | Construction de trois chalets mitoyens de logements familiaux., Salvan | RES Real Estate Service SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/e8f404c0-ce5f-4988-9019-175721b5c312/pdf) |
| 14.08.2026 | Saint-Maurice | projet public | Démolition du bâtiment existant, Saint-Maurice | Fondation de l'[masqué] de Saint-Maurice | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/07986c7d-7845-4fb0-8607-c3574637292d/pdf) |
| 14.08.2026 | Conthey | logements collectifs | Construction d'une maison d'habitation de deux appartements, Conthey | TMB Partners SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/8d3a97d9-07ec-435d-af7a-78456ddb6c04/pdf) |
| 14.08.2026 | Riddes | logements collectifs + projet public | Changement d’affectation de locaux du rez-de-chaussée en 6 appartements protégés., Riddes | Fondation [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/c6bcfd52-084a-4e3e-9460-0c0f3bef95be/pdf) |
| 21.08.2026 | Martigny | logements collectifs | Construction de 2 immeubles de 3 appartements chacun, Martigny | No Name Architecture sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/5597b7ab-9e02-485d-b51a-edd42b0a063e/pdf) |
| 21.08.2026 | Fully | logements collectifs | Construction d'un immeuble de 9 logements, avec couvert à véhicules au rez-de-chaussée et  | VS2020 SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/85ebeb07-2b8e-4427-b074-2ef2f1ae6e10/pdf) |
| 28.08.2026 | Martigny | halle / atelier | Construction d'une halle de stockage, Martigny | AB Box SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/383b02f2-283e-4143-bd3a-50e004c46a34/pdf) |
| 28.08.2026 | Saxon | halle / atelier | Modification d'ouverture en façade d'une halle industrielle, Saxon | Sébastien Cheseaux SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/87e6b6f5-3dcf-4790-bb3e-b2c28b0a5f96/pdf) |
| 28.08.2026 | Riddes | logements collectifs | Démolition de granges existantes / Construction d'un immeuble d'habitation de 16 apparteme | Nova Architecture SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/9b78cecc-7e53-4e1a-8450-92b9d6f053ce/pdf) |
| 28.08.2026 | Vétroz | logements collectifs | Démolition d'un bâtiment existant et construction d'un immeuble de 5 logements, Vétroz | CARTI Construction SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/cedb8aa9-0fd0-47a5-aba1-6afa96a98f15/pdf) |
| 28.08.2026 | Martigny | logements collectifs | Rénovation énergétique de l'immeuble "[masqué]", Martigny | ADM Immobilier Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/f2886d08-a773-4799-9ce0-faf2c6e7751d/pdf) |
| 28.08.2026 | Chamoson | logements collectifs | Ajout d'un bain à remous dans jardin privé d'un immeuble d'habitation à Chamoson, Chamoson | BimBoum SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/fe53e0c0-7fa3-4eaf-8b79-55e66ca4d791/pdf) |
| 04.09.2026 | Saxon | logements collectifs | Démolition d'un villa et construction d'un immeuble de logements y compris PAC air-eau et  | SDD Invest Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/490e982c-2a4f-4429-b5a6-f71a24bb7d50/pdf) |
| 04.09.2026 | Val de Bagnes | logements collectifs | Démolition d'un garage et construction d'un bâtiment d'habitation de 11 appartements et d' | Christian Constantin SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/7e5a26fc-2fc9-439f-82b7-fc8f559465df/pdf) |
| 11.09.2026 | Saillon | halle / atelier | Démolition d'un hangar existant, construction de 9 villas groupées, transformation du sous | Ocoteau SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/766cb19f-893e-4b59-b607-2fb901d08505/pdf) |
| 11.09.2026 | Ardon | halle / atelier | Modifications d'ouvertures d'un dépôt dans le cadre d'une procédure de régularisation, Ard | IMMO SWISS CONSTRUCTIONS Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/81a49d89-bf36-4f5c-9361-d62293dbd001/pdf) |
| 18.09.2026 | Saxon | halle / atelier | Démolition d'une maison existante et construction d'une halle de stockage, Saxon | MAY & BRONJA SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/639add67-bf44-4b5e-a336-df63e4455210/pdf) |
| 25.09.2026 | Saxon | halle / atelier | Construction d'une halle artisanale, Saxon | O.A.L. Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/7195c6bb-49b6-46a3-a38b-c195e304d7b4/pdf) |
| 25.09.2026 | Ardon | logements collectifs | Changement d'affectation (bureaux en logements) dans le cadre d'une procédure de régularis | A&D invest Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/e9c93085-b44c-44f9-9119-df82f736cc2b/pdf) |

## Tous les projets avec un requérant entreprise ou public

| Date | Commune | Type | Titre (masqué) | Requérant entreprise ou organisme public | Lien |
|---|---|---|---|---|---|
| 07.08.2026 | commission cantonale | projet public | Aufstellen von zwei [masqué] zur autonomen Betreibung der best. Funksendeanlage, Zermatt | Bundesamt für Zoll, Burgergemeinde Zermatt | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/0cc16e20-5f5d-4df4-aecf-c7662130ab80/pdf) |
| 07.08.2026 | commission cantonale | projet public | Démolition d'un garage préfabriqué en béton, Sierre | Ville de Sierre | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/34ee04d3-b17a-4dd3-a9d8-246757908df8/pdf) |
| 07.08.2026 | Vouvry | projet public | Projet de défense contre les chutes de pierres "Porte du [masqué] Sud et [masqué] Sud", Vo | Commune de Vouvry | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/49a698cf-5473-4e9f-900d-fb7436d49440/pdf) |
| 07.08.2026 | Martigny | halle / atelier | Construction d'une halle avec création de 68 places de parc, installation de panneaux sola | Novadrive sàrl, Novadrive sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/63401de9-b7c5-47f6-b25d-783c8f945d3e/pdf) |
| 07.08.2026 | Sion | logements collectifs | Construction d'un immeuble d'habitations, Sion | Sovalco SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/7a05ace2-bdcd-49a5-b38c-f82cb578275a/pdf) |
| 07.08.2026 | Leukerbad | projet public | Umbau [masqué] "altes Schulhaus", Leukerbad | Einwohnergemeinde Leukerbad | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/a0a5ae29-0d89-4d6e-85a3-2b7a3a3da522/pdf) |
| 07.08.2026 | commission cantonale | logements collectifs | Construction de 6 immeubles résidentiels, un logement de fonction et un tea-room, Chamoson | ASE SA, Commune de Chamoson | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/a160ab70-0aea-4543-a5cc-7b12beea7a79/pdf) |
| 07.08.2026 | Raron | logements collectifs | Neubau Wohnüberbauung mit 3 Mehrfamilienhäuser ''MFH [masqué], Raron | imvista SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/c7feadd3-6460-45e3-8790-bea7f37b4ebe/pdf) |
| 07.08.2026 | Turtmann-Unterems | projet public | Neubau [masqué] und Multifunktionshalle Turtmann, Turtmann-Unterems | Burgergemeinde Turtmann, Verein [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/ce6c47df-543f-4a75-bf70-0230a7f21e7b/pdf) |
| 07.08.2026 | Saxon | halle / atelier | POSE DE PANNEAUX SOLAIRES ET CHANGEMENT DE LA COUVERTURE SUR LE DEPOT, Saxon | EGG RAYMOND SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/e400ce71-661d-4f57-9956-3f2de99ec4e1/pdf) |
| 07.08.2026 | Salvan | logements collectifs | Construction de trois chalets mitoyens de logements familiaux., Salvan | RES Real Estate Service SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/e8f404c0-ce5f-4988-9019-175721b5c312/pdf) |
| 10.08.2026 | commission cantonale | projet public | Mise à l'enquête publique d'un projet d'améliorations structurelles, Val de Bagnes | Consortage de l'alpage de [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/4d31398e-16a8-430f-8ed6-dbad31da8e7b/pdf) |
| 14.08.2026 | Saint-Maurice | projet public | Démolition du bâtiment existant, Saint-Maurice | Fondation de l'[masqué] de Saint-Maurice | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/07986c7d-7845-4fb0-8607-c3574637292d/pdf) |
| 14.08.2026 | Fiesch | logements collectifs | Umbau eines nicht mehr wirtschaftlich betriebenen [masqué] in 16 Wohnungen. Energetische u | Fiesch Living AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/0f08aa2c-45c1-457f-999f-0fa1b664e598/pdf) |
| 14.08.2026 | commission cantonale | projet public | Installation d'une statue sur les abords du [masqué] du [masqué], Lens | Bourgeoisie de Lens, Fondation [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/33099e75-6c6b-44d3-909a-1de530cf0d03/pdf) |
| 14.08.2026 | Savièse | projet public | nouveau revêtement de façade, Savièse | Coop Société Coopérative, Direction [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/49159df6-4d95-43e1-8258-9336a8f9c0ef/pdf) |
| 14.08.2026 | commission cantonale | projet public | Pose d'un panneau de chantier pour les travaux phase 1 du [masqué] de St-Maurice, Saint-Ma | Service [masqué], État du Valais | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/7af7a641-fc25-4921-84c7-739eb70fe635/pdf) |
| 14.08.2026 | Conthey | logements collectifs | Construction d'une maison d'habitation de deux appartements, Conthey | TMB Partners SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/8d3a97d9-07ec-435d-af7a-78456ddb6c04/pdf) |
| 14.08.2026 | Lens | projet public | remise aux normes du Parking du [masqué] et installation de sanitaires et d'une yourte, Le | Bourgeoisie de Chermignon | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/c5a3fa61-e93f-4d48-86dd-268fd74cfbcd/pdf) |
| 14.08.2026 | Riddes | logements collectifs + projet public | Changement d’affectation de locaux du rez-de-chaussée en 6 appartements protégés., Riddes | Fondation [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/c6bcfd52-084a-4e3e-9460-0c0f3bef95be/pdf) |
| 14.08.2026 | Zermatt | logements collectifs | Überbauung [masqué] mit [masqué], Umbauten und Neubauten - neue Wohnungen ohne Nutzungsbes | Matterstone AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/d48930a4-380e-4a37-9f6e-241a27b67b60/pdf) |
| 14.08.2026 | commission cantonale | projet public | Sanierung [masqué] Fiesch, Fiesch | Die Genossenschaft [masqué] Fiesch | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/e371da5e-99d1-4bf8-8380-06ebf8cd7fcd/pdf) |
| 21.08.2026 | Ernen | projet public | Instandstellung Speicher, Ernen | Stiftung [masqué], Stiftung [masqué] & [masqué] Ernen | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/1e365302-8c24-499d-98e1-28f9e7b6c4f8/pdf) |
| 21.08.2026 | commission cantonale | projet public | Umbau [masqué].OG und Erstellen Aussentreppe und Unterstand [masqué], Brig-Glis | Gemeinde Brig-Glis | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/48a42513-d110-44ff-95ab-f4d83b7020f8/pdf) |
| 21.08.2026 | Martigny | logements collectifs | Construction de 2 immeubles de 3 appartements chacun, Martigny | No Name Architecture sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/5597b7ab-9e02-485d-b51a-edd42b0a063e/pdf) |
| 21.08.2026 | Collombey-Muraz | projet public | Rénovation (remplacer les fenêtres et volets, nouvelle drainage du bâtiments, réfection de | Paroisse [masqué] Muraz | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/7360eb70-431f-4a35-9771-9c22a53138a1/pdf) |
| 21.08.2026 | Fully | logements collectifs | Construction d'un immeuble de 9 logements, avec couvert à véhicules au rez-de-chaussée et  | VS2020 SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/85ebeb07-2b8e-4427-b074-2ef2f1ae6e10/pdf) |
| 21.08.2026 | Savièse | logements collectifs | Immeuble résidentiel, Savièse | Archi&immo Sàrl, ON-X SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/9c8677b0-fe04-4c2d-8831-a036fbc48f6a/pdf) |
| 21.08.2026 | commission cantonale | projet public | Bauten, Abbruch, Anlagen, Landschaftsgestaltung, Visp | Gemeinde Visp | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/b2b91542-6435-41a9-b8f5-5a3a2aec8c8e/pdf) |
| 21.08.2026 | Salgesch | logements collectifs | Abänderungsgesuch zur Publikation vom 03.04.2026 "Abbruch bestehende Gebäude und Neubau Me | C & B Development AG, C & B Development AG, C & B Development AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/c0f5f7e4-1334-4106-8a82-96062285f38c/pdf) |
| 21.08.2026 | Naters | logements collectifs | Abänderungsgesuch: Neubau eines Mehrfamilienhauses in der [masqué] in Naters, Naters | Valterra Living AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/fd8d4303-f13d-4fe2-86bd-2bab2945d751/pdf) |
| 25.08.2026 | commission cantonale | projet public | Mise à l'enquête publique d'un projet d'améliorations structurelles, Anniviers | Consortage de l'alpage d'[masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/34ecda7b-5466-48d4-8306-4ac345548dfa/pdf) |
| 28.08.2026 | commission cantonale | projet public | Optimisation du réseau d'eau potable d'[masqué] à [masqué], Orsières | Bourgeoisie d'Orsières, Commune d'Orsières, service des eaux | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/09f4eaae-6692-4ad0-9ea4-9dae48aef1a9/pdf) |
| 28.08.2026 | Leuk | logements collectifs | Neubau Mehrfamilienhaus ([masqué] Art. 15-[masqué]), Leuk | H+W Konzept AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/11983868-edb2-4d73-ad3e-f375a9fcecb3/pdf) |
| 28.08.2026 | commission cantonale | projet public | Sanierung Kehrichtplatz "[masqué]" (Abbruch best. Kehrichthaus, Umgestaltung [masqué]), Un | Gemeinde Unterbäch | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/17a6cc2f-0fad-4178-b256-0a2eeae7d2cb/pdf) |
| 28.08.2026 | Monthey | projet public | [masqué] : Démolition et reconstruction de la structure signalétique dans le parking sud d | Commercialis SA, Maus Frères SA, Département Projet | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/3664fb6c-37c5-4e05-9ee3-5928225aad76/pdf) |
| 28.08.2026 | Martigny | halle / atelier | Construction d'une halle de stockage, Martigny | AB Box SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/383b02f2-283e-4143-bd3a-50e004c46a34/pdf) |
| 28.08.2026 | commission cantonale | projet public | Sanierung [masqué] und [masqué] einer Kneippanlage, Zermatt | Gemeinde Zermatt, Pfarrei Zermatt | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/5259ae7e-99e4-4024-a2a6-c12b78e2b76c/pdf) |
| 28.08.2026 | Saxon | halle / atelier | Modification d'ouverture en façade d'une halle industrielle, Saxon | Sébastien Cheseaux SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/87e6b6f5-3dcf-4790-bb3e-b2c28b0a5f96/pdf) |
| 28.08.2026 | commission cantonale | projet public | PV Anlage [masqué], Ausserberg | Gemeinde Ausserberg | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/90a866e4-da6b-4b1f-9491-2c2f8c43f21f/pdf) |
| 28.08.2026 | Riddes | logements collectifs | Démolition de granges existantes / Construction d'un immeuble d'habitation de 16 apparteme | Nova Architecture SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/9b78cecc-7e53-4e1a-8450-92b9d6f053ce/pdf) |
| 28.08.2026 | Vétroz | logements collectifs | Démolition d'un bâtiment existant et construction d'un immeuble de 5 logements, Vétroz | CARTI Construction SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/cedb8aa9-0fd0-47a5-aba1-6afa96a98f15/pdf) |
| 28.08.2026 | commission cantonale | projet public | Anbau Notausgang [masqué], Grächen | Gemeinde Grächen | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/dca876b9-a850-43c2-8a73-290425d53040/pdf) |
| 28.08.2026 | Martigny | logements collectifs | Rénovation énergétique de l'immeuble "[masqué]", Martigny | ADM Immobilier Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/f2886d08-a773-4799-9ce0-faf2c6e7751d/pdf) |
| 28.08.2026 | commission cantonale | projet public | Aménagement d'un [masqué] et construction d'un mur de soutènement en béton, Orsières | Bourgeoisie d'Orsières, Commune d'Orsières | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/fb23484e-6a72-41e0-b1ec-47f428404cea/pdf) |
| 28.08.2026 | Chamoson | logements collectifs | Ajout d'un bain à remous dans jardin privé d'un immeuble d'habitation à Chamoson, Chamoson | BimBoum SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/fe53e0c0-7fa3-4eaf-8b79-55e66ca4d791/pdf) |
| 04.09.2026 | commission cantonale | projet public | Aménagement d'un parc à chiens régularisation, Martigny | Administration Communale | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/0d5fbf46-9d27-4575-91d7-4b4b14e96df2/pdf) |
| 04.09.2026 | commission cantonale | projet public | Neubau Hochhaus [masqué] Nord, Verschiebung [masqué], Standortverschiebung Antenne [masqué | Gemeinde Visp, Stiftung [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/33556fab-be1c-467d-814c-981a75af20fb/pdf) |
| 04.09.2026 | commission cantonale | projet public | Mise en place de couverts à vélos et déplacement du box à vélos, Val de Bagnes | Commune de Val de Bagnes | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/44b82f99-f5df-4212-ab57-1b35053b5791/pdf) |
| 04.09.2026 | Saxon | logements collectifs | Démolition d'un villa et construction d'un immeuble de logements y compris PAC air-eau et  | SDD Invest Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/490e982c-2a4f-4429-b5a6-f71a24bb7d50/pdf) |
| 04.09.2026 | Val de Bagnes | logements collectifs | Démolition d'un garage et construction d'un bâtiment d'habitation de 11 appartements et d' | Christian Constantin SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/7e5a26fc-2fc9-439f-82b7-fc8f559465df/pdf) |
| 04.09.2026 | commission cantonale | projet public | Démolition de containers, construction d'un escalier extérieur et d'un couvert, Leytron | Commune de Leytron | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/832ade5f-fb84-4a9b-85f8-703cb5976139/pdf) |
| 04.09.2026 | commission cantonale | projet public | Pose d'un cabanon de jardin, Saxon | Administration communale de Saxon | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/a31b0bd6-4a4e-41a8-9d61-2db9054a56a2/pdf) |
| 04.09.2026 | Naters | projet public | Erstellung einer Fluchttreppe und einer Wärmepumpe (Aussengerät) sowie nachträgliches Baug | Genossenschaft Restaurant "BIRGISCH" | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/a447c703-7961-4fe4-8317-f26ee4d70804/pdf) |
| 04.09.2026 | Zermatt | logements collectifs | Projektänderung zum BG-Nr. 2025-0019 - Neubau Mehrfamilienhaus [masqué], Erstwohnungen gem | Platin Immobilien AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/ac6b48de-3d20-4b60-8ec6-abe61b294f38/pdf) |
| 04.09.2026 | commission cantonale | projet public | [masqué] géotechniques pour la nouvelle école de Leytron (autorisation complémentaire au d | Commune de Leytron | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/bf744a2c-d881-483c-88b7-3767d072ca02/pdf) |
| 04.09.2026 | Ried-Brig | logements collectifs | Neubau Mehrfamilienhaus, Ried-Brig | S.A.M. Invest GmbH | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/d69ef886-9ef2-495e-a105-a2502b83efe7/pdf) |
| 04.09.2026 | Zermatt | logements collectifs | Neubau MFH [masqué] und MFH [masqué], Erstwohnungen gem. Art. 7 Abs. 1 Bst. a ZWG - Neubau | MOJE AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/f5ba0c71-5174-44b9-afb2-3ff58b6f779f/pdf) |
| 11.09.2026 | Lens | logements collectifs | Construction de deux immeubles, Lens | Cordonier Développement Sàrl, Ormy Immobilier Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/5f0b82a5-a4ce-4328-8762-c780a40b09ee/pdf) |
| 11.09.2026 | Saillon | halle / atelier | Démolition d'un hangar existant, construction de 9 villas groupées, transformation du sous | Ocoteau SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/766cb19f-893e-4b59-b607-2fb901d08505/pdf) |
| 11.09.2026 | Ardon | halle / atelier | Modifications d'ouvertures d'un dépôt dans le cadre d'une procédure de régularisation, Ard | IMMO SWISS CONSTRUCTIONS Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/81a49d89-bf36-4f5c-9361-d62293dbd001/pdf) |
| 11.09.2026 | commission cantonale | halle / atelier | POSE DE PANNEAUX SOLAIRES ET CHANGEMENT DE LA COUVERTURE SUR LE DEPOT, Saxon | EGG RAYMOND SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/91205bb2-b0f6-4aca-a1dd-7966e3f6bb59/pdf) |
| 11.09.2026 | commission cantonale | projet public | La pose d’un store toile et l’inscription d’enseignes sur des murs, Troistorrents | Commune de Troistorrents | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/a90bfb38-35a5-4cff-affb-d41af76fe7f7/pdf) |
| 11.09.2026 | Commune Noble-Contrée | logements collectifs | La Construction d'un immeuble d'habitation en terrasse, création d'une pergola pour véhicu | Homy valais SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/b98618db-8e9e-49b5-857e-d50e3a2c9320/pdf) |
| 18.09.2026 | commission cantonale | projet public | Projet de passerelle pour l’eau potable et réseaux sur le torrent de la [masqué] du [masqu | Commune Troistorrents | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/13b16dcc-e561-435f-ae34-4458a8b01e48/pdf) |
| 18.09.2026 | commission cantonale | projet public | Mise à l'enquête publique d'un projet d'améliorations structurelles, Nendaz | Commune de Nendaz, Eglise [masqué], société coopérative | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/1fd2fe02-4825-4f50-ac88-dc36145320ca/pdf) |
| 18.09.2026 | commission cantonale | projet public | Réalisation d'un pavillon scolaire provisoire, Martigny | Commune de Martigny, Etat du Valais | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/3c0965f8-443c-4dca-8b4b-3896ee2be503/pdf) |
| 18.09.2026 | Saxon | halle / atelier | Démolition d'une maison existante et construction d'une halle de stockage, Saxon | MAY & BRONJA SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/639add67-bf44-4b5e-a336-df63e4455210/pdf) |
| 18.09.2026 | Unterbäch (VS) | logements collectifs | Umbau best. Wohnungen [masqué].OG und DG, Terrassenanbau [masqué],, Unterbäch | Unterbäch Alpin AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/99312a1c-a82f-41c5-ad4e-1d2608e428e1/pdf) |
| 18.09.2026 | commission cantonale | projet public | Ouverture de deux fenêtres de toiture, remplacement des deux panneaux solaires existants,  | Association [masqué] | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/c40687bb-c5c4-485c-8b9c-6c28014b657a/pdf) |
| 25.09.2026 | commission cantonale | projet public | Remise en état de la décharge de la [masqué] et amélioration du potentiel agricole de la p | Commune d'Arbaz | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/0ccab11a-c5b8-407d-9fce-139d36dc2f58/pdf) |
| 25.09.2026 | Ried-Brig | logements collectifs | Umbau und Umnutzung des ehemaligen [masqué] zu 6 Wohnungen, Ried-Brig | Mario Furrer Immobilien GmbH | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/3bb86fba-456e-4424-81f8-bd4d6c12eb6a/pdf) |
| 25.09.2026 | Troistorrents | logements collectifs | Construction de trois chalets de trois appartements avec accès couvert pour le chalet [mas | RTB Corvaglia Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/3eb4421a-0c2c-4a5b-8bfd-c75c3664652b/pdf) |
| 25.09.2026 | Ayent | logements collectifs | Modification du projet publié le 12.06.2026 pour la construction d'un immeuble de 3 appart | Zhubi Sauthier Immobilier sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/65ef3d8e-f8c0-47f9-8288-9f31db22660d/pdf) |
| 25.09.2026 | Hérémence | logements collectifs | Construction d'une maison de deux logements affectés à la résidence principale et aménagem | Cime 4000 SA | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/6cda1bae-e530-45fe-bf6b-4e30330458df/pdf) |
| 25.09.2026 | Saxon | halle / atelier | Construction d'une halle artisanale, Saxon | O.A.L. Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/7195c6bb-49b6-46a3-a38b-c195e304d7b4/pdf) |
| 25.09.2026 | Blatten | projet public | [masqué] Garage für [masqué], Blatten | Departement für Mobilität, Dienststelle für Mobilität, Gemeinde Blatten | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/9e003256-5de3-433d-ac77-d2312ffb2610/pdf) |
| 25.09.2026 | Turtmann-Unterems | logements collectifs | Neubau MFH [masqué], Turtmann- Unterems | Severa Pro AG | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/ad172445-799f-4fb1-a13c-9f8cc2a15315/pdf) |
| 25.09.2026 | commission cantonale | projet public | Réfection de la toiture du couvert de [masqué], Dorénaz | Commune de Dorénaz | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/d668119c-e437-4cc2-b2c9-4eb1208e5c93/pdf) |
| 25.09.2026 | Ardon | logements collectifs | Changement d'affectation (bureaux en logements) dans le cadre d'une procédure de régularis | A&D invest Sàrl | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/e9c93085-b44c-44f9-9119-df82f736cc2b/pdf) |
| 25.09.2026 | Blatten | projet public | [masqué] Garage für [masqué] & Aufstellung von 2 temporären [masqué], Blatten | Departement für Mobilität, Dienststelle für Mobilität | [BO](https://bulletin-officiel.vs.ch/api/v1/publications/f3be0a79-991e-48e0-a180-7c5823a4a07a/pdf) |

## Limites

- Fenêtre courte (8 semaines) : ces permis ne peuvent pas encore entrer dans le classement backtesté. Il faudrait au
  moins 8 semaines de marchés simap après la fenêtre, ou des exports plus anciens. Ils s'affichent comme **signaux de
  contexte** dans la fiche entreprise et la liste d'appels (demandes publiées dans la commune de l'entreprise,
  entreprise citée comme requérante ou auteure des plans).
- Un requérant entreprise n'est pas forcément l'entreprise de construction : promoteur, gérance ou bureau
  d'architectes. C'est au consultant de le qualifier.
- Le masquage prudent des titres peut cacher un nom de lieu-dit ou un mot rare : le lien vers la publication
  officielle donne le titre complet.
