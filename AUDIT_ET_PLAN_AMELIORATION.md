# Audit Complet & Plan d'Amélioration — Assistant Matanne

> **Date**: 3 avril 2026  
> **Scope**: Application complète (Backend + Frontend + SQL + Tests + Docs)  
> **Objectif**: Détection bugs/gaps, plan d'amélioration, interactions inter-modules, UI, IA, automatisations

---

## Table des matières

1. [Notes globales par catégorie](#1-notes-globales-par-catégorie)
2. [Bugs et problèmes détectés](#2-bugs-et-problèmes-détectés)
3. [Code mort et legacy à supprimer](#3-code-mort-et-legacy-à-supprimer)
4. [Gaps fonctionnels et features manquantes](#4-gaps-fonctionnels-et-features-manquantes)
5. [Consolidation SQL](#5-consolidation-sql)
6. [Interactions intra-modules et inter-modules](#6-interactions-intra-modules-et-inter-modules)
7. [Opportunités IA supplémentaires](#7-opportunités-ia-supplémentaires)
8. [Jobs automatiques et automations](#8-jobs-automatiques-et-automations)
9. [Telegram — extensions possibles](#9-telegram--extensions-possibles)
10. [Email — notifications manquantes](#10-email--notifications-manquantes)
11. [Mode admin manuel (pour tests)](#11-mode-admin-manuel-pour-tests)
12. [Tests — couverture et qualité](#12-tests--couverture-et-qualité)
13. [Documentation — état et nettoyage](#13-documentation--état-et-nettoyage)
14. [UI/UX — améliorations visuelles](#14-uiux--améliorations-visuelles)
15. [Nettoyage fichiers et nommage](#15-nettoyage-fichiers-et-nommage)
16. [Axes d'innovation](#16-axes-dinnovation)
17. [Plan d'exécution priorisé](#17-plan-dexécution-priorisé)

---

## 1. Notes globales par catégorie

| Catégorie | Note /10 | Commentaire |
|-----------|----------|-------------|
| **Architecture backend** | 8.5 | Modulaire, bien découpée, patterns cohérents. Quelques stub `pass` et imports circulaires à nettoyer |
| **Architecture frontend** | 9.0 | 40+ pages complètes, 138+ composants, stack moderne (React 19, Next.js 16, TanStack Query v5) |
| **Modèles de données** | 8.0 | 32 fichiers ORM cohérents, quelques tables orphelines et un model au nommage suspect |
| **API REST** | 7.5 | 57 routes complètes mais 5+ endpoints avec `pass` stub, et endpoints OCR/Vinted encore actifs (à supprimer) |
| **Schémas Pydantic/Zod** | 8.0 | Bonne couverture, miroir backend↔frontend, quelques schémas inutilisés |
| **Base de données SQL** | 8.5 | 22 fichiers modulaires + script de régénération, duplication index mineure |
| **Tests** | 5.5 | 234 fichiers côté backend, 50+ côté frontend. Bonne couverture du noyau, mais gaps majeurs sur routes et services |
| **Documentation** | 7.0 | 45+ fichiers, complète mais chevauchements (automations, cron), noms de fichiers avec sprint/phase |
| **UI/UX** | 8.0 | Riche (3D, heatmaps, Sankey, drag-n-drop), mobile-first, dark mode. Accessibilité à renforcer |
| **Interactions inter-modules** | 8.5 | 21+ bridges explicites, event bus 32 événements / 51 subscribers. Très bon réseau |
| **IA / Mistral** | 7.5 | BaseAIService solide, rate limiting, cache sémantique. Certains services IA expérimentaux pas testés |
| **Automatisations / Cron** | 8.0 | 68 jobs enregistrés, moteur si/alors, exécution toutes les 5 min. Bien couvert |
| **Notifications** | 8.0 | 4 canaux (ntfy, push, email, Telegram), fallback chain, throttling, digest mode |
| **Admin / DevTools** | 9.0 | 51 endpoints admin, dry-run, simulation de flux, console IA, feature flags. Excellent |
| **Sécurité** | 7.5 | JWT, sanitizer anti-XSS, rate limiting. Quelques endpoints admin sans validation SQL stricte |
| **Performance** | 7.5 | Cache 3 niveaux, lazy loading, Suspense. Redis optionnel pas partout intégré |
| **Qualité du code** | 7.0 | Zéro TODO/FIXME dans le code actif, mais commentaires avec noms de phase, fichiers fourre-tout |
| **DevOps / Déploiement** | 7.5 | Dockerfile multi-stage, Docker Compose staging, Sentry, Prometheus. Railway Free limité |

**Note globale pondérée : 7.8 / 10**

---

## 2. Bugs et problèmes détectés

### 2.1 Bugs critiques (impact utilisateur)

| # | Fichier | Problème | Impact |
|---|---------|----------|--------|
| B1 | `src/api/routes/assistant.py` L88 | Endpoint `/chat` contient un `pass` — ne fait rien | L'utilisateur envoie un message et reçoit une réponse vide |
| B2 | `src/api/routes/famille_jules.py` L198 | Suivi alimentaire Jules contient `pass` | Feature Jules nutrition silencieusement cassée |
| B3 | `src/api/routes/preferences.py` L389, L394 | Deux handlers de préférences avec `pass` | Changement de préférences ne persiste pas |
| B4 | `src/api/routes/dashboard.py` L765, L1264 | Error handlers `except: pass` | Les erreurs sont silencieusement avalées, pas de log |
| B5 | `src/core/models/jeux.py` L361 | Générateur de données placeholder (match/équipes) | Crée des données fictives si l'ID n'existe pas — masque des bugs |

### 2.2 Bugs moyens (qualité/maintenabilité)

| # | Fichier | Problème | Impact |
|---|---------|----------|--------|
| B6 | `src/core/models/famille.py` L74-83 | Forward references avec `# noqa: F821` | Analyse de type cassée, refactoring risqué |
| B7 | `src/api/routes/famille.py` et `maison.py` | Imports circulaires (late import pattern) | Risque de boucle infinie si sub-router importe le parent |
| B8 | `src/core/models/systeme.py` | Model `SauvegardeMoelleOsseuseDB` — nommage incohérent | Confusion totale ("moelle osseuse" = backup système ?) |
| B9 | `frontend/src/bibliotheque/api/planning.ts` L196 | Stub `harnessTablierMeteo()` non implémenté | Pas de données météo dans le planning |
| B10 | `tests/services/batch_cooking/test_service.py` | ~15 tests avec `pytest.skip()` (session impossible) | Zéro couverture batch cooking |

### 2.3 Problèmes de cohérence

| # | Problème | Détail |
|---|----------|--------|
| B11 | Fichier frontend `admin/whatsapp-test/page.tsx` | Le nom dit WhatsApp, le contenu est Telegram — legacy non renommé |
| B12 | Fichier API client `ia_avancee.ts` (underscore) | Tous les autres utilisent kebab-case → incohérence |
| B13 | `sql/schema/13_views.sql` L107-129 | Indexes dupliqués — aussi dans `14_indexes.sql` |
| B14 | `sql/schema/17_migrations_absorbees.sql` | Fichier vide, migrations V005-V007 jamais absorbées |

---

## 3. Code mort et legacy à supprimer

### 3.1 Features actives mais rejetées par l'utilisateur

| # | Feature | Fichiers concernés | Action |
|---|---------|--------------------|---------| 
| L1 | **OCR/Scan de tickets** | `src/api/routes/courses.py` (endpoint `/ocr-ticket-caisse`), `src/api/routes/upload.py` (`/ocr-document`), `src/api/routes/jeux_dashboard.py` (`/ocr-ticket`), `src/api/routes/maison_finances.py` (`/ocr-ticket`), `src/services/utilitaires/ocr_service.py` | **Supprimer** tous les endpoints OCR et le service OCR |
| L2 | **Intégration Vinted** | `src/api/schemas/famille.py` (schemas `AnnonceVinted*`), `src/services/famille/achats_ia.py` (Vinted service) | **Supprimer** schemas et code Vinted |
| L3 | **Gamification familiale générale** | `src/core/models/gamification.py` (tables Badge, Point, Historique), `src/api/routes/dashboard.py` (endpoint `/points-famille`), jobs `points_famille_hebdo` | **Limiter** strictement au Garmin/sport ou **supprimer** si pas lié au sport |
| L4 | **Jeu responsable** | Résidus dans `src/api/routes/jeux_dashboard.py` L555 ("Budget jeu responsable") | **Supprimer** toute référence |

### 3.2 Code legacy/historique à nettoyer

| # | Élément | Détail | Action |
|---|---------|--------|---------| 
| L5 | Commentaires avec noms de phase/sprint | 150+ occurrences : "Phase 5.2", "Sprint 4", "Phase A2", "Phase B", "Phase M", etc. dans tous les fichiers Python et TypeScript | **Remplacer** par des commentaires fonctionnels (ce que ça fait, pas quand c'est arrivé) |
| L6 | `src/services/utilitaires/ocr_service.py` | Marqué "Adaptateur legacy" mais toujours importé | **Supprimer** |
| L7 | `src/core/monitoring/rerun_profiler.py` | "Removed — only stubs no-op" | **Supprimer** |
| L8 | Tables SQL orphelines | `stats_home`, `taches_home`, `archive_articles`, `journal_sante` — documentées dans `test_schema_coherence.py` | **Investiguer** : drop si vraiment inutilisées |
| L9 | Fichier `scripts/generate_screenshots.ts` | TypeScript dans un dossier de scripts Python | **Déplacer** vers `frontend/scripts/` ou supprimer |

### 3.3 Fichiers fourre-tout et mal nommés

| # | Fichier | Problème | Action |
|---|---------|----------|--------|
| L10 | `src/api/routes/fonctionnalites_avancees.py` | 16+ endpoints dans un fichier "avancées" — trop vague | **Éclater** en fichiers spécifiques (`batch_cooking_avance.py`, `tendances.py`, `journaux.py`) |
| L11 | `AUDIT_COMPLET_AVRIL_2026.md` (racine) | Audit historique, sera remplacé par ce document | **Supprimer** quand ce plan est validé |
| L12 | `PLANNING_IMPLEMENTATION.md` (racine) | Plan historique d'implémentation | **Archiver** dans `docs/archive/` ou supprimer |
| L13 | `frontend/src/app/(app)/admin/whatsapp-test/page.tsx` | Fichier nommé WhatsApp mais c'est Telegram | **Renommer** en `telegram-test/page.tsx` |

---

## 4. Gaps fonctionnels et features manquantes

### 4.1 Backend — Endpoints incomplets

| # | Module | Gap | Priorité |
|---|--------|-----|----------|
| G1 | Assistant IA | `/chat` ne fait rien (stub `pass`) | Haute |
| G2 | Jules nutrition | Suivi alimentaire incomplet | Haute |
| G3 | Préférences | Sauvegarde des préférences cassée | Haute |
| G4 | Météo → Planning | Stub `harnessTablierMeteo()` — pas de météo dans le planning | Moyenne |
| G5 | Tablet mode cuisine | Page existe mais contenu potentiellement incomplet | Basse |
| G6 | Recherche globale | Route existe mais profondeur de recherche cross-module à valider | Moyenne |
| G7 | WebSocket sync | Test websocket courses skippé ("deadlock sync TestClient") — validé manuellement seulement | Moyenne |

### 4.2 Frontend — Améliorations UI manquantes

| # | Page | Gap | Priorité |
|---|------|-----|----------|
| G8 | Courses | Fichier 1200+ lignes — composants non extraits | Moyenne |
| G9 | Travaux maison | 730+ lignes — composants à extraire | Basse |
| G10 | Accessibilité | Pas de `aria-live` pour mises à jour temps réel (courses WebSocket) | Moyenne |
| G11 | Accessibilité | `aria-describedby` manquant sur composants complexes | Basse |
| G12 | Accessibilité | `htmlFor` pas toujours associé aux labels de formulaire | Basse |

### 4.3 Backend → Frontend — Features backend sans UI

| # | Feature backend | Endpoint | UI existante ? |
|---|----------------|----------|----------------|
| G13 | Inline queries Telegram | `webhooks_telegram.py` | Non (Telegram only) — OK |
| G14 | Export config admin | `GET /admin/config/export` | UI admin incomplète pour import/export config |
| G15 | Simulation de flux | `POST /admin/simulate/flow` | Bouton existe dans page admin mais retours non visualisés |

---

## 5. Consolidation SQL

### 5.1 État actuel
- 22 fichiers de schéma ordonnés par dépendance (`01_users.sql` → `22_automations.sql`)
- 1 fichier compilé `INIT_COMPLET.sql` (régénéré par `scripts/db/regenerate_init.py` avec SHA256)
- Test de cohérence ORM ↔ SQL (`tests/sql/test_schema_coherence.py`)

### 5.2 Actions de consolidation

| # | Action | Détail |
|---|--------|--------|
| S1 | **Dédupliquer les indexes** | `13_views.sql` lignes 107-129 dupliquent des index de `14_indexes.sql`. Tous les index → `14_indexes.sql` uniquement |
| S2 | **Clarifier fichier 17** | `17_migrations_absorbees.sql` est vide — soit y mettre les migrations V005-V007 consolidées, soit supprimer le fichier |
| S3 | **Supprimer tables orphelines** | Tables `stats_home`, `taches_home`, `archive_articles`, `journal_sante` — valider qu'aucun code ne les utilise, puis DROP |
| S4 | **Supprimer tables gamification** | Si gamification limitée au Garmin, les tables `badges`, `points`, `historique_gamification` sont inutiles → DROP ou limiter au sport |
| S5 | **Régénérer INIT_COMPLET.sql** | Après tous les nettoyages, relancer `python scripts/db/regenerate_init.py` pour le fichier compilé |
| S6 | **Audit ORM ↔ SQL final** | Relancer `python scripts/analysis/audit_orm_sql.py` et `pytest tests/sql/test_schema_coherence.py` pour validation |

---

## 6. Interactions intra-modules et inter-modules

### 6.1 Carte des 21+ bridges existants

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CUISINE    │     │   FAMILLE    │     │    MAISON    │
│              │     │              │     │              │
│ Recettes     │◄────│ Jules growth │     │ Projets      │
│ Planning     │◄────│ (portions)   │     │ Entretien    │
│ Courses      │◄────│              │     │ Jardin ──────┼──► Planning (récoltes→recettes)
│ Inventaire   │◄────│ Budget ──────┼──►  │ Énergie      │
│ Batch cook.  │     │ Annivers. ───┼──►  │ Finances     │
│ Anti-gaspi   │◄────│ Garmin ──────┼──►  │ Diagnostics  │
│              │     │ Documents ───┼──►  │              │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  TRANSVERSAL  │
                    │               │
                    │ Chat IA ctx   │
                    │ Event bus     │
                    │ Notifications │
                    │ Dashboard     │
                    │ Automations   │
                    └───────────────┘
```

### 6.2 Bridges existants détaillés

| Source → Cible | Bridge | Déclencheur |
|----------------|--------|-------------|
| Inventaire → Planning | `inter_module_inventaire_planning.py` | Stock bas → suggestions recettes avec ce qu'on a |
| Jules croissance → Planning | `inter_module_jules_nutrition.py` | Jalon Jules → adapter portions recettes |
| Saisonnalité → Planning IA | `inter_module_saison_menu.py` | Changement de mois → suggestions saisonnières |
| Courses total → Budget | `inter_module_courses_budget.py` | Achat validé → sync budget catégorie alimentation |
| Batch cooking → Stock | `inter_module_batch_inventaire.py` | Session terminée → déduire ingrédients |
| Péremption → Recettes | `inter_module_peremption_recettes.py` | J-3 péremption → anti-gaspillage recettes |
| Jardin récolte → Planning | `inter_module_jardin_recettes.py` | Récolte collectée → planning semaine suivante |
| Garmin → Santé | `inter_module_garmin_health.py` | Sync quotidienne 6h → données activité |
| Documents → Calendrier | `inter_module_documents_notifications.py` | Expiration J-14 → événement calendrier + notif |
| Jeux P&L → Budget jeux | `inter_module_budget_jeux.py` | Résultats paris → catégorie budget jeux (séparé) |
| Anomalie budget → Alerte | `inter_module_budget_anomalie.py` | Dépassement +30% → notification |
| Anniversaire → Budget | `inter_module_anniversaires_budget.py` | J-14 anniversaire → réserve budgétaire |
| Entretien → Courses | `inter_module_entretien_courses.py` | Tâche entretien due → produits dans courses |
| Énergie → Analyse | `inter_module_energie_cuisine.py` | Hausse +20% → alerte + tâche diagnostic |
| Photo diagnostic → Projet | `inter_module_diagnostics_ia.py` | Photo panne → diagnostic IA → créer projet réparation |
| Multi-module → Chat IA | `inter_module_chat_contexte.py` | Message chat → contexte enrichi (frigo, planning, budget, etc.) |
| Voyage → Planning | `inter_module_planning_voyage.py` | Départ voyage → ajuster planning repas/quantités |

### 6.3 Nouvelles interactions proposées

| # | Source → Cible | Description | Valeur |
|---|----------------|-------------|--------|
| I1 | **Planning validé → Courses auto** | Quand le planning semaine est validé, générer auto la liste de courses | Haute — évite un clic utilisateur |
| I2 | **Météo → Jardin** | Prévisions météo → ajuster alertes arrosage/protection gel | Moyenne |
| I4 | **Budget mensuel → Rapport famille** | Clôture mois → intégrer données budget dans résumé hebdo | Moyenne |
| I5 | **Entretien terminé → Mise à jour équipement** | Tâche entretien validée → date dernier entretien sur fiche équipement | Haute — cohérence données |
| I6 | **Batch cooking → Planning semaine** | Session batch terminée → pré-remplir les repas du planning | Haute — enchaînement logique |
| I7 | **Anniversaire → Suggestions recettes** | Anniversaire J-3 → suggérer recettes festives/gâteau | Moyenne — attention délicat |
| I8 | **Garmin activité sportive → Planning nutrition** | Grosse séance sport → suggérer repas plus copieux/protéiné | Moyenne — si Garmin connecté |
| I9 | **Fin de voyage → Résumé dépenses** | Retour voyage → résumé automatique budget voyage + réintégration planning | Basse |
| I10 | **Feedback recette → Poids suggestion** | Note recette 5★ → plus suggérée, 1★ → exclue automatiquement | Haute — amélioration continue |

---

## 7. Opportunités IA supplémentaires

### 7.1 IA déjà en place

| Module | Utilisation IA | Service |
|--------|---------------|---------|
| Planning repas | Génération planning semaine (Mistral) | `BaseAIService.call_with_list_parsing_sync()` |
| Anti-gaspillage | Suggestions recettes avec produits proches péremption | `AntiGaspillageService` |
| Batch cooking | Génération plan batch + étapes | `BatchCookingService` |
| Jules coaching | Conseils développement enfant | `JulesAIService` |
| Weekend | Suggestions activités weekend (météo + âge Jules) | `WeekendAIService` |
| Dashboard | Résumé narratif hebdomadaire IA | `DashboardService` |
| Diagnostics maison | Analyse photo → diagnostic panne | `MultimodalService` |
| Estimation travaux | Photo → estimation coût travaux | `MultimodalService` |
| Chat assistant | Conversation libre avec contexte famille | `AssistantService` (⚠️ stub) |
| Nutritionniste | Analyse nutritionnelle du planning | `NutritionService` |

### 7.2 Nouvelles opportunités IA

| # | Opportunité | Description | Complexité |
|---|-------------|-------------|------------|
| IA1 | **Coach jardin IA** | Analyser photos des plantes pour diagnostiquer maladies, conseiller taille/arrosage | Moyenne (vision) |
| IA2 | **Optimisateur énergie IA** | Analyser les patterns de consommation et suggérer des économies | Faible (texte) |
| IA3 | **Résumé matinal personnalisé** | Briefing matinal narratif par Telegram: météo + repas + tâches + Jules en une phrase | Faible (texte, cron 7h) |
| IA4 | **Adaptation recettes IA** | "J'ai pas de crème fraîche" → l'IA adapte la recette en temps réel | Moyenne (texte) |
| IA5 | **Prédiction restock intelligent** | Analyser fréquence achat + quantité → prédire quand racheter chaque article | Moyenne (data + IA) |
| IA6 | **Assistant vocal amélioré** | Mode mains occupées en cuisine: "Étape suivante", "Minuteur 10 min" | Moyenne (voice + streaming) |
| IA7 | **Analyse tendances familiales** | Résumé mensuel: "Ce mois vous avez mangé +italique, moins poisson, Jules a atteint 3 jalons" | Faible (agrégation + prompt) |
| IA8 | **Planificateur sorties IA** | Entrée: budget + météo + âge Jules + localisation → plan sortie complet | Moyenne (texte) |
| IA9 | **Générateur liste courses intelligente** | Analyser les courses des 4 dernières semaines → "vous avez oublié le lait" | Faible (data + prompt) |
| IA10 | **Coach entretien prédictif** | Historique entretien + âge équipement → "La chaudière devrait être révisée dans 2 mois" | Faible (texte + data) |

---

## 8. Jobs automatiques et automations

### 8.1 Jobs cron existants (68 enregistrés)

| Heure | Job | Module | Canal |
|-------|-----|--------|-------|
| 06:00 | `alertes_peremption_48h` | Inventaire | push, ntfy |
| 06:00 | `garmin_sync_matinal` | Famille/Garmin | silencieux |
| 06:15 | `sync_recoltes_inventaire` | Jardin → Inventaire | silencieux |
| 07:00 | `rappels_famille` | Famille | push, ntfy, Telegram |
| 07:00 | `alerte_stock_bas` | Inventaire | push, ntfy |
| 07:00 | `alertes_energie` | Maison/Énergie | push, email |
| 07:30 | `digest_telegram_matinal` | Transversal | Telegram |
| 08:00 | `rappels_maison` | Maison | push, ntfy |
| 08:00 | `check_garmin_anomalies` | Garmin | push |
| 08:30 | `rappels_generaux` | Transversal | push, ntfy |
| 09:00 (lun) | `rappel_vaccins` | Famille/Santé | push, ntfy |
| 17:00 (ven) | `score_weekend` | Famille/Weekend | Telegram |
| 19:00 (dim) | `planning_semaine_si_vide` | Cuisine/Planning | push |
| 20:00 | `verification_budget_quotidien` | Famille/Budget | push si dépass. |
| 20:30 (dim) | `resume_hebdo_ia` | Transversal | Telegram, email |
| 22:00 | `sync_jeux_budget` | Jeux → Budget | silencieux |
| 22:15 (mar/ven) | `resultat_tirage_loto` | Jeux | Telegram |
| 23:00 | `sync_google_calendar` | Famille/Calendar | silencieux |
| 01:00 | `nettoyage_cache_7j` | Système | silencieux |
| 02:00 | `backup_donnees_critiques` | Système | email si erreur |
| 1er du mois 08:15 | `rapport_mensuel_budget` | Budget | email |
| 1er du mois 09:30 | `rapport_maison_mensuel` | Maison | email |
| Trimestriel | `tache_jardin_saisonniere` | Jardin | push |
| Toutes les 5 min | `automations_runner` | Moteur automatisations | variable |

### 8.2 Nouveaux jobs proposés

| # | Job | Schedule | Module | Description |
|---|-----|----------|--------|-------------|
| J1 | `briefing_matinal_ia` | Quotidien 7h | Transversal | Résumé narratif IA par Telegram (météo + repas + tâches + Jules) |
| J2 | `comparateur_abonnements_mensuel` | 1er du mois | Maison/Abonnements | Comparer prix actuels vs offres marché (eau, élec, internet) |
| J4 | `rapport_nutritionnel_jules` | Hebdo dimanche 19h | Famille/Jules | Résumé nutritionnel hebdo de Jules (portions, diversité, alertes) |
| J5 | `nettoyage_notifications_30j` | Mensuel | Système | Purger `historique_notifications` > 30 jours |
| J6 | `prediction_depenses_mensuelles` | 15 du mois | Budget | IA prédit dépenses fin de mois basé sur les 15 premiers jours |
| J7 | `alerte_plantes_arrosage` | Quotidien 8h (été) | Jardin | Si météo chaude + pas d'arrosage enregistré depuis X jours |
| J8 | `sync_tirages_euromillions` | Mar/Ven 22:30 | Jeux | Sync auto des résultats Euromillions (si pas déjà fait) |

### 8.3 Automations moteur si/alors — extensions

| # | Déclencheur | Condition | Action |
|---|------------|-----------|--------|
| A1 | Recette notée 1★ | `feedback.note <= 2` | Exclure de la suggestion automatique |
| A2 | Planning validé | `planning.statut = 'valide'` | Générer courses auto (bridge I1) |
| A3 | Session batch terminée | `batch.statut = 'termine'` | Pré-remplir planning (bridge I6) |
| A4 | Température < 0°C | `meteo.temp_min < 0` | Alerte protection plantes jardin |
| A5 | Dernier entretien > fréquence | `entretien.derniere_date + frequence < today` | Créer tâche + notification |

---

## 9. Telegram — extensions possibles

### 9.1 Commandes existantes (11)

`/planning`, `/courses`, `/ajout [article]`, `/repas [midi|soir]`, `/jules`, `/maison`, `/budget`, `/meteo`, `/menu`, `/aide`

### 9.2 Nouvelles commandes proposées

| # | Commande | Description | Priorité |
|---|----------|-------------|----------|
| T1 | `/inventaire` | Liste rapide du frigo avec icônes péremption (🟢🟡🔴) | Haute |
| T2 | `/recette [nom]` | Montrer une recette rapide avec ingrédients | Haute |
| T3 | `/batch` | Résumé de la session batch cooking en cours/dernière | Moyenne |
| T4 | `/jardin` | Résumé : prochaines tâches + prochaines récoltes | Moyenne |
| T5 | `/energie` | KPIs énergie du mois (si connecté) | Basse |
| T6 | `/rappels` | Tous les rappels/notifications en attente groupés | Haute |
| T7 | `/timer [Xmin]` | Lancer un minuteur depuis Telegram → notification quand fini | Moyenne |
| T8 | `/note [texte]` | Créer une note rapide depuis Telegram | Moyenne |

### 9.3 Interactions Telegram enrichies

| # | Feature | Description |
|---|---------|-------------|
| T9 | **Boutons de validation courses** | À chaque article : ✅ Acheté / ❌ Pas trouvé / 🔄 Reporter |
| T10 | **Mini-sondage repas** | "Qu'est-ce qui vous ferait plaisir cette semaine ?" → boutons choix |
| T11 | **Photo → IA** | Envoyer une photo du frigo → IA analyse contenu → suggestions recettes |

---

## 10. Email — notifications manquantes

### 10.1 Emails existants

- Résumé hebdomadaire (`resume_hebdo` — dimanche 20h30)
- Rapport budget mensuel (1er du mois)
- Rapport maison mensuel (1er du mois)
- Alertes anomalies énergie/budget

### 10.2 Emails proposés

| # | Email | Déclencheur | Contenu |
|---|-------|-------------|---------|
| E1 | **Résumé nutritionnel mensuel** | 1er du mois | Diversité repas, scores nutri, tendances |
| E2 | **Bilan trimestriel jardin** | Trimestriel | Récoltes vs prévisions, planning saison suivante |
| E4 | **Backup confirmation** | Après backup réussi | Confirmation avec taille et hash du backup |
| E5 | **Rapport Jules mensuel** | 1er du mois | Jalons atteints, prochaines étapes, photos |

---

## 11. Mode admin manuel (pour tests)

### 11.1 Capacités existantes (excellent — 51 endpoints)

L'admin dispose déjà de :
- ✅ Déclenchement manuel de n'importe quel job cron (`POST /admin/jobs/{id}/run`)
- ✅ Mode dry-run sur les jobs
- ✅ Simulation de flux sans effets de bord (`POST /admin/simulate/flow`)
- ✅ Console IA directe (`POST /admin/ai/console`)
- ✅ Test multi-canal notifications (`POST /admin/notifications/test-all`)
- ✅ Purge cache sélective (`POST /admin/cache/purge`)
- ✅ Feature flags runtime
- ✅ Mode maintenance / mode test
- ✅ Impersonation utilisateur (1h, audité)
- ✅ Export/import config complète
- ✅ Visualisation santé bridges (`GET /admin/bridges/status`)

### 11.2 Améliorations proposées pour l'admin

| # | Feature admin | Description | Priorité |
|---|--------------|-------------|----------|
| AD1 | **Bouton "Run all bridges smoke test"** | Tester tous les 21 bridges en un clic avec rapport visuel | Haute |
| AD2 | **Replay d'événement depuis l'historique** | Sélectionner un événement passé et le re-jouer | Moyenne |
| AD3 | **Tableau de bord jobs en temps réel** | Jobs en cours, dernière exécution, prochaine, taux de succès | Moyenne |
| AD4 | **Simulateur de date** | Tester les jobs comme si on était le 1er du mois, un lundi, etc. | Haute (très pratique pour tester les cron) |
| AD5 | **Log en direct (tail)** | Stream des logs serveur en temps réel dans la page admin | Moyenne |
| AD6 | **Générateur de données de test** | Bouton pour peupler la DB avec des données réalistes | Haute |
| AD7 | **Diff de config** | Comparer la config actuelle vs la config par défaut | Basse |
| AD8 | **Page admin invisible pour l'utilisateur** | S'assurer que le lien admin n'apparaît PAS dans la sidebar classique, seulement accessible par URL ou raccourci clavier secret | Haute |

---

## 12. Tests — couverture et qualité

### 12.1 État actuel

| Domaine | Fichiers test | Couverture estimée | Statut |
|---------|---------------|-------------------|--------|
| API Auth | 3 | 90% | ✅ Bon |
| Core DB / Sessions | 8 | 85% | ✅ Bon |
| Core Cache | 5 | 80% | ✅ Bon |
| Core Models | 4 | 70% | ⚠️ Moyen |
| Core Config | 3 | 75% | ✅ OK |
| Schémas Pydantic | 6 | 80% | ✅ Bon |
| Services cuisine | 5 | 60% | ⚠️ Partiel |
| Services famille | 4 | 50% | ⚠️ Partiel |
| Services maison | 3 | 40% | ⚠️ Faible |
| Services jeux | 2 | 30% | ⚠️ Faible |
| Routes API | 35 | 45% | ⚠️ Gaps majeurs |
| Batch cooking | 1 | 0% | ❌ Tous skippés |
| Admin routes | 1+ | 20% | ⚠️ Faible |
| Bridges inter-modules | 3 | 35% | ⚠️ Faible |
| Frontend unit tests | 50+ | 60% | ⚠️ Partiel |
| Frontend E2E | 1 | 5% | ❌ Minimal |

### 12.2 Plan de tests à ajouter

| # | Priorité | Cible | Tests à écrire |
|---|----------|-------|----------------|
| T1 | Haute | `assistant.py` — `/chat` | Test endpoint (après implémentation du stub) |
| T2 | Haute | `preferences.py` | Tests CRUD préférences |
| T3 | Haute | `famille_jules.py` nutrition | Tests suivi alimentaire |
| T4 | Haute | Batch cooking service | Fixer les 15 tests skippés (problème de session DB) |
| T5 | Haute | `fonctionnalites_avancees.py` | 16 endpoints sans aucun test |
| T6 | Moyenne | `habitat.py` | Tests CRUD scenarios/propriétés |
| T7 | Moyenne | `voyages.py` | Tests CRUD voyages |
| T8 | Moyenne | `garmin.py` | Tests sync Garmin (mock API) |
| T9 | Moyenne | `upload.py` | Tests upload fichier (sans OCR) |
| T10 | Moyenne | Bridges inter-modules | Tests unitaires pour chaque bridge |
| T11 | Moyenne | WebSocket courses | Résoudre le deadlock et tester proprement |
| T12 | Basse | Admin routes | Tests pour chaque catégorie admin (audit, jobs, cache, etc.) |
| T13 | Basse | Frontend E2E | Parcours complets: login → créer recette → planifier → courses |
| T14 | Basse | Tests de contrats OpenAPI | Étendre schemathesis pour couvrir les nouveaux endpoints |

### 12.3 Nommage des fichiers de test

| Problème | Action |
|----------|--------|
| Fichiers nommés avec des phases/sprints dans les tests | Renommer tous les fichiers de test avec des noms descriptifs (ex: `test_phase_e5.py` → `test_admin_bridges.py`) |
| Fichiers `test_bridges_nim.py` — "NIM" non explicite | Renommer en `test_bridges_cross_module.py` |

---

## 13. Documentation — état et nettoyage

### 13.1 Documents à fusionner/supprimer

| Action | Fichiers | Raison |
|--------|----------|--------|
| **Fusionner** | `AUTOMATIONS.md` + `AUTOMATION_GUIDE.md` | Chevauchement — un seul guide automations |
| **Fusionner** | `CRON_JOBS.md` + `CRON_DEVELOPMENT.md` | Chevauchement — un seul guide cron |
| **Renommer** | `TELEGRAM_RECETTE_SPRINT5.md` | Nommé avec sprint → renommer `TELEGRAM_RECETTES.md` |
| **Renommer** | `EXPLAIN_ANALYZE_SPRINT2.md` | Nommé avec sprint → renommer `PERFORMANCE_QUERIES.md` |
| **Archiver/Supprimer** | `AUDIT_COMPLET_AVRIL_2026.md` (racine) | Remplacé par ce document |
| **Archiver/Supprimer** | `PLANNING_IMPLEMENTATION.md` (racine) | Plan historique, plus actif |
| **Documenter** | `docs/guides/` et `docs/user-guide/` | Contenu non référencé — ajouter un index |

### 13.2 Documentation manquante

| # | Doc à créer | Contenu |
|---|-------------|---------|
| D1 | `docs/INTER_MODULES_MAP.md` | Carte visuelle de tous les bridges avec déclencheurs et flux |
| D2 | `docs/ADMIN_QUICK_REFERENCE.md` | Cheatsheet admin avec les commandes les plus utilisées |
| D3 | `scripts/README.md` | Documentation des 18 scripts (4 non documentés actuellement) |
| D4 | Mise à jour `DEPRECATED.md` | Ajouter OCR, Vinted, gamification générale, WhatsApp |

---

## 14. UI/UX — améliorations visuelles

### 14.1 Visualisations déjà en place

| Type | Composant | Librairie | Module |
|------|-----------|-----------|--------|
| 3D Plan de maison | `plan-3d.tsx` | Three.js / @react-three/fiber | Maison |
| Jardin interactif | `vue-jardin-interactive.tsx` | SVG/Canvas | Maison |
| Heatmap numéros loto | `heatmap-numeros.tsx` | D3.js | Jeux |
| Heatmap cotes paris | `heatmap-cotes.tsx` | D3.js | Jeux |
| Heatmap nutritionnel | `heatmap-nutritionnel.tsx` | D3.js | Cuisine |
| Sankey flux financiers | `sankey-flux-financiers.tsx` | D3.js | Finances |
| Treemap budget | `treemap-budget.tsx` | D3.js | Budget |
| Treemap inventaire | `treemap-inventaire.tsx` | D3.js | Inventaire |
| Radar nutrition famille | `radar-nutrition-famille.tsx` | Recharts | Cuisine |
| Radar skills Jules | `radar-skill-jules.tsx` | Recharts | Famille |
| Calendrier énergie | `calendrier-energie.tsx` | D3.js | Maison |
| Graphe réseau modules | `graphe-reseau-modules.tsx` | D3.js | Admin |
| Sparklines | `sparkline.tsx` | SVG custom | Dashboard |
| Kanban projets | `kanban-projets.tsx` | @dnd-kit | Maison |
| Drag-n-drop dashboard | `grille-dashboard-dnd.tsx` | @dnd-kit | Dashboard |
| Timeline batch cooking | `timeline-batch-cooking.tsx` | Custom | Cuisine |

### 14.2 Améliorations UI proposées

| # | Amélioration | Description | Composant cible | Priorité |
|---|-------------|-------------|-----------------|----------|
| UI1 | **Calendrier repas visuel** | Vue mosaïque des repas avec photos miniatures (type Instagram grid) | Planning | Haute |
| UI2 | **Carte jardin 2D améliorée** | Vue satellite/plan du jardin avec zones colorées par état (planté, récolté, vide) | Jardin | Moyenne |
| UI3 | **Graphe temporel dépenses** | Courbe d'évolution des dépenses avec annotations intelligentes (points marquants) | Finances | Moyenne |
| UI4 | **Dashboard widgets personnalisables** | Permettre à l'utilisateur de choisir/réorganiser ses widgets dashboard | Dashboard | Haute |
| UI5 | **Vue chrono Jules** | Timeline verticale sculptée avec photos et jalons (type story scroll) | Jules | Haute |
| UI6 | **Mode "cuisine"** | Vue épurée pour la tablette en cuisine: gros texte, gros boutons, minuteurs intégrés | Recettes | Haute |
| UI7 | **Graphe Sankey amélioré** | Flux budget → catégories → sous-catégories avec animation au survol | Finances | Basse |
| UI8 | **Barre de progression batch cooking** | Progress bar animée avec étapes en cours, passées, à venir | Batch cooking | Moyenne |
| UI9 | **Animations micro-interactions** | Framer Motion sur les transitions de pages, les ajouts au panier, les validations | Global | Basse |
| UI10 | **Mode sombre amélioré** | Revue complète du dark mode — contraste, couleurs accent, readability | Global | Moyenne |
| UI11 | **Indicateur météo dans le header** | Mini widget météo permanent en haut de page | Layout | Basse |
| UI12 | **Skeleton loaders contextuels** | Skeletons qui ressemblent au contenu réel (pas juste des barres) | Global | Basse |
| UI13 | **Vue planning semaine en colonnes** | Planning type Google Calendar (colonnes jours, blocs horaires) | Planning | Moyenne |
| UI14 | **Diagramme de Gantt projets maison** | Visualisation temporelle des projets maison avec dépendances | Maison/Travaux | Moyenne |

### 14.3 Simplification du flux utilisateur

| # | Flux actuel | Flux simplifié proposé |
|---|------------|----------------------|
| F1 | Dashboard → Cuisine → Planning → Générer → Valider → Courses → Générer | Dashboard → **"Planifier ma semaine"** (1 bouton) → Validation → Courses auto-générées |
| F2 | Créer recette → Revenir au planning → Ajouter au planning | Depuis la recette : bouton **"Ajouter au planning de cette semaine"** |
| F3 | Inventaire → Voir péremptions → Anti-gaspillage → Voir suggestions | **Notification push directe** avec suggestions anti-gaspillage (pas besoin d'ouvrir l'app) |
| F4 | Ouvrir app → Chercher quoi faire → Naviguer entre modules | **Page Focus** (existe déjà) comme page d'accueil par défaut — le "quoi faire maintenant" |
| F5 | Aller dans maison → Entretien → Voir tâches → Cocher | **Notification avec bouton ✅** directement dans Telegram |

---

## 15. Nettoyage fichiers et nommage

### 15.1 Commentaires à mettre à jour (supprimer noms de phase)

| Type | Recherche | Remplacement |
|------|----------|--------------|
| Backend Python | `# Phase X.Y`, `# Sprint N`, `# phase N` | Supprimer ou remplacer par description fonctionnelle |
| Frontend TypeScript | `// Phase X`, `// Sprint N` | Idem |
| Fichiers de test | `test_phase_*.py`, `test_sprint_*.py` | Renommer avec noms descriptifs |
| Documentation | `*SPRINT*.md`, `*PHASE*.md` | Renommer sans référence temporelle |

### 15.2 Fichiers à renommer

| Fichier actuel | Nouveau nom | Raison |
|---------------|-------------|--------|
| `admin/whatsapp-test/page.tsx` | `admin/telegram-test/page.tsx` | Legacy WhatsApp |
| `frontend/src/bibliotheque/api/ia_avancee.ts` | `ia-avancee.ts` | Cohérence kebab-case |
| `docs/TELEGRAM_RECETTE_SPRINT5.md` | `docs/TELEGRAM_RECETTES.md` | Supprimer référence sprint |
| `docs/EXPLAIN_ANALYZE_SPRINT2.md` | `docs/PERFORMANCE_QUERIES.md` | Supprimer référence sprint |
| `sql/schema/17_migrations_absorbees.sql` | Supprimer ou remplir | Fichier vide inutile |

### 15.3 Fichiers fourre-tout à éclater

| Fichier | Lignes | Action |
|---------|--------|--------|
| `src/api/routes/fonctionnalites_avancees.py` | 16+ endpoints | Éclater en fichiers par domaine |
| `frontend/src/app/(app)/cuisine/courses/page.tsx` | 1200+ lignes | Extraire composants dans `composants/courses/` |
| `frontend/src/app/(app)/maison/travaux/page.tsx` | 730+ lignes | Extraire composants dans `composants/maison/` |
| `frontend/src/bibliotheque/validateurs.ts` | Long | Éclater par domaine (`validateurs-recettes.ts`, `validateurs-famille.ts`, etc.) |

---

## 16. Axes d'innovation

### 16.1 UX — Quick wins à fort impact

| # | Innovation | Description | Impact utilisateur |
|---|-----------|-------------|-------------------|
| X1 | **Mode "Quick Add" global** | `Cmd+K` pour ajouter rapidement: recette, article courses, note, tâche — sans naviguer | ⭐⭐⭐ Gain de temps majeur |
| X2 | **Widget tablette écran d'accueil** | Widget Android pour tablette avec repas du jour + tâches urgentes | ⭐⭐⭐ Pratique au quotidien |
| X3 | **PWA offline complète** | Toutes les données critiques en IndexedDB, sync au retour online | ⭐⭐ Fiabilité |

### 16.2 Data & intelligence

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X6 | **Score foyer** | Indicateur composite: nutrition + budget + entretien + routines = score de bien-être familial | ⭐⭐ Vue d'ensemble |
| X7 | **Prédictions intelligentes** | ML sur 6 mois de données: prédire budget, courses, tâches → anticipation | ⭐⭐⭐ Proactif vs réactif |
| X8 | **Saisonnalité automatique** | Adapter automatiquement les recettes/jardin à la saison sans action utilisateur | ⭐⭐ Naturel |
| X9 | **"Pourquoi cette suggestion?"** | Expliquer d'où vient chaque suggestion IA (transparence) | ⭐ Confiance utilisateur |

### 16.3 Intégrations

| # | Innovation | Description | Impact |
|---|-----------|-------------|--------|
| X11 | **Google Calendar sync bidirectionnelle** | Les événements planning/tâches s'ajoutent automatiquement au Google Calendar | ⭐⭐⭐ Centralisation agenda |
| X12 | **Import recettes par URL amélioré** | Coller URL → parsing automatique des ingrédients/étapes de n'importe quel site de recettes | ⭐⭐ Gain de temps |

---

## 17. Plan d'exécution priorisé

### Phase 1 — Nettoyage & corrections (priorité critique)

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 1.1 | Supprimer tous les endpoints OCR (L1) | 2h | Cohérence avec les préférences utilisateur |
| 1.2 | Supprimer code Vinted (L2) | 1h | Idem |
| 1.3 | Limiter gamification au Garmin (L3) | 2h | Idem |
| 1.4 | Supprimer référence "jeu responsable" (L4) | 30min | Idem |
| 1.5 | Implémenter les 5 stubs `pass` (B1-B4) | 4h | Bugs silencieux |
| 1.6 | Supprimer `ocr_service.py`, `rerun_profiler.py` (L6, L7) | 30min | Code mort |
| 1.7 | Renommer `SauvegardeMoelleOsseuseDB` (B8) | 15min | Lisibilité |
| 1.8 | Renommer `whatsapp-test/` → `telegram-test/` (L13) | 15min | Cohérence |

### Phase 2 — Nettoyage commentaires et nommage

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 2.1 | Supprimer/remplacer tous les commentaires Phase/Sprint (150+) | 3h | Lisibilité code |
| 2.2 | Renommer fichiers docs avec sprint/phase | 30min | Clarté documentation |
| 2.3 | Renommer fichiers de test avec noms descriptifs | 1h | Clarté tests |
| 2.4 | Renommer `ia_avancee.ts` → `ia-avancee.ts` | 15min | Cohérence |
| 2.5 | Éclater `fonctionnalites_avancees.py` en fichiers spécifiques | 2h | Organisation |
| 2.6 | Éclater `validateurs.ts` par domaine | 1h | Maintenance |

### Phase 3 — Consolidation SQL et données

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 3.1 | Dédupliquer indexes SQL (S1) | 30min | Propreté |
| 3.2 | Résoudre fichier `17_migrations_absorbees.sql` (S2) | 15min | Clarté |
| 3.3 | Drop tables orphelines après validation (S3) | 1h | Propreté DB |
| 3.4 | Régénérer `INIT_COMPLET.sql` (S5) | 15min | Cohérence |
| 3.5 | Relancer audit ORM↔SQL (S6) | 15min | Validation |

### Phase 4 — Tests et couverture

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 4.1 | Fixer les 15 tests batch cooking skippés | 3h | Couverture |
| 4.2 | Tests pour `fonctionnalites_avancees.py` (16 endpoints) | 4h | Couverture critique |
| 4.3 | Tests bridges inter-modules | 4h | Sécurité des flux |
| 4.4 | Tests `habitat.py`, `voyages.py`, `garmin.py` | 3h | Couverture |
| 4.5 | Tests admin routes complets | 3h | Sécurité admin |
| 4.6 | Frontend E2E: parcours login → course | 3h | Validation intégration |
| 4.7 | Résoudre deadlock WebSocket test | 2h | Couverture en temps réel |

### Phase 5 — Documentation

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 5.1 | Fusionner `AUTOMATIONS.md` + `AUTOMATION_GUIDE.md` | 1h | Clarté |
| 5.2 | Fusionner `CRON_JOBS.md` + `CRON_DEVELOPMENT.md` | 1h | Clarté |
| 5.3 | Créer `docs/INTER_MODULES_MAP.md` | 2h | Compréhension architecture |
| 5.4 | Documenter les 4 scripts non documentés | 1h | Onboarding |
| 5.5 | Mise à jour `DEPRECATED.md` | 30min | Référence complète |
| 5.6 | Archiver fichiers racine (`PLANNING_IMPLEMENTATION.md`, etc.) | 15min | Propreté |

### Phase 6 — Interactions inter-modules

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 6.1 | Bridge I1: Planning validé → Courses auto | 3h | ⭐⭐⭐ Gain de temps utilisateur |
| 6.2 | Bridge I5: Entretien terminé → MAJ équipement | 2h | Cohérence données |
| 6.3 | Bridge I6: Batch cooking → Planning semaine | 2h | Enchaînement logique |
| 6.4 | Bridge I10: Feedback recette → Poids suggestion | 2h | Amélioration continue |

### Phase 7 — IA et automations

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 7.1 | IA3: Résumé matinal personnalisé Telegram | 3h | ⭐⭐⭐ Valeur quotidienne |
| 7.2 | IA4: Adaptation recettes "J'ai pas de X" | 4h | Pratique en cuisine |
| 7.3 | IA10: Coach entretien prédictif | 3h | Proactif |
| 7.4 | Jobs J1-J8: Nouveaux jobs cron | 4h | Automatisation |
| 7.5 | Automations A1-A5: Nouvelles règles | 3h | Automatisation |

### Phase 8 — Telegram et notifications

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 8.1 | Commandes Telegram T1-T8 | 4h | Accès rapide mobile |
| 8.2 | Interactions enrichies T9-T12 | 4h | UX Telegram |
| 8.3 | Emails manquants E1-E5 | 3h | Communications complètes |

### Phase 9 — UI/UX améliorations

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 9.1 | UI1: Calendrier repas avec photos miniatures | 4h | Visuel planning |
| 9.2 | UI4: Dashboard widgets personnalisables | 6h | Personnalisation |
| 9.3 | UI5: Timeline Jules style story | 4h | Suivi enfant |
| 9.4 | UI6: Mode cuisine tablette | 4h | Expérience cuisine |
| 9.5 | F1-F5: Simplification des flux utilisateur | 6h | UX globale |
| 9.6 | UI13: Planning colonnes style Google Calendar | 4h | Visualisation planning |
| 9.7 | UI14: Diagramme de Gantt projets maison | 4h | Visualisation projets |
| 9.8 | Refactoring pages longues (courses 1200L, travaux 730L) | 3h | Maintenabilité |

### Phase 10 — Mode admin avancé

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 10.1 | AD4: Simulateur de date pour tester les cron | 3h | Confort dev/test |
| 10.2 | AD6: Générateur de données de test | 3h | Rapidité tests |
| 10.3 | AD8: Admin invisible dans la sidebar | 1h | Séparation admin/user |
| 10.4 | AD1: Smoke test tous bridges en 1 clic | 2h | Validation rapide |

### Phase 11 — Innovations

| # | Tâche | Effort estimé | Impact |
|---|-------|---------------|--------|
| 11.1 | X1: Mode Quick Add global (Cmd+K) | 4h | ⭐⭐⭐ |
| 11.2 | X6: Score foyer composite | 3h | ⭐⭐ |
| 11.3 | X11: Google Calendar sync bidirectionnelle | 4h | ⭐⭐⭐ |

---

## Récapitulatif des chiffres clés

| Métrique | Valeur |
|----------|--------|
| Routes API | 57 fichiers, ~200+ endpoints |
| Modèles ORM | 32 fichiers |
| Schémas Pydantic | 30 fichiers |
| Tables SQL | ~130 |
| Pages frontend | 42+ |
| Composants frontend | 138+ |
| Clients API frontend | 33 |
| Hooks React | 19 |
| Tests backend | 234 fichiers |
| Tests frontend | 50+ fichiers |
| Jobs cron | 68 enregistrés |
| Événements bus | 32 types, 51 subscribers |
| Bridges inter-modules | 21+ |
| Canaux de notification | 4 (ntfy, push, email, Telegram) |
| Endpoints admin | 51 |
| Feature flags | 18 |
| Documentation | 45+ fichiers |
| Bugs détectés | 14 (5 critiques, 5 moyens, 4 cohérence) |
| Code mort à supprimer | 9 éléments identifiés |
| Tests manquants | 14 domaines prioritaires |
| Nouvelles interactions proposées | 9 bridges |
| Nouvelles opportunités IA | 10 |
| Nouveaux jobs proposés | 8 |
| Nouvelles commandes Telegram | 8 + 4 enrichies |
| Améliorations UI | 14 propositions |
| Innovations | 15 axes |

---

*Ce document remplace `AUDIT_COMPLET_AVRIL_2026.md` et sert de roadmap pour les prochaines itérations de développement.*
