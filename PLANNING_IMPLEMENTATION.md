# Planning d'Implementation - Assistant Matanne

> **Date** : 1er avril 2026
> **Source** : ANALYSE_COMPLETE.md - audit exhaustif integral
> **Objectif** : roadmap complete couvrant bugs, gaps, SQL, interactions intra/inter-modules, IA, CRON, notifications, admin, tests, docs, UX, visualisations et innovations.

---

## Navigation rapide

- Section 1 : notation par categorie
- Section 2 : etat des lieux synthetique
- Sections 3 a 7 : phases A a E
- Section 8 : referentiel complet par axe d'analyse
- Section 9 : annexes
- Section 10 : recapitulatif global et metriques de sante

---

## 1. Notation par categorie

> ?valuation au 1er avril 2026 ? bas?e sur l'audit exhaustif

| Cat?gorie | Note | Justification |
| ----------- | ------ | --------------- |
| **Architecture backend** | **9/10** | FastAPI + SQLAlchemy 2.0 + Pydantic v2. Patterns exemplaires : service registry `@service_factory`, event bus pub/sub (21 types, 40+ subscribers), cache multi-niveaux (L1/L2/L3/Redis), r?silience composable (retry, timeout, circuit breaker, bulkhead). 38 routeurs, ~250 endpoints, 7 middlewares. |
| **Architecture frontend** | **8/10** | Next.js 16 App Router, React 19, Zustand 5, TanStack Query v5, ~60+ pages, 208+ composants (29 shadcn/ui), 34 clients API, 15 hooks custom. Points n?gatifs : couverture tests ~40%, doubles biblioth?ques charts (Recharts + Chart.js). |
| **Base de donn?es / SQL** | **8/10** | 80+ tables PostgreSQL, RLS, triggers, vues, 18 fichiers schema ordonn?s. Points n?gatifs : 7 migrations non consolid?es dans les fichiers schema, audit ORM?SQL non ex?cut?, index potentiellement manquants. |
| **Couverture tests backend** | **6.5/10** | 74+ fichiers, ~1000 fonctions test, ~55% couverture estim?e. Bien couvert : routes cuisine, services budget, rate limiting. Faible : export PDF (~30%), webhooks (~25%), event bus (~20%), WebSocket (~25%), int?grations (~20%). |
| **Couverture tests frontend** | **4.5/10** | 71 fichiers tests, ~40% couverture. Bien couvert : pages cuisine, stores Zustand. Faible : pages famille/maison/admin (~30%), API clients (~15%), E2E Playwright (~10%). Seuil Vitest 50% ? non atteint. |
| **Int?gration IA** | **8.5/10** | Client Mistral unifi? + cache s?mantique + circuit breaker. 9 services IA fonctionnels (suggestions, planning, rescue, batch, weekend, bien-?tre, chat, jules, IA avanc?e partielle). 12 nouvelles opportunit?s IA identifi?es. |
| **Syst?me de notifications** | **8/10** | 4 canaux (push VAPID, ntfy.sh, WhatsApp Meta, email Resend), failover intelligent, throttle 2h/type/canal. Points n?gatifs : WhatsApp state non persist? (B9), commandes texte limit?es, pas d'actions dans les push. |
| **Interactions inter-modules** | **8/10** | 21 bridges actifs bien pens?s. 10 nouvelles interactions identifi?es dont 3 haute priorit? (r?colte?recettes, budget?notifications, documents?dashboard). |
| **UX / Flux utilisateur** | **5.5/10** | Pages fonctionnelles mais flux courants en 4-6 clics au lieu de 3 max. Pas de drag-drop planning, pas de mode offline courses, pas d'auto-compl?tion historique, transitions de page absentes. FAB actions rapides et swipe-to-complete existants mais sous-exploit?s. |
| **Visualisations** | **5/10** | Base pr?sente (Recharts heatmaps, camemberts, graphiques ROI, Leaflet cartes). Plan 3D maison (Three.js) non connect? aux donn?es. Manquent : heatmap nutrition, treemap budget, radar Jules, sparklines dashboard, Gantt entretien. |
| **Documentation** | **6/10** | ~60% ? jour (35/58 fichiers estim?s). CRON_JOBS.md, NOTIFICATIONS.md, AUTOMATIONS.md obsol?tes post-phases 8-10. PLANNING_IMPLEMENTATION.md et ROADMAP.md p?rim?s. Docs manquantes : guide CRON complet, guide notifications refonte, guide bridges. |
| **Administration** | **9/10** | Panneau admin tr?s complet : 10 pages frontend, 20+ endpoints, raccourci Ctrl+Shift+A, event bus manuel, feature flags, impersonation, dry-run workflows, IA console, WhatsApp test, export/import config. Am?liorations possibles : console commande rapide, scheduler visuel, replay ?v?nements. |
| **Jobs CRON** | **7.5/10** | 68+ jobs bien structur?s (quotidiens, hebdo, mensuels). Points n?gatifs : fichier `jobs.py` monolithique (3500+ lignes), ~30% test?s, 10 nouveaux jobs propos?s (pr?diction courses, planning auto, alertes budget). |
| **Infrastructure / DevOps** | **7/10** | Docker, Sentry (50%), Prometheus metrics. Points n?gatifs : pas de CI/CD GitHub Actions, pas de monitoring co?t IA, Sentry pas complet. |
| **S?curit?** | **7/10** | JWT + 2FA TOTP, RLS, rate limiting multi-strategy, security headers, sanitization. Points n?gatifs : B1 (API_SECRET_KEY random par process en multi-worker), B7 (X-Forwarded-For spoofable), B10 (CORS vide en prod sans erreur). |
| **Performance & r?silience** | **8.5/10** | Cache multi-niveaux (L1?L2?L3?Redis), middleware ETag, r?silience composable, rate limiting (60 req/min standard, 10 req/min IA). Metrics capped ? 500 endpoints (B8). |
| **Donn?es de r?f?rence** | **9/10** | 14+ fichiers JSON/CSV couvrant nutrition, saisons, entretien, jardin, vaccins, soldes, pannes, lessive, nettoyage, domotique, travaux, plantes, routines. |

### Note globale : **7.5/10**

> Application ambitieuse et impressionnante : ~250 endpoints, 80+ tables SQL, ~60+ pages, 208+ composants, 68+ CRON jobs, 21 bridges inter-modules, 4 canaux de notification, 9+ services IA. Architecture professionnelle avec des patterns bien ma?tris?s. Principales faiblesses : tests (~50% global), UX multi-clics, bugs critiques de production (auth multi-worker, WebSocket sans fallback), et docs partiellement obsol?tes.

---

## 2. ?tat des lieux synth?tique

### Chiffres cl?s

| M?trique | Valeur |
| ---------- | -------- |
| Routes API (endpoints) | ~250+ |
| Routeurs FastAPI | 38 |
| Mod?les SQLAlchemy (ORM) | 100+ (32 fichiers) |
| Sch?mas Pydantic | ~150+ (25 fichiers) |
| Tables SQL | 80+ |
| Pages frontend | ~60+ |
| Composants React | 208+ |
| Clients API frontend | 34 |
| Hooks React custom | 15 |
| Stores Zustand | 4 |
| Sch?mas Zod | 22 |
| Fichiers de tests (backend) | 74+ |
| Fichiers de tests (frontend) | 71 |
| CRON jobs | 68+ |
| Bridges inter-modules | 21 |
| Middlewares | 7 couches |
| WebSockets | 5 impl?mentations |
| Canaux de notification | 4 (push, ntfy, WhatsApp, email) |

### Stack technique

| Couche | Technologie |
| -------- | ------------- |
| Backend | Python 3.13+, FastAPI 0.109, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 16.2.1, React 19, TypeScript 5, Tailwind CSS v4 |
| Base de donn?es | Supabase PostgreSQL, migrations SQL-file |
| IA | Mistral AI (client custom + cache s?mantique + circuit breaker) |
| ?tat frontend | TanStack Query v5, Zustand 5 |
| Charts | Recharts 3.8, Chart.js 4.5 |
| 3D | Three.js 0.183, @react-three/fiber 9.5 |
| Cartes | Leaflet 1.9, react-leaflet 5.0 |
| Tests | pytest + Vitest 4.1 + Testing Library + Playwright |
| Monitoring | Prometheus, Sentry |
| Notifications | ntfy.sh, Web Push VAPID, Meta WhatsApp Cloud, Resend |

### Modules par domaine

| Module | Routes | Services | Bridges | CRON | Tests | Statut |
| -------- | -------- | ---------- | --------- | ------ | ------- | -------- |
| ??? Cuisine/Recettes | 20 | RecetteService, ImportService | 7 | 5 | ? Complet | ? Mature |
| ?? Courses | 20 | CoursesService | 3 | 3 | ? Complet | ? Mature |
| ?? Inventaire | 14 | InventaireService | 4 | 3 | ? Complet | ? Mature |
| ?? Planning | 15 | PlanningService (5 sous-modules) | 5 | 4 | ? Complet | ? Mature |
| ????? Batch Cooking | 8 | BatchCookingService | 1 | 1 | ? OK | ? Stable |
| ?? Anti-Gaspillage | 6 | AntiGaspillageService | 2 | 2 | ? OK | ? Stable |
| ?? Suggestions IA | 4 | BaseAIService | 0 | 0 | ? OK | ? Stable |
| ?? Famille/Jules | 20 | JulesAIService | 7 | 5 | ? Complet | ? Mature |
| ?? Maison | 15+ | MaisonService | 4 | 6 | ? OK | ? Stable |
| ?? Habitat | 10 | HabitatService | 0 | 2 | ?? Partiel | ?? En cours |
| ?? Jeux | 12 | JeuxService | 1 | 3 | ? OK | ? Stable |
| ??? Calendriers | 6 | CalendrierService | 2 | 2 | ?? Partiel | ?? En cours |
| ?? Dashboard | 3 | DashboardService | 0 | 0 | ? OK | ? Stable |
| ?? Documents | 6 | DocumentService | 1 | 1 | ?? Partiel | ?? En cours |
| ?? Utilitaires | 10+ | Notes, Journal, Contacts | 1 | 0 | ?? Partiel | ?? En cours |
| ?? IA Avanc?e | 14 | Multi-service | 0 | 0 | ?? Partiel | ?? En cours |
| ?? Voyages | 8 | VoyageService | 2 | 1 | ?? Partiel | ?? En cours |
| ? Garmin | 5 | GarminService | 1 | 1 | ?? Minimal | ?? En cours |
| ?? Auth / Admin | 15+ | AuthService | 0 | 0 | ? OK | ? Stable |
| ?? Export PDF | 3 | RapportService | 0 | 0 | ?? Partiel | ?? En cours |
| ?? Push / Webhooks | 8 | NotificationService | 0 | 5 | ?? Partiel | ?? En cours |
| ?? Automations | 6 | AutomationsEngine | 0 | 1 | ?? Partiel | ?? En cours |

