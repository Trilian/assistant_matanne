# ðŸ” Analyse ComplÃ¨te â€” Assistant Matanne

> **Date**: 1er Avril 2026
> **Scope**: Backend (FastAPI/Python) + Frontend (Next.js 16) + SQL + Tests + Docs + IntÃ©grations
> **Objectif**: Audit exhaustif, plan d'action, axes d'amÃ©lioration

---

## Table des matiÃ¨res

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Inventaire des modules](#2-inventaire-des-modules)
3. [Bugs et problÃ¨mes dÃ©tectÃ©s](#3-bugs-et-problÃ¨mes-dÃ©tectÃ©s)
4. [Gaps et fonctionnalitÃ©s manquantes](#4-gaps-et-fonctionnalitÃ©s-manquantes)
5. [Consolidation SQL](#5-consolidation-sql)
6. [Interactions intra-modules](#6-interactions-intra-modules)
7. [Interactions inter-modules](#7-interactions-inter-modules)
8. [OpportunitÃ©s IA](#8-opportunitÃ©s-ia)
9. [Jobs automatiques (CRON)](#9-jobs-automatiques-cron)
10. [Notifications â€” WhatsApp, Email, Push](#10-notifications--whatsapp-email-push)
11. [Mode Admin manuel](#11-mode-admin-manuel)
12. [Couverture de tests](#12-couverture-de-tests)
13. [Documentation](#13-documentation)
14. [Organisation et architecture](#14-organisation-et-architecture)
15. [AmÃ©liorations UI/UX](#15-amÃ©liorations-uiux)
16. [Visualisations 2D et 3D](#16-visualisations-2d-et-3d)
17. [Simplification du flux utilisateur](#17-simplification-du-flux-utilisateur)
18. [Axes d'innovation](#18-axes-dinnovation)
19. [Plan d'action priorisÃ©](#19-plan-daction-priorisÃ©)

---

## 1. Vue d'ensemble du projet

### Chiffres clÃ©s

| MÃ©trique | Valeur |
| ---------- | -------- |
| Routes API (endpoints) | ~250+ |
| Routeurs FastAPI | 38 |
| ModÃ¨les SQLAlchemy (ORM) | 100+ (32 fichiers) |
| SchÃ©mas Pydantic | ~150+ (25 fichiers) |
| Tables SQL | 80+ |
| Pages frontend | ~60+ |
| Composants React | 208+ |
| Clients API frontend | 34 |
| Hooks React custom | 15 |
| Stores Zustand | 4 |
| SchÃ©mas Zod | 22 |
| Fichiers de tests (backend) | 74+ |
| Fichiers de tests (frontend) | 71 |
| CRON jobs | 68+ |
| Bridges inter-modules | 21 |
| Middlewares | 7 couches |
| WebSockets | 5 implÃ©mentations |
| Canaux de notification | 4 (push, ntfy, WhatsApp, email) |

### Stack technique

| Couche | Technologie |
| -------- | ------------- |
| Backend | Python 3.13+, FastAPI 0.109, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 16.2.1, React 19, TypeScript 5, Tailwind CSS v4 |
| Base de donnÃ©es | Supabase PostgreSQL, migrations SQL-file |
| IA | Mistral AI (client custom + cache sÃ©mantique + circuit breaker) |
| Ã‰tat frontend | TanStack Query v5, Zustand 5 |
| Charts | Recharts 3.8, Chart.js 4.5 |
| 3D | Three.js 0.183, @react-three/fiber 9.5 |
| Cartes | Leaflet 1.9, react-leaflet 5.0 |
| Tests backend | pytest, SQLite in-memory |
| Tests frontend | Vitest 4.1, Testing Library, Playwright |
| Monitoring | Prometheus metrics, Sentry |
| Notifications | ntfy.sh, Web Push VAPID, Meta WhatsApp Cloud, Resend |

---

## 2. Inventaire des modules

### Backend â€” Modules par domaine

| Module | Routes | Services | Bridges | CRON | Tests | Statut |
| -------- | -------- | ---------- | --------- | ------ | ------- | -------- |
| ðŸ½ï¸ **Cuisine/Recettes** | 20 endpoints | RecetteService, ImportService | 7 | 5 | âœ… Complet | âœ… Mature |
| ðŸ›’ **Courses** | 20 endpoints | CoursesService | 3 | 3 | âœ… Complet | âœ… Mature |
| ðŸ“¦ **Inventaire** | 14 endpoints | InventaireService | 4 | 3 | âœ… Complet | âœ… Mature |
| ðŸ“… **Planning** | 15 endpoints | PlanningService (5 sous-modules) | 5 | 4 | âœ… Complet | âœ… Mature |
| ðŸ§‘â€ðŸ³ **Batch Cooking** | 8 endpoints | BatchCookingService | 1 | 1 | âœ… OK | âœ… Stable |
| â™»ï¸ **Anti-Gaspillage** | 6 endpoints | AntiGaspillageService | 2 | 2 | âœ… OK | âœ… Stable |
| ðŸ’¡ **Suggestions IA** | 4 endpoints | BaseAIService | 0 | 0 | âœ… OK | âœ… Stable |
| ðŸ‘¶ **Famille/Jules** | 20 endpoints | JulesAIService | 7 | 5 | âœ… Complet | âœ… Mature |
| ðŸ¡ **Maison** | 15+ endpoints | MaisonService | 4 | 6 | âœ… OK | âœ… Stable |
| ðŸ  **Habitat** | 10 endpoints | HabitatService | 0 | 2 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸŽ® **Jeux** | 12 endpoints | JeuxService | 1 | 3 | âœ… OK | âœ… Stable |
| ðŸ—“ï¸ **Calendriers** | 6 endpoints | CalendrierService | 2 | 2 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ“Š **Dashboard** | 3 endpoints | DashboardService | 0 | 0 | âœ… OK | âœ… Stable |
| ðŸ“„ **Documents** | 6 endpoints | DocumentService | 1 | 1 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ”§ **Utilitaires** | 10+ endpoints | Notes, Journal, Contacts | 1 | 0 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ¤– **IA AvancÃ©e** | 14 endpoints | Multi-service | 0 | 0 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| âœˆï¸ **Voyages** | 8 endpoints | VoyageService | 2 | 1 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| âŒš **Garmin** | 5 endpoints | GarminService | 1 | 1 | âš ï¸ Minimal | ðŸŸ¡ En cours |
| ðŸ” **Auth / Admin** | 15+ endpoints | AuthService | 0 | 0 | âœ… OK | âœ… Stable |
| ðŸ“¤ **Export PDF** | 3 endpoints | RapportService | 0 | 0 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ”” **Push / Webhooks** | 8 endpoints | NotificationService | 0 | 5 | âš ï¸ Partiel | ðŸŸ¡ En cours |
| ðŸ¤– **Automations** | 6 endpoints | AutomationsEngine | 0 | 1 | âš ï¸ Partiel | ðŸŸ¡ En cours |

### Frontend â€” Pages par module

| Module | Pages | Composants spÃ©cifiques | Tests | Statut |
| -------- | ------- | ------------------------ | ------- | -------- |
| ðŸ½ï¸ **Cuisine** | 12 pages (recettes, planning, courses, inventaire, batch, anti-gasp, frigo, nutrition) | ~20 | âœ… 8 fichiers | âœ… Mature |
| ðŸ‘¶ **Famille** | 10 pages (jules, activitÃ©s, routines, budget, anniversaires, weekend, contacts, docs) | ~8 | âš ï¸ 3 fichiers | ðŸŸ¡ Gaps |
| ðŸ¡ **Maison** | 8 pages (projets, charges, entretien, jardin, stocks, Ã©nergie, artisans, visualisation) | ~15 | âš ï¸ 2 fichiers | ðŸŸ¡ Gaps |
| ðŸ  **Habitat** | 3 pages (hub, veille-immo, scÃ©narios) | ~6 | âš ï¸ 1 fichier | ðŸŸ¡ Gaps |
| ðŸŽ® **Jeux** | 7 pages (paris, loto, euromillions, performance, bankroll, OCR) | ~12 | âœ… 5 fichiers | âœ… OK |
| ðŸ“… **Planning** | 2 pages (hub, timeline) | ~3 | âœ… 2 fichiers | âœ… OK |
| ðŸ§° **Outils** | 6 pages (chat-ia, notes, minuteur, mÃ©tÃ©o, nutritionniste, assistant-vocal) | ~5 | âœ… 6 fichiers | âœ… OK |
| âš™ï¸ **ParamÃ¨tres** | 3 pages + 7 onglets | ~7 | âš ï¸ 1 fichier | ðŸŸ¡ Gaps |
| ðŸ”§ **Admin** | 10 pages (jobs, users, services, events, cache, IA, SQL, flags, WhatsApp, notif) | ~5 | âš ï¸ 2 fichiers | ðŸŸ¡ Gaps |

---

## 3. Bugs et problÃ¨mes dÃ©tectÃ©s

### ðŸ”´ Critiques

| # | Bug / ProblÃ¨me | Module | Impact | Fichier |
| --- | ---------------- | -------- | -------- | --------- |
| B1 | **API_SECRET_KEY random par process** â€” En multi-process (production), chaque worker gÃ©nÃ¨re un secret diffÃ©rent â†’ les tokens d'un worker sont invalides sur un autre | Auth | Tokens invalides en production multi-worker | `src/api/auth.py` |
| B2 | **WebSocket courses sans fallback HTTP** â€” Si le WebSocket est indisponible (proxy restrictif, mobile 3G), pas de polling HTTP alternatif â†’ la collaboration temps rÃ©el casse silencieusement | Courses | Perte de sync en temps rÃ©el | `utiliser-websocket-courses.ts` |
| B3 | **Promesse non gÃ©rÃ©e dans l'intercepteur auth** â€” Le refresh token peut timeout et laisser l'utilisateur bloquÃ© (ni connectÃ© ni dÃ©connectÃ©) | Frontend Auth | UX dÃ©gradÃ©e sur token expirÃ© | `api/client.ts` |
| B4 | **Event bus en mÃ©moire uniquement** â€” L'historique des Ã©vÃ©nements est perdu au redÃ©marrage du serveur, impossible de rejouer des Ã©vÃ©nements aprÃ¨s un crash | Core Events | Perte d'audit trail | `src/services/core/events/` |

### ðŸŸ¡ Importants

| # | Bug / ProblÃ¨me | Module | Impact | Fichier |
| --- | ---------------- | -------- | -------- | --------- |
| B5 | **Rate limiting en mÃ©moire non bornÃ©** â€” Le stockage en mÃ©moire croÃ®t avec chaque IP/user unique sans Ã©viction â†’ fuite mÃ©moire lente | Rate Limiting | Memory leak en production long | `rate_limiting/storage.py` |
| B6 | **Maintenance mode avec cache 5s** â€” La mise en maintenance peut prendre jusqu'Ã  5 secondes pour Ãªtre effective â†’ requÃªtes acceptÃ©es pendant la transition | Admin | RequÃªtes pendant maintenance | `src/api/main.py` |
| B7 | **X-Forwarded-For spoofable** â€” L'IP client est extraite du header sans vÃ©rifier la confiance du proxy â†’ bypass possible du rate limiting | SÃ©curitÃ© | Rate limiting contournable | `rate_limiting/limiter.py` |
| B8 | **Metrics capped Ã  500 endpoints / 1000 samples** â€” Les percentiles (p95, p99) deviennent imprÃ©cis aprÃ¨s beaucoup de requÃªtes | Monitoring | MÃ©triques dÃ©gradÃ©es | `src/api/utils/metrics.py` |
| B9 | **Multi-turn WhatsApp sans persistence d'Ã©tat** â€” La state machine de planning WhatsApp perd son Ã©tat entre les messages â†’ flux interrompu si l'utilisateur tarde | WhatsApp | Conversation WhatsApp cassÃ©e | `webhooks_whatsapp.py` |
| B10 | **CORS vide en production** â€” Si CORS_ORIGINS n'est pas configurÃ©, toutes les origines sont bloquÃ©es mais aucune erreur explicite | Config | Frontend bloquÃ© en prod sans config | `src/api/main.py` |

### ðŸŸ¢ Mineurs

| # | Bug / ProblÃ¨me | Module | Impact |
| --- | ---------------- | -------- | -------- |
| B11 | **ResponseValidationError** loggÃ© en 500 sans contexte debug â†’ difficile Ã  diagnostiquer | API | DX dÃ©gradÃ©e |
| B12 | **Pagination cursor** â€” Les suppressions concurrentes peuvent sauter des enregistrements | Pagination | DonnÃ©es manquÃ©es rarement |
| B13 | **ServiceMeta auto-sync wrappers** â€” La gÃ©nÃ©ration automatique de wrappers sync pour les mÃ©thodes async n'est pas testÃ©e exhaustivement | Core Services | Bugs potentiels subtils |
| B14 | **Sentry intÃ©gration Ã  50%** â€” ConfigurÃ© mais ne capture pas tous les erreurs frontend | Frontend | Erreurs non tracÃ©es |

---

## 4. Gaps et fonctionnalitÃ©s manquantes

### Par module

#### ðŸ½ï¸ Cuisine

| # | Gap | PrioritÃ© | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G1 | **Drag-drop recettes dans planning** | Moyenne | 2j | Le planning repas n'a pas de drag-drop pour rÃ©organiser les repas â†’ UX fastidieuse |
| G2 | **Import recettes par photo** | Moyenne | 3j | L'import URL/PDF existe mais pas l'import par photo d'un livre de cuisine (Pixtral disponible cÃ´tÃ© IA) |
| G3 | **Partage recette via WhatsApp** | Basse | 1j | Le partage existe par lien mais pas d'envoi direct WhatsApp avec preview |
| G4 | **Veille prix articles dÃ©sirÃ©s** | Moyenne | 3j | Scraper une API de suivi de prix (type Dealabs/Idealo) pour des articles ajoutÃ©s Ã  une wishlist + alertes soldes automatiques via `calendrier_soldes.json` dÃ©jÃ  prÃ©sent. Pas de saisie manuelle de prix Ã  chaque achat (trop fastidieux) |
| G5 | **Mode hors-ligne courses** | Haute | 3j | PWA installÃ©e mais pas de cache offline pour consulter la liste en magasin sans rÃ©seau |

#### ðŸ‘¶ Famille

| # | Gap | PrioritÃ© | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G6 | **PrÃ©vision budget IA** | Haute | 3j | Le budget famille n'a que le rÃ©sumÃ© mensuel, pas de prÃ©diction "fin de mois" avec IA |
| G7 | **Timeline Jules visuelle** | Moyenne | 2j | Les jalons de dÃ©veloppement existent mais pas de frise chronologique visuelle interactive |
| G8 | **Export calendrier anniversaires** | Basse | 1j | Les anniversaires ne s'exportent pas vers Google Calendar |
| G9 | **Photos souvenirs liÃ©es aux activitÃ©s** | Moyenne | 2j | Les activitÃ©s familiales n'ont pas d'upload photo pour le journal |

#### ðŸ¡ Maison

| # | Gap | PrioritÃ© | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G10 | **Plan 3D interactif limitÃ©** | Haute | 5j | Le composant Three.js existe mais n'est pas connectÃ© aux donnÃ©es rÃ©elles (tÃ¢ches par piÃ¨ce, consommation Ã©nergie) |
| G11 | **Historique Ã©nergie avec graphes** | Moyenne | 2j | Les relevÃ©s existent mais pas de visualisation tendancielle (courbes mois/annÃ©e) |
| G12 | **Catalogue artisans enrichi** | Basse | 2j | Pas d'avis/notes sur les artisans, pas de recherche par mÃ©tier |
| G13 | **Devis comparatif** | Moyenne | 3j | Pas de visualisation comparative des devis pour un mÃªme projet |

#### ðŸŽ® Jeux

| # | Gap | PrioritÃ© | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G14 | **Graphique ROI temporel** | Haute | 2j | Le ROI global existe mais pas la courbe d'Ã©volution mensuelle du ROI paris sportifs |
| G15 | **Alertes cotes temps rÃ©el** | Moyenne | 3j | Pas d'alerte quand une cote atteint un seuil dÃ©fini par l'utilisateur |
| G16 | **Comparaison stratÃ©gies loto** | Basse | 2j | Le backtest existe mais pas la comparaison cÃ´te Ã  cÃ´te de 2+ stratÃ©gies |

#### ðŸ“… Planning

| # | Gap | PrioritÃ© | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G17 | **Sync Google Calendar bidirectionnelle** | Haute | 4j | L'export iCal existe, la sync Google est Ã  ~60% â†’ pas de push automatique des repas/activitÃ©s vers Google Calendar |
| G18 | **Planning familial consolidÃ© visuel** | Moyenne | 3j | Pas de vue Gantt complÃ¨te mÃªlant repas + activitÃ©s + entretien + anniversaires |
| G19 | **RÃ©currence d'Ã©vÃ©nements** | Moyenne | 2j | Pas de gestion native "tous les mardis" pour les routines dans le calendrier |

#### ðŸ§° GÃ©nÃ©ral

| # | Gap | PrioritÃ© | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G20 | **Recherche globale incomplÃ¨te** | Haute | 3j | La recherche globale (Ctrl+K) ne couvre pas tous les modules (manque: notes, jardin, contrats) |
| G21 | **Mode hors-ligne (PWA)** | Haute | 5j | Service Worker enregistrÃ© mais pas de stratÃ©gie de cache offline structurÃ©e |
| G22 | **Onboarding interactif** | Moyenne | 3j | Le composant tour-onboarding existe mais n'est pas activÃ©/configurÃ© avec les Ã©tapes du parcours utilisateur |
| G23 | **Export donnÃ©es backup incomplet** | Moyenne | 2j | L'export JSON fonctionne mais l'import/restauration UI est incomplet |

---

## 5. Consolidation SQL

### Ã‰tat actuel

```
sql/
â”œâ”€â”€ INIT_COMPLET.sql          # Auto-gÃ©nÃ©rÃ© (4922 lignes, 18 fichiers schema)
â”œâ”€â”€ schema/                   # 18 fichiers organisÃ©s (01_extensions â†’ 99_footer)
â”‚   â”œâ”€â”€ 01_extensions.sql
â”‚   â”œâ”€â”€ 02_types_enums.sql
â”‚   â”œâ”€â”€ 03_system_tables.sql
â”‚   â”œâ”€â”€ 04_cuisine.sql
â”‚   â”œâ”€â”€ 05_famille.sql
â”‚   â”œâ”€â”€ 06_maison.sql
â”‚   â”œâ”€â”€ 07_jeux.sql
â”‚   â”œâ”€â”€ 08_habitat.sql
â”‚   â”œâ”€â”€ 09_voyages.sql
â”‚   â”œâ”€â”€ 10_notifications.sql
â”‚   â”œâ”€â”€ 11_gamification.sql
â”‚   â”œâ”€â”€ 12_automations.sql
â”‚   â”œâ”€â”€ 13_utilitaires.sql
â”‚   â”œâ”€â”€ 14_indexes.sql
â”‚   â”œâ”€â”€ 15_rls_policies.sql
â”‚   â”œâ”€â”€ 16_triggers.sql
â”‚   â”œâ”€â”€ 17_views.sql
â”‚   â””â”€â”€ 99_footer.sql
â””â”€â”€ migrations/               # 7 fichiers (V003-V008) + README
    â”œâ”€â”€ V003_*.sql
    â”œâ”€â”€ V004_*.sql
    â”œâ”€â”€ V005_phase2_sql_consolidation.sql
    â”œâ”€â”€ V006_*.sql
    â”œâ”€â”€ V007_*.sql
    â””â”€â”€ V008_phase4.sql
```

### Actions recommandÃ©es (mode dev, pas de versioning)

| # | Action | PrioritÃ© | DÃ©tail |
| --- | -------- | ---------- | -------- |
| S1 | **RegÃ©nÃ©rer INIT_COMPLET.sql** | Haute | ExÃ©cuter `python scripts/db/regenerate_init.py` pour s'assurer que le fichier monolithique est synchronisÃ© avec les 18 fichiers schema |
| S2 | **Audit ORM â†” SQL** | Haute | ExÃ©cuter `python scripts/audit_orm_sql.py` pour dÃ©tecter les divergences entre les modÃ¨les SQLAlchemy et les tables SQL |
| S3 | **Consolider les migrations en un seul schema** | Haute | En mode dev, fusionner les 7 migrations dans les fichiers schema correspondants et rÃ©gÃ©nÃ©rer INIT_COMPLET.sql. Une seule source de vÃ©ritÃ© |
| S4 | **VÃ©rifier les index manquants** | Moyenne | Certaines colonnes frÃ©quemment requÃªtÃ©es (user_id, date, statut) peuvent manquer d'index dans `14_indexes.sql` |
| S5 | **Nettoyer les tables inutilisÃ©es** | Basse | VÃ©rifier si toutes les 80+ tables ont un modÃ¨le ORM et une route API correspondante |
| S6 | **Vues SQL non utilisÃ©es** | Basse | VÃ©rifier que les vues dans `17_views.sql` sont rÃ©ellement utilisÃ©es par le backend |

### Proposition de workflow simplifiÃ©

```
1. Modifier le fichier schema appropriÃ© (ex: sql/schema/04_cuisine.sql)
2. ExÃ©cuter: python scripts/db/regenerate_init.py
3. Appliquer: exÃ©cuter INIT_COMPLET.sql sur Supabase (SQL Editor)
4. VÃ©rifier: python scripts/audit_orm_sql.py
```

> Pas de migrations ni de versioning en phase dev. Un seul INIT_COMPLET.sql fait foi.

---

## 6. Interactions intra-modules

### Cuisine (interne)

```
Recettes â”€â”€â”€â”€ planifiÃ©es â”€â”€â”€â†’ Planning
    â”‚                            â”‚
    â”‚                            â”œâ”€â”€ gÃ©nÃ¨re â”€â”€â†’ Courses
    â”‚                            â”‚
    â””â”€â”€ version Jules â”€â”€â†’ portions adaptÃ©es
                                 â”‚
Inventaire â—„â”€â”€â”€â”€â”€â”€ checkout â”€â”€â”€â”€â”˜
    â”‚
    â”œâ”€â”€ pÃ©remption â”€â”€â†’ Anti-Gaspillage â”€â”€â†’ Recettes rescue
    â”‚
    â””â”€â”€ stock bas â”€â”€â†’ Automation â”€â”€â†’ Courses auto
    
Batch Cooking â—„â”€â”€ planning semaine â”€â”€ prÃ©pare â”€â”€â†’ bloque planning
```

**âœ… Bien connectÃ©** â€” Le module cuisine a le plus d'interactions internes, toutes fonctionnelles.

**ðŸ”§ Ã€ amÃ©liorer:**
- Le checkout courses â†’ inventaire pourrait mettre Ã  jour les prix moyens automatiquement
- Le batch cooking manque un "mode robot" intelligent qui optimise l'ordre des Ã©tapes par appareil

### Famille (interne)

```
Jules profil â”€â”€â†’ jalons developpement
    â”‚               â”‚
    â”‚               â””â”€â”€ notifications anniversaire jalon
    â”‚
Budget â—„â”€â”€â”€â”€ dÃ©penses catÃ©gorisÃ©es
    â”‚
Routines â”€â”€â†’ check quotidien â”€â”€â†’ gamification (limitÃ©e)
    â”‚
Anniversaires â”€â”€â†’ checklist â”€â”€â†’ budget cadeau
    â”‚
Documents â”€â”€â†’ expiration â”€â”€â†’ rappels calendrier
```

**ðŸ”§ Ã€ amÃ©liorer:**
- Jules jalons â†’ suggestions d'activitÃ©s adaptÃ©es Ã  l'Ã¢ge (IA contextuelle)
- Budget anomalies â†’ pas de notification proactive ("tu dÃ©penses +30% en restaurants ce mois")
- Routines â†’ pas de tracking de complÃ©tion visuel (streak)

### Maison (interne)

```
Projets â”€â”€â†’ tÃ¢ches â”€â”€â†’ devis â”€â”€â†’ dÃ©penses
    â”‚
Entretien â”€â”€â†’ calendrier â”€â”€â†’ produits nÃ©cessaires
    â”‚
Jardin â”€â”€â†’ arrosage/rÃ©colte â”€â”€â†’ saison
    â”‚
Ã‰nergie â”€â”€â†’ relevÃ©s compteurs â”€â”€â†’ historique
    â”‚
Stocks (cellier) â”€â”€â†’ consolidÃ© avec inventaire cuisine
```

**ðŸ”§ Ã€ amÃ©liorer:**
- Projets â†’ pas de timeline visuelle Gantt des travaux
- Ã‰nergie â†’ pas de graphe d'Ã©volution ni de comparaison N vs N-1
- Entretien â†’ pas de suggestions IA proactives ("votre chaudiÃ¨re a 8 ans, prÃ©voir rÃ©vision")

---

## 7. Interactions inter-modules

### Bridges existants (21 actifs) âœ…

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ CUISINE  â”‚â—„â”€â”€â”€â–ºâ”‚ PLANNING  â”‚â—„â”€â”€â”€â–ºâ”‚ COURSES  â”‚
â”‚          â”‚     â”‚           â”‚     â”‚          â”‚
â”‚ recettes â”‚     â”‚ repas     â”‚     â”‚ listes   â”‚
â”‚ inventaireâ”‚    â”‚ semaine   â”‚     â”‚ articles â”‚
â”‚ nutrition â”‚    â”‚ conflits  â”‚     â”‚          â”‚
â”‚ batch     â”‚    â”‚           â”‚     â”‚          â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
     â”‚                 â”‚                 â”‚
     â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤                 â”‚
     â”‚    â”‚            â”‚                 â”‚
â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â–¼â”€â”€â”   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”
â”‚  FAMILLE   â”‚   â”‚  MAISON  â”‚     â”‚  BUDGET  â”‚
â”‚            â”‚   â”‚          â”‚     â”‚          â”‚
â”‚ jules      â”‚   â”‚ entretienâ”‚     â”‚ famille  â”‚
â”‚ routines   â”‚   â”‚ jardin   â”‚     â”‚ jeux (sÃ©parÃ©)
â”‚ annivers.  â”‚   â”‚ Ã©nergie  â”‚     â”‚ maison   â”‚
â”‚ documents  â”‚   â”‚ projets  â”‚     â”‚          â”‚
â”‚ weekend    â”‚   â”‚ stocks   â”‚     â”‚          â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â”‚                â”‚
     â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
     â”‚    â”‚           â”‚
â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â–¼â”€â”€â”   â”Œâ”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”
â”‚ CALENDRIER â”‚   â”‚  JEUX    â”‚
â”‚            â”‚   â”‚          â”‚
â”‚ google cal â”‚   â”‚ paris    â”‚
â”‚ Ã©vÃ©nements â”‚   â”‚ loto     â”‚
â”‚            â”‚   â”‚ bankroll â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Bridges inter-modules dÃ©taillÃ©s

| # | Bridge | De â†’ Vers | Fonctionnel | Description |
| --- | -------- | ----------- | ------------- | ------------- |
| 1 | `inter_module_inventaire_planning` | Stock â†’ Planning | âœ… | Priorise recettes par ingrÃ©dients disponibles |
| 2 | `inter_module_jules_nutrition` | Jules â†’ Recettes | âœ… | Portions adaptÃ©es Ã¢ge, filtrage allergÃ¨nes |
| 3 | `inter_module_saison_menu` | Saison â†’ Planning | âœ… | Produits frais de saison dans les suggestions |
| 4 | `inter_module_courses_budget` | Courses â†’ Budget | âœ… | Suivi impact budget des courses |
| 5 | `inter_module_batch_inventaire` | Batch â†’ Inventaire | âœ… | Mise Ã  jour stock aprÃ¨s batch cooking |
| 6 | `inter_module_planning_voyage` | Voyage â†’ Planning | âœ… | Exclusion planning pendant les voyages |
| 7 | `inter_module_peremption_recettes` | PÃ©remption â†’ Recettes | âœ… | Recettes rescue des produits bientÃ´t pÃ©rimÃ©s |
| 8 | `inter_module_documents_calendrier` | Documents â†’ Calendrier | âœ… | Rappels renouvellement docs expirÃ©s |
| 9 | `inter_module_meteo_activites` | MÃ©tÃ©o â†’ ActivitÃ©s | âœ… | Suggestions activitÃ©s selon mÃ©tÃ©o |
| 10 | `inter_module_weekend_courses` | Weekend â†’ Courses | âœ… | Liste courses pour activitÃ©s weekend |
| 11 | `inter_module_voyages_budget` | Voyages â†’ Budget | âœ… | Sync coÃ»ts voyage â†’ budget |
| 12 | `inter_module_anniversaires_budget` | Anniversaires â†’ Budget | âœ… | Tracking dÃ©penses cadeaux/fÃªtes |
| 13 | `inter_module_budget_jeux` | Jeux â†” Budget | âœ… (info) | Sync pour info uniquement (budgets sÃ©parÃ©s volontairement) |
| 14 | `inter_module_garmin_health` | Garmin â†’ Dashboard | âœ… | Score bien-Ãªtre intÃ©grant fitness |
| 15 | `inter_module_entretien_courses` | Entretien â†’ Courses | âœ… | Produits mÃ©nagers pour tÃ¢ches Ã  venir |
| 16 | `inter_module_jardin_entretien` | Jardin â†’ Entretien | âœ… | Coordination jardinage/entretien |
| 17 | `inter_module_charges_energie` | Charges â†’ Ã‰nergie | âœ… | Budget insights factures |
| 18 | `inter_module_energie_cuisine` | Ã‰nergie â†’ Cuisine | âœ… | Optimisation cuisson heures creuses |
| 19 | `inter_module_chat_contexte` | Tous â†’ Chat IA | âœ… | Contexte multi-module injectÃ© dans le chat |
| 20 | `inter_module_voyages_calendrier` | Voyages â†’ Calendrier | âœ… | Sync dates voyage dans calendrier |
| 21 | `inter_module_garmin_planning` | Garmin â†’ Planning | âš ï¸ | Partiellement connectÃ© |

### Interactions manquantes Ã  implÃ©menter

| # | Interaction proposÃ©e | De â†’ Vers | Valeur | Effort |
| --- | --------------------- | ----------- | -------- | -------- |
| I1 | **RÃ©colte jardin â†’ Recettes semaine suivante** | Jardin â†’ Planning | âœ… AcceptÃ©e | 2j |
| I2 | **Entretien rÃ©current â†’ Planning unifiÃ©** | Entretien â†’ Planning global | Haute | 2j |
| I3 | **Budget anomalie â†’ Notification proactive** | Budget â†’ Notifications | Haute | 2j |
| I4 | **Voyages â†’ Inventaire** (dÃ©stockage avant dÃ©part) | Voyages â†’ Inventaire | Moyenne | 1j |
| I5 | **Documents expirÃ©s â†’ Dashboard alerte** | Documents â†’ Dashboard | Haute | 1j |
| I6 | **Anniversaire proche â†’ Suggestions cadeaux IA** | Anniversaires â†’ IA | Moyenne | 2j |
| I7 | **Contrats/Garanties â†’ Dashboard widgets** | Maison â†’ Dashboard | Moyenne | 1j |
| I8 | **MÃ©tÃ©o â†’ Entretien maison** (ex: gel â†’ penser au jardin) | MÃ©tÃ©o â†’ Maison | Moyenne | 2j |
| I9 | **Planning sport Garmin â†’ Planning repas** (adapter alimentation) | Garmin â†’ Cuisine | Moyenne | 3j |
| I10 | **Courses historique â†’ PrÃ©diction prochaine liste** | Courses â†’ IA | Haute | 3j |

---

## 8. OpportunitÃ©s IA

### IA actuellement en place âœ…

| FonctionnalitÃ© | Service | Module | Statut |
| ---------------- | --------- | -------- | -------- |
| Suggestions recettes | BaseAIService | Cuisine | âœ… Fonctionnel |
| GÃ©nÃ©ration planning IA | PlanningService | Planning | âœ… Fonctionnel |
| Recettes rescue anti-gaspi | AntiGaspillageService | Cuisine | âœ… Fonctionnel |
| Batch cooking optimisÃ© | BatchCookingService | Cuisine | âœ… Fonctionnel |
| Suggestions weekend | WeekendAIService | Famille | âœ… Fonctionnel |
| Score bien-Ãªtre | DashboardService | Dashboard | âœ… Fonctionnel |
| Chat IA contextualisÃ© | AssistantService | Outils | âœ… Fonctionnel |
| Version Jules recettes | JulesAIService | Famille | âœ… Fonctionnel |
| 14 endpoints IA avancÃ©e | Multi-services | IA AvancÃ©e | âš ï¸ Partiel |

### Nouvelles opportunitÃ©s IA Ã  exploiter

| # | OpportunitÃ© | Module(s) | Description | PrioritÃ© | Effort |
| --- | ------------- | ----------- | ------------- | ---------- | -------- |
| IA1 | **PrÃ©diction courses intelligente** | Courses + Historique | Analyser l'historique des courses (frÃ©quence, quantitÃ©s) pour prÃ©-remplir la prochaine liste. "Tu achÃ¨tes du lait tous les 5 jours, il est temps d'en commander" | ðŸ”´ Haute | 3j |
| IA2 | **Planificateur adaptatif mÃ©tÃ©o+stock+budget** | Planning + MÃ©tÃ©o + Inventaire + Budget | L'endpoint existe mais sous-utilisÃ©. Exploiter : mÃ©tÃ©o chaude â†’ salades/grillades, stock important de tomates â†’ les utiliser, budget serrÃ© â†’ recettes avec ce qu'on a | ðŸ”´ Haute | 2j |
| IA3 | **Diagnostic pannes maison** | Maison | Photo d'un appareil en panne â†’ diagnostic IA (Pixtral) + suggestion d'action (appeler artisan X, piÃ¨ce Ã  commander) | ðŸŸ¡ Moyenne | 3j |
| IA4 | **Assistant vocal contextuel** | Tous | Google Assistant connectÃ© mais capacitÃ©s limitÃ©es Ã  quelques intents. Ã‰tendre: "Hey Google, qu'est-ce qu'on mange ce soir ?" â†’ lecture du planning + suggestions si vide | ðŸŸ¡ Moyenne | 4j |
| IA5 | **RÃ©sumÃ© hebdomadaire intelligent** | Dashboard | RÃ©sumÃ© IA de la semaine: repas cuisinÃ©s, tÃ¢ches accomplies, budget, scores, prochaines Ã©chÃ©ances. Format narratif agrÃ©able Ã  lire | ðŸ”´ Haute | 2j |
| IA6 | **Optimisation Ã©nergie prÃ©dictive** | Maison/Ã‰nergie | Analyser les relevÃ©s compteurs + mÃ©tÃ©o â†’ prÃ©dire la facture du mois + suggÃ©rer des Ã©conomies ciblÃ©es | ðŸŸ¡ Moyenne | 3j |
| IA7 | **Analyse nutritionnelle photo** | Cuisine/Nutrition | Prendre en photo un plat â†’ l'IA estime les calories/macros/micros (Pixtral) | ðŸŸ¡ Moyenne | 3j |
| IA8 | **Suggestion d'organisation batch cooking** | Batch Cooking | Analyser le planning de la semaine + les appareils dispo (robot, four, etc.) â†’ proposer un plan de batch cooking optimal avec timeline parallÃ¨le | ðŸ”´ Haute | 3j |
| IA9 | **Jules: conseil dÃ©veloppement proactif** | Famille/Jules | "Ã€ l'Ã¢ge de Jules, les enfants commencent Ã ..." â€” suggestions d'activitÃ©s/jouets/apprentissages adaptÃ©s en fonction des jalons franchis vs attendus | ðŸŸ¡ Moyenne | 2j |
| IA10 | **Auto-catÃ©gorisation budget** | Budget | CatÃ©goriser automatiquement les dÃ©penses Ã  partir du nom du commerÃ§ant/article (pas d'OCR ticket, juste texte) | ðŸŸ¡ Moyenne | 2j |
| IA11 | **GÃ©nÃ©ration checklist voyage** | Voyages | Ã€ partir de la destination, dates, participants â†’ checklist complÃ¨te IA (vÃªtements, documents, rÃ©servations, vaccins si besoin) | ðŸŸ¡ Moyenne | 2j |
| IA12 | **Score Ã©cologique repas** | Cuisine | Ã‰valuer l'impact Ã©cologique du planning repas (saisonnalitÃ©, distance parcourue des aliments, protÃ©ines vÃ©gÃ©tales vs animales) | ðŸŸ¢ Basse | 2j |

---

## 9. Jobs automatiques (CRON)

### Jobs existants (68+)

#### Quotidiens

| Job | Horaire | Action | Canaux | Modules impliquÃ©s |
| ----- | --------- | -------- | -------- | ------------------- |
| `digest_whatsapp_matinal` | 07h30 | Repas du jour, tÃ¢ches, pÃ©remptions, boutons interactifs | WhatsApp | Cuisine, Maison, Inventaire |
| `rappels_famille` | 07h00 | Anniversaires, documents, jalons Jules | WhatsApp + Push + ntfy | Famille |
| `rappels_maison` | 08h00 | Garanties, contrats, entretien | Push + ntfy | Maison |
| `digest_ntfy` | 09h00 | Digest compact | ntfy | Multi-module |
| `rappel_courses` | 18h00 | Revue liste interactive | WhatsApp | Courses |
| `push_contextuel_soir` | 18h00 | PrÃ©paration lendemain | Push | Planning |
| `alerte_stock_bas` | 07h00 | Stock bas â†’ ajout auto courses | Automation | Inventaire â†’ Courses |
| `sync_google_calendar` | 23h00 | Push planning vers Google Cal | - | Planning â†’ Calendrier |
| `garmin_sync_matinal` | 06h00 | Sync donnÃ©es Garmin | - | Garmin |
| `automations_runner` | Toutes les 5 min | ExÃ©cution rÃ¨gles automation | Variable | Automations |

#### Hebdomadaires

| Job | Jour/Horaire | Action | Canaux |
| ----- | ------------- | -------- | -------- |
| `resume_hebdo` | Lundi 07h30 | RÃ©sumÃ© semaine passÃ©e | ntfy, email, WhatsApp |
| `score_weekend` | Vendredi 17h00 | Contexte weekend (mÃ©tÃ©o, activitÃ©s, suggestions) | WhatsApp |
| `score_bien_etre_hebdo` | Dimanche 20h00 | Score consolidÃ© bien-Ãªtre | Dashboard |
| `points_famille_hebdo` | Dimanche 20h00 | Points gamification | Dashboard |
| `sync_openfoodfacts` | Dimanche 03h00 | RafraÃ®chir cache produits | - |

#### Mensuels

| Job | Jour/Horaire | Action | Canaux |
| ----- | ------------- | -------- | -------- |
| `rapport_mensuel_budget` | 1er 08h15 | RÃ©sumÃ© budget + tendances | Email |
| `controle_contrats_garanties` | 1er 09h00 | Alertes renouvellement | Push + ntfy |
| `rapport_maison_mensuel` | 1er 09h30 | RÃ©sumÃ© entretien maison | Email |

### Nouveaux jobs proposÃ©s

| # | Job proposÃ© | FrÃ©quence | Modules | Description | PrioritÃ© |
| --- | ------------- | ----------- | --------- | ------------- | ---------- |
| J1 | **`prediction_courses_hebdo`** | Vendredi 16h | Courses + IA | PrÃ©-gÃ©nÃ©rer une liste de courses prÃ©dictive pour la semaine suivante basÃ©e sur l'historique | ðŸ”´ Haute |
| J2 | **`planning_auto_semaine`** | Dimanche 19h | Planning + IA | Si le planning de la semaine suivante est vide, proposer un planning IA via WhatsApp (valider/modifier/rejeter) | ðŸ”´ Haute |
| J3 | **`nettoyage_cache_export`** | Quotidien 02h | Export | Supprimer les fichiers d'export > 7 jours dans data/exports/ | ðŸŸ¡ Moyenne |
| J4 | **`rappel_jardin_saison`** | Hebdo (Lundi) | Jardin | "C'est la saison pour planter les tomates" â€” rappels saisonniers intelligents | ðŸŸ¡ Moyenne |
| J5 | **`sync_budget_consolidation`** | Quotidien 22h | Budget | Consolider les dÃ©penses de tous les modules (courses, maison, jeux info, voyages) en un seul suivi | ðŸŸ¡ Moyenne |
| J6 | **`verification_sante_systeme`** | Toutes les heures | Admin | VÃ©rifier DB, cache, IA, et envoyer alerte ntfy si un service est down | ðŸŸ¡ Moyenne |
| J7 | **`backup_auto_json`** | Hebdo (Dimanche 04h) | Admin | Export automatique de toutes les donnÃ©es en JSON (backup) | ðŸŸ¢ Basse |
| J8 | **`tendances_nutrition_hebdo`** | Dimanche 18h | Cuisine/Nutrition | Analyser les repas de la semaine â†’ score nutritionnel + recommandations | ðŸŸ¡ Moyenne |
| J9 | **`alertes_budget_seuil`** | Quotidien 20h | Budget | VÃ©rifier si une catÃ©gorie dÃ©passe 80% du budget mensuel â†’ alerte proactive | ðŸ”´ Haute |
| J10 | **`rappel_activite_jules`** | Quotidien 09h | Famille | "Jules a 18 mois aujourd'hui ! Voici les activitÃ©s recommandÃ©es pour son Ã¢ge" | ðŸŸ¡ Moyenne |

---

## 10. Notifications â€” WhatsApp, Email, Push

### Architecture actuelle

```
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  Ã‰vÃ©nement      â”‚
                    â”‚  (CRON / User)  â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  Router de      â”‚
                    â”‚  notifications  â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚                â”‚                â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”
    â”‚  Web Push    â”‚ â”‚   ntfy.sh    â”‚ â”‚ WhatsApp   â”‚
    â”‚  (VAPID)     â”‚ â”‚  (open src)  â”‚ â”‚ (Meta API) â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚    Email        â”‚
                    â”‚   (Resend)      â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
    
    Failover: Push â†’ ntfy â†’ WhatsApp â†’ Email
    Throttle: 2h par type d'Ã©vÃ©nement par canal
```

### AmÃ©liorations WhatsApp proposÃ©es

| # | AmÃ©lioration | PrioritÃ© | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| W1 | **Persistence Ã©tat conversation** | ðŸ”´ Haute | 2j | Le state machine planning perd l'Ã©tat entre les messages. Stocker dans Redis/DB pour permettre des conversations multi-tour |
| W2 | **Commandes texte enrichies** | ðŸ”´ Haute | 3j | Supporter: "ajoute du lait Ã  la liste", "qu'est-ce qu'on mange demain", "combien j'ai dÃ©pensÃ© ce mois" â†’ parsing NLP via Mistral |
| W3 | **Boutons interactifs Ã©tendus** | ðŸŸ¡ Moyenne | 2j | Ajouter des boutons quick-reply pour: valider courses, noter une dÃ©pense, signaler un problÃ¨me maison |
| W4 | **Photo â†’ action** | ðŸŸ¡ Moyenne | 3j | Envoyer une photo de plante malade â†’ diagnostic IA. Photo d'un plat â†’ identification + ajout recette |
| W5 | **RÃ©sumÃ© quotidien personnalisable** | ðŸŸ¡ Moyenne | 2j | Permettre Ã  l'utilisateur de choisir quelles infos recevoir dans le digest matinal (via paramÃ¨tres) |

### AmÃ©liorations Email proposÃ©es

| # | AmÃ©lioration | PrioritÃ© | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| E1 | **Templates HTML jolis** | ðŸŸ¡ Moyenne | 2j | Les emails actuels sont basiques. CrÃ©er des templates HTML modernes (MJML) pour les rapports mensuels |
| E2 | **RÃ©sumÃ© hebdo email** | ðŸŸ¡ Moyenne | 1j | Pas d'email hebdomadaire automatique (seulement ntfy/WhatsApp). Ajouter un email digest optionnel |
| E3 | **Alertes critiques par email** | ðŸ”´ Haute | 1j | Les alertes critiques (document expirÃ©, stock critique, budget dÃ©passÃ©) devraient aussi aller par email en plus des autres canaux |

### AmÃ©liorations Push proposÃ©es

| # | AmÃ©lioration | PrioritÃ© | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| P1 | **Actions dans la notification** | ðŸŸ¡ Moyenne | 2j | "Ajouter au courses" directement depuis la notification push (web push actions) |
| P2 | **Push conditionnel (heure calme)** | ðŸŸ¡ Moyenne | 1j | Respecter les heures calmes configurÃ©es dans les paramÃ¨tres utilisateur |
| P3 | **Badge app PWA** | ðŸŸ¢ Basse | 1j | Afficher le nombre de notifications non lues sur l'icÃ´ne PWA |

---

## 11. Mode Admin manuel

### Existant âœ… (trÃ¨s complet)

L'application a dÃ©jÃ  un **panneau admin robuste** accessible via:
- **Frontend**: `/admin/*` (10 pages dÃ©diÃ©es)
- **Raccourci**: `Ctrl+Shift+A` (panneau flottant overlay)
- **Backend**: `POST /api/v1/admin/*` (20+ endpoints admin)

#### FonctionnalitÃ©s admin existantes

| CatÃ©gorie | FonctionnalitÃ© | Status |
| ----------- | --------------- | -------- |
| **Jobs CRON** | Lister tous les jobs + prochain run | âœ… |
| **Jobs CRON** | DÃ©clencher manuellement n'importe quel job | âœ… |
| **Jobs CRON** | Voir l'historique d'exÃ©cution | âœ… |
| **Notifications** | Tester un canal spÃ©cifique (ntfy/push/email/WhatsApp) | âœ… |
| **Notifications** | Broadcast test sur tous les canaux | âœ… |
| **Event Bus** | Voir l'historique des Ã©vÃ©nements | âœ… |
| **Event Bus** | Ã‰mettre un Ã©vÃ©nement manuellement | âœ… |
| **Cache** | Voir les stats du cache | âœ… |
| **Cache** | Purger par pattern | âœ… |
| **Services** | Ã‰tat de tous les services (registre) | âœ… |
| **Feature Flags** | Activer/dÃ©sactiver des features | âœ… |
| **Maintenance** | Mode maintenance ON/OFF | âœ… |
| **Simulation** | Dry-run workflows (pÃ©remption, digest, rappels) | âœ… |
| **IA Console** | Tester des prompts avec contrÃ´le tempÃ©rature/tokens | âœ… |
| **Impersonation** | Switcher d'utilisateur | âœ… |
| **Audit Logs** | TraÃ§abilitÃ© complÃ¨te | âœ… |
| **Security Logs** | Ã‰vÃ©nements sÃ©curitÃ© | âœ… |
| **SQL Views** | Browser de vues SQL | âœ… |
| **WhatsApp Test** | Envoyer un message WhatsApp test | âœ… |
| **Config** | Export/import configuration runtime | âœ… |

### AmÃ©liorations proposÃ©es

| # | AmÃ©lioration | PrioritÃ© | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| A1 | **Console de commande rapide** | ðŸŸ¡ Moyenne | 2j | Un champ texte dans le panneau admin pour lancer des commandes rapides: "run job rappels_famille", "clear cache recettes*", "test whatsapp" |
| A2 | **Dashboard admin temps rÃ©el** | ðŸŸ¡ Moyenne | 3j | WebSocket admin_logs dÃ©jÃ  en place â€” l'afficher en temps rÃ©el sur la page admin avec filtres et auto-scroll |
| A3 | **Scheduler visuel** | ðŸŸ¡ Moyenne | 3j | Vue timeline des 68 CRON jobs avec le prochain run, la derniÃ¨re exÃ©cution, et les dÃ©pendances visuelles |
| A4 | **Replay d'Ã©vÃ©nements** | ðŸŸ¡ Moyenne | 2j | Permettre de rejouer un Ã©vÃ©nement passÃ© du bus avec ses subscriber handlers |
| A5 | **Panneau admin invisible pour l'utilisateur** | âœ… DÃ©jÃ  fait | - | Le panneau est accessible uniquement via `role=admin` et `Ctrl+Shift+A`. Invisible pour l'utilisateur normal |
| A6 | **Logs en temps rÃ©el** | ðŸŸ¡ Moyenne | 2j | Stream les logs du serveur via WebSocket admin_logs (l'endpoint existe, le connecter Ã  l'UI) |
| A7 | **Test E2E one-click** | ðŸŸ¢ Basse | 3j | Bouton "Lancer test complet" qui exÃ©cute un scÃ©nario E2E (crÃ©er recette â†’ planifier â†’ gÃ©nÃ©rer courses â†’ checkout â†’ vÃ©rifier inventaire) |

---

## 12. Couverture de tests

### Backend (Python/pytest)

| Zone | Fichiers test | Fonctions test | Couverture estimÃ©e | Note |
| ------ | ------------- | ---------------- | --------------------- | ------ |
| Routes API (cuisine) | 8 | ~120 | âœ… ~85% | Bien couvert |
| Routes API (famille) | 6 | ~80 | âœ… ~75% | OK |
| Routes API (maison) | 5 | ~60 | âš ï¸ ~60% | Gaps sur jardin, Ã©nergie |
| Routes API (jeux) | 2 | ~30 | âš ï¸ ~55% | Gaps sur loto, euromillions |
| Routes API (admin) | 2 | ~40 | âœ… ~70% | OK |
| Routes API (export/upload) | 2 | ~15 | âŒ ~30% | TrÃ¨s faible |
| Routes API (webhooks) | 2 | ~10 | âŒ ~25% | TrÃ¨s faible |
| Services | 20+ | ~300 | âš ï¸ ~60% | Variable |
| Core (config, db, cache) | 6 | ~200 | âš ï¸ ~55% | Cache orchestrateur faible |
| Event Bus | 1 | ~10 | âŒ ~20% | TrÃ¨s faible |
| RÃ©silience | 1 | ~15 | âš ï¸ ~40% | Manque scÃ©narios rÃ©els |
| WebSocket | 1 | ~8 | âŒ ~25% | Edge cases manquants |
| IntÃ©grations | 3 | ~20 | âŒ ~20% | Stubs mais pas end-to-end |
| **TOTAL** | **74+** | **~1000** | **âš ï¸ ~55%** | **50-60% estimÃ©** |

### Frontend (Vitest)

| Zone | Fichiers test | Couverture estimÃ©e | Note |
| ------ | ------------- | --------------------- | ------ |
| Pages cuisine | 8 | âœ… ~70% | Bien couvert |
| Pages jeux | 5 | âœ… ~65% | OK |
| Pages outils | 6 | âœ… ~60% | OK |
| Pages famille | 3 | âš ï¸ ~35% | Gaps importants |
| Pages maison | 2 | âš ï¸ ~30% | Gaps importants |
| Pages admin | 2 | âš ï¸ ~30% | Gaps importants |
| Pages paramÃ¨tres | 1 | âŒ ~15% | TrÃ¨s faible |
| Hooks | 2 | âš ï¸ ~45% | WebSocket sous-testÃ© |
| Stores | 4 | âœ… ~80% | Bien couvert |
| Composants | 12 | âš ï¸ ~40% | Variable |
| API clients | 1 | âŒ ~15% | TrÃ¨s faible |
| E2E (Playwright) | Quelques | âŒ ~10% | Quasi inexistant |
| **TOTAL** | **71** | **âš ï¸ ~40%** | **Min Vitest: 50%** |

### Tests manquants prioritaires

| # | Test Ã  ajouter | Module | PrioritÃ© | Description |
| --- | --------------- | -------- | ---------- | ------------- |
| T1 | **Tests export PDF** | Export | ðŸ”´ Haute | VÃ©rifier gÃ©nÃ©ration PDF pour courses, planning, recettes, budget |
| T2 | **Tests webhooks WhatsApp** | Notifications | ðŸ”´ Haute | Tester state machine planning, parsing commandes |
| T3 | **Tests event bus scenarios** | Core | ðŸ”´ Haute | Pub/sub avec wildcards, prioritÃ©s, erreurs handlers |
| T4 | **Tests cache L1/L2/L3** | Core | ðŸŸ¡ Moyenne | ScÃ©narios promotion/Ã©viction entre niveaux |
| T5 | **Tests WebSocket edge cases** | Courses | ðŸŸ¡ Moyenne | Reconnexion, timeout, messages malformÃ©s |
| T6 | **Tests E2E parcours utilisateur** | Frontend | ðŸ”´ Haute | ScÃ©nario complet: login â†’ crÃ©er recette â†’ planifier â†’ courses â†’ checkout |
| T7 | **Tests API clients frontend** | Frontend | ðŸŸ¡ Moyenne | Erreurs rÃ©seau, refresh token, pagination |
| T8 | **Tests pages paramÃ¨tres** | Frontend | ðŸŸ¡ Moyenne | Chaque onglet de paramÃ¨tres |
| T9 | **Tests pages admin** | Frontend | ðŸŸ¡ Moyenne | Jobs, services, cache, feature flags |
| T10 | **Tests Playwright accessibilitÃ©** | Frontend | ðŸŸ¢ Basse | axe-core sur les pages principales |

---

## 13. Documentation

### Ã‰tat actuel

| Document | DerniÃ¨re MÃ J | Statut | Action nÃ©cessaire |
| ---------- | ------------- | -------- | ------------------- |
| `docs/INDEX.md` | 1 Avril 2026 | âœ… Courant | - |
| `docs/MODULES.md` | 1 Avril 2026 | âœ… Courant | - |
| `docs/API_REFERENCE.md` | 1 Avril 2026 | âœ… Courant | - |
| `docs/API_SCHEMAS.md` | 1 Avril 2026 | âœ… Courant | - |
| `docs/SERVICES_REFERENCE.md` | 1 Avril 2026 | âœ… Courant | - |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | 31 Mars 2026 | âœ… Courant | - |
| `docs/ERD_SCHEMA.md` | 31 Mars 2026 | âœ… Courant | - |
| `docs/ARCHITECTURE.md` | 1 Mars 2026 | âš ï¸ 1 mois | RafraÃ®chir avec les changements core rÃ©cents |
| `docs/DATA_MODEL.md` | Inconnu | âš ï¸ VÃ©rifier | Peut Ãªtre obsolÃ¨te post-phases 8-10 |
| `docs/DEPLOYMENT.md` | Mars 2026 | âš ï¸ VÃ©rifier | VÃ©rifier config Railway/Vercel actuelle |
| `docs/ADMIN_RUNBOOK.md` | Inconnu | âš ï¸ VÃ©rifier | Les 20+ endpoints admin ont-ils tous un doc ? |
| `docs/CRON_JOBS.md` | Inconnu | ðŸ”´ ObsolÃ¨te | 68+ jobs, probablement plus Ã  jour depuis phases 8-10 |
| `docs/NOTIFICATIONS.md` | Inconnu | ðŸ”´ ObsolÃ¨te | SystÃ¨me refait en phase 8 |
| `docs/AUTOMATIONS.md` | Inconnu | ðŸ”´ ObsolÃ¨te | Expansion phases 8-10 |
| `docs/INTER_MODULES.md` | Inconnu | âš ï¸ VÃ©rifier | 21 bridges â€” tous documentÃ©s ? |
| `docs/EVENT_BUS.md` | Inconnu | âš ï¸ VÃ©rifier | Subscribers Ã  jour ? |
| `docs/MONITORING.md` | Inconnu | âš ï¸ VÃ©rifier | Prometheus metrics actuelles ? |
| `docs/SECURITY.md` | Inconnu | âš ï¸ VÃ©rifier | Rate limiting, 2FA, CORS docs Ã  jour ? |
| `PLANNING_IMPLEMENTATION.md` | Inconnu | ðŸ”´ ObsolÃ¨te | Liste seulement sprints 1-9, projet Ã  Phase 10+ |
| `ROADMAP.md` | Inconnu | ðŸ”´ ObsolÃ¨te | PrioritÃ©s peut-Ãªtre obsolÃ¨tes |

### Documentation manquante

| # | Document Ã  crÃ©er | PrioritÃ© | Description |
| --- | ----------------- | ---------- | ------------- |
| D1 | **Guide complet des CRON jobs** | ðŸ”´ Haute | Lister les 68+ jobs, horaires, dÃ©pendances, comment ajouter un nouveau job |
| D2 | **Guide des notifications** (refonte) | ðŸ”´ Haute | 4 canaux, failover, throttle, templates WhatsApp, configuration |
| D3 | **Guide admin** (mise Ã  jour) | ðŸŸ¡ Moyenne | Les 20+ endpoints admin, panneau flottant, simulations, feature flags |
| D4 | **Guide des bridges inter-modules** | ðŸŸ¡ Moyenne | Les 21 bridges, comment en crÃ©er un nouveau, naming convention |
| D5 | **Guide de test** (unifiÃ©) | ðŸŸ¡ Moyenne | Backend pytest + Frontend Vitest + E2E Playwright, fixtures, mocks communs |
| D6 | **Changelog module par module** | ðŸŸ¢ Basse | Historique des changements par module pour le suivi |

---

## 14. Organisation et architecture

### Points forts âœ…

- **Architecture modulaire** : SÃ©paration claire routes/schemas/services/models
- **Service Registry** : Pattern singleton thread-safe avec `@service_factory`
- **Event Bus** : Pub/sub dÃ©couplÃ© avec wildcards et prioritÃ©s
- **Cache multi-niveaux** : L1 (mÃ©moire) â†’ L2 (session) â†’ L3 (fichier) + Redis optionnel
- **RÃ©silience** : Retry + Timeout + Circuit Breaker composables
- **SÃ©curitÃ©** : JWT + 2FA TOTP + rate limiting + security headers + sanitization
- **Frontend** : App Router Next.js 16 bien structurÃ©, composants shadcn/ui consistants

### Points Ã  amÃ©liorer ðŸ”§

| # | ProblÃ¨me | Fichier(s) | Action |
| --- | ---------- | ----------- | -------- |
| O1 | **jobs.py monolithique (3500+ lignes)** | `src/services/core/cron/jobs.py` | DÃ©couper en fichiers par domaine: `jobs_cuisine.py`, `jobs_famille.py`, `jobs_maison.py`, etc. |
| O2 | **Routes famille Ã©clatÃ©es** | `src/api/routes/famille*.py` (multiples) | Consolider ou documenter le naming pattern des sous-routes famille |
| O3 | **Scripts legacy non archivÃ©s** | `scripts/` (split_init_sql, split_jeux, rename_factory) | DÃ©placer dans `scripts/_archive/` ou supprimer |
| O4 | **Doubles bibliothÃ¨ques de charts** | `chart.js` + `recharts` | Standardiser sur Recharts (dÃ©jÃ  plus utilisÃ©) et retirer chart.js |
| O5 | **RGPD route non pertinente** | `src/api/routes/rgpd.py` | App familiale privÃ©e â€” simplifier en "Export backup" uniquement (prÃ©fÃ©rence utilisateur) |
| O6 | **RÃ©fÃ©rences croisÃ©es types** | `frontend/src/types/` | Certains types sont dupliquÃ©s entre fichiers â€” centraliser via barrel exports |
| O7 | **DonnÃ©es rÃ©fÃ©rence non versionnÃ©es** | `data/reference/*.json` | Ajouter un numÃ©ro de version dans chaque fichier JSON |
| O8 | **Dossier exports non nettoyÃ©** | `data/exports/` | Pas de politique de rÃ©tention automatique |

---

## 15. AmÃ©liorations UI/UX

### Dashboard principal

| # | AmÃ©lioration | PrioritÃ© | Description |
| --- | ------------- | ---------- | ------------- |
| U1 | **Widgets configurables drag-drop** | ðŸ”´ Haute | Le composant `grille-widgets.tsx` existe mais pas de drag-drop pour rÃ©organiser. ImplÃ©menter avec `@dnd-kit/core` |
| U2 | **Cartes avec micro-animations** | ðŸŸ¡ Moyenne | Ajouter des animations subtiles sur les cartes dashboard (compteurs qui s'incrÃ©mentent, barres de progression animÃ©es) avec Framer Motion |
| U3 | **Mode sombre raffinÃ©** | ðŸŸ¡ Moyenne | Le dark mode fonctionne mais certains composants (charts, calendrier) n'ont pas de palette dÃ©diÃ©e |
| U4 | **Squelettes de chargement cohÃ©rents** | ðŸŸ¡ Moyenne | Les skeleton loaders existent mais ne reflÃ¨tent pas fidÃ¨lement la forme du contenu final |

### Navigation

| # | AmÃ©lioration | PrioritÃ© | Description |
| --- | ------------- | ---------- | ------------- |
| U5 | **Sidebar avec favoris dynamiques** | ðŸŸ¡ Moyenne | Le composant `favoris-rapides.tsx` existe â€” interconnecter avec le store pour pins persistants |
| U6 | **Breadcrumbs interactifs** | ðŸŸ¢ Basse | Les breadcrumbs sont lÃ  mais pas cliquables sur tous les niveaux de navigation |
| U7 | **Transitions de page fluides** | ðŸŸ¡ Moyenne | Pas de transitions entre pages â€” ajouter un fade-in/slide avec `framer-motion` ou les View Transitions API |
| U8 | **Bottom bar mobile enrichie** | ðŸŸ¡ Moyenne | 5 items fixes â€” ajouter un indicateur visuel de la page active + animation |

### Formulaires

| # | AmÃ©lioration | PrioritÃ© | Description |
| --- | ------------- | ---------- | ------------- |
| U9 | **Auto-complÃ©tion intelligente** | ðŸ”´ Haute | Les formulaires d'ajout (recettes, inventaire, courses) devraient proposer auto-complÃ©tion basÃ©e sur l'historique |
| U10 | **Validation inline en temps rÃ©el** | ðŸŸ¡ Moyenne | Les erreurs Zod s'affichent au submit â€” ajouter validation pendant la saisie (onBlur) |
| U11 | **Assistant formulaire IA** | ðŸŸ¡ Moyenne | "Aide-moi Ã  remplir" â€” L'IA prÃ©-remplit les champs basÃ© sur le contexte (ex: recette â†’ prÃ©-remplit les ingrÃ©dients courants) |

### Mobile

| # | AmÃ©lioration | PrioritÃ© | Description |
| --- | ------------- | ---------- | ------------- |
| U12 | **Swipe actions** | ðŸŸ¡ Moyenne | Le composant `swipeable-item.tsx` existe â€” l'appliquer Ã  toutes les listes (courses, tÃ¢ches, recettes) pour supprimer/archiver |
| U13 | **Pull-to-refresh** | ðŸŸ¡ Moyenne | Pattern mobile natif absent â€” TanStack Query le supporte |
| U14 | **Haptic feedback** | ðŸŸ¢ Basse | Vibrations sur les actions importantes (checkout, suppression, validation) via Vibration API |

### Micro-interactions

| # | AmÃ©lioration | PrioritÃ© | Description |
| --- | ------------- | ---------- | ------------- |
| U15 | **Confetti sur accomplissement** | ðŸŸ¢ Basse | Animation confetti quand un planning complet est validÃ©, quand toutes les courses sont cochÃ©es, etc. |
| U16 | **Compteurs animÃ©s dashboard** | ðŸŸ¡ Moyenne | Les chiffres du dashboard s'incrÃ©mentent de 0 Ã  la valeur rÃ©elle Ã  l'affichage |
| U17 | **Toast notifications amÃ©liorÃ©es** | ðŸŸ¡ Moyenne | Utiliser Sonner avec des styles custom: succÃ¨s vert + check animÃ©, erreur rouge + shake |

---

## 16. Visualisations 2D et 3D

### Existant

| Composant | Technologie | Module | Statut |
| ----------- | ------------- | -------- | -------- |
| Plan 3D maison | Three.js / @react-three/fiber | Maison | âš ï¸ Squelette (non connectÃ© aux donnÃ©es) |
| Heatmap numÃ©ros loto | Recharts | Jeux | âœ… Fonctionnel |
| Heatmap cotes paris | Recharts | Jeux | âœ… Fonctionnel |
| Camembert budget | Recharts | Famille | âœ… Fonctionnel |
| Graphique ROI | Recharts | Jeux | âœ… Fonctionnel |
| Graphique jalons Jules | Recharts | Famille | âœ… Fonctionnel |
| Timeline planning | Custom CSS | Planning | âš ï¸ Basique |
| Carte Leaflet (habitat) | react-leaflet | Habitat | âš ï¸ Partiel |

### AmÃ©liorations visualisation proposÃ©es

#### 3D

| # | Visualisation | Module | Technologie | Description |
| --- | --------------- | -------- | ------------- | ------------- |
| V1 | **Plan 3D maison interactif** | Maison | Three.js + @react-three/drei | Connecter le plan 3D aux donnÃ©es rÃ©elles: couleur des piÃ¨ces par nombre de tÃ¢ches en attente, indicateurs Ã©nergie par piÃ¨ce, clic â†’ dÃ©tail des tÃ¢ches de la piÃ¨ce |
| V2 | **Vue jardin 3D/2D** | Maison/Jardin | Three.js ou Canvas 2D | Plan du jardin avec les zones de plantation, Ã©tat des plantes (couleur), calendrier d'arrosage visuel |
| V3 | **Globe 3D voyages** | Voyages | Three.js (globe.gl) | Vue globe avec les destinations passÃ©es et Ã  venir, tracÃ© des itinÃ©raires |

#### 2D â€” Graphiques avancÃ©s

| # | Visualisation | Module | Technologie | Description |
| --- | --------------- | -------- | ------------- | ------------- |
| V4 | **Calendrier nutritionnel heatmap** | Cuisine | D3.js ou Recharts | Grille type GitHub contributions: chaque jour colorÃ© selon le score nutritionnel (rouge â†’ vert) |
| V5 | **Treemap budget** | Famille/Budget | Recharts Treemap | Visualisation proportionnelle des catÃ©gories de dÃ©penses, cliquable pour drill-down |
| V6 | **Sunburst recettes** | Cuisine | D3.js Sunburst | CatÃ©gories â†’ sous-catÃ©gories â†’ recettes, proportionnel au nombre de fois cuisinÃ©es |
| V7 | **Radar skill Jules** | Famille/Jules | Recharts RadarChart | Diagramme araignÃ©e des compÃ©tences de Jules (motricitÃ©, langage, social, cognitif) vs normes OMS |
| V8 | **Sparklines dans les cartes** | Dashboard | Inline SVG / Recharts | Mini graphiques dans les cartes dashboard (tendance 7 jours) pour chaque mÃ©trique |
| V9 | **Graphe rÃ©seau modules** | Admin | D3.js Force Graph ou vis.js | Visualisation interactive des 21 bridges inter-modules: noeuds = modules, liens = bridges, Ã©paisseur = frÃ©quence d'utilisation |
| V10 | **Timeline Gantt entretien** | Maison | Recharts ou dhtmlxGantt | Planification visuelle des tÃ¢ches d'entretien sur l'annÃ©e |
| V11 | **Courbe Ã©nergie N vs N-1** | Maison/Ã‰nergie | Recharts AreaChart | Comparaison consommation Ã©nergie mois par mois vs annÃ©e prÃ©cÃ©dente |
| V12 | **Flux Sankey courses â†’ catÃ©gories** | Courses/Budget | D3.js Sankey | Visualiser le flux de dÃ©penses: fournisseurs â†’ catÃ©gories â†’ sous-catÃ©gories |
| V13 | **Wheel fortune loto** | Jeux | Canvas / CSS animation | Animation roue pour la rÃ©vÃ©lation des numÃ©ros gÃ©nÃ©rÃ©s par l'IA |

---

## 17. Simplification du flux utilisateur

### Principes de design

> L'utilisateur doit pouvoir accomplir ses tÃ¢ches quotidiennes en **3 clics maximum**.
> Les actions frÃ©quentes sont en **premier plan**, les actions rares en **menus secondaires**.
> L'IA fait le travail lourd en **arriÃ¨re-plan**, l'utilisateur **valide**.

### Flux principaux simplifiÃ©s

#### ðŸ½ï¸ Flux cuisine (central)

```
Semaine vide
    â”‚
    â”œâ”€â”€â†’ IA propose un planning â”€â”€â†’ Valider / Modifier / RÃ©gÃ©nÃ©rer
    â”‚                                    â”‚
    â”‚                                    â–¼
    â”‚                            Planning validÃ©
    â”‚                                    â”‚
    â”‚                              â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”
    â”‚                              â”‚            â”‚
    â”‚                    Auto-gÃ©nÃ¨re         Notif WhatsApp
    â”‚                    courses               recap
    â”‚                        â”‚
    â”‚                        â–¼
    â”‚                  Liste courses
    â”‚                  (triÃ©e par rayon)
    â”‚                        â”‚
    â”‚                        â–¼
    â”‚              En magasin: cocher au fur et Ã  mesure
    â”‚                        â”‚
    â”‚                        â–¼
    â”‚              Checkout â†’ transfert automatique inventaire
    â”‚                        â”‚
    â”‚                        â–¼
    â”‚              Score anti-gaspi mis Ã  jour
    â”‚
    â””â”€â”€â†’  Fin de semaine: "Qu'avez-vous vraiment mangÃ© ?" â†’ feedback IA
```

**Actions utilisateur**: 3 (valider planning â†’ cocher courses â†’ checkout)
**Actions IA**: Planning, liste courses, organisation rayons, transfert inventaire

#### ðŸ‘¶ Flux famille quotidien

```
Matin (auto WhatsApp 07h30)
    â”‚
    â”œâ”€â”€ "Bonjour ! Aujourd'hui: repas X, tÃ¢che Y, Jules a Z mois"
    â”‚   â””â”€â”€ Bouton: "OK" ou "Modifier"
    â”‚
    â”œâ”€â”€ Routines Jules (checklist)
    â”‚   â””â”€â”€ Cocher les Ã©tapes faites
    â”‚
    â””â”€â”€ Soir: rÃ©cap auto
        â””â”€â”€ "Aujourd'hui: 3/5 tÃ¢ches, 2 repas ok, Jules: poids notÃ©"
```

**Actions utilisateur**: Cocher les routines, rÃ©pondre OK/Modifier
**Actions IA**: Digest, rappels, scores

#### ðŸ¡ Flux maison

```
Notification push (automatique)
    â”‚
    â”œâ”€â”€ "TÃ¢che entretien Ã  faire: [tÃ¢che] â€” Voir dÃ©tail"
    â”‚   â””â”€â”€ Clic â†’ fiche tÃ¢che avec guide
    â”‚       â””â”€â”€ Marquer "fait" â†’ auto-prochaine date
    â”‚
    â”œâ”€â”€ "Stock produit [X] bas"
    â”‚   â””â”€â”€ Bouton: "Ajouter aux courses"
    â”‚
    â””â”€â”€ Rapport mensuel (1er du mois)
        â””â”€â”€ Email avec rÃ©sumÃ© tÃ¢ches + budget maison
```

**Actions utilisateur**: Marquer fait, ajouter aux courses
**Actions IA**: Rappels, planification, rapport

### Actions rapides (FAB mobile)

Le composant `fab-actions-rapides.tsx` existe â€” le configurer avec:

| Action rapide | Cible | IcÃ´ne |
| -------------- | ------- | ------- |
| + Recette rapide | Formulaire simplifiÃ© (nom + photo) | ðŸ“¸ |
| + Article courses | Ajout vocal ou texte | ðŸ›’ |
| + DÃ©pense | Montant + catÃ©gorie | ðŸ’° |
| + Note | Texte libre | ðŸ“ |
| Scan barcode | Scanner â†’ inventaire ou courses | ðŸ“· |
| Timer cuisine | Minuteur rapide | â±ï¸ |

---

## 18. Axes d'innovation

### Innovations proposÃ©es (au-delÃ  du scope actuel)

| # | Innovation | Modules | Description | Effort | Impact |
| --- | ----------- | --------- | ------------- | -------- | -------- |
| IN1 | **Mode "Pilote automatique"** | Tous | L'IA gÃ¨re le planning, les courses, les rappels sans intervention. L'utilisateur reÃ§oit un rÃ©sumÃ© quotidien et intervient uniquement pour corriger. Bouton ON/OFF dans les paramÃ¨tres | 5j | ðŸ”´ TrÃ¨s Ã©levÃ© |
| IN2 | **Widget tablette Google (Ã©cran d'accueil)** | Dashboard | Widget Android/web widget affichant: repas du jour, prochaine tÃ¢che, mÃ©tÃ©o, timer actif. Compatible avec la tablette Google | 4j | ðŸ”´ Ã‰levÃ© |
| IN3 | **Vue "Ma journÃ©e" unifiÃ©e** | Planning + Cuisine + Famille + Maison | Une seule page "Aujourd'hui" avec tout: repas, tÃ¢ches, routines Jules, mÃ©tÃ©o, anniversaires, timer. Le concentrÃ© de la journÃ©e | 3j | ðŸ”´ TrÃ¨s Ã©levÃ© |
| IN4 | **Suggestions proactives contextuelles** | IA + Tous | BanniÃ¨re en haut de chaque module avec une suggestion IA contextuelle: "Il reste des tomates qui expirent demain â†’ [Voir recettes]", "Budget restaurants atteint 80% â†’ [Voir dÃ©tail]" | 3j | ðŸ”´ Ã‰levÃ© |
| IN5 | **Journal familial automatique** | Famille | L'app gÃ©nÃ¨re automatiquement un journal de la semaine: repas cuisinÃ©s, activitÃ©s faites, jalons Jules, photos uploadÃ©es, mÃ©tÃ©o, dÃ©penses. Exportable en PDF joli | 3j | ðŸŸ¡ Moyen |
| IN6 | **Mode focus/zen** | UI | Le composant `focus/` existe en squelette. ImplÃ©menter un mode "concentration" qui masque tout sauf la tÃ¢che en cours (recette en cuisine, liste de courses en magasin) | 2j | ðŸŸ¡ Moyen |
| IN7 | **Comparateur de prix courses** | Courses + IA | Ã€ partir de la liste de courses, l'IA compare avec les prix rÃ©fÃ©rence (sans OCR tickets) et donne un budget estimÃ© | 3j | ðŸŸ¡ Moyen |
| IN8 | **IntÃ©gration Google Home routines** | Assistant | Routines Google Home: "Bonsoir" â†’ lecture du repas du lendemain + tÃ¢ches demain. Ã‰tendre les intents Google Assistant existants | 4j | ðŸŸ¡ Moyen |
| IN9 | **Seasonal meal prep planner** | Cuisine + IA | Chaque saison, l'IA propose un plan de batch cooking saisonnier avec les produits de saison et les congÃ©lations recommandÃ©es | 2j | ðŸŸ¡ Moyen |
| IN10 | **Score famille hebdomadaire** | Dashboard | Score composite: nutrition + dÃ©penses maÃ®trisÃ©es + activitÃ©s + entretien Ã  jour + bien-Ãªtre. Graphe d'Ã©volution semaine par semaine | 2j | ðŸ”´ Ã‰levÃ© |
| IN11 | **Export rapport mensuel PDF** | Export + IA | Un beau rapport PDF mensuel avec graphiques: budget, nutrition, entretien, Jules, jeux. RÃ©sumÃ© narratif IA | 3j | ðŸŸ¡ Moyen |
| IN12 | **Planning vocal** | Assistant + Planning | "Ok Google, planifie du poulet pour mardi soir" â†’ crÃ©Ã© le repas + vÃ©rifie le stock + ajoute les manquants aux courses | 3j | ðŸŸ¡ Moyen |
| IN13 | **Tableau de bord Ã©nergie** | Maison | Dashboard dÃ©diÃ© Ã©nergie: consommation temps rÃ©el (si compteur Linky connectÃ©), historique, comparaison N-1, prÃ©vision facture, tips IA | 4j | ðŸŸ¡ Moyen |
| IN14 | **Mode "invitÃ©" pour le conjoint** | Auth | Vue simplifiÃ©e pour un 2Ã¨me utilisateur: juste les courses, le planning, les routines. Sans admin ni config | 2j | ðŸ”´ Ã‰levÃ© |

---

## 19. Plan d'action priorisÃ©

### ðŸ”´ Phase A â€” Stabilisation (Semaine 1-2)

> **Objectif**: Corriger les bugs, consolider SQL, couvrir les tests critiques

| # | TÃ¢che | Effort | CatÃ©gorie |
| --- | ------- | -------- | ----------- |
| A1 | Fixer B1 (API_SECRET_KEY multi-process) | 1h | Bug critique |
| A2 | Fixer B2 (WebSocket fallback HTTP polling) | 1j | Bug critique |
| A3 | Fixer B3 (Intercepteur auth promise non gÃ©rÃ©e) | 2h | Bug critique |
| A4 | Fixer B5 (Rate limiting mÃ©moire non bornÃ© â€” ajouter LRU) | 2h | Bug important |
| A5 | Fixer B9 (WhatsApp state persistence â€” Redis/DB) | 1j | Bug important |
| A6 | ExÃ©cuter audit_orm_sql.py et corriger divergences (S2) | 1j | SQL |
| A7 | Consolider migrations dans les fichiers schema (S3) | 1j | SQL |
| A8 | RÃ©gÃ©nÃ©rer INIT_COMPLET.sql propre (S1) | 30min | SQL |
| A9 | Ajouter tests export PDF (T1) | 1j | Tests |
| A10 | Ajouter tests webhooks WhatsApp (T2) | 1j | Tests |
| A11 | Ajouter tests event bus scÃ©narios (T3) | 1j | Tests |
| A12 | Mettre Ã  jour CRON_JOBS.md (D1) | 2h | Doc |
| A13 | Mettre Ã  jour NOTIFICATIONS.md (D2) | 2h | Doc |

### ðŸŸ¡ Phase B â€” FonctionnalitÃ©s & IA (Semaine 3-4)

> **Objectif**: Combler les gaps fonctionnels, enrichir l'IA

| # | TÃ¢che | Effort | CatÃ©gorie |
| --- | ------- | -------- | ----------- |
| B1 | ImplÃ©menter G5 (Mode offline courses) | 3j | Gap |
| B2 | ImplÃ©menter IA1 (PrÃ©diction courses intelligente) | 3j | IA |
| B3 | ImplÃ©menter J2 (Planning auto semaine CRON) | 2j | CRON |
| B4 | ImplÃ©menter J9 (Alertes budget seuil CRON) | 1j | CRON |
| B5 | ImplÃ©menter W2 (Commandes WhatsApp enrichies) | 3j | WhatsApp |
| B6 | ImplÃ©menter I1 (RÃ©colte jardin â†’ Recettes) | 2j | Inter-module |
| B7 | ImplÃ©menter I3 (Budget anomalie â†’ notification) | 2j | Inter-module |
| B8 | ImplÃ©menter I5 (Documents expirÃ©s â†’ Dashboard) | 1j | Inter-module |
| B9 | ImplÃ©menter IA5 (RÃ©sumÃ© hebdo intelligent) | 2j | IA |
| B10 | ImplÃ©menter IA8 (Suggestion batch cooking intelligent) | 3j | IA |
| B11 | Ajouter tests pages famille frontend (T8 Ã©tendu) | 2j | Tests |
| B12 | Ajouter tests E2E parcours utilisateur (T6) | 3j | Tests |

### ðŸŸ¢ Phase C â€” UI/UX & Visualisations (Semaine 5-6)

> **Objectif**: Rendre l'interface belle, moderne, fluide

| # | TÃ¢che | Effort | CatÃ©gorie |
| --- | ------- | -------- | ----------- |
| C1 | ImplÃ©menter U1 (Dashboard widgets drag-drop) | 2j | UI |
| C2 | ImplÃ©menter IN3 (Page "Ma journÃ©e" unifiÃ©e) | 3j | Innovation |
| C3 | ImplÃ©menter V1 (Plan 3D maison interactif connectÃ©) | 5j | 3D |
| C4 | ImplÃ©menter V4 (Calendrier nutritionnel heatmap) | 2j | 2D |
| C5 | ImplÃ©menter V5 (Treemap budget) | 2j | 2D |
| C6 | ImplÃ©menter V7 (Radar skill Jules) | 1j | 2D |
| C7 | ImplÃ©menter V8 (Sparklines dans cartes dashboard) | 1j | 2D |
| C8 | ImplÃ©menter U7 (Transitions de page fluides) | 2j | UI |
| C9 | ImplÃ©menter U12 (Swipe actions listes) | 1j | Mobile |
| C10 | ImplÃ©menter U16 (Compteurs animÃ©s dashboard) | 1j | UI |
| C11 | ImplÃ©menter U9 (Auto-complÃ©tion intelligent formulaires) | 2j | UX |
| C12 | ImplÃ©menter IN4 (Suggestions proactives contextuelles) | 3j | Innovation |

### ðŸ”µ Phase D â€” Admin & Automatisations (Semaine 7-8)

> **Objectif**: Enrichir le mode admin, nouvelles automatisations

| # | TÃ¢che | Effort | CatÃ©gorie |
| --- | ------- | -------- | ----------- |
| D1 | ImplÃ©menter A1 (Console commande rapide admin) | 2j | Admin |
| D2 | ImplÃ©menter A3 (Scheduler visuel CRON) | 3j | Admin |
| D3 | ImplÃ©menter A6 (Logs temps rÃ©el via WebSocket) | 2j | Admin |
| D4 | ImplÃ©menter J1 (CRON prÃ©diction courses hebdo) | 1j | CRON |
| D5 | ImplÃ©menter J4 (Rappels jardin saisonniers) | 1j | CRON |
| D6 | ImplÃ©menter J6 (VÃ©rif santÃ© systÃ¨me horaire) | 1j | CRON |
| D7 | ImplÃ©menter J7 (Backup auto hebdomadaire JSON) | 1j | CRON |
| D8 | ImplÃ©menter W1 (WhatsApp state persistence) | 2j | Notifications |
| D9 | ImplÃ©menter E1 (Templates email HTML/MJML) | 2j | Notifications |
| D10 | DÃ©couper jobs.py en modules (O1) | 1j | Refactoring |
| D11 | Archiver scripts legacy (O3) | 30min | Nettoyage |
| D12 | Standardiser sur Recharts uniquement (O4) | 1j | Nettoyage |

### ðŸŸ£ Phase E â€” Innovations (Semaine 9+)

> **Objectif**: Features diffÃ©renciantes

| # | TÃ¢che | Effort | CatÃ©gorie |
| --- | ------- | -------- | ----------- |
| E1 | ImplÃ©menter IN1 (Mode Pilote automatique) | 5j | Innovation |
| E2 | ImplÃ©menter IN2 (Widget tablette Google) | 4j | Innovation |
| E3 | ImplÃ©menter IN10 (Score famille hebdomadaire) | 2j | Innovation |
| E4 | ImplÃ©menter IN14 (Mode invitÃ© conjoint) | 2j | Innovation |
| E5 | ImplÃ©menter V9 (Graphe rÃ©seau modules admin) | 2j | Visualisation |
| E6 | ImplÃ©menter V10 (Timeline Gantt entretien) | 2j | Visualisation |
| E7 | ImplÃ©menter V2 (Vue jardin 2D/3D) | 3j | Visualisation |
| E8 | ImplÃ©menter IN5 (Journal familial automatique) | 3j | Innovation |
| E9 | ImplÃ©menter IN11 (Rapport mensuel PDF export) | 3j | Innovation |
| E10 | ImplÃ©menter IN8 (Google Home routines Ã©tendues) | 4j | Innovation |
| E11 | ImplÃ©menter G17 (Sync Google Calendar bidirectionnelle) | 4j | Gap |
| E12 | ImplÃ©menter IA4 (Assistant vocal Ã©tendu) | 4j | IA |

---

## Annexe A â€” RÃ©sumÃ© des fichiers clÃ©s

### Backend Python

```
src/
â”œâ”€â”€ api/
â”‚   â”œâ”€â”€ main.py                    # FastAPI app + 7 middlewares + health
â”‚   â”œâ”€â”€ auth.py                    # JWT + 2FA TOTP
â”‚   â”œâ”€â”€ dependencies.py            # require_auth, require_role
â”‚   â”œâ”€â”€ routes/                    # 41 fichiers routeurs (~250 endpoints)
â”‚   â”œâ”€â”€ schemas/                   # 25 fichiers Pydantic (~150 modÃ¨les)
â”‚   â”œâ”€â”€ utils/                     # Exception handler, pagination, metrics, ETag, security
â”‚   â”œâ”€â”€ rate_limiting/             # Multi-strategy (memory/Redis/file)
â”‚   â”œâ”€â”€ websocket_courses.py       # WS collaboration courses
â”‚   â””â”€â”€ websocket/                 # 4 autres WebSockets
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ ai/                        # Mistral client, cache sÃ©mantique, circuit breaker
â”‚   â”œâ”€â”€ caching/                   # L1/L2/L3 + Redis
â”‚   â”œâ”€â”€ config/                    # Pydantic BaseSettings
â”‚   â”œâ”€â”€ db/                        # Engine, sessions, migrations
â”‚   â”œâ”€â”€ decorators/                # @avec_session_db, @avec_cache, @avec_resilience
â”‚   â”œâ”€â”€ models/                    # 32 fichiers ORM (100+ classes)
â”‚   â”œâ”€â”€ resilience/                # Retry + Timeout + CircuitBreaker
â”‚   â””â”€â”€ validation/                # Pydantic schemas + sanitizer
â””â”€â”€ services/
    â”œâ”€â”€ core/
    â”‚   â”œâ”€â”€ base/                  # BaseAIService (4 mixins)
    â”‚   â”œâ”€â”€ cron/                  # 68+ jobs (3500+ lignes)
    â”‚   â”œâ”€â”€ events/                # Pub/Sub event bus
    â”‚   â””â”€â”€ registry.py            # @service_factory singleton
    â”œâ”€â”€ cuisine/                   # RecetteService, ImportService
    â”œâ”€â”€ famille/                   # JulesAI, WeekendAI
    â”œâ”€â”€ maison/                    # MaisonService
    â”œâ”€â”€ jeux/                      # JeuxService
    â”œâ”€â”€ planning/                  # 5 sous-modules
    â”œâ”€â”€ inventaire/                # InventaireService
    â”œâ”€â”€ dashboard/                 # AgrÃ©gation multi-module
    â”œâ”€â”€ integrations/              # Multimodal, webhooks
    â””â”€â”€ utilitaires/               # Automations, divers
```

### Frontend Next.js

```
frontend/src/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ (auth)/                    # Login / Inscription
â”‚   â”œâ”€â”€ (app)/                     # App protÃ©gÃ©e (~60 pages)
â”‚   â”‚   â”œâ”€â”€ page.tsx               # Dashboard
â”‚   â”‚   â”œâ”€â”€ cuisine/               # 12 pages
â”‚   â”‚   â”œâ”€â”€ famille/               # 10 pages
â”‚   â”‚   â”œâ”€â”€ maison/                # 8 pages
â”‚   â”‚   â”œâ”€â”€ jeux/                  # 7 pages
â”‚   â”‚   â”œâ”€â”€ planning/              # 2 pages
â”‚   â”‚   â”œâ”€â”€ outils/                # 6 pages
â”‚   â”‚   â”œâ”€â”€ parametres/            # 3 pages + 7 onglets
â”‚   â”‚   â”œâ”€â”€ admin/                 # 10 pages
â”‚   â”‚   â”œâ”€â”€ habitat/               # 3 pages
â”‚   â”‚   â””â”€â”€ ia-avancee/            # IA avancÃ©e
â”‚   â””â”€â”€ share/                     # Partage public
â”œâ”€â”€ composants/
â”‚   â”œâ”€â”€ ui/                        # 29 shadcn/ui
â”‚   â”œâ”€â”€ disposition/               # 19 layout components
â”‚   â”œâ”€â”€ cuisine/                   # Composants cuisine
â”‚   â”œâ”€â”€ famille/                   # Composants famille
â”‚   â”œâ”€â”€ jeux/                      # Composants jeux (heatmaps, grilles)
â”‚   â”œâ”€â”€ maison/                    # Composants maison (plan 3D, drawers)
â”‚   â”œâ”€â”€ habitat/                   # Composants habitat
â”‚   â”œâ”€â”€ graphiques/                # Charts rÃ©utilisables
â”‚   â””â”€â”€ planning/                  # Timeline, calendrier
â”œâ”€â”€ bibliotheque/
â”‚   â”œâ”€â”€ api/                       # 34 clients API
â”‚   â””â”€â”€ validateurs.ts             # 22 schÃ©mas Zod
â”œâ”€â”€ crochets/                      # 15 hooks custom
â”œâ”€â”€ magasins/                      # 4 stores Zustand
â”œâ”€â”€ types/                         # 15 fichiers TypeScript
â””â”€â”€ fournisseurs/                  # 3 providers React
```

### SQL

```
sql/
â”œâ”€â”€ INIT_COMPLET.sql               # 4922 lignes, source unique (prod)
â”œâ”€â”€ schema/ (18 fichiers)          # Source de vÃ©ritÃ© par domaine
â””â”€â”€ migrations/ (7 fichiers)       # Ã€ consolider dans schema/
```

---

## Annexe B â€” MÃ©triques de santÃ© projet

| Indicateur | Valeur | Cible | Statut |
| ----------- | -------- | ------- | -------- |
| Tests backend | ~55% couverture | â‰¥70% | ðŸŸ¡ |
| Tests frontend | ~40% couverture | â‰¥50% | ðŸ”´ |
| Tests E2E | ~10% | â‰¥30% | ðŸ”´ |
| Docs Ã  jour | ~60% (35/58 fichiers) | â‰¥90% | ðŸŸ¡ |
| SQL ORM sync | Non vÃ©rifiÃ© | 100% | âš ï¸ |
| Endpoints documentÃ©s | ~80% | 100% | ðŸŸ¡ |
| Bridges inter-modules | 21 actifs | 31 possibles | ðŸŸ¡ |
| CRON jobs testÃ©s | ~30% | â‰¥70% | ðŸ”´ |
| Bugs critiques ouverts | 4 | 0 | ðŸ”´ |
| SÃ©curitÃ© (OWASP) | Bon (JWT, sanitize, rate limit) | Complet | ðŸŸ¡ |

---

> **DerniÃ¨re mise Ã  jour**: 1er Avril 2026
> **Prochaine revue prÃ©vue**: AprÃ¨s Phase A (stabilisation)
