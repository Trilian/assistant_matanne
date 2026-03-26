# 📊 État d'Implémentation des 28 Phases — Assistant Matanne

> **Dernière mise à jour** : 26 mars 2026 (session infrastructure & qualité)  
> **Audit réalisé** : Scan complet du codebase (backend routes, services, modèles + frontend pages, composants, API clients)

---

## 🏗️ Infrastructure & Qualité Technique

> Ces items ne correspondent pas aux phases A-AC (features applicatives) mais sont trackés ici pour visibilité globale.

| Item | Statut | Notes |
|------|--------|-------|
| **Sentry backend** | ✅ Configuré | `FastApiIntegration` + `SqlalchemyIntegration` + `LoggingIntegration` — activer `SENTRY_DSN` sur Railway |
| **Sentry frontend** | ✅ Configuré | `sentry.client.config.ts` prêt — activer `NEXT_PUBLIC_SENTRY_DSN` sur Vercel |
| **CI/CD GitHub Actions** | ✅ Opérationnel | 8 workflows, Vitest ajouté au gate `deploy.yml` |
| **PWA offline mode** | ✅ Opérationnel | `sw.js` v3 stale-while-revalidate, `EnregistrementSW` dans root layout |
| **Tests E2E Playwright** | ✅ Opérationnel | 10 specs : auth, recettes, courses, planning-ia, jules, projets, navigation |
| **Cache Redis L2** | ✅ Prêt | Auto-détecté via `REDIS_URL` — recommandé : Upstash (free tier Railway) |
| **Prometheus / Grafana** | ✅ Configuré | `docker-compose.monitoring.yml` + `prometheus.yml` + dashboard JSON auto-provisionné |
| **Tests de charge k6** | ✅ Créé | `tests/load/k6_baseline.js` — 4 scénarios, seuils p95 < 500ms / 8s IA |
| **Migration V002 user_id** | ✅ Créé | `sql/migrations/002_standardize_user_id_uuid.sql` — application manuelle Supabase |
| **Audit sécurité** | ✅ Validé | CORS, rate limiting (60/min + 10/min IA), `NettoyeurEntrees`, `SecurityHeadersMiddleware` |
| **Responsive mobile** | 🔄 À faire | Audit Chrome DevTools (sidebar, formulaires, tableaux) |
| **Accessibilité ARIA** | 🔄 À faire | `jest-axe`, focus-trap modals, `aria-label`, contrastes 4.5:1 |
| **Migration Alembic** | ❌ Won't do | Système SQL-file maison conservé (`GestionnaireMigrations`) |
| **Multi-famille** | ❌ Won't do | Hors scope définitif |

---

## 🎯 Vue d'ensemble

**Progrès global** : 7/28 phases complètes (25%), 18/28 partielles (64%), 3/28 non implémentées (11%)

Les 28 phases correspondent au plan de refonte complet de l'application, organisé par module :
- **Cuisine (A-L)** : 12 phases — Flux repas, batch cooking, nutrition, anti-gaspi
- **Famille (M-R)** : 6 phases — Moteur contextuel, hub intelligent, activités météo, achats IA
- **Jeux (S-W)** : 5 phases — Dashboard, paris IA, loto/euromillions stats, jeu responsable
- **Maison (X-AB)** : 5 phases — Moteur contextuel, hub, planning universel, entretien prédictif
- **Navigation (AC)** : 4 sous-phases — Planning central, outils contextuels, paramètres discrets, sidebar simplifiée

### Légende des statuts

- ✅ **COMPLÈTE** : Tous les éléments implémentés et fonctionnels (backend + frontend + intégration)
- 🔄 **PARTIELLE** : Infrastructure backend existe, mais endpoints API manquants ou frontend basique
- ❌ **NON IMPLÉMENTÉE** : Aucun élément trouvé dans le codebase

---

## 🍽️ MODULE CUISINE (Phases A-L)

### Phase A : Réparer & Connecter le Planning 🔄 PARTIELLE

**Objectif** : Unifier les 2 pages planning, réparer le bouton "✨ IA", créer dialog sélecteur de recettes

**Ce qui existe** :
- ✅ Endpoint `POST /api/v1/planning/generer` fonctionnel
- ✅ Service `PlanningService.generer_planning_ia()` opérationnel (BaseAIService)
- ✅ Page `/cuisine/planning` avec grille semaine + navigation
- ✅ Modèle `Repas` avec `recette_id` FK

**Ce qui manque** :
- ❌ Dialog sélecteur recettes intelligent (recherche + suggestions + "Surprise du chef")
- ❌ Endpoint `GET /api/v1/suggestions/repas-rapide` pour suggestions contextuelles
- ❌ Redirection `/planning/` → `/cuisine/planning/` (2 pages existent encore)

**Fichiers clés** :
- `src/api/routes/planning.py` : Endpoint generer ✅
- `src/services/planning/service.py` : Service IA ✅
- `frontend/src/app/(app)/cuisine/planning/page.tsx` : Page principale ✅

---

### Phase B : Planning → Courses en 1 Clic ✅ COMPLÈTE ⚡ **CONFIRMÉ EXISTANT**

**Objectif** : Générer liste de courses depuis le planning avec soustraction inventaire