### Frontend ? Pages par module

| Module | Pages | Composants | Tests | Statut |
| -------- | ------- | ------------ | ------- | -------- |
| ??? Cuisine | 12 | ~20 | ? 8 fichiers | ? Mature |
| ?? Famille | 10 | ~8 | ?? 3 fichiers | ?? Gaps |
| ?? Maison | 8 | ~15 | ?? 2 fichiers | ?? Gaps |
| ?? Habitat | 3 | ~6 | ?? 1 fichier | ?? Gaps |
| ?? Jeux | 7 | ~12 | ? 5 fichiers | ? OK |
| ?? Planning | 2 | ~3 | ? 2 fichiers | ? OK |
| ?? Outils | 6 | ~5 | ? 6 fichiers | ? OK |
| ?? Param?tres | 3 + 7 onglets | ~7 | ?? 1 fichier | ?? Gaps |
| ?? Admin | 10 | ~5 | ?? 2 fichiers | ?? Gaps |

---

## 3. Phase A ? Stabilisation ? TERMIN?E

> **Objectif** : Corriger les bugs critiques/importants, consolider SQL, couvrir les tests critiques, mettre ? jour la doc obsol?te
> **Semaines** : 1-2
> **Priorit?** : ?? BLOQUANT
> **Statut** : ? **Termin?e** ? 16/16 t?ches compl?t?es

| # | T?che | Source | Effort | Cat?gorie | Statut |
| --- | ------- | -------- | -------- | ----------- | -------- |
| A1 | Fixer B1 ? API_SECRET_KEY random par process (tokens invalides en multi-worker) | ?3 Bug critique | 1h | S?curit? | ? |
| A2 | Fixer B2 ? WebSocket courses sans fallback HTTP polling | ?3 Bug critique | 1j | R?silience | ? |
| A3 | Fixer B3 ? Intercepteur auth promise non g?r?e (token expir? ? utilisateur bloqu?) | ?3 Bug critique | 2h | Frontend | ? |
| A4 | Fixer B4 ? Event bus en m?moire uniquement (historique perdu au restart) | ?3 Bug critique | 1j | Core | ? |
| A5 | Fixer B5 ? Rate limiting m?moire non born? (fuite m?moire lente) ? LRU | ?3 Bug important | 2h | Perf | ? |
| A6 | Fixer B7 ? X-Forwarded-For spoofable (bypass rate limiting) | ?3 Bug important | 2h | S?curit? | ? |
| A7 | Fixer B9 ? WhatsApp state non persist? (conversation cass?e) ? DB | ?3 Bug important | 1j | WhatsApp | ? |
| A8 | Fixer B10 ? CORS vide en production sans erreur explicite | ?3 Bug important | 1h | Config | ? |
| A9 | Ex?cuter audit_orm_sql.py et corriger divergences ORM?SQL (S2) | ?5 SQL | 1j | SQL | ? |
| A10 | Consolider migrations V003-V008 dans les fichiers schema (S3) | ?5 SQL | 1j | SQL | ? |
| A11 | R?g?n?rer INIT_COMPLET.sql propre (S1) | ?5 SQL | 30min | SQL | ? |
| A12 | Tests export PDF (T1) | ?12 Tests | 1j | Tests | ? |
| A13 | Tests webhooks WhatsApp (T2) | ?12 Tests | 1j | Tests | ? |
| A14 | Tests event bus sc?narios (T3) | ?12 Tests | 1j | Tests | ? |
| A15 | Mettre ? jour CRON_JOBS.md ? 68+ jobs ? documenter (D1) | ?13 Doc | 2h | Doc | ? |
| A16 | Mettre ? jour NOTIFICATIONS.md ? syst?me refait en phase 8 (D2) | ?13 Doc | 2h | Doc | ? |

**Total Phase A : 16/16 t?ches ?**

---

## 4. Phase B ? Fonctionnalit?s & IA ? TERMIN?E

> **Objectif** : Combler les gaps fonctionnels, enrichir l'IA, ajouter les CRON et inter-modules critiques
> **Semaines** : 3-4
> **Priorit?** : ?? HAUTE
> **Statut** : ? **Termin?e** ? 13/13 t?ches compl?t?es

| # | T?che | Source | Effort | Cat?gorie | Statut |
| --- | ------- | -------- | -------- | ----------- | -------- |
| B1 | G5 ? Mode hors-ligne courses (PWA cache offline en magasin) | ?4 Gap | 3j | PWA | ? |
| B2 | IA1 ? Pr?diction courses intelligente (historique ? pr?-remplir liste) | ?8 IA | 3j | IA | ? |
| B3 | J2 ? CRON planning auto semaine (dimanche 19h si planning vide) | ?9 CRON | 2j | CRON | ? |
| B4 | J9 ? CRON alertes budget seuil (quotidien 20h, cat?gorie > 80%) | ?9 CRON | 1j | CRON | ? |
| B5 | W2 ? Commandes WhatsApp enrichies ("ajoute du lait", "budget ce mois") via Mistral NLP | ?10 WhatsApp | 3j | WhatsApp | ? |
| B6 | I1 ? Bridge r?colte jardin ? recettes semaine suivante | ?7 Inter-module | 2j | Bridge | ? |
| B7 | I3 ? Bridge budget anomalie ? notification proactive (+30% restaurants) | ?7 Inter-module | 2j | Bridge | ? |
| B8 | I5 ? Bridge documents expir?s ? dashboard alerte widget | ?7 Inter-module | 1j | Bridge | ? |
| B9 | IA5 ? R?sum? hebdomadaire IA intelligent (narratif : repas, t?ches, budget, scores) | ?8 IA | 2j | IA | ? |
| B10 | IA8 ? Suggestion batch cooking intelligent (planning + appareils ? timeline optimale) | ?8 IA | 3j | IA | ? |
| B11 | G20 ? Recherche globale compl?te (Ctrl+K ? couvrir notes, jardin, contrats) | ?4 Gap | 3j | Frontend | ? |
| B12 | Tests pages famille frontend (T8 ?tendu) | ?12 Tests | 2j | Tests | ? |
| B13 | Tests E2E parcours utilisateur complet (T6) | ?12 Tests | 3j | Tests | ? |

**Total Phase B : 13/13 t?ches ?**

---

## 5. Phase C ? UI/UX & Visualisations

> **Objectif** : Rendre l'interface belle, moderne, fluide. Enrichir les visualisations de donn?es
> **Semaines** : 5-6
> **Priorit?** : ?? MOYENNE-HAUTE

| # | T?che | Source | Effort | Cat?gorie |
| --- | ------- | -------- | -------- | ----------- |
| C1 | U1 ? Dashboard widgets drag-drop (`@dnd-kit/core`) | ?15 UI | 2j | UI |
| C2 | IN3 ? Page "Ma journ?e" unifi?e (repas + t?ches + routines + m?t?o + anniversaires) | ?18 Innovation | 3j | Innovation |
| C3 | V1 ? Plan 3D maison interactif (connecter aux donn?es r?elles : t?ches par pi?ce, ?nergie) | ?16 3D | 5j | 3D |
| C4 | V4 ? Calendrier nutritionnel heatmap (type GitHub contributions, rouge ? vert) | ?16 2D | 2j | 2D |
| C5 | V5 ? Treemap budget (proportionnel, cliquable drill-down) | ?16 2D | 2j | 2D |
| C6 | V7 ? Radar skill Jules (motricit?, langage, social, cognitif vs normes OMS) | ?16 2D | 1j | 2D |
| C7 | V8 ? Sparklines dans cartes dashboard (tendance 7 jours) | ?16 2D | 1j | 2D |
| C8 | U7 ? Transitions de page fluides (framer-motion ou View Transitions API) | ?15 UI | 2j | UI |
| C9 | U12 ? Swipe actions sur toutes les listes (courses, t?ches, recettes) | ?15 Mobile | 1j | Mobile |
| C10 | U16 ? Compteurs anim?s dashboard (incr?mentation visuelle) | ?15 UI | 1j | UI |
| C11 | U9 ? Auto-compl?tion intelligente formulaires (bas?e sur historique) | ?15 UX | 2j | UX |
| C12 | IN4 ? Suggestions proactives contextuelles (banni?re IA en haut de chaque module) | ?18 Innovation | 3j | Innovation |

### Total Phase C : 12 taches

### Statut implementation Phase C (2026-04-01)

