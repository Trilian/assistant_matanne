# 🔍 Analyse Complète — Assistant Matanne

> **Date**: 1er Avril 2026
> **Scope**: Backend (FastAPI/Python) + Frontend (Next.js 16) + SQL + Tests + Docs + Intégrations
> **Objectif**: Audit exhaustif, plan d'action, axes d'amélioration

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Inventaire des modules](#2-inventaire-des-modules)
3. [Bugs et problèmes détectés](#3-bugs-et-problèmes-détectés)
4. [Gaps et fonctionnalités manquantes](#4-gaps-et-fonctionnalités-manquantes)
5. [Consolidation SQL](#5-consolidation-sql)
6. [Interactions intra-modules](#6-interactions-intra-modules)
7. [Interactions inter-modules](#7-interactions-inter-modules)
8. [Opportunités IA](#8-opportunités-ia)
9. [Jobs automatiques (CRON)](#9-jobs-automatiques-cron)
10. [Notifications — WhatsApp, Email, Push](#10-notifications--whatsapp-email-push)
11. [Mode Admin manuel](#11-mode-admin-manuel)
12. [Couverture de tests](#12-couverture-de-tests)
13. [Documentation](#13-documentation)
14. [Organisation et architecture](#14-organisation-et-architecture)
15. [Améliorations UI/UX](#15-améliorations-uiux)
16. [Visualisations 2D et 3D](#16-visualisations-2d-et-3d)
17. [Simplification du flux utilisateur](#17-simplification-du-flux-utilisateur)
18. [Axes d'innovation](#18-axes-dinnovation)
19. [Plan d'action priorisé](#19-plan-daction-priorisé)

---

## 1. Vue d'ensemble du projet

### Chiffres clés

| Métrique | Valeur |
|----------|--------|
| Routes API (endpoints) | ~250+ |
| Routeurs FastAPI | 38 |
| Modèles SQLAlchemy (ORM) | 100+ (32 fichiers) |
| Schémas Pydantic | ~150+ (25 fichiers) |
| Tables SQL | 80+ |
| Pages frontend | ~60+ |
| Composants React | 208+ |
| Clients API frontend | 34 |
| Hooks React custom | 15 |
| Stores Zustand | 4 |
| Schémas Zod | 22 |
| Fichiers de tests (backend) | 74+ |
| Fichiers de tests (frontend) | 71 |
| CRON jobs | 68+ |
| Bridges inter-modules | 21 |
| Middlewares | 7 couches |
| WebSockets | 5 implémentations |
| Canaux de notification | 4 (push, ntfy, WhatsApp, email) |

### Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.13+, FastAPI 0.109, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 16.2.1, React 19, TypeScript 5, Tailwind CSS v4 |
| Base de données | Supabase PostgreSQL, migrations SQL-file |
| IA | Mistral AI (client custom + cache sémantique + circuit breaker) |
| État frontend | TanStack Query v5, Zustand 5 |
| Charts | Recharts 3.8, Chart.js 4.5 |
| 3D | Three.js 0.183, @react-three/fiber 9.5 |
| Cartes | Leaflet 1.9, react-leaflet 5.0 |
| Tests backend | pytest, SQLite in-memory |
| Tests frontend | Vitest 4.1, Testing Library, Playwright |
| Monitoring | Prometheus metrics, Sentry |
| Notifications | ntfy.sh, Web Push VAPID, Meta WhatsApp Cloud, Resend |

---

## 2. Inventaire des modules

### Backend — Modules par domaine

| Module | Routes | Services | Bridges | CRON | Tests | Statut |
|--------|--------|----------|---------|------|-------|--------|
| 🍽️ **Cuisine/Recettes** | 20 endpoints | RecetteService, ImportService | 7 | 5 | ✅ Complet | ✅ Mature |
| 🛒 **Courses** | 20 endpoints | CoursesService | 3 | 3 | ✅ Complet | ✅ Mature |
| 📦 **Inventaire** | 14 endpoints | InventaireService | 4 | 3 | ✅ Complet | ✅ Mature |
| 📅 **Planning** | 15 endpoints | PlanningService (5 sous-modules) | 5 | 4 | ✅ Complet | ✅ Mature |
| 🧑‍🍳 **Batch Cooking** | 8 endpoints | BatchCookingService | 1 | 1 | ✅ OK | ✅ Stable |
| ♻️ **Anti-Gaspillage** | 6 endpoints | AntiGaspillageService | 2 | 2 | ✅ OK | ✅ Stable |
| 💡 **Suggestions IA** | 4 endpoints | BaseAIService | 0 | 0 | ✅ OK | ✅ Stable |
| 👶 **Famille/Jules** | 20 endpoints | JulesAIService | 7 | 5 | ✅ Complet | ✅ Mature |
| 🏡 **Maison** | 15+ endpoints | MaisonService | 4 | 6 | ✅ OK | ✅ Stable |
| 🏠 **Habitat** | 10 endpoints | HabitatService | 0 | 2 | ⚠️ Partiel | 🟡 En cours |
| 🎮 **Jeux** | 12 endpoints | JeuxService | 1 | 3 | ✅ OK | ✅ Stable |
| 🗓️ **Calendriers** | 6 endpoints | CalendrierService | 2 | 2 | ⚠️ Partiel | 🟡 En cours |
| 📊 **Dashboard** | 3 endpoints | DashboardService | 0 | 0 | ✅ OK | ✅ Stable |
| 📄 **Documents** | 6 endpoints | DocumentService | 1 | 1 | ⚠️ Partiel | 🟡 En cours |
| 🔧 **Utilitaires** | 10+ endpoints | Notes, Journal, Contacts | 1 | 0 | ⚠️ Partiel | 🟡 En cours |
| 🤖 **IA Avancée** | 14 endpoints | Multi-service | 0 | 0 | ⚠️ Partiel | 🟡 En cours |
| ✈️ **Voyages** | 8 endpoints | VoyageService | 2 | 1 | ⚠️ Partiel | 🟡 En cours |
| ⌚ **Garmin** | 5 endpoints | GarminService | 1 | 1 | ⚠️ Minimal | 🟡 En cours |
| 🔐 **Auth / Admin** | 15+ endpoints | AuthService | 0 | 0 | ✅ OK | ✅ Stable |
| 📤 **Export PDF** | 3 endpoints | RapportService | 0 | 0 | ⚠️ Partiel | 🟡 En cours |
| 🔔 **Push / Webhooks** | 8 endpoints | NotificationService | 0 | 5 | ⚠️ Partiel | 🟡 En cours |
| 🤖 **Automations** | 6 endpoints | AutomationsEngine | 0 | 1 | ⚠️ Partiel | 🟡 En cours |

### Frontend — Pages par module

| Module | Pages | Composants spécifiques | Tests | Statut |
|--------|-------|------------------------|-------|--------|
| 🍽️ **Cuisine** | 12 pages (recettes, planning, courses, inventaire, batch, anti-gasp, frigo, nutrition) | ~20 | ✅ 8 fichiers | ✅ Mature |
| 👶 **Famille** | 10 pages (jules, activités, routines, budget, anniversaires, weekend, contacts, docs) | ~8 | ⚠️ 3 fichiers | 🟡 Gaps |
| 🏡 **Maison** | 8 pages (projets, charges, entretien, jardin, stocks, énergie, artisans, visualisation) | ~15 | ⚠️ 2 fichiers | 🟡 Gaps |
| 🏠 **Habitat** | 3 pages (hub, veille-immo, scénarios) | ~6 | ⚠️ 1 fichier | 🟡 Gaps |
| 🎮 **Jeux** | 7 pages (paris, loto, euromillions, performance, bankroll, OCR) | ~12 | ✅ 5 fichiers | ✅ OK |
| 📅 **Planning** | 2 pages (hub, timeline) | ~3 | ✅ 2 fichiers | ✅ OK |
| 🧰 **Outils** | 6 pages (chat-ia, notes, minuteur, météo, nutritionniste, assistant-vocal) | ~5 | ✅ 6 fichiers | ✅ OK |
| ⚙️ **Paramètres** | 3 pages + 7 onglets | ~7 | ⚠️ 1 fichier | 🟡 Gaps |
| 🔧 **Admin** | 10 pages (jobs, users, services, events, cache, IA, SQL, flags, WhatsApp, notif) | ~5 | ⚠️ 2 fichiers | 🟡 Gaps |

---

## 3. Bugs et problèmes détectés

### 🔴 Critiques

| # | Bug / Problème | Module | Impact | Fichier |
|---|----------------|--------|--------|---------|
| B1 | **API_SECRET_KEY random par process** — En multi-process (production), chaque worker génère un secret différent → les tokens d'un worker sont invalides sur un autre | Auth | Tokens invalides en production multi-worker | `src/api/auth.py` |
| B2 | **WebSocket courses sans fallback HTTP** — Si le WebSocket est indisponible (proxy restrictif, mobile 3G), pas de polling HTTP alternatif → la collaboration temps réel casse silencieusement | Courses | Perte de sync en temps réel | `utiliser-websocket-courses.ts` |
| B3 | **Promesse non gérée dans l'intercepteur auth** — Le refresh token peut timeout et laisser l'utilisateur bloqué (ni connecté ni déconnecté) | Frontend Auth | UX dégradée sur token expiré | `api/client.ts` |
| B4 | **Event bus en mémoire uniquement** — L'historique des événements est perdu au redémarrage du serveur, impossible de rejouer des événements après un crash | Core Events | Perte d'audit trail | `src/services/core/events/` |

### 🟡 Importants

| # | Bug / Problème | Module | Impact | Fichier |
|---|----------------|--------|--------|---------|
| B5 | **Rate limiting en mémoire non borné** — Le stockage en mémoire croît avec chaque IP/user unique sans éviction → fuite mémoire lente | Rate Limiting | Memory leak en production long | `rate_limiting/storage.py` |
| B6 | **Maintenance mode avec cache 5s** — La mise en maintenance peut prendre jusqu'à 5 secondes pour être effective → requêtes acceptées pendant la transition | Admin | Requêtes pendant maintenance | `src/api/main.py` |
| B7 | **X-Forwarded-For spoofable** — L'IP client est extraite du header sans vérifier la confiance du proxy → bypass possible du rate limiting | Sécurité | Rate limiting contournable | `rate_limiting/limiter.py` |
| B8 | **Metrics capped à 500 endpoints / 1000 samples** — Les percentiles (p95, p99) deviennent imprécis après beaucoup de requêtes | Monitoring | Métriques dégradées | `src/api/utils/metrics.py` |
| B9 | **Multi-turn WhatsApp sans persistence d'état** — La state machine de planning WhatsApp perd son état entre les messages → flux interrompu si l'utilisateur tarde | WhatsApp | Conversation WhatsApp cassée | `webhooks_whatsapp.py` |
| B10 | **CORS vide en production** — Si CORS_ORIGINS n'est pas configuré, toutes les origines sont bloquées mais aucune erreur explicite | Config | Frontend bloqué en prod sans config | `src/api/main.py` |

### 🟢 Mineurs

| # | Bug / Problème | Module | Impact |
|---|----------------|--------|--------|
| B11 | **ResponseValidationError** loggé en 500 sans contexte debug → difficile à diagnostiquer | API | DX dégradée |
| B12 | **Pagination cursor** — Les suppressions concurrentes peuvent sauter des enregistrements | Pagination | Données manquées rarement |
| B13 | **ServiceMeta auto-sync wrappers** — La génération automatique de wrappers sync pour les méthodes async n'est pas testée exhaustivement | Core Services | Bugs potentiels subtils |
| B14 | **Sentry intégration à 50%** — Configuré mais ne capture pas tous les erreurs frontend | Frontend | Erreurs non tracées |

---

## 4. Gaps et fonctionnalités manquantes

### Par module

#### 🍽️ Cuisine

| # | Gap | Priorité | Effort | Description |
|---|-----|----------|--------|-------------|
| G1 | **Drag-drop recettes dans planning** | Moyenne | 2j | Le planning repas n'a pas de drag-drop pour réorganiser les repas → UX fastidieuse |
| G2 | **Import recettes par photo** | Moyenne | 3j | L'import URL/PDF existe mais pas l'import par photo d'un livre de cuisine (Pixtral disponible côté IA) |
| G3 | **Partage recette via WhatsApp** | Basse | 1j | Le partage existe par lien mais pas d'envoi direct WhatsApp avec preview |
| G4 | **Veille prix articles désirés** | Moyenne | 3j | Scraper une API de suivi de prix (type Dealabs/Idealo) pour des articles ajoutés à une wishlist + alertes soldes automatiques via `calendrier_soldes.json` déjà présent. Pas de saisie manuelle de prix à chaque achat (trop fastidieux) |
| G5 | **Mode hors-ligne courses** | Haute | 3j | PWA installée mais pas de cache offline pour consulter la liste en magasin sans réseau |

#### 👶 Famille

| # | Gap | Priorité | Effort | Description |
|---|-----|----------|--------|-------------|
| G6 | **Prévision budget IA** | Haute | 3j | Le budget famille n'a que le résumé mensuel, pas de prédiction "fin de mois" avec IA |
| G7 | **Timeline Jules visuelle** | Moyenne | 2j | Les jalons de développement existent mais pas de frise chronologique visuelle interactive |
| G8 | **Export calendrier anniversaires** | Basse | 1j | Les anniversaires ne s'exportent pas vers Google Calendar |
| G9 | **Photos souvenirs liées aux activités** | Moyenne | 2j | Les activités familiales n'ont pas d'upload photo pour le journal |

#### 🏡 Maison

| # | Gap | Priorité | Effort | Description |
|---|-----|----------|--------|-------------|
| G10 | **Plan 3D interactif limité** | Haute | 5j | Le composant Three.js existe mais n'est pas connecté aux données réelles (tâches par pièce, consommation énergie) |
| G11 | **Historique énergie avec graphes** | Moyenne | 2j | Les relevés existent mais pas de visualisation tendancielle (courbes mois/année) |
| G12 | **Catalogue artisans enrichi** | Basse | 2j | Pas d'avis/notes sur les artisans, pas de recherche par métier |
| G13 | **Devis comparatif** | Moyenne | 3j | Pas de visualisation comparative des devis pour un même projet |

#### 🎮 Jeux

| # | Gap | Priorité | Effort | Description |
|---|-----|----------|--------|-------------|
| G14 | **Graphique ROI temporel** | Haute | 2j | Le ROI global existe mais pas la courbe d'évolution mensuelle du ROI paris sportifs |
| G15 | **Alertes cotes temps réel** | Moyenne | 3j | Pas d'alerte quand une cote atteint un seuil défini par l'utilisateur |
| G16 | **Comparaison stratégies loto** | Basse | 2j | Le backtest existe mais pas la comparaison côte à côte de 2+ stratégies |

#### 📅 Planning

| # | Gap | Priorité | Effort | Description |
|---|-----|----------|--------|-------------|
| G17 | **Sync Google Calendar bidirectionnelle** | Haute | 4j | L'export iCal existe, la sync Google est à ~60% → pas de push automatique des repas/activités vers Google Calendar |
| G18 | **Planning familial consolidé visuel** | Moyenne | 3j | Pas de vue Gantt complète mêlant repas + activités + entretien + anniversaires |
| G19 | **Récurrence d'événements** | Moyenne | 2j | Pas de gestion native "tous les mardis" pour les routines dans le calendrier |

#### 🧰 Général

| # | Gap | Priorité | Effort | Description |
|---|-----|----------|--------|-------------|
| G20 | **Recherche globale incomplète** | Haute | 3j | La recherche globale (Ctrl+K) ne couvre pas tous les modules (manque: notes, jardin, contrats) |
| G21 | **Mode hors-ligne (PWA)** | Haute | 5j | Service Worker enregistré mais pas de stratégie de cache offline structurée |
| G22 | **Onboarding interactif** | Moyenne | 3j | Le composant tour-onboarding existe mais n'est pas activé/configuré avec les étapes du parcours utilisateur |
| G23 | **Export données backup incomplet** | Moyenne | 2j | L'export JSON fonctionne mais l'import/restauration UI est incomplet |

---

## 5. Consolidation SQL

### État actuel

```
sql/
├── INIT_COMPLET.sql          # Auto-généré (4922 lignes, 18 fichiers schema)
├── schema/                   # 18 fichiers organisés (01_extensions → 99_footer)
│   ├── 01_extensions.sql
│   ├── 02_types_enums.sql
│   ├── 03_system_tables.sql
│   ├── 04_cuisine.sql
│   ├── 05_famille.sql
│   ├── 06_maison.sql
│   ├── 07_jeux.sql
│   ├── 08_habitat.sql
│   ├── 09_voyages.sql
│   ├── 10_notifications.sql
│   ├── 11_gamification.sql
│   ├── 12_automations.sql
│   ├── 13_utilitaires.sql
│   ├── 14_indexes.sql
│   ├── 15_rls_policies.sql
│   ├── 16_triggers.sql
│   ├── 17_views.sql
│   └── 99_footer.sql
└── migrations/               # 7 fichiers (V003-V008) + README
    ├── V003_*.sql
    ├── V004_*.sql
    ├── V005_phase2_sql_consolidation.sql
    ├── V006_*.sql
    ├── V007_*.sql
    └── V008_phase4.sql
```

### Actions recommandées (mode dev, pas de versioning)

| # | Action | Priorité | Détail |
|---|--------|----------|--------|
| S1 | **Regénérer INIT_COMPLET.sql** | Haute | Exécuter `python scripts/db/regenerate_init.py` pour s'assurer que le fichier monolithique est synchronisé avec les 18 fichiers schema |
| S2 | **Audit ORM ↔ SQL** | Haute | Exécuter `python scripts/audit_orm_sql.py` pour détecter les divergences entre les modèles SQLAlchemy et les tables SQL |
| S3 | **Consolider les migrations en un seul schema** | Haute | En mode dev, fusionner les 7 migrations dans les fichiers schema correspondants et régénérer INIT_COMPLET.sql. Une seule source de vérité |
| S4 | **Vérifier les index manquants** | Moyenne | Certaines colonnes fréquemment requêtées (user_id, date, statut) peuvent manquer d'index dans `14_indexes.sql` |
| S5 | **Nettoyer les tables inutilisées** | Basse | Vérifier si toutes les 80+ tables ont un modèle ORM et une route API correspondante |
| S6 | **Vues SQL non utilisées** | Basse | Vérifier que les vues dans `17_views.sql` sont réellement utilisées par le backend |

### Proposition de workflow simplifié

```
1. Modifier le fichier schema approprié (ex: sql/schema/04_cuisine.sql)
2. Exécuter: python scripts/db/regenerate_init.py
3. Appliquer: exécuter INIT_COMPLET.sql sur Supabase (SQL Editor)
4. Vérifier: python scripts/audit_orm_sql.py
```

> Pas de migrations ni de versioning en phase dev. Un seul INIT_COMPLET.sql fait foi.

---

## 6. Interactions intra-modules

### Cuisine (interne)

```
Recettes ──── planifiées ───→ Planning
    │                            │
    │                            ├── génère ──→ Courses
    │                            │
    └── version Jules ──→ portions adaptées
                                 │
Inventaire ◄────── checkout ────┘
    │
    ├── péremption ──→ Anti-Gaspillage ──→ Recettes rescue
    │
    └── stock bas ──→ Automation ──→ Courses auto
    
Batch Cooking ◄── planning semaine ── prépare ──→ bloque planning
```

**✅ Bien connecté** — Le module cuisine a le plus d'interactions internes, toutes fonctionnelles.

**🔧 À améliorer:**
- Le checkout courses → inventaire pourrait mettre à jour les prix moyens automatiquement
- Le batch cooking manque un "mode robot" intelligent qui optimise l'ordre des étapes par appareil

### Famille (interne)

```
Jules profil ──→ jalons developpement
    │               │
    │               └── notifications anniversaire jalon
    │
Budget ◄──── dépenses catégorisées
    │
Routines ──→ check quotidien ──→ gamification (limitée)
    │
Anniversaires ──→ checklist ──→ budget cadeau
    │
Documents ──→ expiration ──→ rappels calendrier
```

**🔧 À améliorer:**
- Jules jalons → suggestions d'activités adaptées à l'âge (IA contextuelle)
- Budget anomalies → pas de notification proactive ("tu dépenses +30% en restaurants ce mois")
- Routines → pas de tracking de complétion visuel (streak)

### Maison (interne)

```
Projets ──→ tâches ──→ devis ──→ dépenses
    │
Entretien ──→ calendrier ──→ produits nécessaires
    │
Jardin ──→ arrosage/récolte ──→ saison
    │
Énergie ──→ relevés compteurs ──→ historique
    │
Stocks (cellier) ──→ consolidé avec inventaire cuisine
```

**🔧 À améliorer:**
- Projets → pas de timeline visuelle Gantt des travaux
- Énergie → pas de graphe d'évolution ni de comparaison N vs N-1
- Entretien → pas de suggestions IA proactives ("votre chaudière a 8 ans, prévoir révision")

---

## 7. Interactions inter-modules

### Bridges existants (21 actifs) ✅

```
┌──────────┐     ┌───────────┐     ┌──────────┐
│ CUISINE  │◄───►│ PLANNING  │◄───►│ COURSES  │
│          │     │           │     │          │
│ recettes │     │ repas     │     │ listes   │
│ inventaire│    │ semaine   │     │ articles │
│ nutrition │    │ conflits  │     │          │
│ batch     │    │           │     │          │
└────┬─────┘     └─────┬─────┘     └────┬─────┘
     │                 │                 │
     │    ┌────────────┤                 │
     │    │            │                 │
┌────▼────▼──┐   ┌────▼─────┐     ┌────▼─────┐
│  FAMILLE   │   │  MAISON  │     │  BUDGET  │
│            │   │          │     │          │
│ jules      │   │ entretien│     │ famille  │
│ routines   │   │ jardin   │     │ jeux (séparé)
│ annivers.  │   │ énergie  │     │ maison   │
│ documents  │   │ projets  │     │          │
│ weekend    │   │ stocks   │     │          │
└────┬───────┘   └────┬─────┘     └──────────┘
     │                │
     │    ┌───────────┤
     │    │           │
┌────▼────▼──┐   ┌───▼──────┐
│ CALENDRIER │   │  JEUX    │
│            │   │          │
│ google cal │   │ paris    │
│ événements │   │ loto     │
│            │   │ bankroll │
└────────────┘   └──────────┘
```

### Bridges inter-modules détaillés

| # | Bridge | De → Vers | Fonctionnel | Description |
|---|--------|-----------|-------------|-------------|
| 1 | `inter_module_inventaire_planning` | Stock → Planning | ✅ | Priorise recettes par ingrédients disponibles |
| 2 | `inter_module_jules_nutrition` | Jules → Recettes | ✅ | Portions adaptées âge, filtrage allergènes |
| 3 | `inter_module_saison_menu` | Saison → Planning | ✅ | Produits frais de saison dans les suggestions |
| 4 | `inter_module_courses_budget` | Courses → Budget | ✅ | Suivi impact budget des courses |
| 5 | `inter_module_batch_inventaire` | Batch → Inventaire | ✅ | Mise à jour stock après batch cooking |
| 6 | `inter_module_planning_voyage` | Voyage → Planning | ✅ | Exclusion planning pendant les voyages |
| 7 | `inter_module_peremption_recettes` | Péremption → Recettes | ✅ | Recettes rescue des produits bientôt périmés |
| 8 | `inter_module_documents_calendrier` | Documents → Calendrier | ✅ | Rappels renouvellement docs expirés |
| 9 | `inter_module_meteo_activites` | Météo → Activités | ✅ | Suggestions activités selon météo |
| 10 | `inter_module_weekend_courses` | Weekend → Courses | ✅ | Liste courses pour activités weekend |
| 11 | `inter_module_voyages_budget` | Voyages → Budget | ✅ | Sync coûts voyage → budget |
| 12 | `inter_module_anniversaires_budget` | Anniversaires → Budget | ✅ | Tracking dépenses cadeaux/fêtes |
| 13 | `inter_module_budget_jeux` | Jeux ↔ Budget | ✅ (info) | Sync pour info uniquement (budgets séparés volontairement) |
| 14 | `inter_module_garmin_health` | Garmin → Dashboard | ✅ | Score bien-être intégrant fitness |
| 15 | `inter_module_entretien_courses` | Entretien → Courses | ✅ | Produits ménagers pour tâches à venir |
| 16 | `inter_module_jardin_entretien` | Jardin → Entretien | ✅ | Coordination jardinage/entretien |
| 17 | `inter_module_charges_energie` | Charges → Énergie | ✅ | Budget insights factures |
| 18 | `inter_module_energie_cuisine` | Énergie → Cuisine | ✅ | Optimisation cuisson heures creuses |
| 19 | `inter_module_chat_contexte` | Tous → Chat IA | ✅ | Contexte multi-module injecté dans le chat |
| 20 | `inter_module_voyages_calendrier` | Voyages → Calendrier | ✅ | Sync dates voyage dans calendrier |
| 21 | `inter_module_garmin_planning` | Garmin → Planning | ⚠️ | Partiellement connecté |

### Interactions manquantes à implémenter

| # | Interaction proposée | De → Vers | Valeur | Effort |
|---|---------------------|-----------|--------|--------|
| I1 | **Récolte jardin → Recettes semaine suivante** | Jardin → Planning | ✅ Acceptée | 2j |
| I2 | **Entretien récurrent → Planning unifié** | Entretien → Planning global | Haute | 2j |
| I3 | **Budget anomalie → Notification proactive** | Budget → Notifications | Haute | 2j |
| I4 | **Voyages → Inventaire** (déstockage avant départ) | Voyages → Inventaire | Moyenne | 1j |
| I5 | **Documents expirés → Dashboard alerte** | Documents → Dashboard | Haute | 1j |
| I6 | **Anniversaire proche → Suggestions cadeaux IA** | Anniversaires → IA | Moyenne | 2j |
| I7 | **Contrats/Garanties → Dashboard widgets** | Maison → Dashboard | Moyenne | 1j |
| I8 | **Météo → Entretien maison** (ex: gel → penser au jardin) | Météo → Maison | Moyenne | 2j |
| I9 | **Planning sport Garmin → Planning repas** (adapter alimentation) | Garmin → Cuisine | Moyenne | 3j |
| I10 | **Courses historique → Prédiction prochaine liste** | Courses → IA | Haute | 3j |

---

## 8. Opportunités IA

### IA actuellement en place ✅

| Fonctionnalité | Service | Module | Statut |
|----------------|---------|--------|--------|
| Suggestions recettes | BaseAIService | Cuisine | ✅ Fonctionnel |
| Génération planning IA | PlanningService | Planning | ✅ Fonctionnel |
| Recettes rescue anti-gaspi | AntiGaspillageService | Cuisine | ✅ Fonctionnel |
| Batch cooking optimisé | BatchCookingService | Cuisine | ✅ Fonctionnel |
| Suggestions weekend | WeekendAIService | Famille | ✅ Fonctionnel |
| Score bien-être | DashboardService | Dashboard | ✅ Fonctionnel |
| Chat IA contextualisé | AssistantService | Outils | ✅ Fonctionnel |
| Version Jules recettes | JulesAIService | Famille | ✅ Fonctionnel |
| 14 endpoints IA avancée | Multi-services | IA Avancée | ⚠️ Partiel |

### Nouvelles opportunités IA à exploiter

| # | Opportunité | Module(s) | Description | Priorité | Effort |
|---|-------------|-----------|-------------|----------|--------|
| IA1 | **Prédiction courses intelligente** | Courses + Historique | Analyser l'historique des courses (fréquence, quantités) pour pré-remplir la prochaine liste. "Tu achètes du lait tous les 5 jours, il est temps d'en commander" | 🔴 Haute | 3j |
| IA2 | **Planificateur adaptatif météo+stock+budget** | Planning + Météo + Inventaire + Budget | L'endpoint existe mais sous-utilisé. Exploiter : météo chaude → salades/grillades, stock important de tomates → les utiliser, budget serré → recettes avec ce qu'on a | 🔴 Haute | 2j |
| IA3 | **Diagnostic pannes maison** | Maison | Photo d'un appareil en panne → diagnostic IA (Pixtral) + suggestion d'action (appeler artisan X, pièce à commander) | 🟡 Moyenne | 3j |
| IA4 | **Assistant vocal contextuel** | Tous | Google Assistant connecté mais capacités limitées à quelques intents. Étendre: "Hey Google, qu'est-ce qu'on mange ce soir ?" → lecture du planning + suggestions si vide | 🟡 Moyenne | 4j |
| IA5 | **Résumé hebdomadaire intelligent** | Dashboard | Résumé IA de la semaine: repas cuisinés, tâches accomplies, budget, scores, prochaines échéances. Format narratif agréable à lire | 🔴 Haute | 2j |
| IA6 | **Optimisation énergie prédictive** | Maison/Énergie | Analyser les relevés compteurs + météo → prédire la facture du mois + suggérer des économies ciblées | 🟡 Moyenne | 3j |
| IA7 | **Analyse nutritionnelle photo** | Cuisine/Nutrition | Prendre en photo un plat → l'IA estime les calories/macros/micros (Pixtral) | 🟡 Moyenne | 3j |
| IA8 | **Suggestion d'organisation batch cooking** | Batch Cooking | Analyser le planning de la semaine + les appareils dispo (robot, four, etc.) → proposer un plan de batch cooking optimal avec timeline parallèle | 🔴 Haute | 3j |
| IA9 | **Jules: conseil développement proactif** | Famille/Jules | "À l'âge de Jules, les enfants commencent à..." — suggestions d'activités/jouets/apprentissages adaptés en fonction des jalons franchis vs attendus | 🟡 Moyenne | 2j |
| IA10 | **Auto-catégorisation budget** | Budget | Catégoriser automatiquement les dépenses à partir du nom du commerçant/article (pas d'OCR ticket, juste texte) | 🟡 Moyenne | 2j |
| IA11 | **Génération checklist voyage** | Voyages | À partir de la destination, dates, participants → checklist complète IA (vêtements, documents, réservations, vaccins si besoin) | 🟡 Moyenne | 2j |
| IA12 | **Score écologique repas** | Cuisine | Évaluer l'impact écologique du planning repas (saisonnalité, distance parcourue des aliments, protéines végétales vs animales) | 🟢 Basse | 2j |

---

## 9. Jobs automatiques (CRON)

### Jobs existants (68+)

#### Quotidiens

| Job | Horaire | Action | Canaux | Modules impliqués |
|-----|---------|--------|--------|-------------------|
| `digest_whatsapp_matinal` | 07h30 | Repas du jour, tâches, péremptions, boutons interactifs | WhatsApp | Cuisine, Maison, Inventaire |
| `rappels_famille` | 07h00 | Anniversaires, documents, jalons Jules | WhatsApp + Push + ntfy | Famille |
| `rappels_maison` | 08h00 | Garanties, contrats, entretien | Push + ntfy | Maison |
| `digest_ntfy` | 09h00 | Digest compact | ntfy | Multi-module |
| `rappel_courses` | 18h00 | Revue liste interactive | WhatsApp | Courses |
| `push_contextuel_soir` | 18h00 | Préparation lendemain | Push | Planning |
| `alerte_stock_bas` | 07h00 | Stock bas → ajout auto courses | Automation | Inventaire → Courses |
| `sync_google_calendar` | 23h00 | Push planning vers Google Cal | - | Planning → Calendrier |
| `garmin_sync_matinal` | 06h00 | Sync données Garmin | - | Garmin |
| `automations_runner` | Toutes les 5 min | Exécution règles automation | Variable | Automations |

#### Hebdomadaires

| Job | Jour/Horaire | Action | Canaux |
|-----|-------------|--------|--------|
| `resume_hebdo` | Lundi 07h30 | Résumé semaine passée | ntfy, email, WhatsApp |
| `score_weekend` | Vendredi 17h00 | Contexte weekend (météo, activités, suggestions) | WhatsApp |
| `score_bien_etre_hebdo` | Dimanche 20h00 | Score consolidé bien-être | Dashboard |
| `points_famille_hebdo` | Dimanche 20h00 | Points gamification | Dashboard |
| `sync_openfoodfacts` | Dimanche 03h00 | Rafraîchir cache produits | - |

#### Mensuels

| Job | Jour/Horaire | Action | Canaux |
|-----|-------------|--------|--------|
| `rapport_mensuel_budget` | 1er 08h15 | Résumé budget + tendances | Email |
| `controle_contrats_garanties` | 1er 09h00 | Alertes renouvellement | Push + ntfy |
| `rapport_maison_mensuel` | 1er 09h30 | Résumé entretien maison | Email |

### Nouveaux jobs proposés

| # | Job proposé | Fréquence | Modules | Description | Priorité |
|---|-------------|-----------|---------|-------------|----------|
| J1 | **`prediction_courses_hebdo`** | Vendredi 16h | Courses + IA | Pré-générer une liste de courses prédictive pour la semaine suivante basée sur l'historique | 🔴 Haute |
| J2 | **`planning_auto_semaine`** | Dimanche 19h | Planning + IA | Si le planning de la semaine suivante est vide, proposer un planning IA via WhatsApp (valider/modifier/rejeter) | 🔴 Haute |
| J3 | **`nettoyage_cache_export`** | Quotidien 02h | Export | Supprimer les fichiers d'export > 7 jours dans data/exports/ | 🟡 Moyenne |
| J4 | **`rappel_jardin_saison`** | Hebdo (Lundi) | Jardin | "C'est la saison pour planter les tomates" — rappels saisonniers intelligents | 🟡 Moyenne |
| J5 | **`sync_budget_consolidation`** | Quotidien 22h | Budget | Consolider les dépenses de tous les modules (courses, maison, jeux info, voyages) en un seul suivi | 🟡 Moyenne |
| J6 | **`verification_sante_systeme`** | Toutes les heures | Admin | Vérifier DB, cache, IA, et envoyer alerte ntfy si un service est down | 🟡 Moyenne |
| J7 | **`backup_auto_json`** | Hebdo (Dimanche 04h) | Admin | Export automatique de toutes les données en JSON (backup) | 🟢 Basse |
| J8 | **`tendances_nutrition_hebdo`** | Dimanche 18h | Cuisine/Nutrition | Analyser les repas de la semaine → score nutritionnel + recommandations | 🟡 Moyenne |
| J9 | **`alertes_budget_seuil`** | Quotidien 20h | Budget | Vérifier si une catégorie dépasse 80% du budget mensuel → alerte proactive | 🔴 Haute |
| J10 | **`rappel_activite_jules`** | Quotidien 09h | Famille | "Jules a 18 mois aujourd'hui ! Voici les activités recommandées pour son âge" | 🟡 Moyenne |

---

## 10. Notifications — WhatsApp, Email, Push

### Architecture actuelle

```
                    ┌─────────────────┐
                    │  Événement      │
                    │  (CRON / User)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Router de      │
                    │  notifications  │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼──────┐ ┌──────▼───────┐ ┌─────▼──────┐
    │  Web Push    │ │   ntfy.sh    │ │ WhatsApp   │
    │  (VAPID)     │ │  (open src)  │ │ (Meta API) │
    └──────────────┘ └──────────────┘ └────────────┘
                             │
                    ┌────────▼────────┐
                    │    Email        │
                    │   (Resend)      │
                    └─────────────────┘
    
    Failover: Push → ntfy → WhatsApp → Email
    Throttle: 2h par type d'événement par canal
```

### Améliorations WhatsApp proposées

| # | Amélioration | Priorité | Effort | Description |
|---|-------------|----------|--------|-------------|
| W1 | **Persistence état conversation** | 🔴 Haute | 2j | Le state machine planning perd l'état entre les messages. Stocker dans Redis/DB pour permettre des conversations multi-tour |
| W2 | **Commandes texte enrichies** | 🔴 Haute | 3j | Supporter: "ajoute du lait à la liste", "qu'est-ce qu'on mange demain", "combien j'ai dépensé ce mois" → parsing NLP via Mistral |
| W3 | **Boutons interactifs étendus** | 🟡 Moyenne | 2j | Ajouter des boutons quick-reply pour: valider courses, noter une dépense, signaler un problème maison |
| W4 | **Photo → action** | 🟡 Moyenne | 3j | Envoyer une photo de plante malade → diagnostic IA. Photo d'un plat → identification + ajout recette |
| W5 | **Résumé quotidien personnalisable** | 🟡 Moyenne | 2j | Permettre à l'utilisateur de choisir quelles infos recevoir dans le digest matinal (via paramètres) |

### Améliorations Email proposées

| # | Amélioration | Priorité | Effort | Description |
|---|-------------|----------|--------|-------------|
| E1 | **Templates HTML jolis** | 🟡 Moyenne | 2j | Les emails actuels sont basiques. Créer des templates HTML modernes (MJML) pour les rapports mensuels |
| E2 | **Résumé hebdo email** | 🟡 Moyenne | 1j | Pas d'email hebdomadaire automatique (seulement ntfy/WhatsApp). Ajouter un email digest optionnel |
| E3 | **Alertes critiques par email** | 🔴 Haute | 1j | Les alertes critiques (document expiré, stock critique, budget dépassé) devraient aussi aller par email en plus des autres canaux |

### Améliorations Push proposées

| # | Amélioration | Priorité | Effort | Description |
|---|-------------|----------|--------|-------------|
| P1 | **Actions dans la notification** | 🟡 Moyenne | 2j | "Ajouter au courses" directement depuis la notification push (web push actions) |
| P2 | **Push conditionnel (heure calme)** | 🟡 Moyenne | 1j | Respecter les heures calmes configurées dans les paramètres utilisateur |
| P3 | **Badge app PWA** | 🟢 Basse | 1j | Afficher le nombre de notifications non lues sur l'icône PWA |

---

## 11. Mode Admin manuel

### Existant ✅ (très complet)

L'application a déjà un **panneau admin robuste** accessible via:
- **Frontend**: `/admin/*` (10 pages dédiées)
- **Raccourci**: `Ctrl+Shift+A` (panneau flottant overlay)
- **Backend**: `POST /api/v1/admin/*` (20+ endpoints admin)

#### Fonctionnalités admin existantes

| Catégorie | Fonctionnalité | Status |
|-----------|---------------|--------|
| **Jobs CRON** | Lister tous les jobs + prochain run | ✅ |
| **Jobs CRON** | Déclencher manuellement n'importe quel job | ✅ |
| **Jobs CRON** | Voir l'historique d'exécution | ✅ |
| **Notifications** | Tester un canal spécifique (ntfy/push/email/WhatsApp) | ✅ |
| **Notifications** | Broadcast test sur tous les canaux | ✅ |
| **Event Bus** | Voir l'historique des événements | ✅ |
| **Event Bus** | Émettre un événement manuellement | ✅ |
| **Cache** | Voir les stats du cache | ✅ |
| **Cache** | Purger par pattern | ✅ |
| **Services** | État de tous les services (registre) | ✅ |
| **Feature Flags** | Activer/désactiver des features | ✅ |
| **Maintenance** | Mode maintenance ON/OFF | ✅ |
| **Simulation** | Dry-run workflows (péremption, digest, rappels) | ✅ |
| **IA Console** | Tester des prompts avec contrôle température/tokens | ✅ |
| **Impersonation** | Switcher d'utilisateur | ✅ |
| **Audit Logs** | Traçabilité complète | ✅ |
| **Security Logs** | Événements sécurité | ✅ |
| **SQL Views** | Browser de vues SQL | ✅ |
| **WhatsApp Test** | Envoyer un message WhatsApp test | ✅ |
| **Config** | Export/import configuration runtime | ✅ |

### Améliorations proposées

| # | Amélioration | Priorité | Effort | Description |
|---|-------------|----------|--------|-------------|
| A1 | **Console de commande rapide** | 🟡 Moyenne | 2j | Un champ texte dans le panneau admin pour lancer des commandes rapides: "run job rappels_famille", "clear cache recettes*", "test whatsapp" |
| A2 | **Dashboard admin temps réel** | 🟡 Moyenne | 3j | WebSocket admin_logs déjà en place — l'afficher en temps réel sur la page admin avec filtres et auto-scroll |
| A3 | **Scheduler visuel** | 🟡 Moyenne | 3j | Vue timeline des 68 CRON jobs avec le prochain run, la dernière exécution, et les dépendances visuelles |
| A4 | **Replay d'événements** | 🟡 Moyenne | 2j | Permettre de rejouer un événement passé du bus avec ses subscriber handlers |
| A5 | **Panneau admin invisible pour l'utilisateur** | ✅ Déjà fait | - | Le panneau est accessible uniquement via `role=admin` et `Ctrl+Shift+A`. Invisible pour l'utilisateur normal |
| A6 | **Logs en temps réel** | 🟡 Moyenne | 2j | Stream les logs du serveur via WebSocket admin_logs (l'endpoint existe, le connecter à l'UI) |
| A7 | **Test E2E one-click** | 🟢 Basse | 3j | Bouton "Lancer test complet" qui exécute un scénario E2E (créer recette → planifier → générer courses → checkout → vérifier inventaire) |

---

## 12. Couverture de tests

### Backend (Python/pytest)

| Zone | Fichiers test | Fonctions test | Couverture estimée | Note |
|------|-------------|----------------|---------------------|------|
| Routes API (cuisine) | 8 | ~120 | ✅ ~85% | Bien couvert |
| Routes API (famille) | 6 | ~80 | ✅ ~75% | OK |
| Routes API (maison) | 5 | ~60 | ⚠️ ~60% | Gaps sur jardin, énergie |
| Routes API (jeux) | 2 | ~30 | ⚠️ ~55% | Gaps sur loto, euromillions |
| Routes API (admin) | 2 | ~40 | ✅ ~70% | OK |
| Routes API (export/upload) | 2 | ~15 | ❌ ~30% | Très faible |
| Routes API (webhooks) | 2 | ~10 | ❌ ~25% | Très faible |
| Services | 20+ | ~300 | ⚠️ ~60% | Variable |
| Core (config, db, cache) | 6 | ~200 | ⚠️ ~55% | Cache orchestrateur faible |
| Event Bus | 1 | ~10 | ❌ ~20% | Très faible |
| Résilience | 1 | ~15 | ⚠️ ~40% | Manque scénarios réels |
| WebSocket | 1 | ~8 | ❌ ~25% | Edge cases manquants |
| Intégrations | 3 | ~20 | ❌ ~20% | Stubs mais pas end-to-end |
| **TOTAL** | **74+** | **~1000** | **⚠️ ~55%** | **50-60% estimé** |

### Frontend (Vitest)

| Zone | Fichiers test | Couverture estimée | Note |
|------|-------------|---------------------|------|
| Pages cuisine | 8 | ✅ ~70% | Bien couvert |
| Pages jeux | 5 | ✅ ~65% | OK |
| Pages outils | 6 | ✅ ~60% | OK |
| Pages famille | 3 | ⚠️ ~35% | Gaps importants |
| Pages maison | 2 | ⚠️ ~30% | Gaps importants |
| Pages admin | 2 | ⚠️ ~30% | Gaps importants |
| Pages paramètres | 1 | ❌ ~15% | Très faible |
| Hooks | 2 | ⚠️ ~45% | WebSocket sous-testé |
| Stores | 4 | ✅ ~80% | Bien couvert |
| Composants | 12 | ⚠️ ~40% | Variable |
| API clients | 1 | ❌ ~15% | Très faible |
| E2E (Playwright) | Quelques | ❌ ~10% | Quasi inexistant |
| **TOTAL** | **71** | **⚠️ ~40%** | **Min Vitest: 50%** |

### Tests manquants prioritaires

| # | Test à ajouter | Module | Priorité | Description |
|---|---------------|--------|----------|-------------|
| T1 | **Tests export PDF** | Export | 🔴 Haute | Vérifier génération PDF pour courses, planning, recettes, budget |
| T2 | **Tests webhooks WhatsApp** | Notifications | 🔴 Haute | Tester state machine planning, parsing commandes |
| T3 | **Tests event bus scenarios** | Core | 🔴 Haute | Pub/sub avec wildcards, priorités, erreurs handlers |
| T4 | **Tests cache L1/L2/L3** | Core | 🟡 Moyenne | Scénarios promotion/éviction entre niveaux |
| T5 | **Tests WebSocket edge cases** | Courses | 🟡 Moyenne | Reconnexion, timeout, messages malformés |
| T6 | **Tests E2E parcours utilisateur** | Frontend | 🔴 Haute | Scénario complet: login → créer recette → planifier → courses → checkout |
| T7 | **Tests API clients frontend** | Frontend | 🟡 Moyenne | Erreurs réseau, refresh token, pagination |
| T8 | **Tests pages paramètres** | Frontend | 🟡 Moyenne | Chaque onglet de paramètres |
| T9 | **Tests pages admin** | Frontend | 🟡 Moyenne | Jobs, services, cache, feature flags |
| T10 | **Tests Playwright accessibilité** | Frontend | 🟢 Basse | axe-core sur les pages principales |

---

## 13. Documentation

### État actuel

| Document | Dernière MàJ | Statut | Action nécessaire |
|----------|-------------|--------|-------------------|
| `docs/INDEX.md` | 1 Avril 2026 | ✅ Courant | - |
| `docs/MODULES.md` | 1 Avril 2026 | ✅ Courant | - |
| `docs/API_REFERENCE.md` | 1 Avril 2026 | ✅ Courant | - |
| `docs/API_SCHEMAS.md` | 1 Avril 2026 | ✅ Courant | - |
| `docs/SERVICES_REFERENCE.md` | 1 Avril 2026 | ✅ Courant | - |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | 31 Mars 2026 | ✅ Courant | - |
| `docs/ERD_SCHEMA.md` | 31 Mars 2026 | ✅ Courant | - |
| `docs/ARCHITECTURE.md` | 1 Mars 2026 | ⚠️ 1 mois | Rafraîchir avec les changements core récents |
| `docs/DATA_MODEL.md` | Inconnu | ⚠️ Vérifier | Peut être obsolète post-phases 8-10 |
| `docs/DEPLOYMENT.md` | Mars 2026 | ⚠️ Vérifier | Vérifier config Railway/Vercel actuelle |
| `docs/ADMIN_RUNBOOK.md` | Inconnu | ⚠️ Vérifier | Les 20+ endpoints admin ont-ils tous un doc ? |
| `docs/CRON_JOBS.md` | Inconnu | 🔴 Obsolète | 68+ jobs, probablement plus à jour depuis phases 8-10 |
| `docs/NOTIFICATIONS.md` | Inconnu | 🔴 Obsolète | Système refait en phase 8 |
| `docs/AUTOMATIONS.md` | Inconnu | 🔴 Obsolète | Expansion phases 8-10 |
| `docs/INTER_MODULES.md` | Inconnu | ⚠️ Vérifier | 21 bridges — tous documentés ? |
| `docs/EVENT_BUS.md` | Inconnu | ⚠️ Vérifier | Subscribers à jour ? |
| `docs/MONITORING.md` | Inconnu | ⚠️ Vérifier | Prometheus metrics actuelles ? |
| `docs/SECURITY.md` | Inconnu | ⚠️ Vérifier | Rate limiting, 2FA, CORS docs à jour ? |
| `PLANNING_IMPLEMENTATION.md` | Inconnu | 🔴 Obsolète | Liste seulement sprints 1-9, projet à Phase 10+ |
| `ROADMAP.md` | Inconnu | 🔴 Obsolète | Priorités peut-être obsolètes |

### Documentation manquante

| # | Document à créer | Priorité | Description |
|---|-----------------|----------|-------------|
| D1 | **Guide complet des CRON jobs** | 🔴 Haute | Lister les 68+ jobs, horaires, dépendances, comment ajouter un nouveau job |
| D2 | **Guide des notifications** (refonte) | 🔴 Haute | 4 canaux, failover, throttle, templates WhatsApp, configuration |
| D3 | **Guide admin** (mise à jour) | 🟡 Moyenne | Les 20+ endpoints admin, panneau flottant, simulations, feature flags |
| D4 | **Guide des bridges inter-modules** | 🟡 Moyenne | Les 21 bridges, comment en créer un nouveau, naming convention |
| D5 | **Guide de test** (unifié) | 🟡 Moyenne | Backend pytest + Frontend Vitest + E2E Playwright, fixtures, mocks communs |
| D6 | **Changelog module par module** | 🟢 Basse | Historique des changements par module pour le suivi |

---

## 14. Organisation et architecture

### Points forts ✅

- **Architecture modulaire** : Séparation claire routes/schemas/services/models
- **Service Registry** : Pattern singleton thread-safe avec `@service_factory`
- **Event Bus** : Pub/sub découplé avec wildcards et priorités
- **Cache multi-niveaux** : L1 (mémoire) → L2 (session) → L3 (fichier) + Redis optionnel
- **Résilience** : Retry + Timeout + Circuit Breaker composables
- **Sécurité** : JWT + 2FA TOTP + rate limiting + security headers + sanitization
- **Frontend** : App Router Next.js 16 bien structuré, composants shadcn/ui consistants

### Points à améliorer 🔧

| # | Problème | Fichier(s) | Action |
|---|----------|-----------|--------|
| O1 | **jobs.py monolithique (3500+ lignes)** | `src/services/core/cron/jobs.py` | Découper en fichiers par domaine: `jobs_cuisine.py`, `jobs_famille.py`, `jobs_maison.py`, etc. |
| O2 | **Routes famille éclatées** | `src/api/routes/famille*.py` (multiples) | Consolider ou documenter le naming pattern des sous-routes famille |
| O3 | **Scripts legacy non archivés** | `scripts/` (split_init_sql, split_jeux, rename_factory) | Déplacer dans `scripts/_archive/` ou supprimer |
| O4 | **Doubles bibliothèques de charts** | `chart.js` + `recharts` | Standardiser sur Recharts (déjà plus utilisé) et retirer chart.js |
| O5 | **RGPD route non pertinente** | `src/api/routes/rgpd.py` | App familiale privée — simplifier en "Export backup" uniquement (préférence utilisateur) |
| O6 | **Références croisées types** | `frontend/src/types/` | Certains types sont dupliqués entre fichiers — centraliser via barrel exports |
| O7 | **Données référence non versionnées** | `data/reference/*.json` | Ajouter un numéro de version dans chaque fichier JSON |
| O8 | **Dossier exports non nettoyé** | `data/exports/` | Pas de politique de rétention automatique |

---

## 15. Améliorations UI/UX

### Dashboard principal

| # | Amélioration | Priorité | Description |
|---|-------------|----------|-------------|
| U1 | **Widgets configurables drag-drop** | 🔴 Haute | Le composant `grille-widgets.tsx` existe mais pas de drag-drop pour réorganiser. Implémenter avec `@dnd-kit/core` |
| U2 | **Cartes avec micro-animations** | 🟡 Moyenne | Ajouter des animations subtiles sur les cartes dashboard (compteurs qui s'incrémentent, barres de progression animées) avec Framer Motion |
| U3 | **Mode sombre raffiné** | 🟡 Moyenne | Le dark mode fonctionne mais certains composants (charts, calendrier) n'ont pas de palette dédiée |
| U4 | **Squelettes de chargement cohérents** | 🟡 Moyenne | Les skeleton loaders existent mais ne reflètent pas fidèlement la forme du contenu final |

### Navigation

| # | Amélioration | Priorité | Description |
|---|-------------|----------|-------------|
| U5 | **Sidebar avec favoris dynamiques** | 🟡 Moyenne | Le composant `favoris-rapides.tsx` existe — interconnecter avec le store pour pins persistants |
| U6 | **Breadcrumbs interactifs** | 🟢 Basse | Les breadcrumbs sont là mais pas cliquables sur tous les niveaux de navigation |
| U7 | **Transitions de page fluides** | 🟡 Moyenne | Pas de transitions entre pages — ajouter un fade-in/slide avec `framer-motion` ou les View Transitions API |
| U8 | **Bottom bar mobile enrichie** | 🟡 Moyenne | 5 items fixes — ajouter un indicateur visuel de la page active + animation |

### Formulaires

| # | Amélioration | Priorité | Description |
|---|-------------|----------|-------------|
| U9 | **Auto-complétion intelligente** | 🔴 Haute | Les formulaires d'ajout (recettes, inventaire, courses) devraient proposer auto-complétion basée sur l'historique |
| U10 | **Validation inline en temps réel** | 🟡 Moyenne | Les erreurs Zod s'affichent au submit — ajouter validation pendant la saisie (onBlur) |
| U11 | **Assistant formulaire IA** | 🟡 Moyenne | "Aide-moi à remplir" — L'IA pré-remplit les champs basé sur le contexte (ex: recette → pré-remplit les ingrédients courants) |

### Mobile

| # | Amélioration | Priorité | Description |
|---|-------------|----------|-------------|
| U12 | **Swipe actions** | 🟡 Moyenne | Le composant `swipeable-item.tsx` existe — l'appliquer à toutes les listes (courses, tâches, recettes) pour supprimer/archiver |
| U13 | **Pull-to-refresh** | 🟡 Moyenne | Pattern mobile natif absent — TanStack Query le supporte |
| U14 | **Haptic feedback** | 🟢 Basse | Vibrations sur les actions importantes (checkout, suppression, validation) via Vibration API |

### Micro-interactions

| # | Amélioration | Priorité | Description |
|---|-------------|----------|-------------|
| U15 | **Confetti sur accomplissement** | 🟢 Basse | Animation confetti quand un planning complet est validé, quand toutes les courses sont cochées, etc. |
| U16 | **Compteurs animés dashboard** | 🟡 Moyenne | Les chiffres du dashboard s'incrémentent de 0 à la valeur réelle à l'affichage |
| U17 | **Toast notifications améliorées** | 🟡 Moyenne | Utiliser Sonner avec des styles custom: succès vert + check animé, erreur rouge + shake |

---

## 16. Visualisations 2D et 3D

### Existant

| Composant | Technologie | Module | Statut |
|-----------|-------------|--------|--------|
| Plan 3D maison | Three.js / @react-three/fiber | Maison | ⚠️ Squelette (non connecté aux données) |
| Heatmap numéros loto | Recharts | Jeux | ✅ Fonctionnel |
| Heatmap cotes paris | Recharts | Jeux | ✅ Fonctionnel |
| Camembert budget | Recharts | Famille | ✅ Fonctionnel |
| Graphique ROI | Recharts | Jeux | ✅ Fonctionnel |
| Graphique jalons Jules | Recharts | Famille | ✅ Fonctionnel |
| Timeline planning | Custom CSS | Planning | ⚠️ Basique |
| Carte Leaflet (habitat) | react-leaflet | Habitat | ⚠️ Partiel |

### Améliorations visualisation proposées

#### 3D

| # | Visualisation | Module | Technologie | Description |
|---|---------------|--------|-------------|-------------|
| V1 | **Plan 3D maison interactif** | Maison | Three.js + @react-three/drei | Connecter le plan 3D aux données réelles: couleur des pièces par nombre de tâches en attente, indicateurs énergie par pièce, clic → détail des tâches de la pièce |
| V2 | **Vue jardin 3D/2D** | Maison/Jardin | Three.js ou Canvas 2D | Plan du jardin avec les zones de plantation, état des plantes (couleur), calendrier d'arrosage visuel |
| V3 | **Globe 3D voyages** | Voyages | Three.js (globe.gl) | Vue globe avec les destinations passées et à venir, tracé des itinéraires |

#### 2D — Graphiques avancés

| # | Visualisation | Module | Technologie | Description |
|---|---------------|--------|-------------|-------------|
| V4 | **Calendrier nutritionnel heatmap** | Cuisine | D3.js ou Recharts | Grille type GitHub contributions: chaque jour coloré selon le score nutritionnel (rouge → vert) |
| V5 | **Treemap budget** | Famille/Budget | Recharts Treemap | Visualisation proportionnelle des catégories de dépenses, cliquable pour drill-down |
| V6 | **Sunburst recettes** | Cuisine | D3.js Sunburst | Catégories → sous-catégories → recettes, proportionnel au nombre de fois cuisinées |
| V7 | **Radar skill Jules** | Famille/Jules | Recharts RadarChart | Diagramme araignée des compétences de Jules (motricité, langage, social, cognitif) vs normes OMS |
| V8 | **Sparklines dans les cartes** | Dashboard | Inline SVG / Recharts | Mini graphiques dans les cartes dashboard (tendance 7 jours) pour chaque métrique |
| V9 | **Graphe réseau modules** | Admin | D3.js Force Graph ou vis.js | Visualisation interactive des 21 bridges inter-modules: noeuds = modules, liens = bridges, épaisseur = fréquence d'utilisation |
| V10 | **Timeline Gantt entretien** | Maison | Recharts ou dhtmlxGantt | Planification visuelle des tâches d'entretien sur l'année |
| V11 | **Courbe énergie N vs N-1** | Maison/Énergie | Recharts AreaChart | Comparaison consommation énergie mois par mois vs année précédente |
| V12 | **Flux Sankey courses → catégories** | Courses/Budget | D3.js Sankey | Visualiser le flux de dépenses: fournisseurs → catégories → sous-catégories |
| V13 | **Wheel fortune loto** | Jeux | Canvas / CSS animation | Animation roue pour la révélation des numéros générés par l'IA |

---

## 17. Simplification du flux utilisateur

### Principes de design

> L'utilisateur doit pouvoir accomplir ses tâches quotidiennes en **3 clics maximum**.
> Les actions fréquentes sont en **premier plan**, les actions rares en **menus secondaires**.
> L'IA fait le travail lourd en **arrière-plan**, l'utilisateur **valide**.

### Flux principaux simplifiés

#### 🍽️ Flux cuisine (central)

```
Semaine vide
    │
    ├──→ IA propose un planning ──→ Valider / Modifier / Régénérer
    │                                    │
    │                                    ▼
    │                            Planning validé
    │                                    │
    │                              ┌─────┴─────┐
    │                              │            │
    │                    Auto-génère         Notif WhatsApp
    │                    courses               recap
    │                        │
    │                        ▼
    │                  Liste courses
    │                  (triée par rayon)
    │                        │
    │                        ▼
    │              En magasin: cocher au fur et à mesure
    │                        │
    │                        ▼
    │              Checkout → transfert automatique inventaire
    │                        │
    │                        ▼
    │              Score anti-gaspi mis à jour
    │
    └──→  Fin de semaine: "Qu'avez-vous vraiment mangé ?" → feedback IA
```

**Actions utilisateur**: 3 (valider planning → cocher courses → checkout)
**Actions IA**: Planning, liste courses, organisation rayons, transfert inventaire

#### 👶 Flux famille quotidien

```
Matin (auto WhatsApp 07h30)
    │
    ├── "Bonjour ! Aujourd'hui: repas X, tâche Y, Jules a Z mois"
    │   └── Bouton: "OK" ou "Modifier"
    │
    ├── Routines Jules (checklist)
    │   └── Cocher les étapes faites
    │
    └── Soir: récap auto
        └── "Aujourd'hui: 3/5 tâches, 2 repas ok, Jules: poids noté"
```

**Actions utilisateur**: Cocher les routines, répondre OK/Modifier
**Actions IA**: Digest, rappels, scores

#### 🏡 Flux maison

```
Notification push (automatique)
    │
    ├── "Tâche entretien à faire: [tâche] — Voir détail"
    │   └── Clic → fiche tâche avec guide
    │       └── Marquer "fait" → auto-prochaine date
    │
    ├── "Stock produit [X] bas"
    │   └── Bouton: "Ajouter aux courses"
    │
    └── Rapport mensuel (1er du mois)
        └── Email avec résumé tâches + budget maison
```

**Actions utilisateur**: Marquer fait, ajouter aux courses
**Actions IA**: Rappels, planification, rapport

### Actions rapides (FAB mobile)

Le composant `fab-actions-rapides.tsx` existe — le configurer avec:

| Action rapide | Cible | Icône |
|--------------|-------|-------|
| + Recette rapide | Formulaire simplifié (nom + photo) | 📸 |
| + Article courses | Ajout vocal ou texte | 🛒 |
| + Dépense | Montant + catégorie | 💰 |
| + Note | Texte libre | 📝 |
| Scan barcode | Scanner → inventaire ou courses | 📷 |
| Timer cuisine | Minuteur rapide | ⏱️ |

---

## 18. Axes d'innovation

### Innovations proposées (au-delà du scope actuel)

| # | Innovation | Modules | Description | Effort | Impact |
|---|-----------|---------|-------------|--------|--------|
| IN1 | **Mode "Pilote automatique"** | Tous | L'IA gère le planning, les courses, les rappels sans intervention. L'utilisateur reçoit un résumé quotidien et intervient uniquement pour corriger. Bouton ON/OFF dans les paramètres | 5j | 🔴 Très élevé |
| IN2 | **Widget tablette Google (écran d'accueil)** | Dashboard | Widget Android/web widget affichant: repas du jour, prochaine tâche, météo, timer actif. Compatible avec la tablette Google | 4j | 🔴 Élevé |
| IN3 | **Vue "Ma journée" unifiée** | Planning + Cuisine + Famille + Maison | Une seule page "Aujourd'hui" avec tout: repas, tâches, routines Jules, météo, anniversaires, timer. Le concentré de la journée | 3j | 🔴 Très élevé |
| IN4 | **Suggestions proactives contextuelles** | IA + Tous | Bannière en haut de chaque module avec une suggestion IA contextuelle: "Il reste des tomates qui expirent demain → [Voir recettes]", "Budget restaurants atteint 80% → [Voir détail]" | 3j | 🔴 Élevé |
| IN5 | **Journal familial automatique** | Famille | L'app génère automatiquement un journal de la semaine: repas cuisinés, activités faites, jalons Jules, photos uploadées, météo, dépenses. Exportable en PDF joli | 3j | 🟡 Moyen |
| IN6 | **Mode focus/zen** | UI | Le composant `focus/` existe en squelette. Implémenter un mode "concentration" qui masque tout sauf la tâche en cours (recette en cuisine, liste de courses en magasin) | 2j | 🟡 Moyen |
| IN7 | **Comparateur de prix courses** | Courses + IA | À partir de la liste de courses, l'IA compare avec les prix référence (sans OCR tickets) et donne un budget estimé | 3j | 🟡 Moyen |
| IN8 | **Intégration Google Home routines** | Assistant | Routines Google Home: "Bonsoir" → lecture du repas du lendemain + tâches demain. Étendre les intents Google Assistant existants | 4j | 🟡 Moyen |
| IN9 | **Seasonal meal prep planner** | Cuisine + IA | Chaque saison, l'IA propose un plan de batch cooking saisonnier avec les produits de saison et les congélations recommandées | 2j | 🟡 Moyen |
| IN10 | **Score famille hebdomadaire** | Dashboard | Score composite: nutrition + dépenses maîtrisées + activités + entretien à jour + bien-être. Graphe d'évolution semaine par semaine | 2j | 🔴 Élevé |
| IN11 | **Export rapport mensuel PDF** | Export + IA | Un beau rapport PDF mensuel avec graphiques: budget, nutrition, entretien, Jules, jeux. Résumé narratif IA | 3j | 🟡 Moyen |
| IN12 | **Planning vocal** | Assistant + Planning | "Ok Google, planifie du poulet pour mardi soir" → créé le repas + vérifie le stock + ajoute les manquants aux courses | 3j | 🟡 Moyen |
| IN13 | **Tableau de bord énergie** | Maison | Dashboard dédié énergie: consommation temps réel (si compteur Linky connecté), historique, comparaison N-1, prévision facture, tips IA | 4j | 🟡 Moyen |
| IN14 | **Mode "invité" pour le conjoint** | Auth | Vue simplifiée pour un 2ème utilisateur: juste les courses, le planning, les routines. Sans admin ni config | 2j | 🔴 Élevé |

---

## 19. Plan d'action priorisé

### 🔴 Phase A — Stabilisation (Semaine 1-2)

> **Objectif**: Corriger les bugs, consolider SQL, couvrir les tests critiques

| # | Tâche | Effort | Catégorie |
|---|-------|--------|-----------|
| A1 | Fixer B1 (API_SECRET_KEY multi-process) | 1h | Bug critique |
| A2 | Fixer B2 (WebSocket fallback HTTP polling) | 1j | Bug critique |
| A3 | Fixer B3 (Intercepteur auth promise non gérée) | 2h | Bug critique |
| A4 | Fixer B5 (Rate limiting mémoire non borné — ajouter LRU) | 2h | Bug important |
| A5 | Fixer B9 (WhatsApp state persistence — Redis/DB) | 1j | Bug important |
| A6 | Exécuter audit_orm_sql.py et corriger divergences (S2) | 1j | SQL |
| A7 | Consolider migrations dans les fichiers schema (S3) | 1j | SQL |
| A8 | Régénérer INIT_COMPLET.sql propre (S1) | 30min | SQL |
| A9 | Ajouter tests export PDF (T1) | 1j | Tests |
| A10 | Ajouter tests webhooks WhatsApp (T2) | 1j | Tests |
| A11 | Ajouter tests event bus scénarios (T3) | 1j | Tests |
| A12 | Mettre à jour CRON_JOBS.md (D1) | 2h | Doc |
| A13 | Mettre à jour NOTIFICATIONS.md (D2) | 2h | Doc |

### 🟡 Phase B — Fonctionnalités & IA (Semaine 3-4)

> **Objectif**: Combler les gaps fonctionnels, enrichir l'IA

| # | Tâche | Effort | Catégorie |
|---|-------|--------|-----------|
| B1 | Implémenter G5 (Mode offline courses) | 3j | Gap |
| B2 | Implémenter IA1 (Prédiction courses intelligente) | 3j | IA |
| B3 | Implémenter J2 (Planning auto semaine CRON) | 2j | CRON |
| B4 | Implémenter J9 (Alertes budget seuil CRON) | 1j | CRON |
| B5 | Implémenter W2 (Commandes WhatsApp enrichies) | 3j | WhatsApp |
| B6 | Implémenter I1 (Récolte jardin → Recettes) | 2j | Inter-module |
| B7 | Implémenter I3 (Budget anomalie → notification) | 2j | Inter-module |
| B8 | Implémenter I5 (Documents expirés → Dashboard) | 1j | Inter-module |
| B9 | Implémenter IA5 (Résumé hebdo intelligent) | 2j | IA |
| B10 | Implémenter IA8 (Suggestion batch cooking intelligent) | 3j | IA |
| B11 | Ajouter tests pages famille frontend (T8 étendu) | 2j | Tests |
| B12 | Ajouter tests E2E parcours utilisateur (T6) | 3j | Tests |

### 🟢 Phase C — UI/UX & Visualisations (Semaine 5-6)

> **Objectif**: Rendre l'interface belle, moderne, fluide

| # | Tâche | Effort | Catégorie |
|---|-------|--------|-----------|
| C1 | Implémenter U1 (Dashboard widgets drag-drop) | 2j | UI |
| C2 | Implémenter IN3 (Page "Ma journée" unifiée) | 3j | Innovation |
| C3 | Implémenter V1 (Plan 3D maison interactif connecté) | 5j | 3D |
| C4 | Implémenter V4 (Calendrier nutritionnel heatmap) | 2j | 2D |
| C5 | Implémenter V5 (Treemap budget) | 2j | 2D |
| C6 | Implémenter V7 (Radar skill Jules) | 1j | 2D |
| C7 | Implémenter V8 (Sparklines dans cartes dashboard) | 1j | 2D |
| C8 | Implémenter U7 (Transitions de page fluides) | 2j | UI |
| C9 | Implémenter U12 (Swipe actions listes) | 1j | Mobile |
| C10 | Implémenter U16 (Compteurs animés dashboard) | 1j | UI |
| C11 | Implémenter U9 (Auto-complétion intelligent formulaires) | 2j | UX |
| C12 | Implémenter IN4 (Suggestions proactives contextuelles) | 3j | Innovation |

### 🔵 Phase D — Admin & Automatisations (Semaine 7-8)

> **Objectif**: Enrichir le mode admin, nouvelles automatisations

| # | Tâche | Effort | Catégorie |
|---|-------|--------|-----------|
| D1 | Implémenter A1 (Console commande rapide admin) | 2j | Admin |
| D2 | Implémenter A3 (Scheduler visuel CRON) | 3j | Admin |
| D3 | Implémenter A6 (Logs temps réel via WebSocket) | 2j | Admin |
| D4 | Implémenter J1 (CRON prédiction courses hebdo) | 1j | CRON |
| D5 | Implémenter J4 (Rappels jardin saisonniers) | 1j | CRON |
| D6 | Implémenter J6 (Vérif santé système horaire) | 1j | CRON |
| D7 | Implémenter J7 (Backup auto hebdomadaire JSON) | 1j | CRON |
| D8 | Implémenter W1 (WhatsApp state persistence) | 2j | Notifications |
| D9 | Implémenter E1 (Templates email HTML/MJML) | 2j | Notifications |
| D10 | Découper jobs.py en modules (O1) | 1j | Refactoring |
| D11 | Archiver scripts legacy (O3) | 30min | Nettoyage |
| D12 | Standardiser sur Recharts uniquement (O4) | 1j | Nettoyage |

### 🟣 Phase E — Innovations (Semaine 9+)

> **Objectif**: Features différenciantes

| # | Tâche | Effort | Catégorie |
|---|-------|--------|-----------|
| E1 | Implémenter IN1 (Mode Pilote automatique) | 5j | Innovation |
| E2 | Implémenter IN2 (Widget tablette Google) | 4j | Innovation |
| E3 | Implémenter IN10 (Score famille hebdomadaire) | 2j | Innovation |
| E4 | Implémenter IN14 (Mode invité conjoint) | 2j | Innovation |
| E5 | Implémenter V9 (Graphe réseau modules admin) | 2j | Visualisation |
| E6 | Implémenter V10 (Timeline Gantt entretien) | 2j | Visualisation |
| E7 | Implémenter V2 (Vue jardin 2D/3D) | 3j | Visualisation |
| E8 | Implémenter IN5 (Journal familial automatique) | 3j | Innovation |
| E9 | Implémenter IN11 (Rapport mensuel PDF export) | 3j | Innovation |
| E10 | Implémenter IN8 (Google Home routines étendues) | 4j | Innovation |
| E11 | Implémenter G17 (Sync Google Calendar bidirectionnelle) | 4j | Gap |
| E12 | Implémenter IA4 (Assistant vocal étendu) | 4j | IA |

---

## Annexe A — Résumé des fichiers clés

### Backend Python

```
src/
├── api/
│   ├── main.py                    # FastAPI app + 7 middlewares + health
│   ├── auth.py                    # JWT + 2FA TOTP
│   ├── dependencies.py            # require_auth, require_role
│   ├── routes/                    # 41 fichiers routeurs (~250 endpoints)
│   ├── schemas/                   # 25 fichiers Pydantic (~150 modèles)
│   ├── utils/                     # Exception handler, pagination, metrics, ETag, security
│   ├── rate_limiting/             # Multi-strategy (memory/Redis/file)
│   ├── websocket_courses.py       # WS collaboration courses
│   └── websocket/                 # 4 autres WebSockets
├── core/
│   ├── ai/                        # Mistral client, cache sémantique, circuit breaker
│   ├── caching/                   # L1/L2/L3 + Redis
│   ├── config/                    # Pydantic BaseSettings
│   ├── db/                        # Engine, sessions, migrations
│   ├── decorators/                # @avec_session_db, @avec_cache, @avec_resilience
│   ├── models/                    # 32 fichiers ORM (100+ classes)
│   ├── resilience/                # Retry + Timeout + CircuitBreaker
│   └── validation/                # Pydantic schemas + sanitizer
└── services/
    ├── core/
    │   ├── base/                  # BaseAIService (4 mixins)
    │   ├── cron/                  # 68+ jobs (3500+ lignes)
    │   ├── events/                # Pub/Sub event bus
    │   └── registry.py            # @service_factory singleton
    ├── cuisine/                   # RecetteService, ImportService
    ├── famille/                   # JulesAI, WeekendAI
    ├── maison/                    # MaisonService
    ├── jeux/                      # JeuxService
    ├── planning/                  # 5 sous-modules
    ├── inventaire/                # InventaireService
    ├── dashboard/                 # Agrégation multi-module
    ├── integrations/              # Multimodal, webhooks
    └── utilitaires/               # Automations, divers
```

### Frontend Next.js

```
frontend/src/
├── app/
│   ├── (auth)/                    # Login / Inscription
│   ├── (app)/                     # App protégée (~60 pages)
│   │   ├── page.tsx               # Dashboard
│   │   ├── cuisine/               # 12 pages
│   │   ├── famille/               # 10 pages
│   │   ├── maison/                # 8 pages
│   │   ├── jeux/                  # 7 pages
│   │   ├── planning/              # 2 pages
│   │   ├── outils/                # 6 pages
│   │   ├── parametres/            # 3 pages + 7 onglets
│   │   ├── admin/                 # 10 pages
│   │   ├── habitat/               # 3 pages
│   │   └── ia-avancee/            # IA avancée
│   └── share/                     # Partage public
├── composants/
│   ├── ui/                        # 29 shadcn/ui
│   ├── disposition/               # 19 layout components
│   ├── cuisine/                   # Composants cuisine
│   ├── famille/                   # Composants famille
│   ├── jeux/                      # Composants jeux (heatmaps, grilles)
│   ├── maison/                    # Composants maison (plan 3D, drawers)
│   ├── habitat/                   # Composants habitat
│   ├── graphiques/                # Charts réutilisables
│   └── planning/                  # Timeline, calendrier
├── bibliotheque/
│   ├── api/                       # 34 clients API
│   └── validateurs.ts             # 22 schémas Zod
├── crochets/                      # 15 hooks custom
├── magasins/                      # 4 stores Zustand
├── types/                         # 15 fichiers TypeScript
└── fournisseurs/                  # 3 providers React
```

### SQL

```
sql/
├── INIT_COMPLET.sql               # 4922 lignes, source unique (prod)
├── schema/ (18 fichiers)          # Source de vérité par domaine
└── migrations/ (7 fichiers)       # À consolider dans schema/
```

---

## Annexe B — Métriques de santé projet

| Indicateur | Valeur | Cible | Statut |
|-----------|--------|-------|--------|
| Tests backend | ~55% couverture | ≥70% | 🟡 |
| Tests frontend | ~40% couverture | ≥50% | 🔴 |
| Tests E2E | ~10% | ≥30% | 🔴 |
| Docs à jour | ~60% (35/58 fichiers) | ≥90% | 🟡 |
| SQL ORM sync | Non vérifié | 100% | ⚠️ |
| Endpoints documentés | ~80% | 100% | 🟡 |
| Bridges inter-modules | 21 actifs | 31 possibles | 🟡 |
| CRON jobs testés | ~30% | ≥70% | 🔴 |
| Bugs critiques ouverts | 4 | 0 | 🔴 |
| Sécurité (OWASP) | Bon (JWT, sanitize, rate limit) | Complet | 🟡 |

---

> **Dernière mise à jour**: 1er Avril 2026
> **Prochaine revue prévue**: Après Phase A (stabilisation)