**Ce qui existe** :
- ✅ Endpoint `POST /api/v1/courses/generer-depuis-planning` — implémentation complète avec soustraction inventaire et agrégation par rayon
- ✅ Service `agregation.py` avec agrégation ingrédients + tri par rayon
- ✅ Modèle `ArticleInventaire` avec `quantite`, `quantite_min`
- ✅ WebSocket courses collaboration temps réel
- ✅ Logique soustraction inventaire dans l'agrégation
- ✅ Bouton "Générer les courses" côté frontend dans le planning

**Impact** : Flux planning→courses fonctionnel

---

### Phase C : Mode Préparation ❌ NON IMPLEMENTÉE

**Objectif** : Générer session batch cooking depuis planning, choix batch/jour par jour, rappels prépa

**Ce qui existe** :
- ✅ Page `/cuisine/batch-cooking` existe
- ✅ Modèle `SessionBatchCooking` avec `planning_id` FK
- ✅ Service `BatchCookingService`

**Ce qui manque** :
- ❌ Endpoint `POST /api/v1/batch-cooking/generer-depuis-planning` absent
- ❌ Dialog choix mode (batch vs jour par jour)
- ❌ Système de rappels jour par jour
- ❌ Lien planning→batch pas exploité

**Impact** : Batch cooking existe mais déconnecté du planning

---

### Phase D : Flux Unifié "Ma Semaine" 🔄 PARTIELLE ⚡ **AVANCÉE CETTE SESSION**

**Objectif** : Page stepper 4 étapes (Planning → Inventaire → Courses → Récap)

**Ce qui existe** :
- ✅ **NOUVEAU** : Page `/cuisine/ma-semaine` avec stepper 4 étapes complet (580 lignes)
- ✅ **NOUVEAU** : Lien "Ma Semaine" ajouté au hub cuisine
- ✅ Integration TanStack Query (queries + mutations)
- ✅ Validation navigation par étape (`peutAvancer`)

**Ce qui manque** :
- ❌ Refonte dashboard cuisine (widget "Ma Semaine")
- ❌ Onboarding popup première utilisation

**Fichiers clés** :
- `frontend/src/app/(app)/cuisine/ma-semaine/page.tsx` ✅ NOUVEAU
- `frontend/src/app/(app)/cuisine/page.tsx` ✅ MODIFIÉ (lien ajouté)

**Impact** : **Phase quasi-complète** — Refonte majeure, UX améliorée

---

### Phase E : Corriger les Recettes 🔄 PARTIELLE

**Objectif** : CRUD recettes robuste (ingrédients/étapes), favoris, notation, nutritioniste

**Ce qui existe** :
- ✅ Schémas Pydantic complets (`RecetteCreate`, `RecettePatch`, `RecetteResponse`)
- ✅ Helpers `_sauvegarder_ingredients()`, `_sauvegarder_etapes()`, `_serialiser_recette()`
- ✅ CRUD complet (GET, POST, PUT, PATCH liste/détail)
- ✅ Import URL fonctionnel via `RecipeImportService`
- ✅ Page détail recette avec ingrédients/étapes

**Ce qui manque** :
- ❌ Endpoints favoris manquants (`POST /{id}/favori`, `DELETE /{id}/favori`) mentionnés dans phase_e_completion.md mais **à vérifier dans routes actuelles**
- ❌ Endpoint notation (`POST /{id}/noter`)
- ❌ Page nutritionniste (`/outils/nutritionniste`) existe mais basique

**Impact** : CRUD solide, favoris/notation à exposer via API

---

### Phase F : Batch Cooking Sélection 🔄 PARTIELLE

**Objectif** : Sélecteur recettes from planning, vue détail session, préparations stockées

**Ce qui existe** :
- ✅ Page `/cuisine/batch-cooking` avec liste sessions
- ✅ Service `BatchCookingService` complet
- ✅ Modèle `SessionBatchCooking` avec relations `PreparationBatch`

**Ce qui manque** :
- ❌ Sélecteur recettes depuis planning absent
- ❌ Page détail session `/cuisine/batch-cooking/[id]` absente
- ❌ Vue préparations stockées (congélateur) absente

**Impact** : Batch cooking existe mais UX limitée

---

### Phase G : Maison Simplifiée ✅ ABSORBÉE

**Objectif** : Simplifier maison (retiré de cette phase)

**Statut** : Fonctionnalité absorbée par **Phase Y (Hub Maison Contextuel)**

---

### Phase H : Nutrition & Diététique ❌ NON IMPLEMENTÉE

**Objectif** : Profil diététique, calcul macro automatique, dashboard nutrition, Nutri-Score

**Ce qui existe** :
- ✅ Table nutrition_table.json existe avec 47 ingrédients (créée cette session)
- ✅ Modèle `Recette` avec champs nutrition (calories, proteines, lipides, glucides)
- ✅ Service d'enrichissement nutrition existe (`enrichers.py`)

**Ce qui manque** :
- ❌ Service `enrichir_nutrition_recette()` standalone (existe dans enrichers mais pas exposé)
- ❌ Profil diététique utilisateur structuré
- ❌ Dashboard nutritionnel hebdomadaire
- ❌ Calcul Nutri-Score automatique
- ❌ Badge nutrition sur recettes

**Impact** : Infrastructure existe mais pas exploitée UI

---

### Phase I : Bio, Local & Éco-responsable 🔄 PARTIELLE

