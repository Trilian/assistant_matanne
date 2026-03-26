# 🗺️ ROADMAP — Assistant Matanne

> Dernière mise à jour : 26 mars 2026

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
- [ ] Standardiser user_id VARCHAR → UUID dans les tables existantes (migration V002, application manuelle)

---

## 📋 Système de Phases (28 phases A-AC)

> Voir [STATUS_PHASES.md](STATUS_PHASES.md) pour le détail complet de l'implémentation

**Vue d'ensemble** : 28 phases organisées par module pour structurer la refonte complète de l'application.

### État global (26 mars 2026) — après P0+P1+P2 + priorités AC2/AC3/AA

| Statut | Nombre | Pourcentage | Description |
|--------|--------|-------------|-------------|
| ✅ **COMPLÈTES** | **11/28** | **39%** | Tous éléments implémentés et fonctionnels |
| 🔄 **PARTIELLES** | **15/28** | **54%** | Infrastructure backend + frontend amélioré |
| ❌ **NON IMPLÉMENTÉES** | **2/28** | **7%** | Aucun élément trouvé |

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

---

## Court terme

### Qualité & stabilité

- [ ] Atteindre 100 % des tests passing (8 tests restants = routes manquantes)
- [ ] Ajouter les 5 routes maison manquantes (DELETE projets, POST routine-repetitions, CRUD cellier-produit)
- [ ] Ajouter les 3 routes dépenses/énergie (prévisions IA, consommation historique)
- [ ] CI/CD : valider les workflows GitHub Actions (deploy.yml, tests.yml)
- [ ] Audit sécurité : valider les headers CORS, rate limiting, et sanitization en production

### Frontend

- [ ] PWA : offline mode fonctionnel (service worker + cache stratégique)
- [ ] Tests E2E Playwright : couverture des parcours critiques (auth, CRUD recettes, courses)
- [ ] Responsive : audit mobile (sidebar, formulaires, tableaux)
- [ ] Accessibilité : rôles ARIA, navigation clavier, contrastes

---

## Moyen terme

### Fonctionnalités (mapping avec phases)

- [ ] **Notifications push** (abonnements push déjà câblés, logique d'envoi à compléter)  
  → *Phases Q (Rappels Famille), W (Jeu Responsable), AA (Entretien Prédictif)*

- [ ] **Collaboration temps réel courses** (WebSocket déjà implémenté, à tester multi-utilisateur)  
  → *Phase B (Planning→Courses), infrastructure existante*

- [ ] **Planning IA amélioré** (suggestions nutritionnelles, prise en compte historique)  
  → *Phases A (Planning IA), H (Nutrition), Z (Planning Maison IA)*

- [ ] **Import recettes par URL ou PDF** (service `importer.py` existant, route à exposer)  
  → ✅ *Phase L (Import enrichissement) — PDF route activée, enrichissement auto opérationnel*

- [ ] **Dashboard widgets configurables** (drag & drop, choix des métriques)  
  → *Phases N (Hub Famille), Y (Hub Maison), S (Dashboard Jeux)*

- [ ] **Suggestions IA contextuelles** (anti-gaspi, weekend, cadeaux, achats, value bets)  
  → *Phases J (Anti-gaspi), O (Activités Météo), P (Achats), T (Paris IA), U (Loto IA)*

- [ ] **Moteurs contextuels** (agrégation famille/maison, briefing, alertes)  
  → *Phases M (Contexte Familial), X (Contexte Maison) — services 100% prêts, endpoints manquants*

### Technique

- [ ] Cache Redis L2 (actuellement L1 mémoire + L3 fichier, Redis optionnel)
- [ ] Observabilité Sentry (DSN déjà en config, intégration à activer)
- [ ] Prometheus / Grafana (métriques déjà collectées, dashboard à créer)
- [ ] Tests de charge (k6 ou locust sur les endpoints critiques)
- [ ] Migration Alembic (remplacer le système SQL-file maison)

---

## Backlog

- [ ] Multi-famille (plusieurs foyers dans la même instance)
- [ ] Scan multi-codes simultané (amélioration scanner codes-barres)
- [ ] Reconnaissance de tickets de caisse (OCR → import courses automatique)
- [ ] Export/import données complet (backup JSON)
- [ ] Intégration calendrier externe (Google Calendar sync bidirectionnelle)
- [ ] Mode hors-ligne complet avec synchronisation au retour en ligne
- [ ] Application mobile native (React Native ou Capacitor)

---

## Principes

- **Pas de feature creep** : chaque ajout doit résoudre un besoin réel de la famille
- **Stabilité d'abord** : corriger les bugs et tests avant d'ajouter des fonctionnalités
- **Documentation à jour** : toute nouvelle feature = mise à jour du guide et de l'API reference
- **Sécurité** : RLS Supabase, JWT, rate limiting, sanitization — non négociables
