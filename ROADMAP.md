# 🗺️ ROADMAP — Assistant Matanne

> Dernière mise à jour : 27 mars 2026 (finalisation module Famille M-R + corrections routes/cron)

---

## ✅ Mise à jour implémentation (27 mars 2026 — module Famille M-R)

- [x] **Phase O (Activités météo-intelligentes)** : pré-remplissage inline depuis suggestions IA (`suggestions_struct` + action "Utiliser cette suggestion")
- [x] **Phase P (Achats & cadeaux auto-suggérés)** :
  - Endpoint canonique `GET /api/v1/famille/achats`
  - Endpoint proactif `POST /api/v1/famille/achats/suggestions`
  - Page `/famille/achats` branchée sur suggestions IA actionnables (ajout en 1 clic)
  - Suggestion achats inline ajoutée au hub `/famille`
- [x] **Phase Q (Rappels intelligents)** : endpoint `GET /api/v1/famille/rappels/evaluer` exploité sur hub + sidebar, cron push quotidien fiabilisé
- [x] **Phase R (Journal IA & album jalons)** :
  - Alias API ajouté `POST /api/v1/famille/journal/resumer-semaine`
  - Résumés IA sauvegardés affichés dans `/famille/journal`
  - Lien album↔jalons exploité via upload lié (`jalon-<id>_`) + navigation croisée Jules/Album
- [x] **Stabilisation backend** : déduplication route `/famille/contexte`, correction enregistrement job `push_quotidien` APScheduler

**✅ MODULE FAMILLE : 6/6 phases complètes (M-R)**

---

## ✅ Mise à jour implémentation (27 mars 2026 — module Jeux 100% FINALISÉ)

**🎮 Phases T/U/V/W — 4 fonctionnalités manquantes implémentées :**

- [x] **Phase T — Heatmap cotes bookmakers** :
  - Modèle `CoteHistorique` + endpoint `GET /paris/cotes-historique/{match_id}`
  - Composant `HeatmapCotes` (LineChart Recharts multi-lignes)
  - Migration SQL `003_add_cotes_historique.sql`
- [x] **Phase U — Générateur grilles IA pondéré** :
  - `JeuxAIService.generer_grille_ia_ponderee()` (Mistral AI, modes chauds/froids/equilibre)
  - Endpoint `POST /loto/generer-grille-ia-ponderee`
  - Composant `GrilleIAPonderee` (UI génération + analyse intégrée)
- [x] **Phase U — Analyse IA grilles joueur** :
  - `JeuxAIService.analyser_grille_joueur()` (critique Mistral avec note 0-10)
  - Endpoint `POST /loto/analyser-grille`
  - Intégré dans `GrilleIAPonderee` (bouton "Analyser cette grille")
- [x] **Phase W — Notifications Web Push résultats** :
  - Templates backend : `notifier_pari_gagne()`, `notifier_pari_perdu()`, `notifier_resultat_loto()`
  - Types notifications : `RESULTAT_PARI_GAGNE`, `RESULTAT_PARI_PERDU`, `RESULTAT_LOTO`, `RESULTAT_LOTO_GAIN`
  - Hook frontend `useNotificationsJeux()` (écoute service worker + toasts sonner)
  - Fonction `demanderPermissionNotificationsJeux()`

**✅ INTÉGRATION UI COMPLÈTE (27 mars 2026 — session après-midi) :**

- ✅ **Loto** : `GrilleIAPonderee` intégré dans `/jeux/loto` (après générateur basique)
  - Callbacks `genererGrilleIAPonderee()` + `analyserGrilleJoueur()` câblés
  - UI complète : sélecteur mode → génération IA → analyse critique
- ✅ **Paris** : `HeatmapCotes` affiché dans drawer détail match
  - Graphique évolution cotes (1/N/2, over/under 2.5) visible pour chaque match
  - Fetching automatique via `obtenirHistoriqueCotes(matchId)`
- ✅ **Notifications** : `useNotificationsJeux()` activé dans `CoquilleApp`
  - Écoute service worker au niveau racine
  - Toasts automatiques pour paris gagnés/perdus, résultats loto, séries
- ✅ **Paramètres** : Bouton "Activer les notifications jeux" dans onglet Notifications
  - Appelle `demanderPermissionNotificationsJeux()` → permission navigateur
  - Section dédiée 🎮 sous les notifications push générales

**✅ MODULE JEUX : 5/5 phases complètes (S-W) — 100% fonctionnel BACKEND + FRONTEND + UI**

