# 📦 Modules — Assistant MaTanne

> Carte complète des modules applicatifs : fonctionnalités, routes API, services backend, modèles ORM et pages frontend.

---

## Vue d'ensemble

| Module | Pages | Routes API | Service | Description |
|--------|-------|-----------|---------|-------------|
| **Cuisine** | 7 | 6 routeurs | `cuisine/`, `planning/`, `inventaire/` | Recettes, planning repas, courses, inventaire, batch cooking, anti-gaspillage |
| **Famille** | 10 | 1 routeur | `famille/` | Jules (suivi enfant), activités, routines, budget, weekend, anniversaires, contacts, documents, journal |
| **Maison** | 9 | 1 routeur | `maison/` | Projets, charges, dépenses, énergie, entretien, jardin, stocks, cellier, artisans, abonnements, diagnostics |
| **Planning** | 2 | 1 routeur | `planning/` | Hub planning, timeline |
| **Jeux** | 4 | 1 routeur | `jeux/` | Paris sportifs, Loto, EuroMillions |
| **Outils** | 6 | 1 routeur | `utilitaires/` | Chat IA, météo, convertisseur, minuteur, notes |
| **Habitat** | 5 | 1 routeur | `habitat/` | Veille immo, scénarios, plans, déco, jardin |
| **IA avancée / Innovations** | 16+ | 2 routeurs | `ia_avancee/`, `innovations/` | Endpoints IA avancés et fonctionnalités innovantes |
| **Dashboard** | 1 | 1 routeur | `dashboard/` | Tableau de bord avec métriques agrégées |

---

## 🍽️ Cuisine

### Fonctionnalités

- **Recettes** — CRUD complet, import depuis URL/PDF, suggestions IA, versions, historique, retours utilisateur
- **Planning repas** — Planification hebdomadaire, suggestions IA, templates semaine, génération liste courses
- **Courses** — Listes collaboratives (WebSocket temps réel), scan code-barres, modèles réutilisables
- **Inventaire** — Gestion stock alimentaire, alertes péremption, lookup OpenFoodFacts
- **Batch cooking** — Sessions de préparation groupée, étapes, préparations
- **Anti-gaspillage** — Score anti-gaspi, suggestions valorisation, actions

### Architecture

| Couche | Chemin |
|--------|--------|
| Routes API | `src/api/routes/recettes.py`, `courses.py`, `inventaire.py`, `planning.py`, `batch_cooking.py`, `anti_gaspillage.py` |
| Schémas | `src/api/schemas/recettes.py`, `courses.py`, `inventaire.py`, `planning.py` |
| Services | `src/services/cuisine/` (service, importer, suggestions), `src/services/planning/`, `src/services/inventaire/` |
| Modèles ORM | `src/core/models/recettes.py`, `courses.py`, `batch_cooking.py`, `planning.py` |
| Frontend | `frontend/src/app/(app)/cuisine/` (recettes, planning, courses, inventaire, batch-cooking, anti-gaspillage) |
| API Client | `frontend/src/bibliotheque/api/recettes.ts`, `courses.ts`, `inventaire.ts`, `planning.ts` |

### Endpoints principaux

| Méthode | Route | Description |
|---------|-------|-------------|
| GET/POST | `/api/v1/recettes` | Liste paginée / Créer recette |
| POST | `/api/v1/recettes/import-url` | Import depuis URL |
| GET/POST | `/api/v1/courses` | Listes de courses |
| WS | `/ws/courses/{liste_id}` | Collaboration temps réel |
| GET/POST | `/api/v1/inventaire` | Stock alimentaire |
| GET/POST | `/api/v1/planning` | Planning repas |
| POST | `/api/v1/suggestions` | Suggestions IA |
| GET/POST | `/api/v1/batch-cooking` | Sessions batch cooking |
| GET | `/api/v1/anti-gaspillage/score` | Score anti-gaspillage |

---

## 👨‍👩‍👦 Famille

### Fonctionnalités

- **Jules** — Suivi développement enfant : jalons, bien-être, alimentation, vaccins, rendez-vous médicaux
- **Activités** — Activités familiales, planification, historique
- **Routines** — Routines quotidiennes (matin/soir), tâches
- **Budget famille** — Achats familiaux, suivi dépenses, catégories
- **Weekend** — Suggestions activités weekend IA, planification
- **Anniversaires** — Suivi anniversaires, rappels
- **Contacts** — Carnet contacts famille
- **Documents** — Documents familiaux (upload, partage)
- **Journal** — Journal de bord familial

### Architecture

| Couche | Chemin |
|--------|--------|
| Routes API | `src/api/routes/famille.py` |
| Schémas | `src/api/schemas/famille.py` |
| Services | `src/services/famille/` (service, jules_ai, weekend_ai) |
| Modèles ORM | `src/core/models/famille.py`, `contacts.py`, `documents.py`, `carnet_sante.py`, `users.py` |
| Frontend | `frontend/src/app/(app)/famille/` (jules, activites, routines, budget, weekend, anniversaires, contacts, documents, journal) |

### Endpoints principaux