| Tache | Statut | Notes implementation |
| --- | --- | --- |
| C1 | Fait | Ajout de `@dnd-kit` + composant drag/drop dashboard (`grille-dashboard-dnd.tsx`) et persistence de l'ordre. |
| C2 | Fait | Nouvelle page unifiee `frontend/src/app/(app)/ma-journee/page.tsx` + lien sidebar. |
| C3 | Fait | `plan-3d.tsx` connecte aux donnees reelles (taches/energie/alertes par piece) via badges et tooltip. |
| C4 | Fait | Heatmap nutritionnelle GitHub-like ajoutee sur `cuisine/nutrition`. |
| C5 | Fait | Treemap budget cliquable avec drill-down ajoutee sur `maison/finances`. |
| C6 | Fait | Radar skills Jules vs reference OMS ajoute sur `famille/jules`. |
| C7 | Fait | Composant sparkline cree et integre dans les cartes metriques dashboard. |
| C8 | Fait | Transitions pages fluides via `framer-motion` dans `contenu-principal.tsx`. |
| C9 | Fait | Swipe actions deployees sur listes cles : dashboard taches, finances depenses, nutrition jours, recettes (planifier/deplanifier). |
| C10 | Fait | Compteurs animes dashboard via `CompteurAnime`. |
| C11 | Fait | Auto-completion intelligente integree au composant reutilisable `DialogueFormulaire` + formulaires Jules/finances. |
| C12 | Fait | Bandeau proactif global ajoute dans la coquille app (`BandeauSuggestionProactive`). |

**Synthese Phase C**: 12 taches faites.

---

## 6. Phase D ? Admin & Automatisations

> **Objectif** : Enrichir le mode admin, ajouter les CRON manquants, am?liorer les notifications
> **Semaines** : 7-8
> **Priorit?** : ?? MOYENNE

| # | T?che | Source | Effort | Cat?gorie |
| --- | ------- | -------- | -------- | ----------- |
| D1 | A1 ? Console commande rapide admin (champ texte : "run job X", "clear cache Y") | ?11 Admin | 2j | Admin |
| D2 | A3 ? Scheduler visuel CRON (timeline 68 jobs, prochain run, d?pendances) | ?11 Admin | 3j | Admin |
| D3 | A6 ? Logs temps r?el via WebSocket admin_logs (endpoint existant ? connecter UI) | ?11 Admin | 2j | Admin |
| D4 | J1 ? CRON pr?diction courses hebdo (vendredi 16h) | ?9 CRON | 1j | CRON |
| D5 | J4 ? CRON rappels jardin saisonniers (hebdo lundi) | ?9 CRON | 1j | CRON |
| D6 | J6 ? CRON v?rification sant? syst?me (horaire ? alerte ntfy si service down) | ?9 CRON | 1j | CRON |
| D7 | J7 ? CRON backup auto hebdo JSON (dimanche 04h) | ?9 CRON | 1j | CRON |
| D8 | W1 ? WhatsApp state persistence (Redis/DB pour multi-turn) | ?10 WhatsApp | 2j | Notifications |
| D9 | E1 ? Templates email HTML/MJML pour rapports mensuels | ?10 Email | 2j | Notifications |
| D10 | O1 ? D?couper jobs.py monolithique (3500+ lignes) en modules par domaine | ?14 Refactoring | 1j | Nettoyage |
| D11 | O3 ? Archiver scripts legacy dans `scripts/_archive/` | ?14 Refactoring | 30min | Nettoyage |
| D12 | O4 ? Standardiser sur Recharts, retirer Chart.js | ?14 Refactoring | 1j | Nettoyage |

### Total Phase D : 12 taches

### Statut d'avancement Phase D (mise a jour: 2026-04-01)

| Tache | Statut | Note |
| --- | --- | --- |
| D1 | Fait | Console commande rapide admin (`/api/v1/admin/quick-command` + page admin console) |
| D2 | Fait | Scheduler visuel CRON (page admin d├®di├®e avec filtres, cat├®gories, prochain run) |
| D3 | Fait | Logs temps r├®el WebSocket connect├®s au frontend (`/api/v1/ws/admin/logs`, `/api/v1/ws/admin/metrics`) |
| D4 | Fait | Job prediction courses hebdo planifi├® vendredi 16h |
| D5 | Fait | Job rappels jardin saisonniers hebdo (lundi 07h) |
| D6 | Fait | Job v├®rification sant├® syst├¿me horaire + alerte ntfy admin |
| D7 | Fait | Job backup auto hebdo JSON (dimanche 04h, rotation des backups) |
| D8 | Fait | Persistance ├®tat conversation WhatsApp multi-turn en DB (`etats_persistants`) |
| D9 | Fait | Template email MJML rapport mensuel + fallback HTML |
| D10 | Fait | D├®but de d├®coupage du monolithe `jobs.py` (modules `jobs_schedule.py`, `jobs_phase_d.py`) |
| D11 | Fait | Scripts legacy archiv├®s dans `scripts/_archive/` |
| D12 | Fait | Standardisation Recharts (suppression d├®pendances Chart.js inutilis├®es) |

---

## 7. Phase E ? Innovations

> **Objectif** : Features diff?renciantes et visionnaires
> **Semaines** : 9+
> **Priorit?** : ?? BASSE

| # | T?che | Source | Effort | Cat?gorie | Status |
| --- | ------- | -------- | -------- | ----------- | ------ |
| E1 | IN1 ? Mode "Pilote automatique" (IA g?re planning/courses/rappels, utilisateur valide) | ?18 Innovation | 5j | Innovation | **Fait** |
| E2 | IN2 ? Widget tablette Google (repas du jour, t?che, m?t?o, timer) | ?18 Innovation | 4j | Innovation | **Fait** |
| E3 | IN10 ? Score famille hebdomadaire composite (nutrition + d?penses + activit?s + entretien) | ?18 Innovation | 2j | Innovation | **Fait** |
| E4 | IN14 ? Mode "invit?" conjoint (vue simplifi?e : courses, planning, routines) | ?18 Innovation | 2j | Innovation | **Fait** |
| E5 | V9 ? Graphe r?seau modules admin (D3.js force graph, 21 bridges visuels) | ?16 3D | 2j | Visualisation | **Fait** |
| E6 | V10 ? Timeline Gantt entretien maison (Recharts, planification annuelle) | ?16 2D | 2j | Visualisation | **Fait** |
| E7 | V2 ? Vue jardin 2D/3D (zones plantation, ?tat plantes, calendrier arrosage) | ?16 3D | 3j | Visualisation | **Fait** |
| E8 | IN5 ? Journal familial automatique (IA g?n?re r?sum? semaine exportable PDF) | ?18 Innovation | 3j | Innovation | **Fait** |
| E9 | IN11 ? Rapport mensuel PDF export (graphiques + r?sum? narratif IA) | ?18 Innovation | 3j | Innovation | **Fait** |
| E10 | IN8 ? Google Home routines ?tendues ("Bonsoir" ? repas demain + t?ches) | ?18 Innovation | 4j | Innovation | **Fait** |
| E11 | G17 ? Sync Google Calendar bidirectionnelle compl?te | ?4 Gap | 4j | Gap | **Fait** |
| E12 | IA4 ? Assistant vocal ?tendu (intents Google Assistant enrichis) | ?8 IA | 4j | IA | **Fait** |

### Total Phase E : 12 taches

---

## 8. R?f?rentiel complet par section d'analyse

### 8.1 Bugs et probl?mes d?tect?s (analyse ?3)

#### ?? Critiques (4)

| # | Bug | Module | Impact | Phase |
| --- | ----- | -------- | -------- | ------- |
| B1 | **API_SECRET_KEY random par process** ? chaque worker g?n?re un secret diff?rent ? tokens invalides en multi-worker | Auth | Tokens invalides en prod | A1 |
| B2 | **WebSocket courses sans fallback HTTP** ? proxy restrictif/3G ? collaboration casse silencieusement | Courses | Perte de sync temps r?el | A2 |
| B3 | **Promesse non g?r?e intercepteur auth** ? refresh token timeout ? utilisateur ni connect? ni d?connect? | Frontend Auth | UX d?grad?e | A3 |
| B4 | **Event bus en m?moire uniquement** ? historique perdu au red?marrage, impossible de rejouer | Core Events | Perte audit trail | A4 |

#### ?? Importants (6)

| # | Bug | Module | Impact | Phase |
| --- | ----- | -------- | -------- | ------- |
| B5 | **Rate limiting m?moire non born?** ? chaque IP/user unique sans ?viction ? fuite m?moire | Rate Limiting | Memory leak prod | A5 |
| B6 | **Maintenance mode cache 5s** ? requ?tes accept?es pendant la transition | Admin | Requ?tes pendant maintenance | Fait (cache court 1s) |
| B7 | **X-Forwarded-For spoofable** ? bypass rate limiting | S?curit? | Rate limiting contournable | A6 |
| B8 | **Metrics capped 500 endpoints / 1000 samples** ? percentiles impr?cis | Monitoring | M?triques d?grad?es | Fait (historique 2000 points) |
| B9 | **WhatsApp multi-turn sans persistence** ? state machine perd ?tat entre messages | WhatsApp | Conversation cass?e | A7 |
| B10 | **CORS vide en production** ? frontend bloqu? sans config explicite | Config | Frontend bloqu? | A8 |

#### ?? Mineurs (4)

| # | Bug | Module | Phase |
| --- | ----- | -------- | ------- |
| B11 | ResponseValidationError logg? en 500 sans contexte debug | API | Backlog |
| B12 | Pagination cursor ? suppressions concurrentes sautent des enregistrements | Pagination | **Fait** ✅ |
| B13 | ServiceMeta auto-sync wrappers non test?e exhaustivement | Core | **Fait** ✅ |
| B14 | Sentry int?gration ? 50% ? erreurs frontend non trac?es | Frontend | B (si temps) |