**Objectif** : Badges Eco/Nutri/NOVA, auto-enrichissement scan, saisonnalité

**Ce qui existe** :
- ✅ Service `OpenFoodFactsService` opérationnel
- ✅ Fichier `produits_de_saison.json` (65 produits)
- ✅ Tags bio/local dans modèle `Recette`
- ✅ Service enrichissement bio/local (`BioLocalTagger` dans enrichers.py)

**Ce qui manque** :
- ❌ Badges Eco/Nutri/NOVA sur inventaire absents
- ❌ Auto-enrichissement scan code-barres incomplet
- ❌ Affichage saisonnalité dans inventaire

**Impact** : Backend riche, frontend basique

---

### Phase J : Anti-Gaspillage Intelligent 🔄 PARTIELLE ⚡ **AVANCÉE CETTE SESSION**

**Objectif** : Suggestions IA restes, gamification, historique gaspillage

**Ce qui existe** :
- ✅ Service `AntiGaspillageService` complet avec scoring
- ✅ Route `GET /api/v1/anti-gaspillage/suggestions`
- ✅ **NOUVEAU** : Route `POST /api/v1/anti-gaspillage/suggestions-ia` — appel IA avec produits urgents
- ✅ Modèle `EvenementGaspillage` avec gamification

**Ce qui manque** :
- ❌ Historique gaspillage non exposé API
- ❌ Gamification (badges) non affichée frontend

**Impact** : Service IA exposé via endpoint, historique et badges restent à câbler

---

### Phase K : Photo-Frigo Amélioré 🔄 PARTIELLE ⚡ **AVANCÉE CETTE SESSION**

**Objectif** : Sync ingrédients→inventaire, cross-référence recettes DB, multi-zone

**Ce qui existe** :
- ✅ Page `/cuisine/photo-frigo` avec upload + analyse IA
- ✅ Service `MultimodalService` (Pixtral vision)
- ✅ Endpoint `POST /api/v1/suggestions/photo-frigo`
- ✅ Cross-référence recettes DB (retour `recettes_db`)
- ✅ Analyse multi-zone côté API (`zones=frigo&zones=placard&...`)
- ✅ Sélection multi-zone côté UI sur `/cuisine/photo-frigo`

**Ce qui manque** :
- ❌ Sync automatique ingrédients détectés → inventaire


**Impact** : Analyse photo-frigo beaucoup plus exploitable (multi-zone + recettes DB), reste l'auto-sync inventaire

---

### Phase L : Enrichissement Import 🔄 PARTIELLE ⚡ **AVANCÉE CETTE SESSION**

**Objectif** : Auto-enrichissement nutrition, saisonnalité, météo après import

**Ce qui existe** :
- ✅ **NOUVEAU** : Service `RecipeEnricher` complet (350+ lignes) avec 4 enrichers
  - `NutritionEnricher` : Calcul calories/proteines/lipides/glucides
  - `BioLocalTagger` : Détection bio/local + saisonnalité
  - `RecipeClassifier` : Tags auto (rapide, batch, congelable, bebe, equilibre)
  - `ApplianceDetector` : Détection Cookeo/Airfryer/Monsieur Cuisine
- ✅ **NOUVEAU** : `data/reference/nutrition_table.json` (47 ingrédients)
- ✅ **NOUVEAU** : Route `POST /api/v1/recettes/import-pdf` fonctionnelle avec enrichissement
- ✅ **NOUVEAU** : Route `POST /api/v1/recettes/import-url` enrichie
- ✅ **NOUVEAU** : Frontend PDF tab activé dans `dialogue-import-recette.tsx`

**Ce qui manque** :
- ❌ Auto-enrichissement saisonnier dans planning IA absent
- ❌ Intégration météo suggestions absente
- ❌ Table nutrition incomplète (47 items, cible 200+)

**Fichiers clés** :
- `src/services/cuisine/recettes/enrichers.py` ✅ NOUVEAU
- `src/api/routes/recettes.py` ✅ MODIFIÉ (import-pdf + import-url)
- `frontend/src/composants/cuisine/dialogue-import-recette.tsx` ✅ MODIFIÉ

**Impact** : **Phase quasi-complète** — Enrichissement automatique opérationnel

---

## 👨‍👩‍👦 MODULE FAMILLE (Phases M-R)

### Phase M : Moteur de Contexte Familial ✅ COMPLÈTE ⚡ **FINALISÉE CETTE SESSION**

**Objectif** : Backend engine qui agrège météo, jours fériés, crèche, push, services IA

**Ce qui existe** :
- ✅ Service `ContexteFamilialService` **COMPLET** (267 lignes)
  - `construire_contexte_aujourd_hui()` : agrège tout
  - `obtenir_evenements_importants()` : anniversaires, documents, budget
  - `suggerer_activites_weekend()` : IA + météo
  - `generer_idees_cadeaux()` : IA anniversaires proches
  - Intégrations : Open-Meteo, jours fériés, services Jules/Weekend/Budget
- ✅ Service `JulesAIService` complet (jalons, sommeil, nutrition, suggestions activités)
- ✅ Service `WeekendAIService` complet (suggestions météo-aware)
- ✅ Service push ntfy.sh opérationnel
- ✅ Modèles riches (JalonEnfant, Routine, ActiviteFamille, Evenement, etc.)