| Méthode | Route | Description |
|---------|-------|-------------|
| GET/POST | `/api/v1/famille/enfants` | Profils enfants |
| GET/POST | `/api/v1/famille/activites` | Activités familiales |
| GET/POST | `/api/v1/famille/routines` | Routines quotidiennes |
| GET/POST | `/api/v1/famille/budget` | Budget / achats |
| GET | `/api/v1/famille/weekend/suggestions` | Suggestions IA weekend |

---

## 🏡 Maison

### Fonctionnalités

- **Projets** — Gestion projets maison (tâches, timeline, budget, ROI)
- **Charges** — Abonnements, alternatives fournisseurs, suivi des échéances
- **Dépenses** — Suivi dépenses maison par catégorie
- **Énergie** — Relevés compteurs, consommation, prévisions IA
- **Entretien** — Tâches entretien, entretiens saisonniers, artisans
- **Jardin** — Plantes, zones, plans, récoltes, objectifs autonomie, météo
- **Stocks** — Stock maison (non-alimentaire)
- **Cellier** — Articles cellier (cave, réserves)
- **Artisans** — Carnet adresses professionnels, interventions
- **Abonnements** — Comparateur abonnements (eau, électricité, gaz, assurances, téléphone, internet)
- **Diagnostics** — DPE, amiante, estimations immobilières

### Architecture

| Couche | Chemin |
|--------|--------|
| Routes API | `src/api/routes/maison.py` |
| Schémas | `src/api/schemas/maison.py` |
| Services | `src/services/maison/` (service) |
| Modèles ORM | `src/core/models/maison.py`, `habitat.py`, `maison_extensions.py`, `abonnements.py`, `jardin.py`, `temps_entretien.py` |
| Frontend | `frontend/src/app/(app)/maison/` (projets, charges, depenses, energie, entretien, jardin, stocks + cellier, artisans, abonnements, diagnostics) |

---

## 📅 Planning

### Fonctionnalités

- **Hub planning** — Vue d'ensemble plannings actifs et prochains événements
- **Timeline** — Vue timeline des repas et événements

### Architecture

| Couche | Chemin |
|--------|--------|
| Routes API | `src/api/routes/planning.py`, `calendriers.py` |
| Services | `src/services/planning/` (service, nutrition, agregation, formatters, validators, prompts) |
| Modèles ORM | `src/core/models/planning.py`, `calendrier.py` |
| Frontend | `frontend/src/app/(app)/planning/` (page, timeline) |

---

## 🎮 Jeux

### Fonctionnalités

- **Paris sportifs** — Suivi paris, équipes, matchs, cotes, value betting, séries
- **Loto** — Tirages, grilles (4 stratégies génération), statistiques, historique
- **EuroMillions** — Tirages, grilles, statistiques spécifiques

### Architecture

| Couche | Chemin |
|--------|--------|
| Routes API | `src/api/routes/jeux.py` |
| Schémas | `src/api/schemas/jeux.py` |
| Services | `src/services/jeux/` (service) |
| Modèles ORM | `src/core/models/jeux.py` (15 classes) |
| Frontend | `frontend/src/app/(app)/jeux/` (paris, loto, euromillions) |

---

## 🛠️ Outils

### Fonctionnalités

- **Chat IA** — Conversation libre Mistral avec contexte familial, streaming SSE
- **Météo** — Météo actuelle + 7 jours, alertes, conseils jardin
- **Convertisseur** — Volumes, poids, températures, devises
- **Minuteur** — Compte à rebours, chronomètre, notifications push (Service Worker)
- **Notes** — Prise de notes, tags, épinglage, recherche full-text

### Architecture

| Couche | Chemin |
|--------|--------|
| Routes API | `src/api/routes/utilitaires.py` |
| Services | `src/services/utilitaires/`, `src/services/integrations/weather/` |
| Modèles ORM | `src/core/models/utilitaires.py` |
| Frontend | `frontend/src/app/(app)/outils/` (chat-ia, meteo, convertisseur, minuteur, notes) |

---

## 📊 Dashboard

### Fonctionnalités

- Métriques agrégées tous modules
- Widgets : repas du jour, courses en attente, tâches en retard, anniversaires proches, météo, budget mensuel
- Raccourcis vers les actions fréquentes

### Architecture

| Couche | Chemin |
|--------|--------|
| Routes API | `src/api/routes/dashboard.py` |
| Services | `src/services/dashboard/service.py` |
| Frontend | `frontend/src/app/(app)/page.tsx` |

---

## Modules transversaux

| Module | Route API | Description |
|--------|-----------|-------------|
| Auth | `/api/v1/auth` | Login, refresh, me (JWT Bearer) |
| Export PDF | `/api/v1/export` | Export recettes, planning, courses, budget en PDF |
| Préférences | `/api/v1/preferences` | Préférences utilisateur (cuisine, UI, IA) |
| Documents | `/api/v1/documents` | Upload et gestion documents |
| Push | `/api/v1/push` | Notifications push (VAPID) |
| Webhooks | `/api/v1/webhooks` | Webhooks externes (HTTP POST sur événements) |
| Upload | `/api/v1/upload` | Upload fichiers et images |