---

### 8.2 Gaps et fonctionnalit?s manquantes (analyse ?4)

#### ??? Cuisine (5 gaps)

| # | Gap | Priorit? | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G1 | **Drag-drop recettes dans planning** ? UX fastidieuse sans | Moyenne | 2j | C |
| G2 | **Import recettes par photo** ? Pixtral disponible c?t? IA | Moyenne | 3j | B/C |
| G3 | **Partage recette via WhatsApp** avec preview | Basse | 1j | D |
| G4 | **Veille prix articles d?sir?s** ? scraper API Dealabs/Idealo + alertes soldes via `calendrier_soldes.json` | Moyenne | 3j | E |
| G5 | **Mode hors-ligne courses** ? PWA sans cache offline en magasin | Haute | 3j | B1 |

#### ?? Famille (4 gaps)

| # | Gap | Priorit? | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G6 | **Pr?vision budget IA** ? pas de pr?diction "fin de mois" | Haute | 3j | B |
| G7 | **Timeline Jules visuelle** ? frise chronologique interactive des jalons | Moyenne | 2j | C |
| G8 | **Export calendrier anniversaires** vers Google Calendar | Basse | 1j | E |
| G9 | **Photos souvenirs li?es aux activit?s** ? upload photo pour le journal | Moyenne | 2j | D |

#### ?? Maison (4 gaps)

| # | Gap | Priorit? | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G10 | **Plan 3D interactif limit?** ? Three.js non connect? aux donn?es r?elles | Haute | 5j | C3 |
| G11 | **Historique ?nergie avec graphes** ? pas de courbes mois/ann?e | Moyenne | 2j | C |
| G12 | **Catalogue artisans enrichi** ? pas d'avis/notes, pas de recherche par m?tier | Basse | 2j | E |
| G13 | **Devis comparatif** ? pas de visualisation comparative devis pour un projet | Moyenne | 3j | E |

#### ?? Jeux (3 gaps)

| # | Gap | Priorit? | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G14 | **Graphique ROI temporel** ? pas de courbe ?volution mensuelle ROI | Haute | 2j | C |
| G15 | **Alertes cotes temps r?el** ? alerte quand cote atteint seuil d?fini | Moyenne | 3j | D |
| G16 | **Comparaison strat?gies loto** ? backtest c?te ? c?te 2+ strat?gies | Basse | 2j | E |

#### ?? Planning (3 gaps)

| # | Gap | Priorit? | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G17 | **Sync Google Calendar bidirectionnelle** ? export iCal existe, sync ~60% | Haute | 4j | E11 |
| G18 | **Planning familial consolid? visuel** ? pas de Gantt repas + activit?s + entretien | Moyenne | 3j | C |
| G19 | **R?currence d'?v?nements** ? pas de "tous les mardis" natif | Moyenne | 2j | D |

#### ?? G?n?ral (4 gaps)

| # | Gap | Priorit? | Effort | Phase |
| --- | ----- | ---------- | -------- | ------- |
| G20 | **Recherche globale incompl?te** ? Ctrl+K manque notes, jardin, contrats | Haute | 3j | B11 |
| G21 | **Mode hors-ligne PWA** ? Service Worker enregistr? mais pas de strat?gie structur?e | Haute | 5j | B/E |
| G22 | **Onboarding interactif** ? composant tour-onboarding existe mais pas activ? | Moyenne | 3j | D |
| G23 | **Export donn?es backup incomplet** ? export JSON OK, import/restauration UI incomplet | Moyenne | 2j | D |

---

### 8.3 Consolidation SQL (analyse ?5)

#### Structure actuelle

```text
sql/
+-- INIT_COMPLET.sql          # Auto-g?n?r? (4922 lignes, 18 fichiers)
+-- schema/                   # 18 fichiers ordonn?s (01_extensions ? 99_footer)
+-- migrations/               # 7 fichiers (V003-V008) + README
```

#### Actions

| # | Action | Priorit? | Phase |
| --- | -------- | ---------- | ------- |
| S1 | R?g?n?rer INIT_COMPLET.sql (`python scripts/db/regenerate_init.py`) | Haute | A11 |
| S2 | Audit ORM?SQL (`python scripts/audit_orm_sql.py`) et corriger divergences | Haute | A9 |
| S3 | Consolider 7 migrations dans les fichiers schema ? source unique | Haute | A10 |
| S4 | V?rifier index manquants (user_id, date, statut) dans `14_indexes.sql` | Moyenne | B |
| S5 | Nettoyer tables inutilis?es (80+ tables toutes ont ORM + route ?) | Basse | E |
| S6 | V?rifier vues SQL (`17_views.sql`) r?ellement utilis?es par le backend | Basse | E |

#### Workflow simplifi? cible

```text
1. Modifier le fichier schema appropri? (ex: sql/schema/04_cuisine.sql)
2. Ex?cuter: python scripts/db/regenerate_init.py
3. Appliquer: INIT_COMPLET.sql sur Supabase (SQL Editor)
4. V?rifier: python scripts/audit_orm_sql.py
```

---

### 8.4 Interactions intra-modules (analyse ?6)

#### Cuisine (interne) ? ? Bien connect?

```text
Recettes ---- planifi?es ---? Planning
    ?                            ?
    ?                            +-- g?n?re --? Courses
    ?                            ?
    +-- version Jules --? portions adapt?es
                                 ?
Inventaire ?------ checkout ----+
    ?
    +-- p?remption --? Anti-Gaspillage --? Recettes rescue
    ?
    +-- stock bas --? Automation --? Courses auto

Batch Cooking ?-- planning semaine -- pr?pare --? bloque planning
```

**? am?liorer :**

| # | Am?lioration | Phase |
| --- | ------------- | ------- |
| IM-C1 | Checkout courses ? MAJ prix moyens inventaire automatiquement | D |
| IM-C2 | Batch cooking "mode robot" ? optimiser ordre ?tapes par appareil | E |

#### Famille (interne) ? ?? Am?liorable

```text
Jules profil --? jalons developpement --? notifications jalon
Budget ?---- d?penses cat?goris?es
Routines --? check quotidien --? gamification
Anniversaires --? checklist --? budget cadeau
Documents --? expiration --? rappels calendrier
```

**? am?liorer :**

| # | Am?lioration | Phase |
| --- | ------------- | ------- |
| IM-F1 | Jules jalons ? suggestions activit?s adapt?es ?ge (IA contextuelle) | B |
| IM-F2 | Budget anomalies ? notification proactive ("tu d?penses +30% en X") | B7 |
| IM-F3 | Routines ? tracking compl?tion visuel (streak) | C |

#### Maison (interne) ? ?? Am?liorable

```text
Projets --? t?ches --? devis --? d?penses
Entretien --? calendrier --? produits n?cessaires
Jardin --? arrosage/r?colte --? saison
?nergie --? relev?s compteurs --? historique
Stocks (cellier) --? consolid? avec inventaire cuisine
```

**? am?liorer :**

| # | Am?lioration | Phase |
| --- | ------------- | ------- |
| IM-M1 | Projets ? timeline Gantt visuelle des travaux | C/E6 |
| IM-M2 | ?nergie ? graphe ?volution + comparaison N vs N-1 | C (V11) |
| IM-M3 | Entretien ? suggestions IA proactives ("chaudi?re 8 ans ? r?vision") | D |

---

### 8.5 Interactions inter-modules (analyse ?7)

#### 21 bridges existants ?

```text
+----------+     +-----------+     +----------+
? CUISINE  ??---?? PLANNING  ??---?? COURSES  ?
? recettes ?     ? repas     ?     ? listes   ?
? inventaire?    ? semaine   ?     ? articles ?
? nutrition ?    ? conflits  ?     ?          ?
? batch     ?    ?           ?     ?          ?
+----------+     +-----------+     +----------+
     ?                 ?                 ?
     ?    +------------?                 ?
     ?    ?            ?                 ?
+----?----?--+   +----?-----+     +----?-----+
?  FAMILLE   ?   ?  MAISON  ?     ?  BUDGET  ?
? jules      ?   ? entretien?     ? famille  ?
? routines   ?   ? jardin   ?     ? jeux (s?par?)
? annivers.  ?   ? ?nergie  ?     ? maison   ?
+------------+   +----------+     +----------+
     ?                ?
     ?    +-----------?
+----?----?--+   +---?------+
? CALENDRIER ?   ?  JEUX    ?
? google cal ?   ? paris    ?
? ?v?nements ?   ? loto     ?
+------------+   +----------+
```

| # | Bridge | De ? Vers | ?tat |
| --- | -------- | ----------- | ------ |
| 1 | `inter_module_inventaire_planning` | Stock ? Planning | ? |
| 2 | `inter_module_jules_nutrition` | Jules ? Recettes | ? |
| 3 | `inter_module_saison_menu` | Saison ? Planning | ? |
| 4 | `inter_module_courses_budget` | Courses ? Budget | ? |
| 5 | `inter_module_batch_inventaire` | Batch ? Inventaire | ? |
| 6 | `inter_module_planning_voyage` | Voyage ? Planning | ? |
| 7 | `inter_module_peremption_recettes` | P?remption ? Recettes | ? |
| 8 | `inter_module_documents_calendrier` | Documents ? Calendrier | ? |
| 9 | `inter_module_meteo_activites` | M?t?o ? Activit?s | ? |
| 10 | `inter_module_weekend_courses` | Weekend ? Courses | ? |
| 11 | `inter_module_voyages_budget` | Voyages ? Budget | ? |
| 12 | `inter_module_anniversaires_budget` | Anniversaires ? Budget | ? |
| 13 | `inter_module_budget_jeux` | Jeux ? Budget | ? (info seulement, budgets s?par?s) |
| 14 | `inter_module_garmin_health` | Garmin ? Dashboard | ? |
| 15 | `inter_module_entretien_courses` | Entretien ? Courses | ? |
| 16 | `inter_module_jardin_entretien` | Jardin ? Entretien | ? |
| 17 | `inter_module_charges_energie` | Charges ? ?nergie | ? |
| 18 | `inter_module_energie_cuisine` | ?nergie ? Cuisine | ? |
| 19 | `inter_module_chat_contexte` | Tous ? Chat IA | ? |
| 20 | `inter_module_voyages_calendrier` | Voyages ? Calendrier | ? |
| 21 | `inter_module_garmin_planning` | Garmin ? Planning | ?? Partiel |

