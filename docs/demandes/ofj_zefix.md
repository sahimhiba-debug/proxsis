# Demande 2 — Zefix (Office fédéral de la justice, Office fédéral du registre du commerce)

Texte corrigé par Hiba et envoyé par elle (octobre 2026), copié mot pour mot depuis l'annexe de la suite 10 du brief
(le brief, notes de travail non publiées, « Les quatre demandes, telles que préparées le 13.10.2026 ») ; Hiba a pu le
retoucher un peu avant l'envoi. Personne d'autre ne contacte ce destinataire : ni l'équipe, ni un agent.

- **À** : zefix@bj.admin.ch
- **Objet** : Demande d'identifiants pour l'API ZefixPublicREST
- **Statut** : envoyée (octobre 2026)
- **Adresse** : Adresse citée par la documentation de l'API (`docs/recherche/donnees.md`, § 4.3).

---

Madame, Monsieur,

Je développe Proxsis, un prototype indépendant d'aide à la prospection pour les agences de placement de personnel.
Pour relier sans erreur les entreprises citées dans les publications officielles (marchés publics, demandes
d'autorisation de construire, FOSC) à leur numéro IDE, je souhaite utiliser l'API ZefixPublicREST, en particulier :
- GET /api/v1/company/uid/{uid} (raison sociale, forme juridique, siège, statut) ;
- POST /api/v1/company/search (recherche par nom, pour relier le lauréat d'un marché public à son numéro IDE) ;
- GET /api/v1/sogc/bydate/{date} (publications FOSC du jour).

Pourriez-vous m'attribuer des identifiants, avec l'adresse e-mail de ce message comme nom d'utilisateur ?

Usage prévu : quelques centaines d'appels par jour au plus, au moins une seconde entre deux appels, avec une mise en
cache. Seules les données d'entreprises sont conservées (raison sociale, IDE, forme juridique, siège, but, statut).
Les données de personnes (organes, signataires) ne sont ni stockées ni exploitées.

Merci de m'indiquer les conditions d'utilisation et les limites de débit applicables.

Avec mes salutations distinguées,

Hiba Sahim
AI Engineer — Proxsis (prototype indépendant)
