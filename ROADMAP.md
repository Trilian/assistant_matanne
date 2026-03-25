# 🗺️ ROADMAP — Assistant Matanne

> Dernière mise à jour : 25 mars 2026

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

### État global (25 mars 2026)

| Statut | Nombre | Pourcentage | Description |
|--------|--------|-------------|-------------|
| ✅ **COMPLÈTES** | **1/28** | **4%** | Tous éléments implémentés et fonctionnels |
| 🔄 **PARTIELLES** | **21/28** | **75%** | Infrastructure backend + frontend basique |
| ❌ **NON IMPLÉMENTÉES** | **6/28** | **21%** | Aucun élément trouvé |

### Par module

- **🍽️ Cuisine (A-L)** : 0/12 complètes, 6/12 partielles, 6/12 non implémentées
- **👨‍👩‍👦 Famille (M-R)** : 0/6 complètes, 4/6 partielles, 2/6 non implémentées  
- **🎮 Jeux (S-W)** : 0/5 complètes, 5/5 partielles, 0/5 non implémentées
- **🏡 Maison (X-AB)** : 0/5 complètes, 3/5 partielles, 2/5 non implémentées
- **🧭 Navigation (AC)** : 1/5 complètes, 0/5 partielles, 4/5 non implémentées

### Phases prioritaires

#### 🚀 P0 — Impact Immédiat (Débloquants)

1. **Exposer les moteurs contextuels** (Phases M, X)
   - `GET /api/v1/famille/contexte` — ContexteFamilialService prêt
   - `GET /api/v1/maison/briefing` — ContexteMaisonService prêt
   - **Impact** : Débloque toutes les phases Famille/Maison

2. **Exposer les services IA** (Phases M, S, J)
   - `POST /api/v1/weekend/suggestions-ia` — WeekendAIService prêt
   - `POST /api/v1/jeux/dashboard` — SeriesService + ValueBets prêts
   - `POST /api/v1/anti-gaspillage/suggestions-ia` — Service prêt
   - **Impact** : Valeur utilisateur immédiate

3. **Flux Planning→Courses** (Phase B)
   - `POST /api/v1/courses/generer-depuis-planning` avec soustraction inventaire
   - **Impact** : Débloque flux cuisine complet

#### 📊 P1 — Refonte UX (Visible)

4. **Refondre les hubs** (Phases N, Y, S)
   - Hub Famille contextuel (CarteAnniversaire, CarteMeteoActivites, CarteSuggestionAchats)
   - Hub Maison contextuel (CarteGaranties, CarteEntretien, CarteJardin)
   - Dashboard Jeux opportunités (CarteValueBets, CarteSeries, CartePredictions)
   - **Impact** : UX transformée — "ça pop que quand c'est utile"

5. **Finaliser Phase Z** (Planning Maison)
   - Planning semaine IA (répartition intelligente tâches ménage/entretien/jardin)
   - **Impact** : 60% déjà fait (page ménage bien implémentée)

#### 🔧 P2 — Finalisation (Polissage)

6. **Automatisation**
   - Jobs cron (push notifications, alertes, entretien saisonnier)
   - Déclencheurs IA (anniversaires J-14, jalons bébé, saison jardin)

7. **Phase AC** (Navigation unifiée)
   - Ma Semaine trans-modules (repas + tâches maison + activités famille + matchs jeux)
   - Outils contextuels (FAB chat IA, minuteur flottant, convertisseur inline)
   - Sidebar simplifiée (4 modules uniquement)

### Constat clé

**Backend MASSIF** (5000+ LOC services jeux, 2 moteurs contextuels complets, 35+ tables maison, catalogues JSON riches) mais **sous-exploité** :
- 60% des endpoints API manquants (services prêts mais pas exposés)
- 70% pages frontend statiques (grilles CRUD au lieu de hubs contextuels)
- 80% IA backend non exploitée

**L'effort principal doit porter sur l'exposition API et la refonte UX contextuelle** — le backend est déjà prêt à 90%.

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