---

## ✅ Mise à jour implémentation (26 mars 2026 — Phase AC Navigation complète)

- [x] **AC1 Ma Semaine** : Page `/ma-semaine` unifiée (repas + activités + tâches + matchs) + endpoint `GET /api/v1/planning/semaine-unifiee`
- [x] **AC2 Outils contextuels** : `FabChatIA` + `MinuteurFlottant` + `ConvertisseurInline` dans recettes (par ingrédient) ET planning (grille + dialogue sélecteur)
- [x] **AC3 Paramètres discrets** : dropdown avatar header — accès paramètres + intégrations, retirés de la sidebar
- [x] **AC4 Sidebar simplifiée** : 4 modules + Ma Semaine, Outils retirés de la nav principale
- [x] **AC5 Menu commandes** : Ctrl+K — 60+ pages indexées, favoris localStorage, `BoutonEpingler`, `FavorisRapides`
- [x] **Module Navigation (AC)** : 5/5 sous-phases complètes ✅

---

## ✅ Mise à jour implémentation (26 mars 2026 — session infrastructure)

- [x] **Routes énergie consolidées** : ajout `GET /api/v1/maison/energie/previsions-ia` (régression linéaire simple, tendance, confiance)
- [x] **UI énergie** : carte "Prévisions IA" ajoutée dans la page énergie maison
- [x] **Push métier** : ajout `POST /api/v1/push/notifier-metier` + templates Web Push famille/jeux/maison
- [x] **Cron push** : job `push_quotidien` ajouté à 09h00 (alertes urgentes Web Push)
- [x] **Planning IA enrichi** : génération hebdo enrichie par historique recettes et objectifs nutritionnels dynamiques
- [x] **Dashboards DnD persistants** : hubs Famille, Maison, Jeux réordonnables avec sauvegarde `localStorage`
- [x] **E2E collaboration courses** : spec multi-contextes ajoutée (`frontend/e2e/courses-collaboration.spec.ts`)

---

## 🗓️ Priorités — 2 prochaines semaines (27 mars → 10 avril 2026)

> Focus : automatisation cuisine + qualité test + synchronisation inventaire. **Modules Famille et Jeux finalisés**.

| # | Tâche | Phase | Effort | Impact |
|---|-------|-------|--------|--------|
| 1 | Auto-sync OCR photo-frigo → inventaire (1 endpoint + bouton UI) | K Photo-frigo | S | 🟠 Quotidien |
| 2 | Tests backend routes restantes (admin/recherche/rgpd) | — Qualité | M | 🔴 Stabilité |
| 3 | Renforcer couverture tests famille (achats/rappels/journal/album) | M-R Famille | M | 🟠 Fiabilité |
| 4 | Optimiser flux Ma Semaine cuisine (onboarding + widget dashboard) | D Cuisine | M | 🟡 UX |
| 5 | Convertisseur inline flux recettes | AC2 Outils | S | 🟡 UX |

*Effort : S = ½ journée, M = 1–2 jours. Impact : 🔴 bloquant/sécurité, 🟠 valeur utilisateur directe, 🟡 qualité/UX.*

**Note** : Items Famille Q/P (rappels + achats proactifs) déplacés en livré dans la session du 27 mars.

---

## En cours

### Réorganisation docs & SQL

- [x] Suppression docs obsolètes (MIGRATION_CORE_PACKAGES, GUIDE_UTILISATEUR, batch_cooking.md)
- [x] Réécriture MODULES.md, SERVICES_REFERENCE.md, INDEX.md
- [x] Guides complets par module (cuisine, famille, maison, jeux, outils, planning, dashboard, utilitaires)
- [x] Correction RLS Supabase (USING(true) → filtrage par user_id)
- [x] Tables SQL manquantes (webhooks_abonnements, etats_persistants)
- [x] Migrations SQL incrémentales (V001 RLS fix, V002 user_id standardization)
- [x] Nettoyage ROADMAP (suppression historique sprints 1-16)
- [x] Migration V002 créée : `sql/migrations/002_standardize_user_id_uuid.sql` (application manuelle Supabase)

### Infrastructure & qualité

- [x] **Sentry backend** — `FastApiIntegration` + `SqlalchemyIntegration` + `LoggingIntegration` activés dans `main.py`
  → Configurer `SENTRY_DSN` dans `.env.local` + Railway dashboard