**Ce qui existe** :
- ✅ Endpoint `GET /api/v1/famille/contexte` exposé
- ✅ Endpoint `POST /api/v1/weekend/suggestions-ia` exposé
- ✅ Endpoint `POST /api/v1/famille/journal/resume-semaine` exposé
- ✅ Endpoints achats famille exposés
- ✅ Push notifications famille planifiées via jobs cron APScheduler

**Impact** : Backend contextuel famille entièrement exploitable côté frontend

---

### Phase N : Hub Famille Intelligent ✅ COMPLÈTE ⚡ **DÉJÀ IMPLÉMENTÉE DANS LE CODEBASE**

**Objectif** : Refonte hub famille en dashboard contextuel (sections "Aujourd'hui", "À venir", "L'IA suggère")

**Ce qui existe** :
- ✅ Page `/famille` refondue en dashboard contextuel
- ✅ Sections dynamiques `Aujourd'hui`, `À venir`, `L'IA suggère`, modules, contexte Jules
- ✅ Composants contextuels présents : `CarteAnniversaire`, `CarteDocumentExpire`, `CarteJourSpecial`, `CarteSuggestionIA`, `BandeauMeteo`
- ✅ Toasts urgences à l'ouverture (anniversaires/documents J-2)

**Impact** : Hub famille vivant et contextuel, consommant directement `GET /api/v1/famille/contexte`

---

### Phase O : Activités Météo-Intelligentes 🔄 PARTIELLE ⚡ **AVANCÉE CETTE SESSION**

**Objectif** : Auto-injection météo dans activités, détection journée libre, suggestions IA contextualised

**Ce qui existe** :
- ✅ Endpoint `POST /api/v1/famille/activites/suggestions-ia-auto` (météo + âge + journée libre auto)
- ✅ Endpoint `POST /api/v1/weekend/suggestions-ia` exposé
- ✅ Page `/famille/activites` avec dialogue IA contextuel
- ✅ Affichage explicite du contexte détecté (météo + journée libre) dans l'UI

**Ce qui manque** :
- ❌ Suggestions inline directement dans le formulaire de création (pré-remplissage auto)

**Impact** : Suggestions activités réellement contextuelles, reste le pré-remplissage direct

---

### Phase P : Achats & Cadeaux Auto-Suggérés 🔄 PARTIELLE

**Objectif** : Suggestions IA achats (anniversaires, saison, jalons), déclencheurs automatiques

**Ce qui existe** :
- ✅ Page `/famille/achats` avec liste + filtres
- ✅ Modèle `AchatFamille` complet (categorie, priorite, destinataire_id, jalon_id, date_limite)
- ✅ CRUD achats fonctionnel

**Ce qui manque** :
- ❌ Service `AchatsIAService` absent
- ❌ Déclencheurs automatiques (anniversaire J-14, jalon bébé, saison)
- ❌ Endpoints API achats famille :
  - `POST /api/v1/famille/achats/suggestions` (IA)
  - `GET /api/v1/famille/achats`
  - `POST /api/v1/famille/achats`
- ❌ Suggestions inline hub famille

**Impact** : Page existe, pas d'IA

---

### Phase Q : Rappels Intelligents 🔄 PARTIELLE

**Objectif** : Affichage badges urgence hub, notifications push automatiques

**Ce qui existe** :
- ✅ Service `ServiceRappelsFamille` opérationnel
- ✅ Infrastructure ntfy.sh fonctionnelle
- ✅ Modèles riches (documents, budgets, activités, crèche)

**Ce qui manque** :
- ❌ Endpoint `GET /api/v1/famille/rappels/evaluer` absent
- ❌ Badges urgence hub famille absents
- ❌ Push automatiques non déclenchés (job cron manquant)

**Impact** : Backend prêt, pas affiché UI

---

### Phase R : Journal IA & Album Jalons 🔄 PARTIELLE

**Objectif** : Résumé hebdo IA, lien album↔jalons, graphique croissance OMS

**Ce qui existe** :
- ✅ Page `/famille/journal` avec entrées quotidiennes
- ✅ Page `/famille/album` avec photos
- ✅ Modèle `SouvenirFamille.jalon_id` FK existe
- ✅ Service Jules avec jalons détaillés

**Ce qui manque** :
- ❌ Endpoint `POST /api/v1/famille/journal/resumer-semaine` (IA) absent
- ❌ Lien album↔jalons non exploité frontend
- ✅ Graphique croissance OMS (courbes percentiles) présent sur `/famille/jules`
- ❌ Résumés hebdo IA non affichés

**Impact** : Pages existent, features avancées absentes

---

## 🎮 MODULE JEUX (Phases S-W)

### Phase S : Dashboard Jeux & Câblage ✅ COMPLÈTE ⚡ **DÉJÀ IMPLÉMENTÉE DANS LE CODEBASE**

**Objectif** : Dashboard jeux opportunités (value bets, séries, alertes IA), endpoints backend

