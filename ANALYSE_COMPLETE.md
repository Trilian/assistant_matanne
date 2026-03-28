# 🔍 Analyse Complète — Assistant Matanne
> Généré le 28 mars 2026 · Codebase state: Sprint 7 terminé, Sprint 8-9 à planifier

---

## Table des Matières

1. [État Général](#1-état-général)
2. [Bugs Critiques & Anomalies](#2-bugs-critiques--anomalies)
3. [Gaps & Features Manquantes par Module](#3-gaps--features-manquantes-par-module)
4. [SQL — État & Consolidation](#4-sql--état--consolidation)
5. [Tests — Couverture & Lacunes](#5-tests--couverture--lacunes)
6. [Documentation — État & Lacunes](#6-documentation--état--lacunes)
7. [Interactions Intra-modules](#7-interactions-intra-modules)
8. [Interactions Inter-modules](#8-interactions-inter-modules)
9. [Opportunités IA](#9-opportunités-ia)
10. [Jobs Automatiques — État & Roadmap](#10-jobs-automatiques--état--roadmap)
11. [WhatsApp & Notifications Proactives](#11-whatsapp--notifications-proactives)
12. [Mode Admin Manuel](#12-mode-admin-manuel)
13. [Organisation & Architecture](#13-organisation--architecture)
14. [Plan Prioritaire de Travail](#14-plan-prioritaire-de-travail)

---

## 1. État Général

### Résumé exécutif

| Dimension | État | Score |
|-----------|------|-------|
| Couverture fonctionnelle | 70 pages, 28 routes API, ~130 tables | ✅ ~95% |
| Bugs bloquants | 2 critiques, 3 hauts, 8 moyens | 🔴 À corriger |
| Couverture tests | ~786 tests API, ~200+ tests services | 🟡 Manques ciblés |
| Documentation | 13 docs techniques + guides | 🟡 Partiellement stale |
| SQL consolidation | INIT_COMPLET.sql v3 (~130 tables) | � V002 intégré |
| IA intégration | Mistral + Multimodal (Pixtral) actifs | ✅ Bien intégré |
| Cron jobs | 19 jobs APScheduler + 6 jeux | ✅ Couvre l'essentiel |
| WhatsApp | Webhook entrant + 3 outbound channels | 🟡 Proactif partiel |
| Sécurité | JWT, 2FA, RGPD, RLS Supabase | 🟡 Quelques gaps |

### Architecture globale (rappel)

```
Frontend Next.js 16 (70 pages, 23 clients API, TanStack Query + Zustand)
     ↓ JWT Bearer
FastAPI (44+ routers, 7 middlewares, WebSocket x4)
     ↓
Services Layer (80+ services, BaseAIService, @service_factory)
     ↓
Core (SQLAlchemy 2.0, Mistral AI, Cache 3 niveaux, APScheduler, VAPID Push)
     ↓
Supabase PostgreSQL (~130 tables, RLS, triggers, vues)
```

---

## 2. Bugs Critiques & Anomalies

### 🔴 CRITIQUE — `recherche.py` : endpoint 100% en erreur

**Fichier :** `src/api/routes/recherche.py` lignes 38–44

```python
from src.core.models import (
    Recette,
    Projet,
    Activite,   # ❌ Inexistant — classe réelle : ActiviteFamille
    Note,       # ❌ Inexistant — classe réelle : NoteMemo
    Contact,    # ❌ Inexistant — classes réelles : ContactFamille / ContactUtile
)
```

**Impact :** `GET /api/v1/recherche/global` lève une `ImportError` sur chaque appel. La barre de recherche globale du frontend est totalement inutilisable. Les blocs `try/except` plus bas n'interceptent pas cette erreur car elle se produit à la résolution de l'import.

**Fix :** Renommer les imports : `ActiviteFamille`, `NoteMemo`, `ContactFamille`. Mettre à jour les filtres ORM correspondants.

---

### 🔴 CRITIQUE — `cron/jobs.py` : SQL sur table inexistante

**Fichier :** `src/services/core/cron/jobs.py` ligne ~222

```sql
SELECT COUNT(*) FROM liste_courses lc
JOIN listes_courses ls ON ls.id = lc.liste_id
```

**Impact :** La table `liste_courses` est un doublon qui doit être supprimé (bug B-10 du PLANNING_IMPLEMENTATION.md). Après ce nettoyage, le job cron `rappel_courses` (lancé chaque jour à 18h00) crashera silencieusement. La table correcte est `articles_courses`.

**Fix :** Mettre à jour la requête SQL pour utiliser `articles_courses` et `listes_courses`.

---

### 🟠 HAUTE — `rgpd.py` : user_id vide passé aux opérations RGPD

**Fichier :** `src/api/routes/rgpd.py` lignes 54, 77

```python
user_id = user.get("sub", user.get("id", ""))  # "" si les deux sont absents
```

**Impact :** Si le JWT ne contient ni `sub` ni `id` (env mal configuré ou token expiré), un `user_id = ""` est passé aux fonctions d'export/suppression RGPD. Selon l'implémentation du service, cela peut exporter toutes les données ou déclencher une suppression globale.

**Fix :**
```python
user_id = user.get("sub") or user.get("id")
if not user_id:
    raise HTTPException(status_code=401, detail="Identifiant utilisateur manquant")
```

---

### 🟠 HAUTE — `automations.py` : mutation DB dans un GET

**Fichier :** `src/api/routes/automations.py` lignes 38–53

**Impact :** `GET /api/v1/automations` exécute un `session.commit()` si la liste est vide et qu'une préférence existe. Cela viole le principe HTTP (idempotence des GET), crée des race conditions, et peut corrompre l'état si deux requêtes arrivent simultanément lors de l'initialisation.

**Fix :** Déplacer la logique d'initialisation dans un `POST /automations/init` ou dans le handler de démarrage de l'application.

---

### 🟠 HAUTE — `assistant.py` : texte utilisateur non sanitisé avant persistance

**Fichier :** `src/api/routes/assistant.py` lignes 66–67

```python
nom_article = course_match.group("article").strip(" .,!?")
# Stocké directement → ArticleCourses(nom=nom_article)
```

**Impact :** Les commandes vocales sont parsées via regex et stockées sans passer par `SanitiseurDonnees`. Un utilisateur malveillant pourrait injecter du HTML/SQL via le flux vocal.

**Fix :** Appeler `SanitiseurDonnees.nettoyer_texte(nom_article)` avant persistance.

---

### 🟡 MOYENNE — `auth.py` : API SQLAlchemy dépréciée (supprimée en 2.0)

**Fichier :** `src/api/routes/auth.py` ligne 96

```python
profil = session.query(ProfilUtilisateur).get(int(user_id))  # ❌ SQLAlchemy 1.x
```

**Fix :**
```python
profil = session.get(ProfilUtilisateur, int(user_id))  # ✅ SQLAlchemy 2.0
```

---

### 🟡 MOYENNE — Exceptions silencieuses sans logging (12 occurrences)

Des blocs `except Exception: pass` sans `logger.warning/error` sont présents dans plusieurs routes critiques :

| Fichier | Ligne(s) | Impact |
|---------|----------|--------|
| `planning.py` | L712 | Météo non chargée, aucune trace |
| `planning.py` | L1123, L1150, L1169 | Vue semaine incomplète sans logs |
| `famille.py` | L787 | Budget IA avec données incomplètes |
| `famille.py` | L2683 | Suggestions jardin dégradées silencieusement |
| `dashboard.py` | L149, L281 | Alertes et métriques partielles sans trace |
| `recherche.py` | L151, L179 | Résultats de recherche vides sans raison |
| `export.py` | L204 | Export partiel silencieux |
| `maison.py` | L3713 | Erreur swallowed service maison |

**Fix systématique :** Remplacer par `except Exception as e: logger.warning(f"[module] Erreur non bloquante: {e}")`.

---

### 🟡 MOYENNE — `cron/jobs.py` : accès à l'attribut privé `_subscriptions`

**Fichier :** `src/services/core/cron/jobs.py` lignes 106, 133

```python
user_ids = set(push_service._subscriptions.keys())  # Contournement encapsulation
```

**Impact :** Si le système redémarre entre deux jobs, `_subscriptions` est vide et les notifications ne partent pas — silencieusement.

**Fix :** Exposer une méthode publique `push_service.obtenir_abonnes()` qui lit toujours depuis la DB.

---

### 🟡 MOYENNE — `backup/service.py` : imports modèles hardcodés

**Fichier :** `src/services/core/backup/service.py` lignes 23–47

La liste des 25 modèles à sauvegarder est hardcodée. Le projet a maintenant 27+ fichiers modèles. Les modèles `gamification.py` et `persistent_state.py` ne sont probablement pas couverts.

**Fix :** Utiliser l'auto-discovery via `inspect.getmembers()` sur `src.core.models`.

---

### 🔵 BAS — `whatsapp.py` : numéro partiel dans les logs (RGPD)

**Fichier :** `src/services/integrations/whatsapp.py` ligne 61

```python
logger.info(f"✅ Message WhatsApp envoyé à {destinataire[:6]}***")
```

Même tronqué à 6 chiffres, un numéro de téléphone reste une donnée personnelle RGPD.

**Fix :** Logger uniquement un hash SHA-256 court ou `"destinataire masqué"`.

---

### 🔵 BAS — `admin/jobs/page.tsx` : absence de garde de rôle côté frontend

La page admin des jobs n'a pas de vérification `role === "admin"` dans le composant (defense in depth manquant).

---

## 3. Gaps & Features Manquantes par Module

### 🍽️ Module Cuisine

| Feature | État | Priorité |
|---------|------|----------|
| Profil diététique personnalisable (objectifs calories/macros par utilisateur) | ❌ Manquant | 🟠 H |
| Rappels jour-par-jour (notifications planning) | ❌ Manquant | 🟠 H |
| OCR frigo → auto-sync inventaire (Sprint 8 MT-09) | ❌ À faire | 🟠 H |
| Cellier ↔ Inventaire consolidation (MT-01) | ❌ Sprint 8 | 🟡 M |
| Table nutrition partielle (47 ingrédients seulement) | 🟡 Fonctionnel mais limité | 🟡 M |
| Import image → recette via Pixtral | 🟡 Service existe, pas d'endpoint | 🔵 L |
| Partage recette (lien public ou PDF) | ❌ Manquant | 🔵 L |
| Notation recette affichée dans liste | 🟡 Endpoint existe, pas affiché | 🔵 L |

### 👶 Module Famille

| Feature | État | Priorité |
|---------|------|----------|
| Timeline familiale visuelle (MT-08) | ❌ Page existe mais vide | 🟠 H |
| Tests API famille/garde et famille/achats (Phase 6) | ❌ Non démarrés | 🟠 H |
| Score bien-être global Jules (MT-03/IA-09) | ❌ Sprint 8 | 🟡 M |
| "Today in family history" (QW-06) | ❌ Sprint 8 | 🔵 L |
| Partage album famille (lien temporaire) | ❌ Manquant | 🔵 L |
| Export carnet de santé Jules (PDF dédié) | 🟡 Service PDF existe, pas d'endpoint | 🔵 L |

### 🏡 Module Maison

| Feature | État | Priorité |
|---------|------|----------|
| Alertes météo cross-module (MT-04) | ❌ Sprint 8 | 🟠 H |
| Consolidation cellier ↔ inventaire cuisine | ❌ Sprint 8 | 🟠 H |
| Page dédiée `/maison/contrats` | ❌ API existe, pas de page | 🟡 M |
| Page dédiée `/maison/artisans` | ❌ API existe, pas de page | 🟡 M |
| Page dédiée `/maison/diagnostics` | ❌ API existe, pas de page | 🟡 M |
| Scan ticket caisse → dépenses auto | 🟡 Service `ticket_caisse.py` non connecté | 🟡 M |
| Visualisation plan maison interactive | 🟡 Service existe, UI basique | 🟡 M |

### 📅 Module Planning / Dashboard

| Feature | État | Priorité |
|---------|------|----------|
| Widgets dashboard configurables drag & drop (MT-06) | ❌ Sprint 8 | 🟠 H |
| Widget météo sur dashboard (QW-01) | ❌ Sprint 8 | 🟡 M |
| Gestion conflits cross-module visible (activités vs repas) | 🟡 Service existe, pas surfacé | 🟡 M |
| Vue calendrier mensuel | ❌ Manquant (vue hebdo seulement) | 🔵 L |
| Export planning PDF depuis UI | 🟡 Endpoint export existe, pas de bouton planning | 🔵 L |

### 🎮 Module Jeux

| Feature | État | Priorité |
|---------|------|----------|
| Détection patterns hot hand / régression (TODO jeux.py L372) | 🔵 TODO | 🔵 L |
| Interface backtest stratégies paris | 🟡 Service existe, UI partielle | 🟡 M |

### 🛠️ Module Outils

| Feature | État | Priorité |
|---------|------|----------|
| `GET /api/v1/recherche/global` opérationnel | 🔴 Cassé | 🔴 C |
| Complétion TODO WhatsApp IA planning (webhooks_whatsapp.py L131) | 🟡 TODO | 🟡 M |
| Page RGPD utilisateur (export/suppression depuis UI) | 🟡 Route et client existent, pas de page | 🟡 M |
| Automations : conditions météo | ❌ Nouveauté à ajouter | 🔵 L |

### 🔐 Module Admin

| Feature | État | Priorité |
|---------|------|----------|
| Trigger manuel des cron jobs depuis UI | 🟡 Page admin/jobs existe, endpoints à vérifier | 🟡 M |
| Monitoring services health depuis UI | 🟡 `/health` endpoint, pas dans admin UI | 🟡 M |
| Gestion utilisateurs (liste, ban, reset password) | ❌ Manquant | 🟡 M |
| Logs sécurité (tentatives login, rate limit hits) | ❌ Manquant | 🟠 H |
| Export audit logs en JSON (en plus CSV) | 🟡 CSV seulement | 🔵 L |

---

## 4. SQL — État & Consolidation

### État actuel

| Fichier | Statut | Notes |
|---------|--------|-------|
| `sql/INIT_COMPLET.sql` | ✅ v3.0 | ~130 tables, RLS, triggers, vues |
| `sql/migrations/V001_rls_security_fix.sql` | ✅ Appliqué | Policies RLS restrictives |
| V002 user_id standardization | ✅ Intégré | user_id UUID correct sur toutes les tables directement dans INIT_COMPLET.sql |
| Alembic | ❌ Archivé intentionnellement | Système custom maintenu |

### Problèmes SQL identifiés

**1. Doublon table `liste_courses` / `listes_courses`**

Bug B-10 documenté dans PLANNING_IMPLEMENTATION.md. La table `liste_courses` (singulier) doit être supprimée de INIT_COMPLET.sql et le cron job corrigé.

**2. Vues potentiellement obsolètes**

Les vues `v_autonomie`, `v_budgets_status`, `v_stats_domaine_mois` ont été créées pour l'ancienne version Streamlit. Vérifier si elles sont utilisées par les routes FastAPI actuelles.

**3. Index manquants identifiés**

| Table | Colonne(s) | Justification |
|-------|-----------|---------------|
| `articles_courses` | `(liste_id, achete)` | Requêtes fréquentes liste active |
| `articles_inventaire` | `(date_peremption)` | Alertes péremption quotidiennes |
| `repas_planning` | `(planning_id, date_repas)` | Vue semaine très fréquente |
| `historique_actions` | `(user_id, created_at)` | Admin audit logs pagination |
| `paris_sportifs` | `(statut, user_id)` | Tableau de bord jeux |

**4. Triggers manquants**

- `listes_courses.modifie_le` non mis à jour quand `articles_courses` change
- Invalidation cache planning lors de modification `repas_planning` (fait pour batch, pas pour planning normal)

---

## 5. Tests — Couverture & Lacunes

### Résumé couverture actuelle

| Domaine | Nb tests | État |
|---------|---------|------|
| API routes (37 fichiers) | ~786 | 🟡 Lacunes ciblées |
| Services (50+ fichiers) | ~200+ | 🟡 Lacunes services maison/cron |
| SQL coherence | 132 | ✅ Bon |
| Frontend Vitest (20 fichiers) | 109+ | 🟡 Pages récentes non couvertes |
| E2E Playwright (6 fichiers) | ~40 | 🟡 Partiel |

### Lacunes critiques

**Routes sans fichier test dédié**

| Route | Gap |
|-------|-----|
| `assistant.py` | `test_routes_assistant.py` manquant |
| `webhooks_whatsapp.py` | `test_routes_whatsapp.py` manquant |
| `automations.py` + `voyages.py` + `garmin.py` | 6 tests partagés pour 3 modules |

**Services sans tests**

| Service | Gap |
|---------|-----|
| `src/services/core/cron/jobs.py` (19 jobs) | Aucun test — complètement non testé |
| `src/services/integrations/whatsapp.py` | Aucun test |
| `src/services/integrations/google_calendar.py` | Aucun test |
| `src/services/integrations/ticket_caisse.py` | Aucun test |
| `src/services/integrations/facture.py` | Aucun test |
| `src/services/cuisine/recettes/enrichers.py` | Aucun test dédié |

**Frontend**

| Gap | Détail |
|-----|--------|
| `error.tsx` manquant | `admin/`, `ma-semaine/`, root `(app)/` |
| `loading.tsx` manquant | `admin/`, `ma-semaine/` |
| Pages sans test | `admin/jobs`, `cuisine/photo-frigo`, `famille/timeline`, `outils/assistant-vocal`, `outils/nutritionniste` |

**Tests famille Phase 6 (prévus mais non créés)**
- `tests/api/test_famille_garde.py`
- Extension `tests/api/test_famille_achats.py`

---

## 6. Documentation — État & Lacunes

### État des docs existantes

| Fichier | État | Problème |
|---------|------|---------|
| `docs/ARCHITECTURE.md` (1 mars 2026) | 🟡 | Sprint 10 non documenté (Garmin, automations, voyages) |
| `docs/API_REFERENCE.md` | 🟡 | Routes Sprint 10 manquantes |
| `docs/SERVICES_REFERENCE.md` | 🟡 | Famille refonte non reflétée |
| `docs/ERD_SCHEMA.md` | 🟠 | Probablement obsolète (V002 non reflétée, ~100 tables vs 130) |
| `docs/REDIS_SETUP.md` | 🔴 | **Trompeur** — Redis n'est pas utilisé (cache mémoire+fichier custom) |
| `docs/MIGRATION_GUIDE.md` | ✅ | Valide |
| `docs/PATTERNS.md` | ✅ | Core patterns à jour |
| `ROADMAP.md` | 🟡 | Sprint 8-9 "À FAIRE" mais certains items Sprint 9 déjà partiellement implémentés |

### Docs manquantes à créer

| Document | Contenu | Priorité |
|----------|---------|----------|
| `docs/WHATSAPP.md` | Machine d'état, commandes, setup Meta Cloud API, variables env | 🟠 H |
| `docs/CRON_JOBS.md` | 19+6 jobs, schedules, dépendances, canaux notif, logs | 🟠 H |
| `docs/ADMIN_GUIDE.md` | Mode admin, audit logs, backup, trigger manuel | 🟡 M |
| `docs/AUTOMATIONS.md` | Moteur Si→Alors, conditions, actions disponibles | 🟡 M |
| `docs/GARMIN.md` | OAuth setup, scopes, sync, modèles | 🟡 M |
| `docs/CACHE_SETUP.md` | Remplace REDIS_SETUP.md — L1/L3, TTL, invalidation | 🟡 M |

---

## 7. Interactions Intra-modules

### Implémentées ✅

| Module | Interaction | Mécanisme |
|--------|-------------|-----------|
| Cuisine | Planning → Batch Cooking → Inventaire | FK `planning_id` + `PreparationBatch.repas_attribues` |
| Cuisine | Inventaire → Anti-gaspillage → Suggestions | `obtenir_produits_urgents()` + IA |
| Cuisine | Recette import → Enrichissement auto | Pipeline `RecipeEnricher` |
| Cuisine | Planning → Courses (génération) | `agreger_courses()` |
| Famille | Activités → Planning (conflit) | `ServiceConflits.detecter_conflits()` |
| Famille | Jules → Repas (adaptation portion) | `plat_jules`, `adaptation_auto` sur `RepasResponse` |
| Maison | Entretien → Notifications | Cron `rappels_maison` |
| Jeux | Paris → Bankroll suivi | `MiseResponsable` + `BudgetGuardMiddleware` |

### À compléter/développer 🟡

| Module | Interaction Manquante | Valeur |
|--------|----------------------|--------|
| Cuisine | Score nutritionnel hebdo → Objectif diététique perso | Comparaison objective vs réel |
| Cuisine | Frigo scanné → Recettes avec stocks dispo | UX clé manquante |
| Famille | Budget → Alertes dépenses anormales surfacées | Endpoint existe, pas visible UI |
| Maison | Cellier → Inventaire cuisine (articles communs) | MT-01 Sprint 8 |
| Maison | Projets → Budget mensuel (prévu vs réel) | Pas de lien finances → projets |

---

## 8. Interactions Inter-modules

### Implémentées ✅

| Modules | Interaction | Mécanisme |
|---------|-------------|-----------|
| Planning ↔ Famille | Activités dans vue semaine | Route planning `_job_vue_semaine()` |
| Planning ↔ Maison | Tâches dans vue semaine | Route planning via maison.py |
| Cuisine ↔ Dashboard | KPIs anti-gaspillage, score, repas Jules | `GET /dashboard/cuisine` |
| Famille ↔ Dashboard | Rappels anniversaires, crèche, jalons | Dashboard global |
| Famille + Maison ↔ Cron | Rapport mensuel budget consolidé | `rapport_mensuel_budget` |

### À développer ❌ (propositions de valeur)

| Modules | Interaction Proposée | Valeur Business |
|---------|---------------------|-----------------|
| Cuisine ↔ Famille (Jules) | Repas adultes adaptés automatiquement pour Jules (mêmes inégrédients, textures 18 mois, sans sel/épices, portions réduites) | Gain de temps majeur |
| Maison (Jardin) ↔ Cuisine | Stock tomates jardin → recettes suggérées | Cohérence locale/bio |
| Jeux ↔ Famille (Budget) | Alerte si paris > X€/semaine → notif famille | Gaming responsable |
| Planning ↔ Famille (Voyages) | Voyage détecté → désactivation planning repas | Automatisation contexte |
| Maison (Energie) ↔ Cuisine | Heures creuses → suggérer Cookeo/four | Optimisation éco/coût |

| Garmin ↔ Planning (Nutrition) | Calories brûlées Garmin → ajustement macros planning | Santé personnalisée |
| Garmin ↔ Famille (Bien-être) | Score Jules + données Garmin adultes → dashboard santé famille | Vue globale |
| Jeux ↔ Outils (Automations) | Si gain jeux > X€ → noter dans journal/budget | Audit automatique |
| Maison (Diagnostics IA) ↔ Artisans | Photo problème → estimation → liste artisans | Workflow réparation complet |

---

## 9. Opportunités IA

### IA déjà intégrée ✅

| Domaine | Feature | Provider |
|---------|---------|---------|
| Recettes | Génération, variantes, suggestions | Mistral |
| Planning | Menus équilibrés, météo boost saisons | Mistral |
| Inventaire | Prédiction consommation, analyse stock | Mistral |
| Batch cooking | Plan optimisé avec parallélisation | Mistral |
| Anti-gaspillage | Recettes urgentes, conseils | Mistral |
| Famille | Activités Jules, weekend, soirée | Mistral |
| Maison | Estimation projets, diagnostics photo | Mistral + Pixtral |
| Jeux | Stratégies paris, backtest | Mistral |
| Journal | Entrées assistées | Mistral |
| Catalogue | Enrichissement mensuel domotique/plantes/routines | Mistral |

### Nouvelles opportunités IA à explorer 🚀

**Haute valeur, faisabilité immédiate :**

| Feature | Description | Module | Impact |
|---------|-------------|--------|--------|
| **Résumé famille contextualisé** | Résumé hebdo bienveillant avec conseils (repas, activités, budget, score) | Dashboard | ⭐⭐⭐ |
| **Coach nutrition adaptatif** | Jules a mangé X, objectif Y → suggestions rééquilibrage | Cuisine/Famille | ⭐⭐⭐ |
| **Prédiction liste courses** | ML historique achats → précompléter liste du dimanche | Courses | ⭐⭐⭐ |
| **Détection anomalies dépenses** | +35% courses vs mois dernier → analyse catégories | Dashboard | ⭐⭐⭐ |
| **Chat IA contextuel cross-module** | Contexte = planning + inventaire + budget + Jules → réponses perso | Chat IA | ⭐⭐⭐ |
| **Suggestions activités Jules contextuelles** | Jules 18 mois, météo pluvieuse, crèche fermée → activités | Famille | ⭐⭐ |
| **Diagnostic maison vocal** | Photo + texte → identification panne → catalogue réparations | Maison | ⭐⭐ |
| **Génération automatique d'automations** | "Je veux que quand..." → règle Si→Alors en JSON | Outils | ⭐⭐ |
| **Prédiction péremption personnalisée** | Date achat + type produit → modèle durée de vie adapté | Inventaire | ⭐⭐ |

**Faisabilité différée (données insuffisantes au démarrage) :**

| Feature | Prérequis |
|---------|----------|
| Recommandation recette collaborative (ML) | 6+ mois historique usage |
| Prédiction budget mensuel | 3+ mois données |
| Optimisation nutritionnelle automatique | Profil diététique + 4+ semaines |

---

## 10. Jobs Automatiques — État & Roadmap

### Jobs existants (19 APScheduler + 6 Jeux)

| Job | Schedule | Canal(aux) | État |
|-----|----------|-----------|------|
| `rappels_famille` | Quotidien 07:00 | ntfy + WhatsApp | ✅ |
| `rappels_maison` | Quotidien 08:00 | ntfy | ✅ |
| `rappels_generaux` | Quotidien 08:30 | ntfy | ✅ |
| `entretien_saisonnier` | Lundi 06:00 | ntfy | ✅ |
| `push_quotidien` | Quotidien 09:00 | Web Push VAPID | ✅ |
| `enrichissement_catalogues` | 1er mois 03:00 | (interne IA) | ✅ |
| `digest_ntfy` | Quotidien 09:00 | ntfy | ✅ |
| `rappel_courses` | Quotidien 18:00 | ntfy + WhatsApp | ⚠️ Bug SQL |
| `push_contextuel_soir` | Quotidien 18:00 | Web Push | ✅ |
| `resume_hebdo` | Lundi 07:30 | ntfy + email + WhatsApp | ✅ |
| `planning_semaine_si_vide` | Dimanche 20:00 | ntfy | ✅ |
| `alertes_peremption_48h` | Quotidien 06:00 | ntfy + WhatsApp | ✅ |
| `rapport_mensuel_budget` | 1er mois 08:15 | ntfy + email | ✅ |
| `score_weekend` | Vendredi 17:00 | ntfy | ✅ |
| `controle_contrats_garanties` | 1er mois 09:00 | ntfy | ✅ |
| `rapport_jardin` | Mercredi 20:00 | ntfy | ✅ |
| `score_bien_etre_hebdo` | Dimanche 20:00 | ntfy | ✅ |
| `garmin_sync_matinal` | Quotidien 06:00 | (interne) | ✅ |
| `automations_runner` | Toutes les 5 min | (interne) | ✅ |
| Jeux fetch/clôture | Quotidien + 23:00 | (interne) | ✅ |
| Loto tirage | Mer 21:30 | ntfy | ✅ |
| EuroMillions tirage | Mar+Ven 22:00 | ntfy | ✅ |

### Jobs à créer (propositions)

| Job | Schedule | Description | Module |
|-----|----------|-------------|--------|
| `sync_google_calendar` | Quotidien 23:00 | Sync planning → Google Calendar | Calendrier |
| `rapport_nutrition_jules` | Dimanche 19:00 | Bilan nutrition Jules semaine | Cuisine/Famille |
| `alerte_stock_bas` | Quotidien 07:00 | Articles < seuil min → liste courses auto | Inventaire |
| `archive_batches_expires` | Quotidien 02:00 | Archiver préparations batch expirées | Batch Cooking |
| `rapport_maison_mensuel` | 1er mois 09:30 | État maison : projets, entretien, dépenses | Maison |
| `sync_openFoodFacts` | Dim 03:00 | Refresh cache OpenFoodFacts | Inventaire |

---

## 11. WhatsApp & Notifications Proactives

### État entrant (webhook)

- ✅ Vérification Meta Challenge (GET)
- ✅ Machine d'état conversationnelle (button replies)
- ✅ Commandes texte : `planning`, `courses`, `frigo`, `menu`
- ✅ Boutons interactifs : valider/modifier/régénérer planning
- ❌ TODO intégration IA régénération (fichier webhooks_whatsapp.py L131)

### État sortant (dispatcher)

| Canal | État |
|-------|------|
| ntfy.sh | ✅ Opérationnel |
| WhatsApp Meta Cloud API | ✅ Opérationnel (message, interactif, planning, péremption) |
| Web Push (VAPID) | ✅ Opérationnel |
| Email SMTP | 🟡 Configuré mais dispatcher incomplet |

### Commandes WhatsApp à ajouter

| Commande | Action | Impact |
|----------|--------|--------|
| `jules` / `bébé` | Résumé Jules (repas, activités, jalons récents) | ⭐⭐⭐ |
| `ajouter [article]` | Ajouter directement en liste courses | ⭐⭐⭐ |
| `budget` | Budget mensuel en cours vs objectif | ⭐⭐ |
| `anniversaires` | Prochains anniversaires 30 jours | ⭐⭐ |
| `recette [nom]` | Fiche recette avec ingrédients | ⭐⭐ |
| `tâches` | Tâches maison en retard | ⭐⭐ |
| `aide admin` | (admin only) liste commandes admin | ⭐⭐ |

### Complétion email requise

- Rapport hebdo famille (planifié en cron mais email non envoyé)
- Rapport mensuel budget
- Alertes critiques (péremption < 24h, garanties < 30j)

---

## 12. Mode Admin Manuel

### Existant

| Feature | Emplacement | État |
|---------|------------|------|
| Dashboard audit logs | `/admin/page.tsx` + `GET /admin/audit-*` | ✅ |
| Trigger jobs UI | `/admin/jobs/page.tsx` | 🟡 À vérifier |
| Backup DB | `python manage.py backup` | ✅ CLI uniquement |
| Health check | `GET /health` + `GET /metrics` | ✅ |

### Endpoints admin à créer

```
POST /api/v1/admin/jobs/{job_id}/run     → Trigger manuel d'un cron job
GET  /api/v1/admin/jobs                  → Liste jobs + dernière exécution + statut
GET  /api/v1/admin/jobs/{job_id}/logs   → Logs dernière exécution
POST /api/v1/admin/whatsapp/test         → Message WhatsApp de test
POST /api/v1/admin/push/test             → Push notification de test
POST /api/v1/admin/email/test            → Email de test
GET  /api/v1/admin/services/health       → Health check registre services
GET  /api/v1/admin/cache/stats           → Statistiques cache hit/miss/size
POST /api/v1/admin/cache/clear           → Vider cache L1 + L3
GET  /api/v1/admin/users                 → Liste utilisateurs
POST /api/v1/admin/users/{id}/disable    → Désactiver compte
GET  /api/v1/admin/db/coherence          → Lancer test_schema_coherence rapide
```

### Pages frontend admin à créer/compléter

```
/admin/
  ├── page.tsx              → Audit logs (existant ✅)
  ├── jobs/page.tsx         → Liste + trigger manuel + logs (à compléter)
  ├── services/page.tsx     → Health check + cache stats (à créer)
  ├── notifications/page.tsx → Test WhatsApp/Push/Email + historique (à créer)
  └── utilisateurs/page.tsx → Gestion comptes (à créer)
```

### Règles de sécurité admin

- Tous les endpoints admin : `Depends(require_role("admin"))`
- Audit log automatique sur chaque action admin (déjà présent pour audit-logs, à généraliser)
- Rate limiting spécifique admin : 5 req/min sur triggers jobs
- Navigation admin conditionnelle `role === "admin"` (déjà fait dans sidebar)
- Logs sécurité séparés pour actions admin (à créer dans `historique_actions`)

---

## 13. Organisation & Architecture

### Points forts ✅

1. **Architecture modulaire** — Services, models, routes bien séparés, patterns cohérents
2. **BaseAIService** — Rate limiting + cache + circuit breaker partagés automatiquement
3. **Event Bus** — Pub/sub pour découplage inter-services
4. **Sécurité** — JWT + 2FA + RLS Supabase + SecurityHeaders + VAPID
5. **Cron APScheduler** — 19 jobs couvrant tous les domaines
6. **WhatsApp** — Bonne base conversationnelle avec machine d'état
7. **Tests** — 786+ tests API + 200+ services + SQL coherence

### Points à améliorer 🟡

**1. Fichiers routes trop longs**

| Fichier | Lignes | Recommandation |
|---------|--------|----------------|
| `maison.py` | ~3700+ | Splitter en `maison_projets.py`, `maison_entretien.py`, `maison_finances.py`, `maison_jardin.py` |
| `famille.py` | ~2700 | Splitter en `famille_jules.py`, `famille_budget.py`, `famille_activites.py` |
| `planning.py` | ~1200+ | Acceptable, surveiller |

**2. Noms de fonctions factory incohérents**

- Convention française : `obtenir_service_xxx()` (à uniformiser)
- Anglais encore présent : `get_xxx_service()` dans certains modules
- Standardiser vers le français (convention du projet)

**3. Types TypeScript non générés depuis Pydantic**

Les types dans `frontend/src/types/` sont maintenus manuellement. Risque de désynchronisation avec les schémas Pydantic backend. Envisager `openapi-typescript` pour génération automatique.

**4. Docs REDIS_SETUP.md trompeur**

`docs/REDIS_SETUP.md` documente une configuration Redis qui n’est pas utilisée dans le projet. L’app utilise son propre système de cache à deux niveaux (L1 mémoire + L3 fichier). Ce fichier est à supprimer et remplacer par `docs/CACHE_SETUP.md` qui décrira le vrai système.

---

## 14. Plan Prioritaire de Travail

### Sprint Correctif — Priorité absolue (~1-2 jours)

| # | Action | Fichier | Impact |
|---|--------|---------|--------|
| C1 | Fix imports `recherche.py` (Activite→ActiviteFamille, Note→NoteMemo, Contact→ContactFamille) | `src/api/routes/recherche.py` | 🔴 Endpoint cassé |
| C2 | Fix SQL cron `liste_courses` → `articles_courses` | `src/services/core/cron/jobs.py` | 🔴 Crash cron imminent |
| C3 | Fix automations GET → extraire mutation vers startup | `src/api/routes/automations.py` | 🟠 Idempotence HTTP |
| C4 | Ajouter `SanitiseurDonnees` dans assistant.py | `src/api/routes/assistant.py` | 🟠 Injection |
| C5 | Fix `Query.get()` → `session.get()` dans auth.py | `src/api/routes/auth.py` | 🟡 Compat SQLAlchemy 2.0 |
| C6 | Remplacer `except Exception: pass` → `logger.warning()` (12 cas) | Tous les concernés | 🟡 Observabilité |
| C7 | Exposer `push_service.obtenir_abonnes()` public | `cron/jobs.py` | 🟡 Encapsulation |

### Sprint SQL (~0.5 jour)

| # | Action |
|---|--------|
| SQL1 | Supprimer doublon `liste_courses` dans INIT_COMPLET.sql |
| ~~SQL2~~ | ✅ V002 intégré — user_id UUID correct sur toutes les tables dans INIT_COMPLET.sql |
| SQL2 | Ajouter 5 index manquants dans INIT_COMPLET.sql |
| SQL3 | Vérifier et supprimer vues obsolètes Streamlit |
| SQL4 | Ajouter triggers `listes_courses.modifie_le` |

### Sprint Tests (~2-3 jours)

| # | Action |
|---|--------|
| T1 | `test_routes_assistant.py` + `test_routes_whatsapp.py` |
| T2 | `test_cron_jobs.py` (avec mocks push_service, DB) |
| T3 | `test_famille_garde.py` + compléter `test_famille_achats.py` |
| T4 | `error.tsx` + `loading.tsx` pour `admin/`, `ma-semaine/`, root |
| T5 | `test_routes_automations.py` dédié + `test_routes_voyages.py` + `test_routes_garmin.py` |

### Sprint Documentation (~1 jour)

| # | Action |
|---|--------|
| D1 | Mettre à jour `ARCHITECTURE.md` (Sprint 10 : Garmin, automations, voyages) |
| D2 | Créer `docs/WHATSAPP.md` |
| D3 | Créer `docs/CRON_JOBS.md` |
| D4 | Supprimer + remplacer `docs/REDIS_SETUP.md` par `docs/CACHE_SETUP.md` |
| D5 | Régénérer `docs/ERD_SCHEMA.md` (130 tables actuelles) |
| D6 | Mettre à jour `ROADMAP.md` (fermer items Sprint 9 partiellement faits) |

### Sprint 8 — Inter-modules + Dashboard avancé

| # | Feature | Effort |
|---|---------|--------|
| S8-1 | Cellier ↔ Inventaire consolidation | M |
| S8-2 | Score bien-être global Jules | M |
| S8-3 | Alertes météo cross-module | S |
| S8-4 | Dashboard widgets drag & drop | L |
| S8-5 | Timeline familiale visuelle | M |
| S8-6 | OCR frigo → auto-sync inventaire | M |
| S8-7 | Widget météo dashboard | S |
| S8-8 | "Today in family history" | S |

### Sprint 9 — WhatsApp proactif + IA avancée

| # | Feature | Effort |
|---|---------|--------|
| S9-1 | Commandes WhatsApp étendues (jules, ajouter, budget) | S |
| S9-2 | Intégration IA régénération planning WhatsApp (TODO L131) | S |
| S9-3 | Compléter dispatcher email SMTP | M |
| S9-4 | Chat IA contextuel cross-module enrichi | M |
| S9-5 | Prédiction liste courses | L |
| S9-6 | Détection anomalies dépenses IA | M |
| S9-7 | Admin mode complet (trigger jobs, test notifs) | M |
| S9-8 | Profil diététique personnalisable | M |

---

## Annexe — Inventaire des Modules

### Modules Backend

| Domaine | Routes | Services | Modèles | Tests API |
|---------|--------|---------|---------|-----------|
| Cuisine | 5 fichiers | ~15 services | 4 fichiers | 5 fichiers |
| Famille | 3 fichiers | ~23 services | 8 fichiers | 5 fichiers |
| Maison | 1 fichier (3700 lignes) | ~15 services | 4 fichiers | 1 fichier |
| Planning | 1 fichier | ~6 services | 2 fichiers | 1 fichier |
| Jeux | 1 fichier | ~9 services | 1 fichier | 1 fichier |
| Dashboard | 1 fichier | 2 services | — | 1 fichier |
| Admin | 1 fichier | 2 services | 1 fichier | 2 fichiers |
| Auth | 1 fichier | 2 services | 1 fichier | 1 fichier |
| Outils/Utilitaires | 4 fichiers | 7 services | 1 fichier | 3 fichiers |
| Integrations | — | 10 services | — | 4 fichiers |
| Cron | — | 1 fichier (25 jobs) | — | ❌ Aucun |

### Modules Frontend (70 pages)

| Domaine | Pages | Tests Vitest | error.tsx | loading.tsx |
|---------|-------|-------------|-----------|-------------|
| Cuisine | 16 | 6 | ✅ | ✅ |
| Famille | 17 | 5 | ✅ | ✅ |
| Maison | 11 | 1 | ✅ | ✅ |
| Jeux | 7 | 2 | ✅ | ✅ |
| Outils | 9 | 1 | ✅ | ✅ |
| Planning | 2 | 1 | ✅ | ✅ |
| Parametres | 3 | 1 | ✅ | ✅ |
| Admin | 2 | 0 | ❌ | ❌ |
| Ma semaine | 1 | 0 | ❌ | ❌ |
| Dashboard | 1 | 1 | ❌ | ✅ |

---

*Document généré par analyse automatique du codebase. 28 mars 2026.*