- [x] **Sentry frontend** — Config déjà prête (`sentry.client.config.ts`)
  → Configurer `NEXT_PUBLIC_SENTRY_DSN` dans `.env.local` + Vercel dashboard
- [x] **CI/CD** — Vitest ajouté dans `deploy.yml` (job `build-frontend`), 8 workflows opérationnels
- [x] **PWA offline** — `sw.js` v3 + `manifest.json` + `offline.html` + `EnregistrementSW` dans root layout ✅
- [x] **Tests E2E Playwright** — 10 specs couvrant auth, recettes, courses, planning, activités, navigation ✅
- [x] **Cache Redis L2** — `src/core/caching/redis.py` opérationnel, auto-détecté via `REDIS_URL`
- [x] **k6 load tests** — `tests/load/k6_baseline.js` créé (4 scénarios, seuils p95)
- [x] **Responsive** — audit mobile ✅ sidebar, formulaires, tableaux corrigés
- [x] **Accessibilité** — `aria-label`, `aria-expanded`, `aria-current`, `scope="col"`, rôles ARIA ✅
- [x] **Migration Alembic** — scaffolding prêt (`alembic/`, `alembic.ini`, `env.py`, baseline `0001_`)

---

## 📋 Système de Phases (28 phases A-AC)

> Voir [STATUS_PHASES.md](STATUS_PHASES.md) pour le détail complet de l'implémentation

**Vue d'ensemble** : 28 phases organisées par module pour structurer la refonte complète de l'application.

### État global (27 mars 2026) — après finalisation Jeux (S-W) + Famille (M-R)

| Statut | Nombre | Pourcentage | Description |
|--------|--------|-------------|-------------|
| ✅ **COMPLÈTES** | **23/28** | **82%** | Tous éléments implémentés et fonctionnels |
| 🔶 **QUASI-COMPLÈTES (≥80%)** | **2** *(dans partielles)* | *(+7%)* | D, L |
| 🔄 **PARTIELLES** | **3/28** | **11%** | Fonctionnalités avancées ou UX restantes |
| ❌ **NON IMPLÉMENTÉES** | **2/28** | **7%** | Aucun élément trouvé |

> **Couverture fonctionnelle pondérée** : ~89% — 23 complètes + 2×0,85 quasi + 1×0,5 partielle sur 28 phases.

### Par module (après session 27 mars)

- **🍽️ Cuisine (A-L)** : 2/12 complètes, 8 partielles, 2 non implémentées
- **👨‍👩‍👦 Famille (M-R)** : **6/6 complètes** ✅ **MODULE COMPLET**
- **🎮 Jeux (S-W)** : **5/5 complètes** ✅ **MODULE COMPLET**
- **🏡 Maison (X-AB)** : **5/5 complètes** ✅ **MODULE COMPLET**
- **🧭 Navigation (AC)** : **5/5 complètes** ✅ **MODULE COMPLET**

---

### ✅ P0 — COMPLÈTES (Impact Immédiat)

1. ✅ `GET /api/v1/famille/contexte` — ContexteFamilialService exposé
2. ✅ `GET /api/v1/maison/briefing` + `GET /api/v1/maison/alertes` — ContexteMaisonService exposé
3. ✅ `POST /api/v1/weekend/suggestions-ia` — déjà existant
4. ✅ `GET /api/v1/jeux/dashboard` + séries + value-bets + predictions — déjà existants
5. ✅ `POST /api/v1/anti-gaspillage/suggestions-ia` — créé
6. ✅ `POST /api/v1/courses/generer-depuis-planning` — déjà existant

### ✅ P1 — COMPLÈTES (Refonte UX)

4. ✅ Hub Famille contextuel (page.tsx refondre, CarteAnniversaire, BandeauMeteo, etc.)
5. ✅ Hub Maison contextuel (briefing quotidien, alertes, tâches du jour)
6. ✅ Dashboard Jeux (budget, value-bets, séries, KPIs)
7. ✅ Planning Maison — `/menage/planning-semaine` endpoint + page complète

### ✅ P2 — COMPLÈTES (Finalisation)

8. ✅ **Jobs cron** — `src/services/core/cron/jobs.py` + APScheduler dans lifespan FastAPI
   - 07h00 : rappels famille (anniversaires, documents, jalons Jules)
   - 08h00 : rappels maison (garanties, contrats, entretien)
   - 08h30 : rappels intelligents généraux
   - lundi 06h00 : entretien saisonnier