**Ce qui existe** :
- ✅ Page `/jeux` refondue en dashboard avec budget, value bets, séries et KPIs
- ✅ Endpoints `GET /api/v1/jeux/dashboard`, `GET /api/v1/jeux/series`, `GET /api/v1/jeux/paris/predictions/{id}`, `GET /api/v1/jeux/paris/value-bets`
- ✅ **Backend MASSIF** :
  - `SeriesService` (loi des séries, stats n-grammes)
  - `PredictionServiceJeux` (modèle prédictif local)
  - `BacktestService` (simulateur ROI)
  - `value_bets.py` (détection value bets)
  - 13 modèles DB (Pari, Match, Equipe, Serie, ValueBet, Ticket, etc.)

**Impact** : Backend jeux câblé au frontend, dashboard opportunités disponible

---

### Phase T : Paris Sportifs Intelligents 🔄 PARTIELLE

**Objectif** : Prédictions inline, value bets, OCR tickets, analytics championnat/confiance

**Ce qui existe** :
- ✅ Page `/jeux/paris` avec CRUD paris
- ✅ Page `/jeux/performance` avec stats globales
- ✅ Service prédictions local (forme, H2H, cotes)
- ✅ Service value bets opérationnel

**Ce qui manque** :
- ❌ Prédictions inline dans formulaire pari
- ❌ Section value bets absente
- ✅ **NOUVEAU** Endpoint `POST /api/v1/jeux/ocr-ticket` (Pixtral) exposé
- ❌ Analytics par championnat/confiance absents
- ❌ Heatmap cotes bookmakers absente

**Impact** : OCR ticket désormais disponible, mais l'intelligence inline/analytics reste à finaliser

---

### Phase U : Loto & Euromillions IA 🔄 PARTIELLE

**Objectif** : Heatmap fréquences, grilles IA pondérées séries, backtest

**Ce qui existe** :
- ✅ Pages `/jeux/loto` et `/jeux/euromillions` avec formulaires
- ✅ Service stats/séries backend opérationnel
- ✅ Modèles Tirage/Serie complets

**Ce qui manque** :
- ❌ Heatmap fréquences numéros absente
- ❌ Générateur grilles IA (pondération séries) absent
- ✅ **NOUVEAU** Endpoint backtest simulation exposé (`GET /api/v1/jeux/backtest?type_jeu=loto|euromillions|paris`)
- ❌ Analyse IA grilles joueur absente

**Impact** : Backtest disponible côté API, reste à enrichir la visualisation et les stratégies IA

---

### Phase V : Performance & Vision 🔄 PARTIELLE

**Objectif** : Breakdown performance (championnat/type/confiance), résumé mensuel IA, OCR tickets loto

**Ce qui existe** :
- ✅ Page `/jeux/performance` avec ROI global
- ✅ Service `BacktestService` opérationnel
- ✅ Données riches (paris, séries, value bets)

**Ce qui manque** :
- ❌ Breakdown par championnat/type/confiance absent
- ❌ Résumé mensuel IA absent
- ✅ **NOUVEAU** OCR tickets loto/euromillions exposé (`POST /api/v1/jeux/ocr-ticket`)
- ❌ Graphiques évolution ROI/bankroll absents

**Impact** : Vision OCR en place, mais drill-down performance encore à construire

---

### Phase W : Jeu Responsable 🔄 PARTIELLE

**Objectif** : Notifications push séries/résultats, middleware budget, auto-exclusion

**Ce qui existe** :
- ✅ Page `/jeux/responsable` avec limites
- ✅ Service `ResponsableGamingService` complet
- ✅ Modèle `LimiteJeu` avec tracking

**Ce qui manque** :
- ❌ Notifications push séries/résultats absentes
- ❌ Guard middleware budget (bloque paris si limite atteinte) absent
- ❌ Auto-exclusion interface incomplète
- ❌ Alertes série dangereuse absentes

**Impact** : Page statique, contrôles backend non appliqués

---

## 🏡 MODULE MAISON (Phases X-AB)

### Phase X : Moteur de Contexte Maison ✅ COMPLÈTE ⚡ **FINALISÉE CETTE SESSION**

**Objectif** : Backend engine agrégation 35+ tables, alertes, briefing, entretien saisonnier

**Ce qui existe** :
- ✅ Service `ContexteMaisonService` **COMPLET** (estimé 400+ LOC)
  - `construire_briefing_maison()` : agrège tout
  - `obtenir_alertes()` : garanties, contrats, diagnostics, entretien
  - `obtenir_taches_aujourdhui()` : ménage, entretien, projets, jardin
  - Catalogues JSON : entretien (19 KB), plantes (54 KB), travaux, domotique, lessive
- ✅ 35+ tables SQL (projets, contrats, garanties, diagnostics, entretien, jardin, domotique)
- ✅ Services JardinService, ProjetService riches

**Ce qui existe** :
- ✅ Endpoint `GET /api/v1/maison/briefing` exposé
- ✅ Endpoint `GET /api/v1/maison/alertes` exposé
- ✅ Push notifications maison planifiées via jobs cron APScheduler
- ✅ Entretien saisonnier hebdomadaire planifié

**Impact** : Backend contextuel maison entièrement exploitable côté frontend

---

### Phase Y : Hub Maison Contextuel ✅ COMPLÈTE ⚡ **DÉJÀ IMPLÉMENTÉE DANS LE CODEBASE**

**Objectif** : Refonte hub maison en dashboard contextuel ("Aujourd'hui", "Alertes", "Projets")