#### 10 nouvelles interactions ? impl?menter

| # | Interaction | De ? Vers | Valeur | Effort | Phase |
| --- | ------------ | ----------- | -------- | -------- | ------- |
| I1 | **R?colte jardin ? Recettes semaine suivante** | Jardin ? Planning | ? Accept?e | 2j | B6 |
| I2 | **Entretien r?current ? Planning unifi?** | Entretien ? Planning | Haute | 2j | D |
| I3 | **Budget anomalie ? Notification proactive** | Budget ? Notifs | Haute | 2j | B7 |
| I4 | **Voyages ? Inventaire** (d?stockage avant d?part) | Voyages ? Inventaire | Moyenne | 1j | D |
| I5 | **Documents expir?s ? Dashboard alerte** | Documents ? Dashboard | Haute | 1j | B8 |
| I6 | **Anniversaire proche ? Suggestions cadeaux IA** | Anniversaires ? IA | Moyenne | 2j | E |
| I7 | **Contrats/Garanties ? Dashboard widgets** | Maison ? Dashboard | Moyenne | 1j | D |
| I8 | **M?t?o ? Entretien maison** (gel ? penser au jardin) | M?t?o ? Maison | Moyenne | 2j | D |
| I9 | **Planning sport Garmin ? Planning repas** (adapter alimentation) | Garmin ? Cuisine | Moyenne | 3j | E |
| I10 | **Courses historique ? Pr?diction prochaine liste** | Courses ? IA | Haute | 3j | B2 |

---

### 8.6 Opportunit?s IA (analyse ?8)

#### IA d?j? en place (9 fonctionnels)

| Fonctionnalit? | Service | Module | Statut |
| ---------------- | --------- | -------- | -------- |
| Suggestions recettes | BaseAIService | Cuisine | ? |
| G?n?ration planning IA | PlanningService | Planning | ? |
| Recettes rescue anti-gaspi | AntiGaspillageService | Cuisine | ? |
| Batch cooking optimis? | BatchCookingService | Cuisine | ? |
| Suggestions weekend | WeekendAIService | Famille | ? |
| Score bien-?tre | DashboardService | Dashboard | ? |
| Chat IA contextualis? | AssistantService | Outils | ? |
| Version Jules recettes | JulesAIService | Famille | ? |
| 14 endpoints IA avanc?e | Multi-services | IA Avanc?e | ?? Partiel |

#### 12 nouvelles opportunit?s

| # | Opportunit? | Module(s) | Priorit? | Effort | Phase |
| --- | ------------- | ----------- | ---------- | -------- | ------- |
| IA1 | **Pr?diction courses intelligente** ? historique ? pr?-remplir liste | Courses + IA | ?? | 3j | B2 |
| IA2 | **Planificateur adaptatif** m?t?o+stock+budget ? endpoint sous-utilis? | Planning + Multi | ?? | 2j | B |
| IA3 | **Diagnostic pannes maison** ? photo Pixtral ? diagnostic + action | Maison | ?? | 3j | D |
| IA4 | **Assistant vocal contextuel ?tendu** ? Google Assistant intents enrichis | Tous | ?? | 4j | E12 |
| IA5 | **R?sum? hebdomadaire intelligent** ? narratif agr?able ? lire | Dashboard | ?? | 2j | B9 |
| IA6 | **Optimisation ?nergie pr?dictive** ? relev?s + m?t?o ? pr?diction facture | Maison/?nergie | ?? | 3j | E |
| IA7 | **Analyse nutritionnelle photo** ? Pixtral ? calories/macros estim?s | Cuisine | ?? | 3j | E |
| IA8 | **Suggestion batch cooking intelligent** ? planning + appareils ? timeline | Batch Cooking | ?? | 3j | B10 |
| IA9 | **Jules conseil d?veloppement proactif** ? suggestions ?ge + jalons | Famille/Jules | ?? | 2j | D |
| IA10 | **Auto-cat?gorisation budget** ? commer?ant/article ? cat?gorie (pas OCR) | Budget | ?? | 2j | D |
| IA11 | **G?n?ration checklist voyage** ? destination + dates ? checklist IA | Voyages | ?? | 2j | D |
| IA12 | **Score ?cologique repas** ? saisonnalit?, distance, v?g?tal vs animal | Cuisine | ?? | 2j | E |

---

### 8.7 Jobs automatiques CRON (analyse ?9)

#### 68+ jobs existants ? R?sum?

**Quotidiens :**

- 06h00 : sync Garmin
- 07h00 : p?remptions, rappels famille, alerte stock bas
- 07h30 : digest WhatsApp matinal
- 08h00 : rappels maison
- 09h00 : digest ntfy
- 18h00 : rappel courses, push contextuel soir
- 23h00 : sync Google Calendar
- 5 min : runner automations

**Hebdomadaires :**

- Lundi 07h30 : r?sum? hebdo
- Vendredi 17h00 : score weekend
- Dimanche 03h00 : sync OpenFoodFacts
- Dimanche 20h00 : score bien-?tre, points gamification

**Mensuels :**

- 1er 08h15 : rapport budget
- 1er 09h00 : contr?le contrats/garanties
- 1er 09h30 : rapport maison

#### 10 nouveaux jobs propos?s

| # | Job | Fr?quence | Modules | Priorit? | Phase |
| --- | ----- | ----------- | --------- | ---------- | ------- |
| J1 | **Pr?diction courses hebdo** | Vendredi 16h | Courses + IA | ?? | D4 |
| J2 | **Planning auto semaine** (si vide ? propose via WhatsApp) | Dimanche 19h | Planning + IA | ?? | B3 |
| J3 | **Nettoyage cache/exports** (> 7 jours) | Quotidien 02h | Export | ?? | D |
| J4 | **Rappel jardin saison** | Hebdo (Lundi) | Jardin | ?? | D5 |
| J5 | **Sync budget consolidation** (tous modules) | Quotidien 22h | Budget | ?? | D |
| J6 | **V?rification sant? syst?me** | Horaire | Admin | ?? | D6 |
| J7 | **Backup auto JSON** | Hebdo (Dimanche 04h) | Admin | ?? | D7 |
| J8 | **Tendances nutrition hebdo** | Dimanche 18h | Cuisine/Nutrition | ?? | E |
| J9 | **Alertes budget seuil** (cat?gorie > 80%) | Quotidien 20h | Budget | ?? | B4 |
| J10 | **Rappel activit? Jules** ("Jules a X mois ? activit?s recommand?es") | Quotidien 09h | Famille | ?? | D |

---

### 8.8 Notifications (analyse ?10)

#### Architecture

```text
                    +-----------------+
                    ?  ?v?nement      ?
                    ?  (CRON / User)  ?
                    +-----------------+
                             ?
                    +--------?--------+
                    ?  Router de      ?
                    ?  notifications  ?
                    +-----------------+
            +----------------+----------------+
            ?                ?                ?
    +-------?------+ +------?-------+ +-----?------+
    ?  Web Push    ? ?   ntfy.sh    ? ? WhatsApp   ?
    ?  (VAPID)     ? ?  (open src)  ? ? (Meta API) ?
    +--------------+ +--------------+ +------------+
                             ?
                    +--------?--------+
                    ?    Email        ?
                    ?   (Resend)      ?
                    +-----------------+
    Failover: Push ? ntfy ? WhatsApp ? Email
    Throttle: 2h par type d'?v?nement par canal
```

#### Am?liorations WhatsApp

| # | Am?lioration | Priorit? | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| W1 | Persistence ?tat conversation multi-turn (Redis/DB) | ?? | 2j | D8 |
| W2 | Commandes texte enrichies ("ajoute du lait", "budget ce mois") via NLP Mistral | ?? | 3j | B5 |
| W3 | Boutons interactifs ?tendus (valider courses, noter d?pense, signaler panne) | ?? | 2j | D |
| W4 | Photo ? action (plante malade ? diagnostic, plat ? identification recette) | ?? | 3j | E |
| W5 | R?sum? quotidien personnalisable (choix infos via param?tres) | ?? | 2j | D |

#### Am?liorations Email

| # | Am?lioration | Priorit? | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| E1 | Templates HTML/MJML jolis pour rapports mensuels | ?? | 2j | D9 |
| E2 | R?sum? hebdo email optionnel | ?? | 1j | D |
| E3 | Alertes critiques par email (document expir?, stock critique, budget d?pass?) | ?? | 1j | B |

#### Am?liorations Push

| # | Am?lioration | Priorit? | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| P1 | Actions dans la notification push ("Ajouter aux courses") | ?? | 2j | C |
| P2 | Push conditionnel (heures calmes configurables) | ?? | 1j | D |
| P3 | Badge app PWA (nombre notifications non lues) | ?? | 1j | E |

---

### 8.9 Mode Admin (analyse ?11)

#### Existant ? ? Tr?s complet