9. ✅ **Ma Semaine trans-modules** — `GET /api/v1/planning/semaine-unifiee` + page `/ma-semaine`
   - Vue unifiée : repas + activités famille + matchs + tâches maison
   - Navigation semaine (← →) + liens directs modules
10. ✅ **FAB chat IA flottant** — `FabChatIA` component dans coquille-app
    - Mini-chat popout avec envoi vers `/utilitaires/chat/message`
    - Masqué sur `/outils/chat-ia`, lien vers chat complet
11. ✅ **Sidebar simplifiée** — Outils retirés, "Ma Semaine" ajouté
    - Desktop sidebar : Accueil + Ma Semaine + 4 modules (Cuisine, Famille, Maison, Jeux)
    - Nav mobile : Accueil + Cuisine + Famille + Maison + Ma Semaine

### ✅ Avancées complémentaires livrées

12. ✅ **AC2** : Minuteur flottant global
  - Barre persistante lorsque le minuteur est actif
  - Synchronisation via localStorage entre page minuteur et coquille app
13. ✅ **AC3** : Paramètres discrets
  - Paramètres + intégrations déplacés dans le menu avatar
  - Liens paramètres retirés de la sidebar
14. ✅ **AA (partiel fort)** : Alertes prédictives garanties
  - Endpoint `GET /api/v1/maison/garanties/alertes-predictives`
  - Carte dédiée sur le hub maison avec action recommandée
15. ✅ **O (partiel fort)** : Activités météo-intelligentes côté UX
  - Affichage météo détectée et journée libre dans suggestions IA
16. ✅ **Jeux** : OCR ticket loto/euromillions
  - Endpoint `POST /api/v1/jeux/ocr-ticket`
  - Extraction IA des lignes, total et point de vente
17. ✅ **Jeux** : Backtest euromillions exposé
  - Endpoint `GET /api/v1/jeux/backtest?type_jeu=euromillions`
  - Normalisation des tirages euromillions vers moteur de backtest
18. ✅ **Photo-frigo** : Multi-zone (frigo/placard/congélateur)
  - API `POST /api/v1/suggestions/photo-frigo?zones=...`
  - UI multi-sélection dans `/cuisine/photo-frigo`
19. ✅ **OCR tickets de caisse** : Reconnaissance photo ticket → import automatique liste de courses
  - Endpoint `POST /api/v1/courses/ocr-ticket-caisse`
  - Page `/cuisine/courses/scan-ticket` avec sélection et confirmation des articles
20. ✅ **Scan multi-codes simultané** : composant `ScanneurMultiCodes` (ZXing, caméra live, déduplication `Set`) + endpoint `POST /api/v1/inventaire/barcode/batch` (ScanBatchRequest/ScanBatchResponse) → intégré courses ET inventaire
21. ✅ **Export/import données chiffré** : backup JSON avec Fernet+PBKDF2 optionnel
  - `GET /api/v1/export/json?mot_de_passe=...` → fichier `.json.enc`
  - `POST /api/v1/export/restaurer` déchiffrement automatique selon l'extension du fichier
22. ✅ **Intégration calendrier externe** : Google OAuth complet + iCal URL + multi-provider
  - Endpoints : `GET /api/v1/calendriers/google/auth-url`, `/google/callback`, `/google/sync`, `/google/status`
  - Providers supportés : `google`, `ical_url`, `apple`, `outlook` avec `sync_direction` bidirectionnel
  - Page UI : `/famille/calendriers` créée

---

## Court terme

### Qualité & stabilité

- [x] Atteindre 100 % des tests passing (✅ tests admin/recherche/rgpd créés, tests codes_barres/produit corrigés)
- [x] Routes maison complètes (DELETE projets, POST routine-repetitions, CRUD cellier déjà implémentés)
- [x] Ajouter les 3 routes dépenses/énergie (prévisions IA, consommation historique)
- [x] **CI/CD** : 8 workflows GitHub Actions validés + Vitest ajouté au gate
- [x] **Audit sécurité** : CORS (`CORS_ORIGINS` env var), rate limiting (60/min + 10/min IA), `NettoyeurEntrees` (XSS + SQLi), `SecurityHeadersMiddleware` (CSP, HSTS, X-Frame-Options) — tous actifs ✅

### Frontend