**Ce qui existe** :
- ✅ Page `/maison` refondue en briefing contextuel quotidien
- ✅ Sections dynamiques : alertes, tâches du jour, indicateurs et accès projet/maison
- ✅ Consommation de `obtenirBriefingMaison`, `envoyerRappelsMaison`, `statsHubMaison`
- ✅ Actions directes depuis le hub

**Impact** : Hub maison contextuel opérationnel et branché au backend

---

### Phase Z : Planning Maison Universel ✅ COMPLÈTE ⚡ **CONFIRMÉ EXISTANT**

**Objectif** : Planning semaine IA (ménage/entretien/travaux/jardin), appareils à cycle, routines matin/soir, fiches tâches

**Ce qui existe** :
- ✅ Page `/maison/menage` complète :
  - Zones/pièces/tâches organisées
  - Référence `guide_travaux_courants.json` (107 KB)
  - Référence `guide_lessive.json` (35 KB)
  - Référence `astuces_domotique.json` (19 KB)
  - Référence `routines_defaut.json`
- ✅ Endpoint `GET /api/v1/maison/menage/planning-semaine`
- ✅ Endpoint `GET /api/v1/maison/taches-jour`
- ✅ Composant `TimerAppareil` (lave-linge, lave-vaisselle, sèche-linge)
- ✅ Composant `DrawerFicheTache` (étapes détaillées + produits + durée)
- ✅ Répartition hebdomadaire et tâches du jour côté frontend

**Fichiers clés** :
- `frontend/src/app/(app)/maison/menage/page.tsx` ✅
- `data/reference/guide_travaux_courants.json` ✅
- `data/reference/guide_lessive.json` ✅
- `data/reference/astuces_domotique.json` ✅

**Impact** : Planning maison hebdomadaire utilisable avec routines, tâches et fiches détaillées

---

### Phase AA : Entretien Prédictif & Garanties 🔄 PARTIELLE ⚡ **AVANCÉE CETTE SESSION**

**Objectif** : Entretien saisonnier auto, alertes durée de vie appareils, actions intelligentes garanties

**Ce qui existe** :
- ✅ Table `entretiens_saisonniers` existe
- ✅ Catalogue entretien avec `duree_vie_ans` existe
- ✅ Modèles Garantie, Contrat, Diagnostic riches

**Ce qui existe** :
- ✅ Entretien saisonnier automatique via job cron hebdomadaire
- ✅ Endpoint `GET /api/v1/maison/garanties/alertes-predictives`
- ✅ Carte hub maison "Garanties & durée de vie prévisionnelle"
- ✅ Actions intelligentes via redirection vers la fiche garantie

**Ce qui manque** :
- ❌ Workflow complet "faire jouer garantie" / "contacter SAV" en 1 clic avec action backend dédiée

**Impact** : Prédictif opérationnel, reste le flux d'action SAV totalement guidé

---

### Phase AB : Jardin & Énergie Contextuels 🔄 PARTIELLE

**Objectif** : Jardin contextuel hub (saison plantes), énergie anomalies, cellier intelligent

**Ce qui existe** :
- ✅ Service `JardinService` opérationnel
- ✅ Catalogue plantes complet (54 KB, 200+ plantes)
- ✅ Page `/maison/jardin` fonctionnelle
- ✅ Page `/maison/energie` avec graphiques
- ✅ Page `/maison/cellier` avec stocks vins

**Ce qui existe** :
- ✅ Cartes hub maison pour jardin contextuel
- ✅ Cartes hub maison pour anomalies énergie
- ✅ Cartes hub maison pour alertes cellier (consommation/péremption)

**Ce qui manque** :
- ❌ Suggestions jardin saisonnières enrichies IA (au-delà des règles catalogues)
- ❌ Analyse énergie comparative avancée (tendance mensuelle/annuelle)

**Impact** : Contextualisation présente, enrichissements analytiques encore à pousser

---

## 🧭 MODULE NAVIGATION (Phase AC)

### Phase AC : Intégration Navigation 🔄 PARTIELLE

**Objectif** : Navigation unifiée — Planning central, outils contextuels, paramètres discrets, sidebar simplifiée

---

#### AC1 : Planning Hub Central ✅ COMPLÈTE ⚡ **IMPLÉMENTÉE CETTE SESSION**

**Objectif** : Page "Ma Semaine" unifiée (repas + tâches maison + activités famille + matchs jeux)

**Ce qui existe** :
- ✅ Page `/ma-semaine` unifiée multi-modules
- ✅ Endpoint `GET /api/v1/planning/semaine-unifiee`
- ✅ Agrégation repas + tâches maison + activités famille + matchs jeux
- ✅ Navigation par semaine avec liens vers les modules concernés

**Impact** : Vue transversale centralisée enfin disponible

---

#### AC2 : Outils Contextuels 🔄 PARTIELLE ⚡ **AVANCÉE CETTE SESSION**

**Objectif** : Chat IA flottant (FAB), minuteur flottant, convertisseur inline, command palette Ctrl+K