| Cat?gorie | Fonctionnalit? | Statut |
| ----------- | --------------- | -------- |
| Jobs CRON | Lister, d?clencher, historique | ? |
| Notifications | Tester un canal, broadcast test | ? |
| Event Bus | Historique, ?mission manuelle | ? |
| Cache | Stats, purge par pattern | ? |
| Services | ?tat registre complet | ? |
| Feature Flags | Activer/d?sactiver features | ? |
| Maintenance | Mode maintenance ON/OFF | ? |
| Simulation | Dry-run workflows (p?remption, digest, rappels) | ? |
| IA Console | Tester prompts (temp?rature, tokens) | ? |
| Impersonation | Switcher d'utilisateur | ? |
| Audit/Security Logs | Tra?abilit? compl?te | ? |
| SQL Views | Browser de vues SQL | ? |
| WhatsApp Test | Message test | ? |
| Config | Export/import runtime | ? |

#### Am?liorations

| # | Am?lioration | Priorit? | Effort | Phase |
| --- | ------------- | ---------- | -------- | ------- |
| A1 | Console commande rapide ("run job X", "clear cache Y") | ?? | 2j | D1 |
| A2 | Dashboard admin temps r?el (WebSocket admin_logs ? UI filtres + auto-scroll) | ?? | 3j | D |
| A3 | Scheduler visuel (timeline 68 jobs, prochain run, d?pendances) | ?? | 3j | D2 |
| A4 | Replay d'?v?nements pass?s du bus avec handlers | ?? | 2j | D |
| A6 | Logs en temps r?el (endpoint WS existe ? connecter UI) | ?? | 2j | D3 |
| A7 | Test E2E one-click (sc?nario complet recette?planning?courses?checkout?inventaire) | ?? | 3j | E |

---

### 8.10 Couverture de tests (analyse ?12)

#### Backend ? ~55% couverture

| Zone | Fichiers | Couverture | Note |
| ------ | ---------- | ------------ | ------ |
| Routes API cuisine | 8 | ? ~85% | Bien |
| Routes API famille | 6 | ? ~75% | OK |
| Routes API maison | 5 | ?? ~60% | Gaps jardin/?nergie |
| Routes API jeux | 2 | ?? ~55% | Gaps loto/euro |
| Routes API admin | 2 | ? ~70% | OK |
| Routes export/upload | 2 | ? ~30% | Tr?s faible |
| Routes webhooks | 2 | ? ~25% | Tr?s faible |
| Services | 20+ | ?? ~60% | Variable |
| Core (config, db, cache) | 6 | ?? ~55% | Cache orchestrateur faible |
| Event Bus | 1 | ? ~20% | Tr?s faible |
| R?silience | 1 | ?? ~40% | Manque sc?narios r?els |
| WebSocket | 1 | ? ~25% | Edge cases manquants |
| Int?grations | 3 | ? ~20% | Stubs sans E2E |

#### Frontend ? ~40% couverture

| Zone | Fichiers | Couverture | Note |
| ------ | ---------- | ------------ | ------ |
| Pages cuisine | 8 | ? ~70% | Bien |
| Pages jeux | 5 | ? ~65% | OK |
| Pages outils | 6 | ? ~60% | OK |
| Pages famille | 3 | ?? ~35% | Gaps importants |
| Pages maison | 2 | ?? ~30% | Gaps importants |
| Pages admin | 2 | ?? ~30% | Gaps importants |
| Pages param?tres | 1 | ? ~15% | Tr?s faible |
| Hooks | 2 | ?? ~45% | WebSocket sous-test? |
| Stores | 4 | ? ~80% | Bien |
| Composants | 12 | ?? ~40% | Variable |
| API clients | 1 | ? ~15% | Tr?s faible |
| E2E Playwright | Quelques | ? ~10% | Quasi inexistant |

#### Tests manquants prioritaires

| # | Test | Module | Priorit? | Phase |
| --- | ------ | -------- | ---------- | ------- |
| T1 | Tests export PDF (courses, planning, recettes, budget) | Export | ?? | A12 |
| T2 | Tests webhooks WhatsApp (state machine, parsing) | Notifications | ?? | A13 |
| T3 | Tests event bus scenarios (pub/sub, wildcards, erreurs) | Core | ?? | A14 |
| T4 | Tests cache L1/L2/L3 (promotion, ?viction) | Core | ?? | B |
| T5 | Tests WebSocket edge cases (reconnexion, timeout, malform?) | Courses | ?? | D |
| T6 | Tests E2E parcours utilisateur complet | Frontend | ?? | B13 |
| T7 | Tests API clients frontend (erreurs r?seau, refresh, pagination) | Frontend | ?? | D |
| T8 | Tests pages param?tres (chaque onglet) | Frontend | ?? | B12 |
| T9 | Tests pages admin (jobs, services, cache, flags) | Frontend | ?? | D |
| T10 | Tests Playwright accessibilit? (axe-core pages principales) | Frontend | ?? | E |

---

### 8.11 Documentation (analyse ?13)

#### ?tat

| Document | Statut | Action | Phase |
| ---------- | -------- | -------- | ------- |
| `docs/INDEX.md` | ? Courant | ? | ? |
| `docs/MODULES.md` | ? Courant | ? | ? |
| `docs/API_REFERENCE.md` | ? Courant | ? | ? |
| `docs/API_SCHEMAS.md` | ? Courant | ? | ? |
| `docs/SERVICES_REFERENCE.md` | ? Courant | ? | ? |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | ? Courant | ? | ? |
| `docs/ERD_SCHEMA.md` | ? Courant | ? | ? |
| `docs/ARCHITECTURE.md` | ?? 1 mois | Rafra?chir | D |
| `docs/DATA_MODEL.md` | ?? V?rifier | Peut ?tre obsol?te post-phases | D |
| `docs/DEPLOYMENT.md` | ?? V?rifier | Config Railway/Vercel actuelle | D |
| `docs/ADMIN_RUNBOOK.md` | ?? V?rifier | 20+ endpoints admin tous docum. ? | D |
| `docs/CRON_JOBS.md` | ? M?J 01/04/2026 | 68 jobs document?s | Termin? |
| `docs/NOTIFICATIONS.md` | ? M?J 01/04/2026 | 4 canaux, failover, digest, templates | Termin? |
| `docs/AUTOMATIONS.md` | ? M?J 01/04/2026 | D?clencheurs/actions r?els document?s | Termin? |
| `docs/INTER_MODULES.md` | ? M?J 01/04/2026 | 21+ bridges et patterns document?s | Termin? |
| `docs/EVENT_BUS.md` | ? M?J 01/04/2026 | 32 ?v?nements, 51 subscribers | Termin? |
| `docs/MONITORING.md` | ?? V?rifier | Prometheus metrics actuelles ? | D |
| `docs/SECURITY.md` | ?? V?rifier | Rate limiting, 2FA, CORS | D |
| `PLANNING_IMPLEMENTATION.md` | ?? Obsol?te | Ce document le remplace | ? |
| `ROADMAP.md` | ?? Obsol?te | Priorit?s p?rim?es | D |

#### Documentation ? cr?er

| # | Document | Priorit? | Phase |
| --- | --------- | ---------- | ------- |
| D1 | Guide complet CRON jobs (68+ jobs, horaires, d?pendances) | ? Fait | Termin? |
| D2 | Guide notifications refonte (4 canaux, failover, templates, config) | ? Fait | Termin? |
| D3 | Guide admin M?J (20+ endpoints, panneau, simulations, flags) | ? Fait | Termin? |
| D4 | Guide bridges inter-modules (21 bridges, naming, comment en cr?er) | ? Fait | Termin? |
| D5 | Guide de test unifi? (pytest + Vitest + Playwright, fixtures, mocks) | ? Fait | Termin? |
| D6 | Changelog module par module | ? Fait | Termin? |

---

### 8.12 Organisation & architecture (analyse ?14)

#### Points forts ?

- Architecture modulaire : s?paration routes/schemas/services/models
- Service Registry : `@service_factory` singleton thread-safe
- Event Bus : pub/sub d?coupl?, wildcards, priorit?s
- Cache multi-niveaux : L1?L2?L3+Redis
- R?silience : retry+timeout+circuit breaker composables
- S?curit? : JWT+2FA TOTP+rate limiting+security headers+sanitization
- Frontend : App Router Next.js 16, composants shadcn/ui consistants

#### Points ? am?liorer

| # | Probl?me | Action | Effort | Phase |
| --- | ---------- | -------- | -------- | ------- |
| O1 | `jobs.py` monolithique (3500+ lignes) | D?couper en `jobs_cuisine.py`, `jobs_famille.py`, etc. | 1j | D10 |
| O2 | Routes famille ?clat?es (multiples fichiers) | Documenter naming pattern | 30min | D |
| O3 | Scripts legacy non archiv?s | D?placer dans `scripts/_archive/` | 30min | D11 |
| O4 | Doubles biblioth?ques charts (Chart.js + Recharts) | Standardiser sur Recharts | 1j | D12 |
| O5 | RGPD route non pertinente (app priv?e) | Simplifier en "Export backup" | 30min | E |
| O6 | Types frontend dupliqu?s entre fichiers | Centraliser via barrel exports | 1j | D |
| O7 | Donn?es r?f?rence non versionn?es | Ajouter version dans chaque JSON | 30min | E |
| O8 | Dossier exports non nettoy? (`data/exports/`) | Politique r?tention automatique (CRON J3) | 30min | D |

---

### 8.13 Am?liorations UI/UX (analyse ?15)

#### Dashboard

| # | Am?lioration | Priorit? | Phase |
| --- | ------------- | ---------- | ------- |
| U1 | **Widgets drag-drop** (`@dnd-kit/core`) | ?? | C1 |
| U2 | Cartes avec micro-animations (Framer Motion) | ?? | C |
| U3 | Mode sombre raffin? (charts, calendrier) | ?? | E |
| U4 | Squelettes de chargement fid?les | ?? | D |

#### Navigation

