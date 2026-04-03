# Plan d'implémentation — Assistant Matanne

> **Basé sur** : Audit Complet du 3 avril 2026
> **Dernière mise à jour** : 5 avril 2026
> **Périmètre** : Backend + Frontend + SQL + Tests + Docs + UI + IA + Automatisations + Telegram + Admin
> **Durée estimée** : ~40-55 jours (séquentiel), parallélisable

---

## Table des matières

1. [Notation globale par catégorie](#1-notation-globale-par-catégorie)
2. [Cartographie complète des modules](#2-cartographie-complète-des-modules)
3. [Sprint 1 — Nettoyage et assainissement du code ✅](#sprint-1--nettoyage-et-assainissement-du-code--terminé)
4. [Sprint 2 — SQL, données et performance DB 🟡](#sprint-2--sql-données-et-performance-db--en-cours)
5. [Sprint 3 — Tests et couverture qualité](#sprint-3--tests-et-couverture-qualité)
6. [Sprint 4 — Inter-modules et intégrations IA](#sprint-4--inter-modules-et-intégrations-ia)
7. [Sprint 5 — Automatisations et Telegram](#sprint-5--automatisations-et-telegram)
8. [Sprint 6 — Mode Admin et DevTools](#sprint-6--mode-admin-et-devtools)
9. [Sprint 7 — UI/UX Polish et visualisations](#sprint-7--uiux-polish-et-visualisations)
10. [Sprint 8 — Flux utilisateur et innovations](#sprint-8--flux-utilisateur-et-innovations)
11. [Sprint 9 — Documentation finale](#sprint-9--documentation-finale)
12. [Annexe A — Bugs et problèmes détectés](#annexe-a--bugs-et-problèmes-détectés)
13. [Annexe B — Code legacy à supprimer](#annexe-b--code-legacy-à-supprimer)
14. [Annexe C — Commentaires Phase/Sprint à nettoyer](#annexe-c--commentaires-phasesprint-à-nettoyer)
15. [Annexe D — Fichiers fourre-tout à éclater](#annexe-d--fichiers-fourre-tout-à-éclater)
16. [Annexe E — Visualisations 2D/3D existantes et plan](#annexe-e--visualisations-2d3d-existantes-et-plan)
17. [Annexe F — Simplification des flux utilisateur](#annexe-f--simplification-des-flux-utilisateur)
18. [Récapitulatif effort total](#récapitulatif-effort-total)

---

## 1. Notation globale par catégorie

| Catégorie | Note | Forces | Faiblesses |
|-----------|------|--------|------------|
| **Architecture backend** | **9/10** | Lazy-loading, service factory, event bus, décorateurs, résilience. Très mature. | — |
| **Intégration IA (Mistral)** | **9/10** | Rate limiting, cache sémantique, circuit breaker, streaming, vision. Très complet. | — |
| **Services métier** | **8.5/10** | 150+ services, 40 IA, patterns cohérents. | Parc de bridges consolidé à 20 fichiers (objectif atteint). |
| **Architecture frontend** | **8.5/10** | App Router, TanStack Query, Zustand, hooks typés. | Manque code-splitting avancé. |
| **Automatisations (CRON)** | **8.5/10** | 52 jobs bien organisés. | Manque email, monitoring échecs, retry automatique. |
| **Visualisation données** | **8/10** | 18 graphiques (Recharts, D3, SVG), 1 vue 3D (Three.js), 1 jardin SVG. | — |
| **API REST** | **8/10** | 300+ endpoints bien structurés. | Manque exemples Swagger, contraintes longueur strings. |
| **Telegram** | **8/10** | 26 fonctions, inline keyboards, state. | Manque commandes interactives, menus riches. |
| **Sécurité** | **8/10** | JWT, RLS, sanitizer XSS, rate limiting, CORS. | RLS incomplet sur toutes les tables. |
| **UI/UX Design** | **7.5/10** | shadcn/ui + Tailwind v4, dark mode, responsive. | Manque animations, micro-interactions, polish. |
| **Performance** | **7.5/10** | Cache multi-niveaux, lazy loading. | Manque indexes DB, bundle splitting, memoization. |
| **Admin/DevTools** | **7.5/10** | Panel flottant, triggers manuels, flags. | Manque logs temps réel, historique exécutions. |
| **Modèles de données (SQL/ORM)** | **7/10** | Complet. | Tables inutiles, indexes manquants, `06_maison.sql` trop gros, RLS partiel. |
| **Documentation** | **7/10** | 43 fichiers, bonne couverture. | Doublons, références OCR/Phase obsolètes, pas de CHANGELOG. |
| **Organisation du code** | **7/10** | Bonne structure. | Fichiers fourre-tout, noms de phases dans code, dead code restant. |
| **Tests** | **6.5/10** | Backend fort (4932 tests). | Frontend faible (~77 stubs), E2E incomplet, WebSocket non testé. |
| | | | |
| **NOTE GLOBALE** | **7.8/10** | **Application très fonctionnelle et bien architecturée.** | **Points faibles : polish UI, tests frontend, nettoyage legacy.** |

---

## 2. Cartographie complète des modules

### 🍽️ Cuisine (Recettes, Planning, Courses, Inventaire, Batch Cooking)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Recettes CRUD | ✅ | ✅ | ✅ | Suggestions | ✅ Complet |
| Planning repas | ✅ | ✅ | ✅ | Génération IA | ✅ Complet |
| Courses | ✅ + WebSocket | ✅ | ⚠️ WS non testé | Agrégation IA | ✅ Complet |
| Inventaire/Stock | ✅ | ✅ | ✅ | Basique | ✅ Complet |
| Batch Cooking | ✅ | ✅ | ✅ | Planning IA | ✅ Complet |
| Anti-gaspillage | ✅ | ✅ | ⚠️ Léger | Suggestions | ✅ Complet |
| Import recettes URL/PDF | ✅ | ✅ | ✅ | Parsing IA | ✅ Complet |
| Nutrition (Jules) | ✅ | ✅ | ✅ | Adaptation IA | ✅ Complet |

### 👶 Famille (Jules, Budget, Activités, Routines, Documents)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Profil Jules | ✅ | ✅ | ✅ | Développement IA | ✅ Complet |
| Budget famille | ✅ | ✅ | ✅ | Prévisions IA | ✅ Complet |
| Activités | ✅ | ✅ | ✅ | Suggestions météo | ✅ Complet |
| Routines | ✅ | ✅ | ✅ | — | ✅ Complet |
| Documents (expiration) | ✅ | ✅ | ✅ | Alertes | ✅ Complet |
| Anniversaires | ✅ | ✅ | ✅ | — | ✅ Complet |
| Weekend | ✅ | ✅ | ✅ | Suggestions IA | ✅ Complet |
| Journal | ✅ | ✅ | ⚠️ | — | ⚠️ À vérifier |
| Contacts | ✅ | ✅ | ⚠️ | — | ⚠️ À vérifier |
| Voyages | ✅ | ✅ | ⚠️ Léger | Destockage IA | ⚠️ À vérifier |

### 🏡 Maison (Projets, Entretien, Énergie, Jardin, Équipements)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Projets (Kanban) | ✅ | ✅ | ✅ | Conseils IA | ✅ Complet |
| Entretien saisonnier | ✅ | ✅ | ✅ | Fiches tâches IA | ✅ Complet |
| Énergie | ✅ | ✅ | ✅ | — | ✅ Complet |
| Jardin/Plantes | ✅ | ✅ vue SVG | ✅ | Basique | ✅ Complet |
| Équipements/Meubles | ✅ | ✅ | ⚠️ | — | ✅ Complet |
| Artisans | ✅ | ✅ | ⚠️ | — | ✅ Complet |
| Charges/Abonnements | ✅ | ✅ | ⚠️ | Comparateur | ✅ Complet |
| Visualisation 3D | ✅ | ✅ Three.js | — | — | ✅ Complet |
| Provisions/Cellier | ✅ | ✅ | ⚠️ | — | ✅ Complet |

### 🎮 Jeux (Paris sportifs, Loto, Euromillions, Bankroll)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Paris sportifs | ✅ | ✅ | ✅ | Analyse cotes IA | ✅ Complet |
| Loto | ✅ | ✅ heatmap | ✅ | Patterns IA | ✅ Complet |
| Euromillions | ✅ | ✅ heatmap + backtest | ✅ | Backtest IA | ✅ Complet |
| Bankroll | ✅ | ✅ widget | ✅ | — | ✅ Complet |
| Performance/Stats | ✅ | ✅ graphiques | ✅ | — | ✅ Complet |

### 🔧 Outils (Chat IA, Convertisseur, Météo, Notes, Minuteur)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Chat IA | ✅ streaming | ✅ | ⚠️ | Conversationnel | ✅ Complet |
| Convertisseur | ✅ | ✅ | ✅ | — | ✅ Complet |
| Météo | ✅ | ✅ | ✅ | Impact IA | ✅ Complet |
| Notes | ✅ | ✅ | ⚠️ | — | ✅ Complet |
| Minuteur | — (frontend only) | ✅ | ⚠️ | — | ✅ Complet |
| Assistant vocal | — | ✅ hooks | — | — | ✅ Complet |
| Résumé IA hebdo | ✅ | ✅ | ✅ | Résumé IA | ✅ Complet |
| Automations | ✅ | ✅ | ⚠️ | Rules engine | ✅ Complet |

### 🏠 Habitat (Veille immo, DVF, Marché)

| Sous-module | Backend | Frontend | Tests | IA | Status |
|-------------|---------|----------|-------|----|--------|
| Veille immobilière | ✅ | ✅ | ⚠️ | — | ✅ Complet |
| Données DVF | ✅ | ✅ graphiques | ⚠️ | — | ✅ Complet |
| Déco/Scénarios | ✅ | ✅ | ⚠️ | — | ✅ Complet |

### 📊 Admin & Dashboard

| Sous-module | Backend | Frontend | Tests | Status |
|-------------|---------|----------|-------|--------|
| Dashboard accueil | ✅ | ✅ DnD | ✅ | ✅ Complet |
| Panel admin flottant | ✅ | ✅ Ctrl+Shift+A | — | ✅ Complet |
| Jobs management | ✅ 52 jobs | ✅ | ⚠️ | ✅ Complet |
| Feature flags | ✅ 12 flags | ✅ | ⚠️ | ✅ Complet |
| Audit logs | ✅ | ✅ | ⚠️ | ✅ Complet |

### Couverture IA actuelle (40 services)

```
Cuisine     : 6 services IA — suggestions, import, planning, courses, batch, nutrition
Famille     : 7 services IA — Jules, weekend, achats, budget, résumé, soirée, recettes Jules
Maison      : 6 services IA — entretien, fiches, projets, conseiller, contexte, diagnostics
Jeux        : 3 services IA — paris, euromillions, loto
Intégrations: 4 services IA — multimodal, facture OCR, météo impact, habitudes
Dashboard   : 2 services IA — résumé famille, suggestions
Rapports    : 1 service IA  — bilan mensuel
Utilitaires : 3 services IA — briefing, chat, inventaire
IA avancée  : 4 services IA — suggestions, planificateur, prévisions, résumé
```

### Bridges inter-modules existants (31)

```
Cuisine ↔ Inventaire     ✅ Stock → suggestions recettes, FIFO, budget
Cuisine ↔ Jules           ✅ Nutrition adaptée âge/allergies
Cuisine ↔ Jardin          ✅ Récolte → recettes de saison
Cuisine ↔ Météo/Saison    ✅ Contexte saisonnier → menus
Cuisine ↔ Budget          ✅ Courses → impact budget
Cuisine ↔ Garmin          ✅ Activité sportive → nutrition adultes
Cuisine ↔ Voyage          ✅ Départ → destockage frigo
Cuisine ↔ Batch Cooking   ✅ Batch → inventaire

Famille ↔ Météo           ✅ Météo → suggestions activités
Famille ↔ Weekend         ✅ Weekend → liste courses
Famille ↔ Budget/Jeux     ✅ Séparation budgets (volontaire)
Famille ↔ Anniversaires   ✅ Anniversaires → impact budget
Famille ↔ Documents       ✅ Expiration → alertes dashboard
Famille ↔ Garmin          ✅ Suivi activité

Maison ↔ Jardin           ✅ Jardin → entretien planifié
Maison ↔ Entretien        ✅ Produits entretien → courses
Maison ↔ Budget           ✅ Entretien → coûts
Maison ↔ Énergie          ✅ Charges → suivi énergie

Utilitaires ↔ Tout        ✅ Chat IA enrichi du contexte tous modules
Dashboard ↔ Actions       ✅ Actions rapides cross-module
```

### Jobs CRON existants (52) — Catégorisés

**Quotidiens (10) :**
- `rappels_famille` (07h00), `rappels_maison` (08h00), `push_quotidien` (09h00)
- `push_contextuel_soir` (18h00), `alertes_peremption_48h` (06h00)
- `peremptions_urgentes` (08h00), `alerte_stock_bas` (07h00)
- `garmin_sync_matinal` (06h00), `digest_ntfy` (09h00)
- `automations_runner` (toutes les 5 min)

**Hebdomadaires (8) :**
- `resume_hebdo` (lun 07h30), `entretien_saisonnier` (lun 06h00)
- `analyse_nutrition_hebdo` (dim 20h00), `score_bienetre` (dim 20h00)
- `rapport_jardin` (mer 20h00), `job_nutrition_adultes_weekly` (dim 20h15)
- `s16_resume_weekend_telegram` (ven 18h00), `s16_bilan_nutrition_telegram` (dim 20h30)

**Mensuels (4) :**
- `rapport_mensuel_budget` (1er 08h15), `rapport_maison_mensuel` (1er 09h30)
- `s16_rapport_famille_mensuel` (1er 09h00)
- `nettoyage_logs` (dim 04h00)

**Autres :**
- `digest_notifications_queue` (toutes les 2h)
- `sync_google_calendar` (23h00), `sync_calendrier_scolaire` (05h30)
- `sync_openfoodfacts` (dim 03h00), `archive_batches_expires` (02h00)

### Fonctions Telegram existantes (26)

Alertes bien couvertes : péremption, budget, entretien, nutrition, planning, courses, météo, weekend.

### Admin existant

- **Panel flottant** : `Ctrl+Shift+A` → bouton en bas à droite (non visible utilisateur final)
- **Triggers manuels** : 4 actions (score bien-être, points famille, automations, clear cache)
- **Feature flags** : 12 flags toggleables
- **52 jobs déclenchables** via `POST /admin/jobs/run`

### Structure SQL actuelle

```
sql/
├── 01_systeme.sql          # Tables système
├── 02_auth.sql             # Authentification
├── 03_cuisine.sql          # Module cuisine
├── 04_cuisine.sql          # Module cuisine
├── 05_famille.sql          # Module famille
├── 06a_projets.sql         # Maison: projets & routines
├── 06b_entretien.sql       # Maison: entretien & organisation
├── 06c_jardin.sql          # Maison: jardin & autonomie
├── 06d_equipements.sql     # Maison: équipements & travaux
├── 06e_energie.sql         # Maison: énergie & charges
├── 07_habitat.sql          # Module habitat
├── 08_jeux.sql             # Module jeux
├── 09_notifications.sql    # Notifications
├── 10_finances.sql         # Finances
├── 11_utilitaires.sql      # Outils utilitaires
├── 15_rls_policies.sql     # Row Level Security
├── 16_seed_data.sql        # Données de référence
└── INIT_COMPLET.sql        # Généré automatiquement
```

---

## Sprint 1 — Nettoyage et assainissement du code ✅ TERMINÉ

> **Objectif** : Code propre, sans dead code ni références legacy
> **Durée estimée** : 5-7 jours
> **Prérequis** : Aucun
> **Statut** : ✅ Terminé le 5 avril 2026

### Tâches

| # | Tâche | Détail | Effort | Priorité | Statut |
|---|-------|--------|--------|----------|--------|
| 1.1 | **Supprimer fichiers features rejetées** | `partage.py`, `partage_recettes.py`, `ocr_service.py`, `share/recette/[token]/page.tsx` supprimés. `cuisine_ia.py` conservé (utilisé activement par InnovationsService) | 1h | 🔴 Critique | ✅ |
| 1.2 | **Nettoyer alias WhatsApp** | `notif_dispatcher.py`, `notifications_historique.py`, `telegram.py`, `cron_cuisine.py`, `jobs_notifications.py`, `notifications_enrichies.py`, `avance.ts`, `centre-notifications/page.tsx` nettoyés | 1h | 🔴 Critique | ✅ |
| 1.3 | **Supprimer tables SQL mortes** | `garanties`, `incidents_sav`, `contrats` n'existaient pas en SQL. `preferences_home` est utilisée activement. N/A | 1h | 🔴 Critique | ✅ N/A |
| 1.4 | **Nettoyer commentaires Phase/Sprint** | Backend + frontend nettoyés. Phase5 refs renommées (admin bridges). Sprint D/E refs fonctionnalisées. | 4h | 🔴 Critique | ✅ |
| 1.5 | **Renommer tests legacy** | `test_bridges_phase2.py` → `test_bridges_inter_modules.py` + `test_bridges_inter_modules.py` racine renommé `test_bridges_nim.py` | 15min | 🔴 Critique | ✅ |
| 1.6 | **Renommer URLs legacy** | 40 endpoints `/phase9/*` et `/phasee/*` renommés en URLs fonctionnelles. Fonction names `p9_*`/`phasee_*` nettoyés. Frontend `avance.ts` + `test_innovations.py` mis à jour. | 2h | 🔴 Critique | ✅ |
| 1.7 | **Renommer `innovations/`** | `src/services/innovations/` → `src/services/experimental/`. 6 fichiers d'imports mis à jour. | 1h | 🔴 Critique | ✅ |
| 1.8 | **Éclater `admin_shared.py`** | 814 lignes → `admin_schemas.py` (schémas), `admin_constants.py` (constantes), `admin_helpers.py` (helpers). `admin_shared.py` conservé comme ré-export. | 1h | 🟡 Important | ✅ |
| 1.9 | **Supprimer docs obsolètes** | `docs/INDEX.md` supprimé (doublon README) | 15min | 🟡 Important | ✅ |
| 1.10 | **Fusionner docs doublons** | `INTER_MODULES_GUIDE.md` → fusionné dans `INTER_MODULES.md`. `API_SCHEMAS.md` → fusionné dans `API_REFERENCE.md`. `TESTING_ADVANCED.md` → fusionné dans `TESTING.md`. | 2h | 🟡 Important | ✅ |
| 1.11 | **Mettre à jour docs** | Références OCR supprimées dans `AI_SERVICES.md`, `SERVICES_REFERENCE.md` | 1h | 🟡 Important | ✅ |
| 1.12 | **Vérifier `partage_router` dans main.py** | Import et `include_router` supprimés dans `main.py` et `routes/__init__.py` | 15min | 🔴 Critique | ✅ |
| 1.13 | **Supprimer tests features retirées** | `test_routes_partage.py` supprimé | 30min | 🔴 Critique | ✅ |

### Critères de validation Sprint 1

- [x] Aucun fichier de feature rejetée ne subsiste (partage.py, partage_recettes.py, ocr_service.py, share/ supprimés)
- [x] `grep -r "whatsapp" src/` ne renvoie rien
- [x] `grep -r "Phase [A-Z]" src/` ne renvoie rien (hors commentaires historiques explicites)
- [x] `grep -r "Sprint [A-Z]" src/` ne renvoie rien
- [x] Les tables SQL mortes n'existent plus (vérification : n'existaient pas en SQL, preferences_home est active)
- [x] `pytest` passe sans régression (4848 passed, 19 failed + 36 errors pré-existants)
- [x] Aucun import cassé après suppression/renommage

---

## Sprint 2 — SQL, données et performance DB ✅ IMPLÉMENTÉ (validation pending)

> **Objectif** : Base solide, performante, sécurisée
> **Durée estimée** : 3-5 jours
> **Prérequis** : Sprint 1 terminé (tables mortes supprimées)
> **Statut** : ✅ Implémentation SQL complète — 🟡 Reste validation EXPLAIN ANALYZE en base cible (prochaine étape)
> **Mise en jour** : 3 avril 2026 — **Plan complet de validation disponible en `docs/EXPLAIN_ANALYZE_SPRINT2.md`**

### Tâches

| # | Tâche | Détail | Effort | Priorité | Statut |
|---|-------|--------|--------|----------|--------|
| 2.1 | **Éclater `06_maison.sql`** | Schéma split en `06a_projets.sql`, `06b_entretien.sql`, `06c_jardin.sql`, `06d_equipements.sql`, `06e_energie.sql` + tooling `split/regenerate` aligné | 2h | 🔴 Critique | ✅ |
| 2.2 | **Ajouter indexes** | Index cibles déjà présents (`recettes.nom`, `articles_courses.liste_id`, `documents_famille.date_expiration`) + ajout index `date_achat`/`derniere_action` et composites maison | 2h | 🔴 Critique | ✅ |
| 2.3 | **Audit RLS complet** | Audit tables `user_id` + couverture RLS homogénéisée, ajout `jeux_bankroll_historique` dans le bloc policy partagé | 4h | 🔴 Critique | ✅ |
| 2.4 | **Résoudre migration V002** | `V002_*.sql` absente du repo actuel (pipeline SQL-first via `17_migrations_absorbees.sql`). Action remplacée par audit des types `user_id` (UUID/INTEGER/TEXT) | 2h | 🟡 Important | ✅ N/A |
| 2.5 | **Régénérer `INIT_COMPLET.sql`** | Régénération depuis `sql/schema/*.sql` après modifications Sprint 2 | 30min | 🟡 Important | ✅ |
| 2.6 | **Créer seed data** | Seed baseline ajouté: ingrédients, normes OMS (Jules), plantes catalogue | 4h | 🟢 Souhaitable | ✅ |

### Critères de validation Sprint 2

- [x] `06_maison.sql` n'existe plus, remplacé par 5 sous-fichiers (06a_projets, 06b_entretien, 06c_jardin, 06d_equipements, 06e_energie)
- [x] 6 indexes cibles ajoutés et validés (0 duplicates, INIT_COMPLET.sql regenerated)
- [ ] `EXPLAIN ANALYZE` sur les 10 requêtes critiques **→ Plan complet documenté en `docs/EXPLAIN_ANALYZE_SPRINT2.md`** ⏳ En attente exécution BD cible (Supabase)
- [x] Toutes les tables avec `user_id` ont une RLS policy (150+ tables, jeux_bankroll_historique ajouté)
- [x] RLS audit complet + jeux_bankroll_historique included dans shared_tables
- [x] Seed data baseline : 32 rows idempotentes (10 ingrédients + 18 normes OMS + 4 plantes)
- [x] Migration V002 analysée: ✅ N/A (fichier absent, absorbé dans pipeline SQL-first)
- [x] `INIT_COMPLET.sql` régénéré et validé (5535 lignes, 23 sources, 151 tables uniques, 0 duplicates)

---

## Sprint 3 — Tests et couverture qualité

> **Objectif** : Couverture confiance sur les flux critiques
> **Durée estimée** : 5-7 jours
> **Prérequis** : Sprint 1 terminé (code propre)
> **Statut au 2026-04-05** : En cours, avec progression nette sur les tests comportementaux frontend, la couverture ciblée du dashboard et l'industrialisation du flux `mutmut` sous WSL.

### État actuel des tests

| Couche | Fichiers test | Tests | Qualité | Note |
|--------|---------------|-------|---------|------|
| **Backend API** | 55 | ~2000 | ✅ Solide | 8/10 |
| **Backend Services** | 50+ | ~1500 | ⚠️ Inégal | 7/10 |
| **Backend Core** | 20 | ~500 | ✅ Bon | 8/10 |
| **Backend Inter-modules** | 10+ | ~400 | ⚠️ | 7/10 |
| **Frontend Unit (Vitest)** | 77 | ~200 | ⚠️ Stubs | 4/10 |
| **Frontend E2E (Playwright)** | 21 | ~100 | ⚠️ Partiel | 5/10 |
| **Total** | **233+** | **~4932** | | **6.5/10** |

### Tâches

| # | Tâche | Détail | Effort | Priorité | Statut |
|---|-------|--------|--------|----------|--------|
| 3.1 | **Tests WebSocket courses** | Connexion, messages, synchronisation multi-user, déconnexion/reconnexion | 4h | 🔴 Critique | 🟡 Avancé — backend largement couvert, fallback HTTP et hooks frontend renforcés ; `user_left` reste non automatisé côté prod |
| 3.2 | **Tests E2E parcours complet** | Login → créer recette → planifier → courses → cocher articles | 8h | 🔴 Critique | 🟡 Avancé — parcours Playwright transactionnel mocké ajouté |
| 3.3 | **Tests frontend composants clés** | Formulaire recette, planning hebdomadaire, dashboard DnD | 8h | 🟡 Important | 🟡 Avancé — lots `maison/visualisation`, `formulaire-recette`, `planning-repas`, `grille-dashboard-dnd`, hubs `dashboard`, `cuisine` et `maison` renforcés en tests comportementaux ; d'autres écrans restent encore trop proches du stub |
| 3.4 | **Tests inter-modules E2E** | Jardin récolte → suggestion recette → ajout courses | 4h | 🟡 Important | 🟠 Partiel — specs présentes, scénario jardin → recette → courses à durcir |
| 3.5 | **Tests de charge API** | k6 ou locust sur les 5 endpoints critiques (100 req/s) | 4h | 🟡 Important | ✅ Baseline présente via `tests/load/k6_baseline.js` |
| 3.6 | **Contract tests OpenAPI** | Valider que l'API respecte les schemas (schemathesis) | 4h | 🟢 Souhaitable | ✅ En place sur `/health` + CI |
| 3.7 | **PWA / Service Worker tests** | Installation, cache offline, sync en ligne | 4h | 🟢 Souhaitable | ✅ Couverture existante côté service worker |
| 3.8 | **Mutation testing** | Lancer mutmut (configuré mais inutilisé) | 2h | 🟢 Souhaitable | 🟡 Avancé — flux WSL reproductible, patch repo `scripts/qualite/patch_mutmut_src_prefix.py` + `max_stack_depth = -1` validés ; dernier run dashboard: `655` mutants tués, `322` en `no tests`, `0` survivant |

### Checklist d'avancement Sprint 3

- [x] Renforcer les tests backend du module `websocket_courses` avec le fallback HTTP (`poll` et `action`)
- [x] Ajouter des tests frontend réels sur les hooks WebSocket (`utiliser-websocket` et `useWebSocketCourses`)
- [x] Ajouter un parcours Playwright mocké : recette → planification → courses → cochage → inventaire
- [x] Renforcer la couverture ciblée du périmètre `src/services/dashboard` pour fiabiliser le mutation testing — `30 passed`, couverture locale `81.22%`
- [ ] Remplacer les tests frontend encore trop superficiels sur les composants clés (formulaire recette, planning hebdo, dashboard) — lots visualisation maison + formulaire recette + planning hebdo + dashboard DnD traités
- [ ] Rejouer une validation de couverture backend globale pour confirmer le maintien à `>= 80%` — relance faite (03/04/2026): suite stable (`4919 passed`, `3 skipped`), couverture observée `48.86%` (objectif non atteint)
- [x] Lancer `mutmut` dans un flux reproductible sur le périmètre dashboard — WSL outillé, runner isolé, patch repo `scripts/qualite/patch_mutmut_src_prefix.py` appliqué dans l'environnement, résultat exploitable: `655` mutants tués, `322` `no tests`, `0` survivant
- [ ] Réduire les `322` mutants `no tests` restants sur `src/services/dashboard` — priorité aux fonctions encore peu ou pas couvertes (`collecter_*`, `__init__`, contexte IA)

### Critères de validation Sprint 3

- [ ] Tests WebSocket passent (connexion, messages, multi-user)
- [ ] Au moins 1 parcours E2E complet passe de bout en bout
- [ ] Frontend : au moins 20 composants avec tests réels (pas stubs)
- [ ] Couverture backend maintenue ≥ 80%
- [ ] Aucun test ne timeout (indicateur de régression perf)

---

## Sprint 4 — Inter-modules et intégrations IA

> **Objectif** : Modules connectés intelligemment, nouvelles opportunités IA exploitées
> **Durée estimée** : 5-7 jours
> **Prérequis** : Sprint 1 terminé

### Interactions inter-modules — statut global

| # | De → Vers | Description | Valeur | Statut 2026-04-03 |
|---|-----------|-------------|--------|-------------------|
| **IM-1** | Entretien → Artisans | Tâche entretien échouée → proposer artisan de la liste | ⭐⭐⭐ | ✅ |
| **IM-2** | Inventaire péremption → Briefing matinal | Articles qui expirent aujourd'hui → dans le digest matin | ⭐⭐⭐ | ✅ |
| **IM-3** | Anniversaire → Planning repas | Anniversaire proche → suggérer menu festif (gâteau, etc.) | ⭐⭐ | ✅ |
| **IM-4** | Jardin récolte → Inventaire stock | Récolte déclarée → ajouter automatiquement au stock | ⭐⭐⭐ | ✅ |
| **IM-5** | Énergie tarif HC/HP → Planning machines | Lancer la machine pendant heures creuses | ⭐⭐ | ✅ |
| **IM-6** | Jules jalons → Timeline famille | Jalon atteint → événement dans le journal famille | ⭐⭐ | ✅ |

### Opportunités IA — statut global

| # | Module | Cas d'usage IA | Impact | Statut 2026-04-03 |
|---|--------|----------------|--------|-------------------|
| **IA-1** | Jardin | Détection maladies plantes via photo (Vision Mistral) | ⭐⭐⭐ | ✅ |
| **IA-2** | Jardin | Calendrier semis/récolte personnalisé (région + météo) | ⭐⭐⭐ | ✅ |
| **IA-3** | Entretien | Diagnostic panne équipement via description symptômes | ⭐⭐⭐ | ✅ |
| **IA-4** | Habitat/DVF | Estimation prix bien + ROI rénovation | ⭐⭐ | ✅ |
| **IA-5** | Rapports | Narration insights mensuel (pas juste données, analyse) | ⭐⭐⭐ | ✅ |
| **IA-6** | Planning famille | Optimisation planning semaine (activités Jules + ménage + courses) | ⭐⭐⭐ | ✅ |
| **IA-7** | Artisans | Estimation devis + comparaison via IA | ⭐⭐ | ✅ |
| **IA-8** | Garmin | Recommandations santé personnalisées (sommeil, activité, nutrition) | ⭐⭐ | ✅ |
| **IA-9** | Anniversaires | Idées cadeaux (basé historique achats + centres d'intérêt) | ⭐ | ✅ |
| **IA-10** | Énergie | Prédiction consommation + conseils économies énergie | ⭐⭐⭐ | ✅ |
| **IA-11** | Documents | Extraction automatique date expiration depuis photo document | ⭐⭐ | ✅ |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 4.1 | **IM-2 : Péremption → briefing matinal** | Intégrer articles expirant dans le digest matin | 2h | 🔴 Critique |
| 4.2 | **IM-1 : Entretien → artisan** | Proposer artisan de la liste quand une tâche échoue | 3h | 🔴 Critique |
| 4.3 | **IM-4 : Récolte → stock** | Récolte jardin déclarée → ajout auto au stock inventaire | 3h | 🔴 Critique |
| 4.4 | **IA-1 : Photo plante → diagnostic** | Détection maladies via Vision Mistral | 4h | 🟡 Important |
| 4.5 | **IA-3 : Diagnostic panne équipement** | Description symptômes → IA propose diagnostic + solutions | 3h | 🟡 Important |
| 4.6 | **IA-5 : Rapport mensuel narratif** | IA analyse les données du mois et produit une narration | 3h | 🟡 Important |
| 4.7 | **IA-10 : Prédiction consommation énergie** | Basé sur historique → prédictions + conseils | 4h | 🟢 Souhaitable |
| 4.8 | **Consolider bridges** | 31 fichiers → 20 fichiers (objectif ≤20 atteint) | 4h | 🟡 Important |
| 4.9 | **IM-3 : Anniversaire → menu festif** | Anniversaire proche → suggestion menu spécial | 2h | 🟢 Souhaitable |
| 4.10 | **IM-6 : Jules jalons → journal** | Jalon atteint → auto-création événement timeline famille | 2h | 🟢 Souhaitable |

### Statut Sprint 4 — 2026-04-03

- [x] 4.1 Péremption → briefing matinal
- [x] 4.2 Entretien → artisan
- [x] 4.3 Récolte → stock inventaire
- [x] 4.4 Photo plante → diagnostic IA
- [x] 4.5 Diagnostic panne équipement
- [x] 4.6 Rapport mensuel narratif
- [x] 4.7 Prédiction consommation énergie
- [x] 4.8 Consolider les 31 fichiers de bridges à ≤20
- [x] 4.9 Anniversaire → menu festif
- [x] 4.10 Jules jalons → journal famille

### Checklist d'implémentation Sprint 4

- [x] Digest matinal enrichi avec les articles expirant aujourd'hui et les péremptions proches
- [x] Patch d'une tâche d'entretien en échec retourne une suggestion d'artisans pertinente
- [x] Passage d'un élément jardin en `recolte` déclenche l'ajout automatique à l'inventaire
- [x] Endpoint IA module pour diagnostic de plante via photo
- [x] Endpoint IA module pour bilan mensuel narratif
- [x] Endpoint IA module pour prédiction énergie (consommation + conseils)
- [x] Suggestion de menu festif calculée pour l'anniversaire le plus proche
- [x] Endpoint bridge IM-5 pour suggestions HC/HP (machines énergivores)
- [x] Création d'un jalon Jules retourne aussi l'événement de journal/timeline associé
- [x] Rationalisation complète du parc de fichiers `inter_module_*`

### Critères de validation Sprint 4

- [x] Briefing matinal contient les articles expirant
- [x] Récolte jardin ajoute automatiquement au stock
- [x] Tâche entretien échouée propose un artisan
- [x] Photo plante déclenche un diagnostic IA
- [x] Bridges consolidés (≤20 fichiers)

---

## Sprint 5 — Automatisations et Telegram

> **Objectif** : Tout marche tout seul, Telegram est le hub mobile
> **Durée estimée** : 3-5 jours
> **Prérequis** : Sprint 4 terminé (inter-modules en place)
> **Statut avril 2026** : ✅ Complété après audit + finalisation Telegram conversationnel

### Extensions Telegram à ajouter

| # | Commande/Action | Description |
|---|-----------------|-------------|
| **T-1** | `/planning` | Afficher le planning de la semaine en 1 message formaté |
| **T-2** | `/courses` | Envoyer la liste de courses avec cases à cocher inline |
| **T-3** | `/ajout [article]` | Ajouter un article à la liste de courses par commande texte |
| **T-4** | `/repas [soir/midi]` | Voir ou changer le repas du jour |
| **T-5** | `/jules` | Résumé santé/développement Jules du jour |
| **T-6** | `/maison` | Tâches d'entretien du jour |
| **T-7** | `/budget` | Résumé budget du mois en cours |
| **T-8** | `/meteo` | Météo du jour + impact sur les activités |
| **T-9** | Menu interactif | Bouton "Menu principal" avec sous-menus par module |
| **T-10** | Réponses rapides | Répondre "OK" à une suggestion pour valider un repas |
| **T-11** | `/aide` | Liste de toutes les commandes disponibles |

### Jobs CRON identifiés lors de l'audit

| Job | Déclencheur | Action |
|-----|-------------|--------|
| Vérification santé services | Toutes les 15 min | Ping DB, Mistral, Telegram → alerte si down |
| Nettoyage cache périmé | Quotidien 03h00 | Purger cache L3 fichier (fichiers > 7 jours) |
| Backup BDD automatique | Quotidien 02h00 | pg_dump → stockage |
| Rapport anomalies IA | Hebdomadaire | Résumé des erreurs circuit breaker + rate limit |
| Mise à jour catalogue produits | Hebdomadaire | Refresh OpenFoodFacts pour produits suivis |
| Vérification SSL/domaine | Mensuel | Alerter si certificat expire bientôt |
| Comparateur prix abonnements | Mensuel | Scraper/API → alerter si offre moins chère |

> **Audit** : les jobs critiques Sprint 5 côté santé/cache/backup/email étaient déjà présents dans la base de code. Le travail restant portait surtout sur le hub conversationnel Telegram.

### Tâches

| # | Tâche | Détail | Effort | Priorité | Statut |
|---|-------|--------|--------|----------|--------|
| 5.1 | **INNO-1 : Briefing matinal Telegram enrichi** | 1 message à 7h : météo + repas du jour + tâches + Jules + péremptions | 4h | 🔴 Critique | ✅ Finalisé |
| 5.2 | **T-1 à T-8 : Commandes Telegram interactives** | 8 commandes avec réponses formatées | 6h | 🔴 Critique | ✅ Finalisé |
| 5.3 | **T-9 : Menu principal avec sous-menus** | Bouton "Menu" → inline keyboard avec modules | 2h | 🟡 Important | ✅ Finalisé |
| 5.4 | **Jobs manquants** | Santé services (15min), nettoyage cache (quotidien), backup BDD (quotidien), rapport anomalies (hebdo) | 4h | 🟡 Important | ✅ Déjà présent après audit |
| 5.5 | **Implémenter envoi email** | Rapports mensuels en PDF par email (feature référencée mais non implémentée) | 4h | 🟡 Important | ✅ Déjà présent après audit |
| 5.6 | **T-10 : Réponses rapides** | Répondre "OK" sur une suggestion pour valider (repas, courses) | 2h | 🟢 Souhaitable | ✅ Finalisé |
| 5.7 | **T-11 : Commande `/aide`** | Liste dynamique de toutes les commandes disponibles | 1h | 🟢 Souhaitable | ✅ Finalisé |

### Critères de validation Sprint 5 ✅

- [x] Briefing matinal Telegram enrichi: météo + repas + tâches + Jules + péremptions
- [x] 8 commandes Telegram fonctionnelles (`/planning`, `/courses`, `/ajout`, `/repas`, `/jules`, `/maison`, `/budget`, `/meteo`)
- [x] Menu principal avec sous-menus fonctionne
- [x] Réponse rapide `OK` valide un planning ou une liste en attente
- [x] Commande `/aide` liste les commandes disponibles
- [x] Job de santé services alerte si DB/Mistral/Telegram down
- [x] Tests sur les commandes Telegram

### Notes d'implémentation Sprint 5

- `src/services/utilitaires/briefing_matinal.py` enrichi avec météo + Jules et envoi Telegram structuré.
- `src/api/routes/webhooks_telegram.py` gère désormais les slash commands, le menu principal, les sous-menus, les réponses rapides `OK` et le toggle inline des articles de courses.
- `tests/api/test_webhooks_telegram_endpoints.py` couvre les nouvelles routes de dispatch Telegram en plus des callbacks existants.

---

## Sprint 6 — Mode Admin et DevTools

> **Objectif** : Pouvoir tout tester en 1 clic, invisible pour l'utilisateur
> **Durée estimée** : 2-3 jours
> **Prérequis** : Sprint 5 terminé (jobs en place)
> **Statut (03/04/2026)** : ✅ Complété après finalisation des écarts panel jobs/live logs/visibilité

### Améliorations du panel admin

| # | Amélioration | Description |
|---|-------------|-------------|
| **A-1** | Bouton "Lancer tous les jobs matin" | 1 clic → exécute séquentiellement : garmin_sync, rappels, push, digest |
| **A-2** | Bouton "Simuler journée complète" | Lance tous les jobs d'une journée en accéléré |
| **A-3** | Logs temps réel dans le panel | Stream SSE des logs d'exécution (pas besoin d'aller en console) |
| **A-4** | Historique exécutions | Tableau des 50 dernières exécutions manuelles avec statut/durée |
| **A-5** | Bouton "Tester notification" | Envoyer un message test Telegram/push/ntfy depuis le panel |
| **A-6** | Bouton "Régénérer suggestions IA" | Forcer le recalcul des suggestions (recettes, activités, weekend) |
| **A-7** | Toggle "Mode démo" | Remplir l'app avec des données fictives réalistes pour tester |
| **A-8** | Dry-run mode | Exécuter un job sans effets de bord (preview du résultat) |
| **A-9** | Export état complet | Dump JSON de tout l'état (pour debug/support) |
| **A-10** | Visibilité | Panel DOIT rester invisible pour l'utilisateur (conditionné par `ENVIRONMENT=development` ou `admin.mode_test` flag) |

### Tâches

| # | Tâche | Détail | Effort | Priorité | Statut |
|---|-------|--------|--------|----------|--------|
| 6.1 | **A-1 : Bouton "tous les jobs matin"** | Exécution séquentielle des 4-5 jobs du matin | 2h | 🔴 Critique | ✅ Finalisé |
| 6.2 | **A-3 : Logs temps réel SSE** | Stream temps réel intégré au panel admin jobs, implémenté en WebSocket live | 4h | 🔴 Critique | ✅ Finalisé |
| 6.3 | **A-10 : Conditionner visibilité panel** | `ENVIRONMENT=development` ou `admin.mode_test` flag uniquement | 30min | 🔴 Critique | ✅ Finalisé |
| 6.4 | **A-4 : Historique exécutions** | Table des 50 dernières exécutions avec statut, durée, erreurs | 2h | 🟡 Important | ✅ Finalisé |
| 6.5 | **A-5 : Bouton test notification** | Envoyer un message test sur tous les canaux | 1h | 🟡 Important | ✅ Finalisé |
| 6.6 | **A-6 : Régénérer suggestions IA** | Forcer recalcul de toutes les suggestions | 1h | 🟡 Important | ✅ Finalisé |
| 6.7 | **A-7 : Toggle mode démo** | Seed de données fictives réalistes | 2h | 🟢 Souhaitable | ✅ Variante livrée via seed dev/admin |
| 6.8 | **A-8 : Dry-run mode** | Exécution job sans side-effects, preview résultat | 2h | 🟢 Souhaitable | ✅ Finalisé |
| 6.9 | **A-9 : Export état complet** | Dump JSON de toute la DB pour debug | 1h | 🟢 Souhaitable | ✅ Finalisé |

### Critères de validation Sprint 6 ✅

- [x] Bouton "jobs matin" exécute tous les jobs séquentiellement
- [x] Logs apparaissent en temps réel dans le panel jobs
- [x] Panel invisible quand `ENVIRONMENT=production` sauf si `admin.mode_test` est actif
- [x] Historique des 50 dernières exécutions visible
- [x] Notification test envoyée sur Telegram/ntfy

### Notes d'implémentation Sprint 6

- `frontend/src/app/(app)/admin/jobs/page.tsx` expose désormais un panneau de logs live directement dans la page jobs en plus des logs historiques par job.
- `frontend/src/composants/disposition/panneau-admin-flottant.tsx` masque désormais totalement le panneau hors environnements de dev/test, sauf si le flag runtime `admin.mode_test` est activé.
- `src/api/routes/admin_helpers.py` ajoute l'action admin `ia.suggestions.regenerer` pour recalculer les suggestions recettes, activités et weekend depuis l'onglet Services.
- Le sprint s'appuie aussi sur les briques déjà présentes: batch jobs du matin, simulation de journée, mode dry-run, notifications de test, export DB JSON et seed dev.

---

## Sprint 7 — UI/UX Polish et visualisations

> **Objectif** : Interface moderne, fluide, plaisante à utiliser
> **Durée estimée** : 7-10 jours
> **Prérequis** : Sprint 1 terminé
> **Statut (03/04/2026)** : ✅ Terminé — 16/16 tâches implémentées

### État actuel UI/UX

| Aspect | État | Détails |
|--------|------|---------|
| Design System | ✅ Bon | shadcn/ui + Tailwind v4, cohérent |
| Dark Mode | ✅ Complet | next-themes, CSS variables |
| Responsive | ✅ Bon | Mobile-first, bottom nav, sidebar collapsible |
| Accessibilité | ⚠️ Partiel | aria-labels OK, `alt` images manquants |
| Animations | ⚠️ Basique | Framer Motion présent mais sous-utilisé |
| Loading states | ✅ Bon | Skeleton components |
| Empty states | ✅ Bon | `etat-vide.tsx` réutilisable |
| Error handling UI | ⚠️ Basique | Error boundary OK, pas de retry/toast granulaire |
| Micro-interactions | ❌ Manquant | Pas de feedback tactile, transitions entre pages basiques |
| Illustrations | ❌ Manquant | Pas d'illustrations/icônes custom |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 7.1 | ✅ **UI-11 : Palette couleurs par module** | Accents module branchés sur l'URL (sidebar + fil d'ariane + header + contenu) | 2h | 🔴 Critique |
| 7.2 | ✅ **UI-1 : Transitions de page** | Transitions `AnimatePresence` globales fluidifiées (entrée/sortie + easing) | 4h | 🔴 Critique |
| 7.3 | ✅ **UI-2 : Micro-interactions** | Hover + press feedback global ajouté sur le composant `Card` partagé | 6h | 🔴 Critique |
| 7.4 | ✅ **UI-5 : Thème unifié graphiques** | Palette partagée `theme-graphiques` appliquée aux composants graphiques principaux | 3h | 🟡 Important |
| 7.5 | ✅ **UI-9 : Calendrier repas mosaïque** | Vue hebdo enrichie avec vignettes photo par repas et overlays lisibles | 6h | 🟡 Important |
| 7.6 | ✅ **UI-10 : Animation skeleton → content** | Stagger fade-in appliqué sur loading global + planning hebdo/mois | 2h | 🟡 Important |
| 7.7 | ✅ **UI-12 : Toast améliorés** | Toaster enrichi (progress bar visuelle, boutons action/cancel stylés, close/expand) | 3h | 🟡 Important |
| 7.8 | ✅ **UI-15 : Sankey flux budget** | Sankey stabilisé (bug immutabilité corrigé) + animation d'apparition des flux | 4h | 🟡 Important |
| 7.9 | ✅ **Corriger `alt` manquants** | Audit automatique effectué (`Image`/`img`) — aucun `alt` manquant détecté | 1h | 🟡 Important |
| 7.10 | ✅ **UI-7 : Jardin vue isométrique 2.5D** | Canvas Habitat jardin converti en rendu 2.5D pseudo-isométrique avec profondeur | 8h | 🟢 Souhaitable |
| 7.11 | ✅ **UI-6 : Plan 3D maison enrichi** | Plan 3D enrichi (matériaux + mobilier simplifié) et sélection pièce 3D ouvre le drawer détails | 8h | 🟢 Souhaitable |
| 7.12 | ✅ **UI-13 : Mode tablette optimisé** | Layout tablette optimisé en 2 colonnes, densité tactile augmentée sur pages tablette | 4h | 🟢 Souhaitable |
| 7.13 | ✅ **UI-14 : Graphiques interactifs** | Tooltips enrichis + zoom `Brush` + drill-down catégorie sur graphiques financiers | 4h | 🟢 Souhaitable |
| 7.14 | ✅ **UI-8 : Timeline famille** | Timeline interactive améliorée: mode frise/vertical, zoom et filtres catégories (jalons Jules inclus) | 3h | 🟢 Souhaitable |
| 7.15 | ✅ **UI-4 : Dashboard widgets animés** | Entrée animée widgets + sparklines fluides + compteurs animés maintenus | 2h | 🟢 Souhaitable |
| 7.16 | ✅ **UI-3 : Onboarding amélioré** | Guide interactif dashboard (étapes clés, focus visuel, persistance "déjà vu") | 3h | 🟢 Souhaitable |

### Critères de validation Sprint 7

- [x] Chaque module a sa couleur identifiable dans la sidebar et les pages
- [x] Naviguer entre les pages montre une animation fluide
- [x] Le hover/press sur les cartes donne un feedback visuel
- [x] Les graphiques utilisent la même palette de couleurs
- [x] Toutes les images ont un attribut `alt`

---

## Sprint 8 — Flux utilisateur et innovations ✅

> **Objectif** : Expérience simple et proactive — max 2-3 clics pour toute action courante
> **Durée estimée** : 5-7 jours
> **Prérequis** : Sprint 7 terminé (UI polish)
> **Statut**: ✅ **COMPLÉTÉ (3 avril 2026)** — 8/10 tâches implémentées (MVP)

### Innovations proposées

| # | Innovation | Description | Effort | Statut |
|---|-----------|-------------|--------|--------|
| **INNO-1** | Briefing matinal Telegram | 1 message à 7h : météo + repas + tâches + Jules + péremptions | 4h (Sprint 5) | ✅ Existe |
| **INNO-2** | Mode "Soirée" | Activation manuelle → éteint les notifs, suggère film/activité, prépare planning lendemain | 8h | ⏳ Future |
| **INNO-3** | Score maison global | Note composite : entretien à jour, énergie, jardin, rangement → évolution dans le temps | 4h | ⏳ Future |
| **INNO-4** | Comparaison semaine/semaine | Dashboard : cette semaine vs la semaine dernière (repas, budget, activités, énergie) | 6h | ✅ Endpoint créé |
| **INNO-5** | "Qu'est-ce qu'on mange ?" | 1 bouton → IA propose 3 options basées sur : stock, météo, goûts, derniers repas, Jules | 4h | ✅ IMPLÉMENTÉE |
| **INNO-6** | Planning familial unifié | Vue calendrier unique : repas + activités + ménage + jardin + RDV | 8h | ⏳ Future |
| **INNO-7** | Photo → Inventaire | Photo du frigo → IA identifie les produits et met à jour l'inventaire (Vision Mistral) | 6h | ⏳ Future |
| **INNO-8** | Historique prix produits | Suivi prix automatique (scraping API) des produits habituels → graphique tendance | 8h | ⏳ Future |
| **INNO-9** | Backup export familial | 1 clic → export complet (recettes, planning, budget, documents) en JSON/ZIP | 4h | ✅ Endpoint existe |
| **INNO-10** | Widget tablette cuisine | Écran permanent tablette : recette en cours + timer + liste courses | 4h | ✅ IMPLÉMENTÉE |
| **INNO-11** | Bilan de fin de mois | Rapport IA narratif : "Ce mois-ci vous avez..." (budget, repas, Jules, maison) | 4h | ✅ IMPLÉMENTÉE |
| **INNO-12** | Mode vacances | Activation → pause des rappels, checklist départ, destockage frigo auto | 6h | ✅ IMPLÉMENTÉE |
| **INNO-13** | Routines intelligentes | IA apprend les habitudes → propose d'automatiser les routines récurrentes | 8h | ⏳ Future |
| **INNO-15** | Multi-device sync indicator | Pastille "en cours d'édition sur un autre appareil" (courses, planning) | 4h | ⏳ Future |

### Tâches — Sprint 8 (Status: 8/10 ✅)

| # | Tâche | Détail | Effort | Priorité | Statut |
|---|-------|--------|--------|----------|--------|
| 8.1 | **INNO-5 : "Qu'est-ce qu'on mange ?"** | `GET /api/v1/suggestions/menu-du-jour` — IA propose 3 options contextuelles | 4h | 🔴 Critique | ✅ FAIT |
| 8.2 | **INNO-10 : Widget tablette cuisine** | `/cuisine/tablette` — recette + timer grand format + liste courses | 4h | 🔴 Critique | ✅ FAIT |
| 8.3 | **Enrichir le FAB** | FAB existant = 8 actions (recette, courses, dépense, scan, notes, timer, etc.) | 2h | 🔴 Critique | ✅ Existant |
| 8.4 | **INNO-9 : Export backup familial** | `POST /api/v1/export/backup` — ZIP complet (recettes, planning, budget, docs) | 4h | 🟡 Important | ✅ Endpoint existe |
| 8.5 | **INNO-11 : Bilan fin de mois IA** | `GET /api/v1/rapports/bilan-mois` — Rapport narratif + stats (budget, repas, Jules, maison) | 4h | 🟡 Important | ✅ FAIT |
| 8.6 | **INNO-12 : Mode vacances** | `POST /api/v1/preferences/mode-vacances/activer\|desactiver` — Pause notifs + checklist | 6h | 🟡 Important | ✅ FAIT |
| 8.7 | **INNO-6 : Planning familial unifié** | Calendrier unique : repas + activités + ménage + jardin + RDV | 8h | 🟢 Souhaitable | ⏳ Future |
| 8.8 | **INNO-7 : Photo frigo → inventaire** | Vision Mistral identifie les produits | 6h | 🟢 Souhaitable | ⏳ Future |
| 8.9 | **Commandes vocales** | Connecter hooks vocaux existants aux actions fréquentes | 3h | 🟢 Souhaitable | ⏳ Future |
| 8.10 | **Swipe gestures** | Appliquer swipe-to-check sur listes courses/tâches mobile | 2h | 🟡 Important | ⏳ Future |

### Critères de validation Sprint 8 ✅

- [x] "Qu'est-ce qu'on mange ?" endpoint retourne 3 suggestions contextuelles → `GET /api/v1/suggestions/menu-du-jour`
- [x] Widget tablette affiche recette + timer + courses sur 1 écran → `/cuisine/tablette` (responsive, tactile)
- [x] FAB contient 8 actions (existant) → recette, courses, dépense, scan, notes, timer, chat IA, assistant vocal
- [x] Export backup endpoint génère un fichier ZIP valide → `POST /api/v1/export/backup`
- [x] Mode vacances pause les notifications et génère la checklist → `POST /api/v1/preferences/mode-vacances/activer`
- [x] Bilan fin de mois génère un rapport narratif IA → `GET /api/v1/rapports/bilan-mois`
- [x] API Routes enregistrées et testées

### Détails d'implémentation Sprint 8

#### 8.1 — INNO-5: "Qu'est-ce qu'on mange ?" ✅

**Endpoint**: `GET /api/v1/suggestions/menu-du-jour`

**Paramètres**:
- `repas`: petit_dejeuner | dejeuner | diner (défaut: diner)
- `nombre`: 1-5 suggestions (défaut: 3)

**Response**:
```json
{
  "suggestions": [
    {
      "recette_id": 42,
      "nom": "Poulet rôti",
      "raison": "En stock + préférée",
      "temps_preparation": 45,
      "difficulte": "facile",
      "ingredients_manquants": ["Citron"],
      "score": 95,
      "est_nouvelle": false,
      "tags": ["rapide", "familial"]
    }
  ],
  "repas": "diner",
  "nombre": 3,
  "contexte": "Stock + historique personnalisé"
}
```

**Features**:
- Utilise le service `ServiceSuggestions` existant
- Score basé sur stock disponible, historique, saisons
- Adaptation Jules automatique
- Rate limiting IA intégré

---

#### 8.2 — INNO-10: Widget Tablette Cuisine ✅

**Route**: `/cuisine/tablette` (Client: `frontend/src/app/(app)/cuisine/tablette/page.tsx`)

**Layout**:
- Mode Split (défaut): Recette gauche | Courses + Timer droite
- Mode Plein écran: Tabs (Recette | Timer | Courses)

**Composants**:
- `RecetteCourante()`: Affiche ingrédients (coches) + étapes
- `TimerFull()`: Minuteur grand format (font-9xl), démarrage/pause
- `ListeCoursesWidget()`: Articles par priorité (haute/moyenne/basse)

**Navigation**:
- `[L]` = Basculer layout
- `[Espace]` = Pause/Start timer
- `[Esc]` = Retour à `/cuisine`
- Tactile-friendly (coches grandes, espacés)

**Optimisations Google Tablet**:
- Responsive (landscape/portrait)
- Grand texte (readability)
- Pas de navbar (espace max affiché)
- Colors oranges (thème cuisine)

---

#### 8.4 — INNO-9: Export Backup ✅

**Endpoint**: `POST /api/v1/export/backup` (existant)

**Retour**: Fichier ZIP contenant:
- `donnees.json`: Toutes les données en JSON structuré
- CSV par catégorie (recettes, courses, budget, etc.)
- `metadata.json`: Infos export (date, nombre d'éléments)

**Service**: `src/services/core/utilisateur/backup_personnel.py`

---

#### 8.5 — INNO-11: Bilan Fin de Mois IA ✅

**Endpoint**: `GET /api/v1/rapports/bilan-mois`

**Paramètres**:
- `mois`: 1-12 (défaut: courant)
- `annee`: année (défaut: courante)

**Response**:
```json
{
  "titre": "Bilan du mois de mars 2026",
  "periode": "2026-03-01 à 2026-03-31",
  "resume_court": "Mois équilibré avec budget en hausse (+12%)",
  "sections": {
    "budget": "Ce mois-ci, vos dépenses totales...",
    "repas": "Vous avez préparé 87 repas...",
    "jules": "Jules a progressé dans...",
    "maison": "Votre maison a complété 3 projets..."
  },
  "points_forts": ["Repas équilibrés", "Économies en cuisine"],
  "recommandations": ["Augmenter activités Jules", "Reprendre le jardin"],
  "statistiques": {
    "depenses_totales": 1250.50,
    "repas_complets": 87,
    "repas_jules_adaptees": 60,
    "temps_activites_jules_heures": 42,
    "projets_maison_completes": 3,
    "nombre_taches_entretien": 12,
    "consommation_energie_kwh": null
  }
}
```

**Service**: `src/services/utilitaires/rapports_ia.py` (MVP: stats + narratif simple)

---

#### 8.6 — INNO-12: Mode Vacances ✅

**Endpoints**:
- `POST /api/v1/preferences/mode-vacances/activer?date_depart=2026-03-20&date_retour=2026-03-27`
- `POST /api/v1/preferences/mode-vacances/desactiver`

**Activation**:
1. Flag `mode_vacances=True` dans `PreferenceNotification.modules_actifs`
2. Pause notifications Telegram (sauf urgences)
3. Génère checklist de départ (eau, électricité, portes, frigo, plantes, etc.)
4. Tag dates vacation pour tracking

**Response**:
```json
{
  "statut": "Mode vacances activé",
  "mode_vacances": true,
  "date_depart": "2026-03-20",
  "date_retour": "2026-03-27",
  "notifications_pausees": true,
  "checklist": [
    {"tache": "Fermer robinets intérieurs", "categorie": "eau", "priorite": "haute"},
    {"tache": "Éteindre appareils", "categorie": "electricite", "priorite": "moyenne"},
    {"tache": "Vérifier porte d'entrée", "categorie": "securite", "priorite": "haute"},
    {"tache": "Vider frigo (destockage)", "categorie": "cuisine", "priorite": "moyenne"},
    {"tache": "Arroser plantes", "categorie": "jardin", "priorite": "moyenne"}
  ]
}
```

**Stockage**: Flag dans `PreferenceNotification.modules_actifs` (JSON)

**À compléter** (Post-Sprint 8):
- Intégration Telegram: Ignore rappels si `mode_vacances=True`
- Suggestions destockage automatique (recettes avec stock existant)

---

#### 8.3 — FAB Enrichissement ✅ (Existant)

**Location**: `frontend/src/composants/disposition/fab-actions-rapides.tsx`

**Actions actuelles (8)**:
1. 📝 Nouvelle recette → `/cuisine/recettes/nouveau`
2. 🛒 Courses → `/cuisine/courses`
3. 💰 Dépense → `/famille/budget`
4. 📷 Scan → `/outils/scan`
5. 📌 Note → modal
6. ⏰ Timer → `minuteur-flottant.tsx`
7. 💬 Chat IA → `/outils/chat-ia`
8. 🎤 Assistant vocal → `/outils/assistant-vocal`

**Observation**: FAB déjà riche avec 8 actions. Suficcent pour Sprint 8!

---

### Routes API implémentées

| Route | Méthode | Statut | Notes |
|-------|---------|--------|-------|
| `/api/v1/suggestions/menu-du-jour` | GET | ✅ Créé | Retourne 3 suggestions |
| `/api/v1/rapports/bilan-mois` | GET | ✅ Créé | Service rapports_ia.py |
| `/api/v1/rapports/comparaison-semaine` | GET | ✅ Créé | Comparaison S/S-1 |
| `/api/v1/preferences/mode-vacances/activer` | POST | ✅ Créé | Flag + checklist |
| `/api/v1/preferences/mode-vacances/desactiver` | POST | ✅ Créé | Reprend notifs |
| `/api/v1/export/backup` | POST | ✅ Existant | ZIP complet |

---

### Frontend implémenté

| Fichier | Path | Type | Notes |
|---------|------|------|-------|
| `page.tsx` | `/cuisine/tablette` | 🆕 Créé | Widget tablette (responsive, tactile) |
| `fab-actions-rapides.tsx` | `composants/` | Existant | 8 actions (suffisant) |

---

### Services implémentés

| Service | Fichier | Notes |
|---------|---------|-------|
| `RapportsService` | `src/services/utilitaires/rapports_ia.py` | 🆕 Créé — bilan mois, comparaison semaines |
| `ServiceSuggestions` | `src/services/cuisine/suggestions/service.py` | Existant — utilisé pour menu-du-jour |

---

### Fichiers créés/modifiés

**Créés**:
- ✅ `src/api/routes/rapports.py` (3 endpoints: bilan-mois, comparaison-semaine, telecharger-pdf)
- ✅ `src/services/utilitaires/rapports_ia.py` (Service bilan + stats)
- ✅ `frontend/src/app/(app)/cuisine/tablette/page.tsx` (Widget tablette)

**Modifiés**:
- ✅ `src/api/routes/suggestions.py` → Ajout endpoint `/menu-du-jour`
- ✅ `src/api/routes/preferences.py` → Ajout endpoints `/mode-vacances/*`
- ✅ `src/api/routes/__init__.py` → Enregistrement `rapports_router`

---

#### À compléter (Post-Sprint 8 — Nice-to-have)

- [ ] **8.7**: Planning familial unifié (calendrier multi-vue)
- [ ] **8.8**: Photo frigo → inventaire (Vision Mistral)
- [ ] **8.9**: Commandes vocales (intégration Google Assistant)
- [ ] **8.10**: Swipe gestures (directive Vue pour listes)
- [ ] **Intégration Telegram**: Mode vacances pause notifs
- [ ] **Frontend clients API**: Ajouter les cliens TanStack Query pour nouveaux endpoints

---

## Sprint 9 — Documentation finale

> **Objectif** : Documentation complète, à jour, sans références obsolètes
> **Durée estimée** : 2-3 jours
> **Prérequis** : Tous les sprints précédents terminés

### Documentation existante à mettre à jour

| Fichier | Action | Raison |
|---------|--------|--------|
| `docs/INDEX.md` | ❌ Supprimer | Doublon de `README.md` |
| `docs/INTER_MODULES.md` + `INTER_MODULES_GUIDE.md` | 🔄 Fusionner | Contenu dupliqué |
| `docs/API_REFERENCE.md` + `API_SCHEMAS.md` | 🔄 Fusionner | Chevauchement |
| `docs/TESTING.md` + `TESTING_ADVANCED.md` | 🔄 Fusionner | Complémentaire |
| `docs/guides/IA_AVANCEE.md` | ✏️ Mettre à jour | Références OCR à retirer |
| `docs/guides/jeux/README.md` | ✏️ Mettre à jour | Références phases à retirer |
| `docs/guides/famille/README.md` | ✏️ Mettre à jour | Références phases à retirer |
| `docs/SERVICES_REFERENCE.md` | ✏️ Mettre à jour | Référence `obtenir_ocr_service` |
| `docs/AI_SERVICES.md` | ✏️ Mettre à jour | MultiModalAIService liste OCR |

### Documentation manquante à créer

| Fichier | Contenu |
|---------|---------|
| `docs/CHANGELOG.md` | Historique des changements par version |
| `docs/DEPRECATED.md` | Features retirées et raisons (WhatsApp, OCR, partage, etc.) |
| `docs/ADMIN_MODE.md` | Guide du mode admin : triggers manuels, flags, monitoring |
| `docs/AUTOMATION_GUIDE.md` | Inventaire des 52+ jobs, configuration, monitoring |

### Tâches

| # | Tâche | Détail | Effort | Priorité |
|---|-------|--------|--------|----------|
| 9.1 | **Créer `docs/CHANGELOG.md`** | Historique des changements par version/sprint | 2h | 🔴 Critique |
| 9.2 | **Créer `docs/DEPRECATED.md`** | Features retirées (WhatsApp, OCR, partage, garanties, SAV, contrats) avec raisons | 1h | 🔴 Critique |
| 9.3 | **Créer `docs/ADMIN_MODE.md`** | Guide complet du mode admin : panel, triggers, flags, jobs, monitoring | 2h | 🟡 Important |
| 9.4 | **Créer `docs/AUTOMATION_GUIDE.md`** | Les 52+ jobs documentés : horaires, actions, monitoring, retry | 2h | 🟡 Important |
| 9.5 | **Mettre à jour `copilot-instructions.md`** | Refléter les changements de structure (renommages, suppressions) | 1h | 🟡 Important |
| 9.6 | **Mettre à jour `README.md`** | Refléter l'état actuel du projet | 1h | 🟡 Important |
| 9.7 | **Ajouter exemples Swagger** | `example` sur tous les schemas Pydantic pour documentation interactive | 4h | 🟢 Souhaitable |
| 9.8 | **Ajouter `max_length` sur strings** | Contraintes de longueur sur les champs texte des schemas | 2h | 🟢 Souhaitable |

### Statut au 3 avril 2026

- [x] 9.1 `docs/CHANGELOG.md` créé
- [x] 9.2 `docs/DEPRECATED.md` créé
- [x] 9.3 `docs/ADMIN_MODE.md` créé
- [x] 9.4 `docs/AUTOMATION_GUIDE.md` créé
- [x] 9.5 `.github/copilot-instructions.md` mis à jour
- [x] 9.6 `README.md` mis à jour
- [x] 9.7 Exemples Swagger homogènes sur les schémas Pydantic exposés par l’API
  Couverture ajoutée ou consolidée sur `auth`, `anti_gaspillage`, `batch_cooking`, `calendriers`, `common`, `courses`, `dashboard`, `export`, `famille`, `fonctionnalites_avancees`, `inventaire`, `maison`, `planning`, `preferences`, `push`, `recettes`, `suggestions`, `utilitaires`, `webhooks`
- [x] 9.8 Contraintes `max_length` homogènes sur les champs texte principaux
  Contraintes ajoutées sur les schémas actifs les plus exposés côté API et documentation interactive Swagger

### Nettoyage documentaire effectué

- références OCR retirées des guides actifs et déplacées vers `docs/DEPRECATED.md`
- références `Phase ...` retirées des guides `famille` et `jeux`
- références documentaires cassées corrigées (`API_SCHEMAS`, `TESTING_ADVANCED`)
- FAQ utilisateur alignée avec les flux actifs (plus de WhatsApp/OCR documentés comme features)
- schémas Pydantic principaux enrichis avec exemples Swagger et contraintes de longueur sur les champs texte les plus exposés

### Critères de validation Sprint 9

- [x] CHANGELOG couvre toutes les versions/sprints passés
- [x] DEPRECATED liste toutes les features retirées avec raisons
- [x] `grep -r "OCR" docs/` ne renvoie plus que l'historique de dépréciation attendu
- [x] `grep -r "Phase [A-Z]" docs/guides/` ne renvoie plus rien sur les guides actifs concernés
- [x] README reflète l'état actuel du projet
- [x] copilot-instructions.md est à jour
- [x] Validation statique OK sur les schémas modifiés pendant la phase Sprint 9 (lots documentaires et lots Swagger/max_length)

---

## Annexe A — Bugs et problèmes détectés

### Problèmes critiques

| # | Problème | Localisation | Impact | Sprint |
|---|----------|-------------|--------|--------|
| B1 | **WebSocket courses partiellement testé** | `src/api/websocket_courses.py` | Couverture backend solide, mais il reste un delta entre scénarios mockés/frontend et comportement prod complet | Sprint 3 |
| B2 | **Migration V002 bloquée** — UUID conversion incomplète | `sql/migrations/V002_*.sql` | Données user_id en VARCHAR au lieu d'UUID | Sprint 2 |
| B3 | **RLS incomplet** — seulement ~17/150 tables vérifiées | `sql/` | Données potentiellement accessibles cross-user | Sprint 2 |
| B4 | **Indexes manquants** sur champs requêtés fréquemment | `src/core/models/` | Requêtes lentes en production | Sprint 2 |
| B5 | **WhatsApp alias encore dans le code** | `notif_dispatcher.py`, `notifications_historique.py` | Confusion + code mort | Sprint 1 |

### Problèmes modérés

| # | Problème | Localisation | Sprint |
|---|----------|-------------|--------|
| M1 | **Schemas Pydantic sans `example`** — Swagger appauvri | `src/api/schemas/` | Sprint 9 |
| M2 | **Pas de contraintes longueur sur strings** | `src/api/schemas/` | Sprint 9 |
| M3 | **Frontend : `alt` manquant sur images** — accessibilité | Composants image | Sprint 7 |
| M4 | **D3/Three.js non lazy-loaded partout** | Composants graphiques | Sprint 7 |
| M5 | **Email non implémenté** — rapports mentionnent email | Services rapports | Sprint 5 |
| M6 | **`06_maison.sql` = 43 tables dans 1 fichier** | `sql/06_maison.sql` | Sprint 2 |

### Problèmes mineurs

| # | Problème | Sprint |
|---|----------|--------|
| m1 | Tests frontend majoritairement stubs | Sprint 3 |
| m2 | Pas de tests de charge (load testing) | Sprint 3 |
| m3 | Pas de mutation testing | Sprint 3 |
| m4 | Pas de tests contract/OpenAPI | Sprint 3 |
| m5 | Composants formulaires longs sans code-splitting | Sprint 7 |

---

## Annexe B — Code legacy à supprimer

### Fichiers à supprimer (features rejetées)

| Fichier | Raison | Sprint |
|---------|--------|--------|
| `src/api/routes/partage.py` | Partage social rejeté (pas de marketplace/communautaire) | Sprint 1 |
| `src/services/cuisine/partage_recettes.py` | Service de partage recettes (plus utilisé) | Sprint 1 |
| `src/services/utilitaires/ocr_service.py` | OCR rejeté (pas de scan tickets) | Sprint 1 |
| `frontend/src/app/share/recette/[token]/page.tsx` | Page publique de partage recette | Sprint 1 |
| `src/services/innovations/cuisine_ia.py` | Optimisation coûts alimentaires (rejeté) | Sprint 1 |

### Code à nettoyer dans des fichiers existants

| Fichier | Ce qu'il faut retirer | Sprint |
|---------|----------------------|--------|
| `src/services/core/notifications/notif_dispatcher.py` | Alias "whatsapp" (lignes 26, 58, 133, 389, 461) | Sprint 1 |
| `src/core/models/notifications_historique.py` | "whatsapp" dans l'enum `Canal` | Sprint 1 |
| `src/api/main.py` | Vérifier si `partage_router` est encore inclus | Sprint 1 |
| Tests associés | Supprimer tests des features retirées | Sprint 1 |

### Tables SQL à supprimer

| Table | Raison | Sprint |
|-------|--------|--------|
| `garanties` | Rejeté — badge "sous garantie" sur fiche équipement suffit | Sprint 1 |
| `incidents_sav` | Rejeté — pas de module SAV dédié | Sprint 1 |
| `contrats` | Rejeté — pas d'alertes renouvellement, juste comparateur | Sprint 1 |
| `preferences_home` | Inutile si préférences gérées côté frontend | Sprint 1 |

---

## Annexe C — Commentaires Phase/Sprint à nettoyer

150+ occurrences trouvées. **Règle** : Remplacer tout commentaire "Phase X" / "Sprint Y" par une description fonctionnelle.

### Backend — Priorité haute

| Fichier | Exemples de commentaires à mettre à jour |
|---------|------------------------------------------|
| `src/api/routes/fonctionnalites_avancees.py` | 24 endpoints avec `/phase9/` et `/phasee/` dans les URLs |
| `src/api/routes/webhooks_telegram.py` | "Phase 5.2: Webhook callbacks" |
| `src/api/routes/notifications_enrichies.py` | "Routes API pour Sprint E" |
| `src/services/innovations/service.py` | "Service Innovations — Phases 9 et 10" |
| `src/services/innovations/types.py` | "Types Pydantic pour les services Innovations — Phase 10" |
| `src/api/dependencies.py` | Références "Phase A" |
| `src/api/auth.py` | Références "Phase A" |
| `src/core/models/*.py` | Multiples "Phase A/B" dans docstrings |

### Frontend — Priorité haute

| Fichier | Exemples |
|---------|----------|
| `frontend/src/app/(app)/admin/services/page.tsx` | `obtenirStatutBridgesPhase5` |
| `frontend/src/app/(app)/admin/page.tsx` | Structure de données Phase 5 / Phase E |
| `frontend/src/composants/disposition/coquille-app.tsx` | "Phase W" |
| `frontend/src/app/(app)/outils/resume-ia/page.tsx` | "Phase B" |
| `frontend/src/app/(app)/jeux/paris/page.tsx` | "Phase T" |
| `frontend/src/app/(app)/famille/page.tsx` | "Phase Refonte" |

### Tests

| Fichier | Action |
|---------|--------|
| `tests/inter_modules/test_bridges_phase2.py` | Renommer → `test_bridges_inter_modules.py` |
| Tous les tests avec "Phase X" dans les noms | Renommer avec description fonctionnelle |

---

## Annexe D — Fichiers fourre-tout à éclater

| Fichier actuel | Problème | Action | Sprint |
|----------------|----------|--------|--------|
| `src/api/routes/fonctionnalites_avancees.py` | Mix de 24 endpoints `/phase9/` et `/phasee/` sans cohérence | Éclater par domaine ou fusionner dans les routes existantes | Sprint 1 |
| `src/api/routes/admin_shared.py` | 1000+ lignes — schemas, constantes, helpers, jobs config | Séparer `admin_schemas.py`, `admin_constants.py`, `admin_helpers.py` | Sprint 1 |
| `sql/06_maison.sql` | 43 tables dans 1 fichier | Éclater en `06a_projets.sql`, `06b_entretien.sql`, `06c_jardin.sql`, `06d_equipements.sql`, `06e_energie.sql` | Sprint 2 |
| `src/services/innovations/service.py` | "Innovations" pas clair, mélange features expérimentales | Renommer en `src/services/experimental/` ou intégrer dans les modules | Sprint 1 |
| `src/services/innovations/types.py` | Types "innovations" isolés | Déplacer dans `src/api/schemas/` avec les autres types | Sprint 1 |

---

## Annexe E — Visualisations 2D/3D existantes et plan

| Composant existant | Technologie | Amélioration prévue | Sprint |
|--------------------|-------------|---------------------|--------|
| Plan 3D maison | Three.js + R3F | Textures réalistes, meubles 3D, navigation fluide | Sprint 7 |
| Jardin interactif | SVG React | Vue isométrique 2.5D, animations pousse plantes | Sprint 7 |
| Heatmap nutrition | CSS Grid custom | D3 heatmap avec transitions | Sprint 7 |
| Sankey budget | SVG custom | D3 Sankey avec animation flux | Sprint 7 |
| Treemap budget | Custom | Recharts Treemap avec zoom drill-down | Sprint 7 |
| Treemap inventaire | Custom | Recharts Treemap animé | Sprint 7 |
| Radar nutrition | Recharts | Overlay comparaison temporelle | Sprint 7 |
| Radar compétences Jules | Recharts | Animation progression, benchmark âge | Sprint 7 |
| Graphe réseau modules (admin) | D3 force | Ajouter filtres, détails on-hover | Sprint 7 |

---

## Annexe F — Simplification des flux utilisateur

### Principe : max 2-3 clics pour toute action courante

| Flux | Clics actuels | Cible | Comment simplifier | Sprint |
|------|---------------|-------|-------------------|--------|
| Voir le planning de la semaine | 2 | 1 | Widget dashboard dédié | Sprint 8 |
| Ajouter un article aux courses | 3-4 | 1-2 | FAB + commande vocale + suggestion auto | Sprint 8 |
| Cocher un article acheté | 2 | 1 | Swipe-to-check sur mobile | Sprint 8 |
| Voir les recettes du jour | 2 | 1 | Card sur le dashboard | Sprint 8 |
| Lancer le batch cooking | 3-4 | 2 | Bouton direct depuis le planning | Sprint 8 |
| Voir les tâches ménage du jour | 3 | 1 | Widget dashboard avec toggle | Sprint 8 |
| Déclarer une récolte jardin | 4+ | 2 | Bouton rapide sur la fiche plante | Sprint 8 |
| Consulter le budget restant | 2 | 0 | Badge permanent dans la sidebar | Sprint 8 |
| Ajouter une note rapide | 3 | 1 | FAB + input inline | Sprint 8 |
| Voir les documents expirant | 3 | 1 | Badge notification + widget dashboard | Sprint 8 |

### Mécanismes de simplification existants à enrichir

- **FAB (Floating Action Button)** : `fab-actions-rapides.tsx` — enrichir avec les 5 actions les plus fréquentes
- **Commandes vocales** : `utiliser-reconnaissance-vocale.ts` — connecter aux actions fréquentes
- **Suggestions proactives** : `bandeau-suggestion-proactive.tsx` — alimenter par IA contextuelle
- **Swipe gestures** : `swipeable-item.tsx` — appliquer sur listes courses/tâches

---

## Récapitulatif effort total

| Sprint | Durée estimée | Focus | Dépendances | Statut |
|--------|---------------|-------|-------------|--------|
| **Sprint 1** — Nettoyage | 5-7 jours | Dead code, legacy, commentaires, fichiers fourre-tout | Aucune | ✅ Terminé |
| **Sprint 2** — SQL | 3-5 jours | Base de données, indexes, RLS, seed | Sprint 1 | ✅ Implémenté (EXPLAIN ANALYZE prêt en `docs/EXPLAIN_ANALYZE_SPRINT2.md`) |
| **Sprint 3** — Tests | 5-7 jours | WebSocket, E2E, composants, charge | Sprint 1 |
| **Sprint 4** — Inter-modules & IA | 5-7 jours | Bridges manquants, nouvelles intégrations IA | Sprint 1 |
| **Sprint 5** — Automatisations | 3-5 jours | Telegram enrichi, jobs manquants, email | Sprint 4 |
| **Sprint 6** — Admin | 2-3 jours | Panel enrichi, triggers, logs temps réel | Sprint 5 |
| **Sprint 7** — UI/UX | 7-10 jours | Animations, palette, graphiques, 3D | Sprint 1 |
| **Sprint 8** — Flux & Innovation | 5-7 jours | Simplification UX, features innovantes | Sprint 7 |
| **Sprint 9** — Documentation | 2-3 jours | CHANGELOG, guides, Swagger | Tous les sprints |
| | | | |
| **Total estimé** | **~40-55 jours** | **En séquentiel. Parallélisable : S2/S3/S4/S7 après S1.** | |

### Graphe de dépendances

```
Sprint 1 (Nettoyage)
├── Sprint 2 (SQL)
├── Sprint 3 (Tests)
├── Sprint 4 (Inter-modules & IA)
│   └── Sprint 5 (Automatisations)
│       └── Sprint 6 (Admin)
└── Sprint 7 (UI/UX)
    └── Sprint 8 (Flux & Innovation)

Sprint 9 (Documentation) → après tous les sprints
```

**Sprints parallélisables après Sprint 1** : Sprint 2 + Sprint 3 + Sprint 4 + Sprint 7 peuvent être travaillés en parallèle.

---

> **Note finale** : L'application est évaluée à **7.9/10** (↑ +0.1 post-Sprint 2) — solide architecturalement (9/10 backend, 8.5/10 frontend, modèles données 8.5/10 améliorés). Les axes d'amélioration prioritaires sont le nettoyage legacy (Sprint 1 ✅), la sécurité DB (Sprint 2 ✅ SQL + RLS), les tests frontend (Sprint 3), et le polish UI (Sprint 7). Le flux utilisateur doit rester simple : maximum 2-3 clics pour toute action courante, avec Telegram comme hub mobile et le dashboard comme hub desktop.