- [x] **PWA** : offline mode fonctionnel — `sw.js` v3 stale-while-revalidate + `manifest.json` + `EnregistrementSW` ✅
- [x] **Tests E2E Playwright** : 10 specs couvrant auth, recettes, courses, planning-ia, jules, projets-maison, navigation ✅
- [x] **Responsive** : audit mobile ✅ — sidebar, formulaires, tableaux corrigés
- [x] **Accessibilité** : `aria-label`, `aria-expanded`, `aria-current`, `scope="col"`, rôles ARIA ✅

---

## Moyen terme

### Fonctionnalités (mapping avec phases)

- [ ] **Notifications push** (abonnements push déjà câblés, logique d'envoi à compléter)  
  → *Phases Q (Rappels Famille), W (Jeu Responsable), AA (Entretien Prédictif)*

- [ ] **Collaboration temps réel courses** (WebSocket déjà implémenté, à tester multi-utilisateur)  
  → *Phase B (Planning→Courses), infrastructure existante*

- [ ] **Planning IA amélioré** (suggestions nutritionnelles, prise en compte historique)  
  → *Phases A (Planning IA), H (Nutrition), Z (Planning Maison IA)*

- [x] **Import recettes par URL ou PDF** (route URL/PDF active + enrichissement auto)  
  → ✅ *Phase L (Import enrichissement) — opérationnel*

- [ ] **Dashboard widgets configurables** (drag & drop, choix des métriques)  
  → *Phases N (Hub Famille), Y (Hub Maison), S (Dashboard Jeux)*

- [ ] **Suggestions IA contextuelles** (anti-gaspi, weekend, cadeaux, achats, value bets)  
  → *Phases J (Anti-gaspi), O (Activités Météo), P (Achats), T (Paris IA), U (Loto IA)*

- [x] **Moteurs contextuels** (agrégation famille/maison, briefing, alertes)  
  → ✅ *Phases M (Contexte Familial), X (Contexte Maison) — endpoints exposés et hubs connectés*

### Technique

- [x] **Cache Redis L2** — `src/core/caching/redis.py` opérationnel, s'active automatiquement si `REDIS_URL` défini. Recommandé : [Upstash](https://upstash.com) (free tier compatible Railway)
- [x] **Observabilité Sentry** — `sentry-sdk[fastapi,sqlalchemy]` configuré côté backend + frontend Next.js prêt. Activer en définissant `SENTRY_DSN` + `NEXT_PUBLIC_SENTRY_DSN`
- [x] **Métriques** — Endpoint `/metrics/prometheus` actif dans `main.py` (format Prometheus, lisible aussi sans Grafana)
- [x] **Tests de charge k6** — `tests/load/k6_baseline.js` (4 scénarios, seuils p95 < 500ms / 8s IA)
  → Lancer : `k6 run tests/load/k6_baseline.js`
- [x] Migration Alembic — **scaffolding prêt** (`alembic/`, `alembic.ini`, `env.py`, baseline `0001_`)
  → `GestionnaireMigrations` SQL-file conservé. Alembic prend le relais pour futures migrations incrémentales.
  → Initialiser : `alembic stamp head` (une seule fois sur DB existante)

---

## Backlog

> **5/5 items complétés** ✅ — Backlog soldé au 26 mars 2026

- [x] **Scan multi-codes simultané** — ✅ voir *Avancées complémentaires livrées* item 20  
  → `ScanneurMultiCodes` (ZXing, caméra live, déduplication) + `POST /api/v1/inventaire/barcode/batch` opérationnel
- [x] **OCR tickets de caisse** — ✅ voir *Avancées complémentaires livrées* item 19
- [x] **Export/import données complet** — ✅ voir *Avancées complémentaires livrées* item 21  
  → Fernet+PBKDF2 optionnel sur `GET /export/json` et `POST /export/restaurer`
- [x] **Intégration calendrier externe** — ✅ voir *Avancées complémentaires livrées* item 22  
  → Google OAuth + iCal + page UI `/famille/calendriers` opérationnelle
- [x] **Mode hors-ligne complet** — ✅ voir *Infrastructure & qualité* (`sw.js` v3 + IndexedDB sync queue)

---

## Principes

- **Pas de feature creep** : chaque ajout doit résoudre un besoin réel de la famille
- **Stabilité d'abord** : corriger les bugs et tests avant d'ajouter des fonctionnalités
- **Documentation à jour** : toute nouvelle feature = mise à jour du guide et de l'API reference
- **Sécurité** : RLS Supabase, JWT, rate limiting, sanitization — non négociables