| # | Am?lioration | Priorit? | Phase |
| --- | ------------- | ---------- | ------- |
| U5 | Sidebar avec favoris dynamiques (composant existant ? store) | ?? | D |
| U6 | Breadcrumbs interactifs (tous niveaux cliquables) | ?? | E |
| U7 | **Transitions de page fluides** (framer-motion ou View Transitions) | ?? | C8 |
| U8 | Bottom bar mobile enrichie (indicateur page active + animation) | ?? | C |

#### Formulaires

| # | Am?lioration | Priorit? | Phase |
| --- | ------------- | ---------- | ------- |
| U9 | **Auto-compl?tion intelligente** (historique) | ?? | C11 |
| U10 | Validation inline temps r?el (onBlur au lieu de submit) | ?? | D |
| U11 | Assistant formulaire IA ("Aide-moi ? remplir") | ?? | E |

#### Mobile

| # | Am?lioration | Priorit? | Phase |
| --- | ------------- | ---------- | ------- |
| U12 | **Swipe actions** sur toutes les listes | ?? | C9 |
| U13 | Pull-to-refresh (TanStack Query le supporte) | ?? | D |
| U14 | Haptic feedback (Vibration API) | ?? | E |

#### Micro-interactions

| # | Am?lioration | Priorit? | Phase |
| --- | ------------- | ---------- | ------- |
| U15 | Confetti sur accomplissement (planning valid?, courses compl?tes) | ?? | E |
| U16 | **Compteurs anim?s dashboard** (0 ? valeur r?elle) | ?? | C10 |
| U17 | Toast notifications Sonner am?lior?es (succ?s check anim?, erreur shake) | ?? | D |

---

### 8.14 Visualisations 2D/3D (analyse ?16)

#### Existant

| Composant | Technologie | Module | Statut |
| ----------- | ------------- | -------- | -------- |
| Plan 3D maison | Three.js/@react-three/fiber | Maison | ?? Non connect? aux donn?es |
| Heatmap num?ros loto | Recharts | Jeux | ? |
| Heatmap cotes paris | Recharts | Jeux | ? |
| Camembert budget | Recharts | Famille | ? |
| Graphique ROI | Recharts | Jeux | ? |
| Graphique jalons Jules | Recharts | Famille | ? |
| Timeline planning | Custom CSS | Planning | ?? Basique |
| Carte Leaflet habitat | react-leaflet | Habitat | ?? Partiel |

#### Nouvelles visualisations

**3D :**

| # | Visualisation | Module | Description | Effort | Phase |
| --- | --------------- | -------- | ------------- | -------- | ------- |
| V1 | **Plan 3D maison interactif** | Maison | Connecter aux donn?es : couleur pi?ces par t?ches, ?nergie par pi?ce, clic ? d?tail | 5j | C3 |
| V2 | **Vue jardin 2D/3D** | Jardin | Zones plantation, ?tat plantes, calendrier arrosage | 3j | E7 |
| V3 | **Globe 3D voyages** | Voyages | Destinations + itin?raires (globe.gl) | 2j | E |

**2D :**

| # | Visualisation | Module | Description | Effort | Phase |
| --- | --------------- | -------- | ------------- | -------- | ------- |
| V4 | **Calendrier nutritionnel heatmap** | Cuisine | Grille GitHub contributions jour par jour (rouge ? vert) | 2j | C4 |
| V5 | **Treemap budget** | Budget | Proportionnel cat?gories, drill-down cliquable | 2j | C5 |
| V6 | **Sunburst recettes** | Cuisine | Cat?gories ? sous-cat?gories ? recettes (D3.js) | 2j | E |
| V7 | **Radar skill Jules** | Famille | Diagramme araign?e comp?tences vs normes OMS | 1j | C6 |
| V8 | **Sparklines dans cartes** | Dashboard | Mini graphiques tendance 7 jours | 1j | C7 |
| V9 | **Graphe r?seau modules** | Admin | 21 bridges visuels (D3.js force graph) | 2j | E5 |
| V10 | **Timeline Gantt entretien** | Maison | Planification annuelle | 2j | E6 |
| V11 | **Courbe ?nergie N vs N-1** | ?nergie | Comparaison consommation | 2j | C |
| V12 | **Flux Sankey courses ? cat?gories** | Courses/Budget | Fournisseurs ? cat?gories ? sous-cat?gories | 2j | E |
| V13 | **Wheel fortune loto** | Jeux | Animation roue r?v?lation num?ros IA | 1j | E |

---

### 8.15 Simplification flux utilisateur (analyse ?17)

> L'utilisateur doit accomplir ses t?ches quotidiennes en **3 clics maximum**.
> L'IA fait le travail lourd en arri?re-plan, l'utilisateur **valide**.

#### ??? Flux cuisine (central)

```text
Semaine vide ? IA propose planning ? Valider/Modifier/R?g?n?rer
                                         ?
                                    Planning valid?
                                   +-----------+
                            Auto-g?n?re      Notif WhatsApp
                            courses           recap
                                ?
                          Liste courses (tri?e par rayon)
                                ?
                     En magasin: cocher au fur et ? mesure
                                ?
                     Checkout ? transfert automatique inventaire
                                ?
                     Score anti-gaspi mis ? jour

Fin de semaine: "Qu'avez-vous vraiment mang? ?" ? feedback IA
```

**Actions utilisateur** : 3 (valider planning ? cocher courses ? checkout)
**Actions IA** : Planning, courses, rayons, transfert inventaire

#### ?? Flux famille quotidien

```text
Matin (auto WhatsApp 07h30):
  "Bonjour ! Repas X, t?che Y, Jules a Z mois" ? OK / Modifier

Journ?e:
  Routines Jules (checklist ? cocher)

Soir:
  R?cap auto: "3/5 t?ches, 2 repas ok, Jules: poids not?"
```

#### ?? Flux maison

```text
Notification push auto:
  "T?che entretien: [t?che]" ? Voir ? Marquer fait ? auto-prochaine date
  "Stock [X] bas" ? Ajouter aux courses (1 clic)
  1er du mois: Rapport email r?sum? t?ches + budget maison
```

#### Actions rapides FAB mobile

| Action rapide | Cible | Ic?ne |
| -------------- | ------- | ------- |
| + Recette rapide | Formulaire simplifi? (nom + photo) | ?? |
| + Article courses | Ajout vocal ou texte | ?? |
| + D?pense | Montant + cat?gorie | ?? |
| + Note | Texte libre | ?? |
| Scan barcode | Scanner ? inventaire ou courses | ?? |
| Timer cuisine | Minuteur rapide | ?? |

### Phase : C (actions rapides), B (flux simplifies cuisine/famille), D (flux maison)

---

### 8.16 Axes d'innovation (analyse ?18)

| # | Innovation | Modules | Description | Effort | Impact | Phase |
| --- | ----------- | --------- | ------------- | -------- | -------- | ------- |
| IN1 | **Mode "Pilote automatique"** | Tous | IA g?re planning/courses/rappels sans intervention. R?sum? quotidien, corrections uniquement. ON/OFF param?tres | 5j | ?? Tr?s ?lev? | E1 |
| IN2 | **Widget tablette Google** | Dashboard | Widget Android/web : repas du jour, t?che, m?t?o, timer. Compatible tablette Google | 4j | ?? ?lev? | E2 |
| IN3 | **Page "Ma journ?e" unifi?e** | Planning+Cuisine+Famille+Maison | Tout en une page : repas, t?ches, routines Jules, m?t?o, anniversaires, timer | 3j | ?? Tr?s ?lev? | C2 |
| IN4 | **Suggestions proactives contextuelles** | IA+Tous | Banni?re IA en haut de chaque module : "tomates expirent ? recettes", "budget restaurants 80% ? d?tail" | 3j | ?? ?lev? | C12 |
| IN5 | **Journal familial automatique** | Famille | IA g?n?re journal de la semaine : repas, activit?s, Jules, photos, m?t?o, d?penses. Exportable PDF | 3j | ?? Moyen | E8 |
| IN6 | **Mode focus/zen** | UI | Masque tout sauf la t?che en cours (recette en cuisine, liste en magasin). Composant `focus/` existant | 2j | ?? Moyen | D |
| IN7 | **Comparateur prix courses** | Courses+IA | Liste ? IA compare prix r?f?rence (sans OCR) ? budget estim? | 3j | ?? Moyen | E |
| IN8 | **Google Home routines ?tendues** | Assistant | "Bonsoir" ? lecture repas demain + t?ches | 4j | ?? Moyen | E10 |
| IN9 | **Seasonal meal prep planner** | Cuisine+IA | Chaque saison ? plan batch cooking saisonnier + cong?lations recommand?es | 2j | ?? Moyen | E |
| IN10 | **Score famille hebdomadaire** | Dashboard | Composite : nutrition + d?penses + activit?s + entretien + bien-?tre. Graphe semaine par semaine | 2j | ?? ?lev? | E3 |
| IN11 | **Export rapport mensuel PDF** | Export+IA | PDF avec graphiques : budget, nutrition, entretien, Jules, jeux. R?sum? narratif IA | 3j | ?? Moyen | E9 |
| IN12 | **Planning vocal** | Assistant+Planning | "Planifie du poulet mardi soir" ? cr?e repas + v?rifie stock + ajoute manquants | 3j | ?? Moyen | E |
| IN13 | **Tableau de bord ?nergie** | Maison | Dashboard d?di? : conso temps r?el (Linky), historique, N-1, pr?vision facture, tips IA | 4j | ?? Moyen | E |
| IN14 | **Mode "invit?" conjoint** | Auth | Vue simplifi?e 2?me utilisateur : courses, planning, routines. Sans admin ni config | 2j | ?? ?lev? | E4 |

---

