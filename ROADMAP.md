# 🗺️ ROADMAP — Assistant Matanne

> Dernière mise à jour : 26 mars 2026 (session infrastructure & qualité)

---

## 🗓️ Priorités — 2 prochaines semaines (26 mars → 9 avril 2026)

> Focus : automatisation proactive + garde-fous + qualité test. Pas de nouvelle feature avant d'avoir ces 3 axes verts.

| # | Tâche | Phase | Effort | Impact |
|---|-------|-------|--------|--------|
| 1 | Guard budget pari (API) + alertes série dangereuse | W Jeu responsable | S | 🔴 Sécurité |
| 2 | Endpoint évaluation rappels + badges urgence hub famille | Q Rappels | M | 🔴 Proactif |
| 3 | Auto-sync OCR photo-frigo → inventaire (1 endpoint + bouton UI) | K Photo-frigo | S | 🟠 Quotidien |
| 4 | Déclencheurs IA achats famille (anniversaire J-14, jalons) | P Achats | M | 🟠 Proactif |
| 5 | Tests backend routes restantes (admin/recherche/rgpd) | — Qualité | M | 🟡 Stabilité |
| 6 | Convertisseur inline flux recettes | AC2 Outils | S | 🟡 UX |

*Effort : S = ½ journée, M = 1–2 jours. Impact : 🔴 bloquant/sécurité, 🟠 valeur utilisateur directe, 🟡 qualité/UX.*

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

### État global (26 mars 2026) — après P0+P1+P2 + priorités AC2/AC3/AA

| Statut | Nombre | Pourcentage | Description |
|--------|--------|-------------|-------------|
| ✅ **COMPLÈTES** | **11/28** | **39%** | Tous éléments implémentés et fonctionnels |
| � **QUASI-COMPLÈTES (≥80%)** | **3** *(dans partielles)* | *(+11%)* | D, L, AA — 1 feature finale restante |
| 🔄 **PARTIELLES** | **15/28** | **54%** | Infrastructure backend + frontend amélioré |
| ❌ **NON IMPLÉMENTÉES** | **2/28** | **7%** | Aucun élément trouvé |

> **Couverture fonctionnelle pondérée** : ~70% — 11 complètes + 3×0,85 quasi + 12×0,5 partielles sur 28 phases.

### Par module (après session P0+P1+P2)

- **🍽️ Cuisine (A-L)** : 1/12 complète (B Planning→Courses), 9 partielles, 2 non implémentées
- **👨‍👩‍👦 Famille (M-R)** : 2/6 complètes (M Contexte, N Hub), 4 partielles
- **🎮 Jeux (S-W)** : 1/5 complète (S Dashboard), 4 partielles
- **🏡 Maison (X-AB)** : 3/5 complètes (X Contexte, Y Hub, Z Planning), 2 partielles (AA, AB)
- **🧭 Navigation (AC)** : 4/5 complètes (AC1 Ma Semaine, AC3 Paramètres discrets, AC4 Sidebar, AC5 Menu commandes), 1 partielle (AC2)

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

---

## Court terme

### Qualité & stabilité

- [x] Atteindre 100 % des tests passing (✅ tests admin/recherche/rgpd créés, tests codes_barres/produit corrigés)
- [x] Routes maison complètes (DELETE projets, POST routine-repetitions, CRUD cellier déjà implémentés)
- [ ] Ajouter les 3 routes dépenses/énergie (prévisions IA, consommation historique)
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

- [ ] **Scan multi-codes simultané** — composant `ScanneurMultiCodes` (caméra live + déduplication) + endpoint `POST /api/v1/inventaire/barcode/batch` → intégré courses ET inventaire
- [x] **OCR tickets de caisse** — ✅ voir *Avancées complémentaires livrées* item 19
- [ ] **Export/import données complet** — backup JSON avec chiffrement Fernet+PBKDF2 optionnel (paramètre `mot_de_passe` sur `/export/json` et `/export/restaurer`)
- [ ] **Intégration calendrier externe** — page UI `/famille/calendriers` à créer (backend Google OAuth + iCal entièrement opérationnel)
- [x] **Mode hors-ligne complet** — ✅ voir *Infrastructure & qualité* (`sw.js` v3 + IndexedDB sync queue)

---

## Principes

- **Pas de feature creep** : chaque ajout doit résoudre un besoin réel de la famille
- **Stabilité d'abord** : corriger les bugs et tests avant d'ajouter des fonctionnalités
- **Documentation à jour** : toute nouvelle feature = mise à jour du guide et de l'API reference
- **Sécurité** : RLS Supabase, JWT, rate limiting, sanitization — non négociables