**Ce qui existe** :
- ✅ Pages outils existent (`/outils/*`)
- ✅ Page `/outils/chat-ia` fonctionnelle
- ✅ Page `/outils/minuteur` existe
- ✅ Page `/outils/convertisseur` existe
- ✅ `FabChatIA` omniprésent ajouté dans la coquille d'application
- ✅ `MinuteurFlottant` (barre persistante tant qu'un timer est actif)
- ✅ Menu commandes `Ctrl+K` déjà implémenté (AC5)

**Ce qui manque** :
- ❌ Convertisseur inline recettes

**Impact** : Chat contextuel disponible partout, reste à compléter pour minuteur/convertisseur

---

#### AC3 : Paramètres Discrets ✅ COMPLÈTE ⚡ **IMPLÉMENTÉE CETTE SESSION**

**Objectif** : Paramètres dans dropdown avatar header (retirés sidebar)

**Ce qui existe** :
- ✅ Dropdown avatar header avec accès paramètres et intégrations
- ✅ Préférences rapides dans le menu avatar
- ✅ Liens paramètres retirés de la sidebar principale

**Impact** : Paramètres discrets conformément au design cible

---

#### AC4 : Sidebar Simplifiée ✅ COMPLÈTE ⚡ **IMPLÉMENTÉE CETTE SESSION**

**Objectif** : Sidebar = uniquement 4 modules (Cuisine, Famille, Maison, Jeux) + Ma Semaine

**Ce qui existe** :
- ✅ Sidebar desktop simplifiée : `Accueil`, `Ma Semaine`, `Cuisine`, `Famille`, `Maison`, `Jeux`
- ✅ Outils retirés de la navigation principale (accès via FAB chat + page dédiée)
- ✅ Navigation mobile simplifiée avec `Ma Semaine`
- ✅ Paramètres déplacés vers le menu avatar (header)

**Impact** : Navigation plus lisible et centrée sur les 4 modules principaux

---

#### AC5 : Menu Commandes & Favoris ✅ COMPLÈTE ⚡ **IMPLÉMENTÉ CETTE SESSION**

**Objectif** : Command palette Cmd+K navigation rapide, favoris épinglables

**Ce qui existe** :
- ✅ **NOUVEAU** : `MenuCommandes` component avec Cmd+K (220+ lignes)
  - 60+ pages indexées avec keywords
  - Groupes par catégorie (Cuisine, Famille, Maison, etc.)
  - Récents (5 dernières visites)
  - LocalStorage historique (max 10)
- ✅ **NOUVEAU** : Système favoris complet :
  - `FavorisRapides` component sidebar
  - `BoutonEpingler` fil d'ariane
  - `utiliserFavoris()` hook
  - LocalStorage persistence
- ✅ **NOUVEAU** : Intégration coquille-app avec store UI

**Fichiers clés** :
- `frontend/src/composants/disposition/menu-commandes.tsx` ✅ NOUVEAU
- `frontend/src/composants/disposition/favoris-rapides.tsx` ✅ NOUVEAU
- `frontend/src/composants/disposition/bouton-epingler.tsx` ✅ NOUVEAU
- `frontend/src/composants/disposition/coquille-app.tsx` ✅ MODIFIÉ
- `frontend/src/composants/disposition/barre-laterale.tsx` ✅ MODIFIÉ
- `frontend/src/composants/disposition/fil-ariane.tsx` ✅ MODIFIÉ

**Impact** : **Navigation rapide opérationnelle** — UX améliorée

---

## 📈 SYNTHÈSE GLOBALE

### Par statut

| Statut | Nombre | Pourcentage | Description |
|--------|--------|-------------|-------------|
| ✅ **COMPLÈTES** | **11/28** | **39%** | Tous éléments implémentés et fonctionnels |
| � **QUASI-COMPLÈTES (≥80%)** | **3** *(inclus dans partielles)* | *(+11%)* | D, L, AA — 1 feature finale restante chacune |
| 🔄 **PARTIELLES** | **15/28** | **54%** | Infrastructure backend ou UX encore à finaliser |
| ❌ **NON IMPLÉMENTÉES** | **2/28** | **7%** | Aucun élément trouvé |

> **Couverture fonctionnelle pondérée** : ~70%  
> *(11 complètes × 1,0) + (3 quasi × 0,85) + (12 partielles × 0,5) = 19,55 / 28*

### Par module

| Module | Complètes | Partielles | Non implémentées | Taux complétion |
|--------|-----------|------------|------------------|-----------------|
| **🍽️ Cuisine (A-L)** | 1/12 | 9/12 dont 2 quasi | 2/12 | ~65% fonctionnel |
| **👨‍👩‍👦 Famille (M-R)** | 2/6 | 4/6 | 0/6 | ~71% fonctionnel |
| **🎮 Jeux (S-W)** | 1/5 | 4/5 | 0/5 | ~60% fonctionnel |
| **🏡 Maison (X-AB)** | 3/5 | 2/5 dont 1 quasi | 0/5 | ~82% fonctionnel |
| **🧭 Navigation (AC)** | 4/5 | 1/5 | 0/5 | ~90% fonctionnel |

*Note: Phase G absorbée par Phase Y ne compte pas dans les totaux*

---

## 🎯 CONSTATS CLÉS

### ✅ Forces actuelles

1. **Infrastructure backend MASSIVE** :
   - 22 services Jeux (5000+ LOC, prédictions, séries, value bets, backtest)
   - 2 moteurs contextuels complets (ContexteFamilialService, ContexteMaisonService)
   - 5 services IA famille (Jules, Weekend, Budget, Journal, Achats)
   - 35+ tables SQL maison avec catalogues JSON riches (entretien, plantes, travaux, domotique, lessive)

2. **Services IA prêts** :
   - BaseAIService (rate limiting, cache, parsing, streaming)
   - AnalyseurIA (parsing JSON/Pydantic)
   - CacheIA (cache sémantique)
   - Services domaine (Planning, Jules, Weekend, Anti-gaspi, Jardin, Projets)

3. **Catalogues données** :
   - `entretien_catalogue.json` (19 KB, 50+ équipements)
   - `plantes_catalogue.json` (54 KB, 200+ plantes)
   - `guide_travaux_courants.json` (107 KB)
   - `guide_lessive.json` (35 KB)
   - `astuces_domotique.json` (19 KB)
   - `produits_de_saison.json` (65 produits)
   - `nutrition_table.json` (47 ingrédients)

4. **Pages frontend** : Presque tous les modules ont leur page (42 routes)

---

### ❌ Gaps principaux

1. **Automatisation IA achats/rappels à finaliser** :
   - Phase P : déclencheurs automatiques cadeaux/achats (anniversaire J-14, jalons, saison)
   - Phase Q : endpoint d'évaluation des rappels + badges urgence consolidés

2. **Flux intelligents encore incomplets** :
   - Phase K : synchronisation auto OCR photo-frigo vers inventaire
   - Phase AC2 : convertisseur inline recettes manquant

3. **Jeux: profondeur analytique et garde-fous** :
   - Phases T/V : analytics avancés (championnat, confiance, breakdown ROI)
   - Phase W : middleware budget bloquant + auto-exclusion et alertes série

4. **Nutrition & diététique** :
   - Phase H reste majoritairement non exploitée côté UI (profil, dashboard, Nutri-Score)

5. **Qualité continue** :
   - Couverture tests à étendre sur routes restantes et parcours critiques
   - Validation CI/CD et durcissement production (sécurité/monitoring)

---

## 🎯 PRIORITÉS RECOMMANDÉES

### 🚀 P0 — Impact Immédiat (Débloquants)

1. **Automatiser Achats & Rappels** (Phases P, Q) :
   - Exposer/fiabiliser déclencheurs IA achats famille
   - Ajouter endpoint d'évaluation des rappels + badges urgence unifiés
   - **Impact** : transforme les modules famille en assistant proactif

2. **Finaliser flux OCR utiles au quotidien** (Phases K, AC2) :
   - Auto-sync photo-frigo → inventaire
   - Convertisseur inline dans les flux recettes/planning
   - **Impact** : gain de temps immédiat sur les parcours cuisine

3. **Renforcer jeu responsable** (Phase W) :
   - Guard budget côté API lors de création pari
   - Alertes série dangereuse + auto-exclusion effective
   - **Impact** : sécurité d'usage avant enrichissements analytiques

---

### 📊 P1 — Refonte UX (Visible)

4. **Approfondir l'intelligence Jeux** (Phases T, U, V) :
   - Analytics championnat/confiance
   - Visualisation backtest avancée et trajectoire bankroll
   - Prédictions inline plus prescriptives dans les formulaires
   - **Impact** : passe de "tableau" à "assistant décisionnel"

5. **Consolider les expériences déjà refondues** (Phases D, N, Y, AC) :
   - Polir les parcours multi-modules (Ma Semaine, hubs contextuels, OCR)
   - Compléter les CTA/action handlers manquants
   - **Impact** : UX homogène et sans impasses

---

### 🔧 P2 — Finalisation (Polissage)

6. **Nutrition & recommandations** (Phases H, L) :
   - Dashboard nutrition hebdo + Nutri-Score
   - Enrichissement saison/météo mieux exploité dans les suggestions

7. **Maison analytique** (Phase AB) :
   - Tendances énergie mensuelles/annuelles
   - Suggestions jardin saisonnières enrichies IA

8. **Qualité/ops** :
   - Campagnes de tests complémentaires backend/frontend
   - Observabilité et alerting production (Sentry/Prometheus)

---

## 📝 NOTES

### Phases complétées cette session (26 mars 2026)

- **Phase D** : Page `/cuisine/ma-semaine` stepper 4 étapes ✅
- **Phase M/X** : endpoints contextuels exposés + briefings hubs branchés ✅
- **Phase AC** : FAB chat + minuteur flottant + sidebar simplifiée + commandes/favoris ✅
- **Jeux/K** : OCR ticket, backtest euromillions et photo-frigo multi-zone ✅

### Phases quasi-complètes (>80%)

- **Phase D** : Flux unifié Ma Semaine (reste onboarding/dashboard cuisine)
- **Phase L** : Enrichissement import (reste profondeur nutrition/saison)
- **Phase AA** : Alertes prédictives garanties (reste workflow SAV 1-clic)

### Phases bloquantes

- **Phase P** : IA achats famille encore peu proactive
- **Phase W** : garde-fous jeu responsable incomplets
- **Phase H** : nutrition non déployée en parcours utilisateur

---

**Conclusion** : L'application a franchi le cap de l'**exposition API critique** et de la **refonte contextuelle des hubs/navigation**. Le prochain levier majeur est l'**automatisation proactive** (achats/rappels/jeu responsable), puis la **profondeur analytique** (jeux/énergie/nutrition) avec une montée continue de la qualité test/ops.