## 9. Annexes

### Annexe A ? Arborescence fichiers cl?s

#### Backend Python

```text
src/
+-- api/
?   +-- main.py                    # FastAPI app + 7 middlewares + health
?   +-- auth.py                    # JWT + 2FA TOTP
?   +-- dependencies.py            # require_auth, require_role
?   +-- routes/                    # 41 fichiers routeurs (~250 endpoints)
?   +-- schemas/                   # 25 fichiers Pydantic (~150 mod?les)
?   +-- utils/                     # Exception handler, pagination, metrics, ETag, security
?   +-- rate_limiting/             # Multi-strategy (memory/Redis/file)
?   +-- websocket_courses.py       # WS collaboration courses
?   +-- websocket/                 # 4 autres WebSockets
+-- core/
?   +-- ai/                        # Mistral client, cache s?mantique, circuit breaker
?   +-- caching/                   # L1/L2/L3 + Redis
?   +-- config/                    # Pydantic BaseSettings
?   +-- db/                        # Engine, sessions, migrations
?   +-- decorators/                # @avec_session_db, @avec_cache, @avec_resilience
?   +-- models/                    # 32 fichiers ORM (100+ classes)
?   +-- resilience/                # Retry + Timeout + CircuitBreaker
?   +-- validation/                # Pydantic schemas + sanitizer
+-- services/
    +-- core/
    ?   +-- base/                  # BaseAIService (4 mixins)
    ?   +-- cron/                  # 68+ jobs (3500+ lignes)
    ?   +-- events/                # Pub/Sub event bus
    ?   +-- registry.py            # @service_factory singleton
    +-- cuisine/                   # RecetteService, ImportService
    +-- famille/                   # JulesAI, WeekendAI
    +-- maison/                    # MaisonService
    +-- jeux/                      # JeuxService
    +-- planning/                  # 5 sous-modules
    +-- inventaire/                # InventaireService
    +-- dashboard/                 # Agr?gation multi-module
    +-- integrations/              # Multimodal, webhooks
    +-- utilitaires/               # Automations, divers
```

#### Frontend Next.js

```text
frontend/src/
+-- app/
?   +-- (auth)/                    # Login / Inscription
?   +-- (app)/                     # App prot?g?e (~60 pages)
?   ?   +-- cuisine/               # 12 pages
?   ?   +-- famille/               # 10 pages
?   ?   +-- maison/                # 8 pages
?   ?   +-- jeux/                  # 7 pages
?   ?   +-- planning/              # 2 pages
?   ?   +-- outils/                # 6 pages
?   ?   +-- parametres/            # 3 pages + 7 onglets
?   ?   +-- admin/                 # 10 pages
?   ?   +-- habitat/               # 3 pages
?   ?   +-- ia-avancee/            # IA avanc?e
?   +-- share/                     # Partage public
+-- composants/
?   +-- ui/                        # 29 shadcn/ui
?   +-- disposition/               # 19 layout components
?   +-- cuisine/, famille/, jeux/, maison/, habitat/
?   +-- graphiques/                # Charts r?utilisables
?   +-- planning/                  # Timeline, calendrier
+-- bibliotheque/
?   +-- api/                       # 34 clients API
?   +-- validateurs.ts             # 22 sch?mas Zod
+-- crochets/                      # 15 hooks custom
+-- magasins/                      # 4 stores Zustand
+-- types/                         # 15 fichiers TypeScript
+-- fournisseurs/                  # 3 providers React
```

#### SQL

```text
sql/
+-- INIT_COMPLET.sql               # 4922 lignes, source unique (prod)
+-- schema/ (18 fichiers)          # Source de v?rit? par domaine
+-- migrations/ (7 fichiers)       # ? consolider dans schema/
```

### Annexe B ? WebSockets

| Route WS | Fonction | ?tat |
| ---------- | ---------- | ------ |
| `/ws/courses/{liste_id}` | Collaboration temps r?el courses | ? (manque fallback HTTP ? B2) |
| `/ws/planning` | Collaboration planning | ? |
| `/ws/notes` | ?dition collaborative notes | ? |
| `/ws/projets` | Kanban projets maison | ? |
| `/ws/admin/logs` | Streaming logs admin | ? (UI non connect?e ? A6/D3) |

### Annexe C ? Donn?es de r?f?rence

```text
data/reference/
+-- astuces_domotique.json           ?
+-- calendrier_soldes.json           ?
+-- calendrier_vaccinal_fr.json      ?
+-- catalogue_pannes_courantes.json  ?
+-- entretien_catalogue.json         ?
+-- guide_lessive.json               ?
+-- guide_nettoyage_surfaces.json    ?
+-- guide_travaux_courants.json      ?
+-- normes_oms.json                  ?
+-- nutrition_table.json             ?
+-- plantes_catalogue.json           ?
+-- produits_de_saison.json          ?
+-- routines_defaut.json             ?
+-- template_import_inventaire.csv   ?
```

### Annexe D ? Canaux de notification par ?v?nement

```text
Failover: Push ? ntfy ? WhatsApp ? Email
Throttle: 2h par type / canal
```

| ?v?nement | Push | ntfy | WhatsApp | Email |
| ----------- | ------ | ------ | ---------- | ------- |
| P?remption J-2 | ? | ? | ? | ? |
| Rappel courses | ? | ? | ? | ? |
| R?sum? hebdomadaire | ? | ? | ? | ? |
| Rapport budget mensuel | ? | ? | ? | ? |
| Anniversaire J-7 | ? | ? | ? | ? |
| T?che entretien urgente | ? | ? | ? | ? |
| ?chec CRON job | ? | ? | ? | ? |
| Document expirant | ? | ? | ? | ? |
| Badge d?bloqu? | ? | ? | ? | ? |
| Stock critique | ? | ? | ? | ? |
| Planning vide dimanche | ? | ? | ? | ? |
| Digest matinal | ? | ? | ? | ? |
| Rapport mensuel | ? | ? | ? | ? |

---

## 10. R?capitulatif global & m?triques de sant?

### Vue synth?tique des phases

| Phase | Objectif | T?ches | Semaines | Priorit? |
| ------- | ---------- | -------- | ---------- | ---------- |
| **Phase A** | Stabilisation : bugs critiques, SQL, tests critiques, doc obsol?te | 16 | 1-2 | ? TERMIN?E |
| **Phase B** | Fonctionnalit?s : gaps, IA, CRON, bridges, recherche, tests | 13 | 3-4 | ? TERMIN?E |
| **Phase C** | UI/UX : visualisations, drag-drop, animations, flux simplifi?s | 12 | 5-6 | ?? MOYENNE-HAUTE |
| **Phase D** | Admin : console, scheduler, CRON, notifications, refactoring | 12 | 7-8 | ?? MOYENNE |
| **Phase E** | Innovations : pilote automatique, widget, Google Home, exports | 12 | 9+ | ?? BASSE |
| **TOTAL** | | **65 t?ches** | | |

### D?pendances

```text
Phase A (Stabilisation) ---- BLOQUANT pour tout
    ?
    +-- Phase B (Features)      ---- Apr?s A
    ?       ?
    ?       +-- Phase C (UI/UX)  ---- Apr?s B
    ?       ?
    ?       +-- Phase D (Admin)  ---- Apr?s B
    ?               ?
    ?               +-- Phase E (Innovations) ---- Apr?s C+D
    ?
    +-- Docs en parall?le de tout
```

### M?triques de sant? projet

| Indicateur | Valeur actuelle | Cible | Statut |
| ----------- | ---------------- | ------- | -------- |
| Tests backend couverture | ~55% | =70% | ?? |
| Tests frontend couverture | ~40% | =50% | ?? |
| Tests E2E | ~10% | =30% | ?? |
| Docs ? jour | ~60% | =90% | ?? |
| SQL ORM sync | Non v?rifi? | 100% | ?? |
| Endpoints document?s | ~80% | 100% | ?? |
| Bridges inter-modules | 21 actifs | 31 possibles | ?? |
| CRON jobs test?s | ~30% | =70% | ?? |
| Bugs critiques ouverts | 4 | 0 | ?? |
| S?curit? (OWASP) | Bon (partiel) | Complet | ?? |

### Comptage total par cat?gorie

| Cat?gorie | Items dans l'analyse | Planifi? |
| ----------- | --------------------- | ---------- |
| Bugs critiques | 4 | Phase A |
| Bugs importants | 6 | Phase A + D |
| Bugs mineurs | 4 | Backlog |
| Gaps fonctionnels | 23 | Phases B-E |
| Actions SQL | 6 | Phase A |
| Interactions intra-modules ? am?liorer | 8 | Phases B-E |
| Nouvelles interactions inter-modules | 10 | Phases B-E |
| Opportunit?s IA | 12 | Phases B-E |
| Nouveaux CRON jobs | 10 | Phases B-D |
| Am?liorations notifications | 11 | Phases B-E |
| Am?liorations admin | 7 | Phase D |
| Tests manquants prioritaires | 10 | Phases A-D |
| Documentation ? cr?er/M?J | 17 | Phases A-D |
| Refactoring organisation | 8 | Phase D |
| Am?liorations UI/UX | 17 | Phases C-E |
| Visualisations 2D/3D | 13 | Phases C-E |
| Innovations | 14 | Phase E |
| **TOTAL items identifi?s** | **~170** | **65 t?ches group?es en 5 phases** |

---

> **Document g?n?r? le 1er avril 2026**
> Bas? int?gralement sur les 19 sections de ANALYSE_COMPLETE.md
> **65 t?ches planifi?es** couvrant **~170 items identifi?s** en **5 phases**
> **Note globale app : 7.5/10** ? Architecture excellente, p?nalis?e par la couverture de tests, la dette UX, et 4 bugs critiques de production
