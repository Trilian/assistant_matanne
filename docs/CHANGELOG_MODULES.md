# Changelog Modules

> Historique fonctionnel consolide par domaines au 1er avril 2026.

---

## Vue chronologique

| Periode | Portee principale | Resultat marquant |
| --- | --- | --- |
| Stabilisation initiale | Socle backend | correction des bugs critiques, premiers cron jobs, notifications/admin, 2FA, WhatsApp webhook |
| Consolidation SQL | SQL, tests, documentation | consolidation schema SQL, archive Alembic, nouveaux tests de non regression, nettoyage docs |
| Inter-modules et dashboard | Dashboard avance | cellier-inventaire, score bien-etre, alertes meteo, widgets configurables, timeline famille |
| IA avancee et canaux sortants | IA, notifications | lots IA et cron avances identifies, une partie deja absorbee ensuite dans le backend |
| Reorganisation architecture | Architecture | split de routeurs, renommage massif des factories `obtenir_*_service`, generation types OpenAPI |
| Notifications multi-canal | Notifications | dispatcher unifie, failover multi-canal, throttling, digest queue, preferences utilisateur |
| IA et cron etendus | IA, cron | lots IA IA1 a IA7, nouveaux jobs planifies et etat admin aligne |
| Documentation consolidee | Documentation | reference technique revue, index complete, guides de testing, cron, notifications, admin, event bus |

## Stabilisation initiale

- correction des bugs critiques push et stabilisation du socle backend
- ajout progressif des briques notifications, admin et 2FA
- mise en place du webhook WhatsApp Meta Cloud API
- activation des premiers jobs APScheduler pour les routines et synchronisations de base
- premiers correctifs cuisine, Jules et dashboard livres en production

## Consolidation SQL et tests

- migrations SQL historiques absorbees dans `sql/INIT_COMPLET.sql`
- archive Alembic laissee en sauvegarde avec `alembic.ini.bak`
- index SQL manquants ajoutes sur les zones critiques
- audit ORM versus SQL renforce avec test de coherence non regressif
- extension des tests push, admin, famille et creation de la page admin jobs
- nettoyage de la documentation et remise a niveau du plan de travail

## Inter-modules et dashboard

### Cuisine et stocks

- consolidation du cellier avec l'inventaire cuisine
- OCR photo-frigo pour amorcer l'auto-sync inventaire

### Dashboard et transversal

- score global de bien-etre
- alertes meteo contextuelles cross-modules
- widgets dashboard configurables avec drag and drop
- widget meteo et bloc "aujourd'hui dans l'histoire de la famille"

### Famille

- timeline de vie familiale agregee

## IA avancee et canaux sortants

- cadrage du lot WhatsApp sortant proactif
- cadrage du lot assistant vocal Web Speech API plus Mistral
- cadrage des cron avances sur peremptions, planning dominical et budget mensuel
- cadrage des lots IA sur vacances, anomalies financieres, optimisation budget et diagnostic photo maison
- une partie de ces chantiers a ete ensuite livree hors du sprint nominal, notamment via les refontes notifications, cron et automatisations

## Reorganisation architecture

- decoupage des routeurs maison et famille pour reduire les fichiers trop volumineux
- renommage de 96 factories vers le format `obtenir_*_service`
- generation automatisee des types frontend a partir d'OpenAPI
- audit ORM/SQL, alignements des modeles et correction `ArticleCourses`
- meilleure lisibilite de l'architecture services/modeles/routes

## Notifications multi-canal

- introduction de `DispatcherNotifications` comme point d'entree unique
- mapping des evenements vers les canaux par priorite
- failover configurable entre ntfy, web push, email et WhatsApp
- throttling utilisateur et digest periodique
- preferences utilisateur exposees via API et historisation des envois
- couverture de tests dediee sur les canaux et sur le routage

## IA et cron etendus

- livraison du lot IA IA1 a IA7
- ajout ou extension des jobs J1, J3, J4, J5 et J6
- mise a jour des libelles admin et des vues de supervision
- suite de tests passee sur le perimetre documente en memoire projet

## Documentation consolidee

- mise a jour de `CRON_JOBS.md` avec les 68 jobs connus, categories, horaires et endpoints admin
- mise a jour de `NOTIFICATIONS.md` avec l'architecture multi-canal reelle
- mise a jour de `ADMIN_RUNBOOK.md` avec 51 endpoints et procedures d'exploitation
- mise a jour de `INTER_MODULES.md`, `EVENT_BUS.md` et `AUTOMATIONS.md`
- creation du guide unifie `TESTING.md`
- alignement de l'index documentaire et des references transverses

## Historique par domaine

### Cuisine

- renforcement du flux planning vers courses vers inventaire
- persistance de `batch_cooking_congelation`
- deduction automatique des ingredients apres session batch cooking
- suggestions IA enrichies selon stock, saisonnalite et feedback utilisateur
- ponts actifs inventaire vers planning, peremption vers anti-gaspillage, jardin vers recettes

### Famille et quotidien

- consolidation des flux Jules, activites, routines et weekend
- enrichissement des achats famille et suggestions associees
- integration des documents, anniversaires et budget previsionnel
- exploitation du contexte meteo pour les suggestions d'activites

### Maison et habitat

- enrichissement du CRUD maison pour contrats, garanties, diagnostics, devis, cellier et depenses
- interactions renforcees entre energie, entretien, courses et dashboard
- generation automatisee de taches saisonnieres jardin et entretien
- extension du module habitat sur veille, scenarios, plans et deco

### Jeux

- consolidation des services paris, loto et euromillions
- synchronisation des tirages et alertes resultats
- sync jeux vers budget automatisee quotidiennement
- archivage mensuel de l'historique ancien des paris sportifs

### Outils et integrations

- conversationnel WhatsApp et webhooks Meta Cloud API
- integration Garmin sport et sante consolidee
- moteur d'automations etendu a 9 declencheurs et 10 actions avec dry-run

### Admin et observabilite

- cockpit admin elargi aux jobs, cache, audit, securite et simulations
- historique d'execution des jobs via `job_executions`
- event bus porte a 32 evenements types et 51 subscribers

### Documentation et qualite

- reference de testing unifiee
- reference API et schemas maintenues en phase avec le backend
- documentation transversale de securite, monitoring, performance et patterns consolidee
