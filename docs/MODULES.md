# ?? Modules ? Assistant MaTanne

> Carte compl?te des modules applicatifs : fonctionnalit?s, routes API, services backend, mod?les ORM et pages frontend.

---

## Vue d'ensemble

| Module | Pages | Routes API | Service | Description |
| -------- | ------- | ----------- | --------- | ------------- |
| **Cuisine** | 7 | 6 routeurs | `cuisine/`, `planning/`, `inventaire/` | Recettes, planning repas, courses, inventaire, batch cooking, anti-gaspillage |
| **Famille** | 10 | 1 routeur | `famille/` | Jules (suivi enfant), activit?s, routines, budget, weekend, anniversaires, contacts, documents, journal |
| **Maison** | 9 | 1 routeur | `maison/` | Projets, charges, d?penses, ?nergie, entretien, jardin, stocks, cellier, artisans, contrats, garanties, diagnostics |
| **Planning** | 2 | 1 routeur | `planning/` | Hub planning, timeline |
| **Jeux** | 4 | 1 routeur | `jeux/` | Paris sportifs, Loto, EuroMillions |
| **Outils** | 6 | 1 routeur | `utilitaires/` | Chat IA, m?t?o, convertisseur, minuteur, notes |
| **Habitat** | 5 | 1 routeur | `habitat/` | Veille immo, sc?narios, plans, d?co, jardin |
| **IA avanc?e / Innovations** | 16+ | 2 routeurs | `ia_avancee/`, `innovations/` | Endpoints IA avanc?s et fonctionnalit?s phase 9/10 |
| **Dashboard** | 1 | 1 routeur | `dashboard/` | Tableau de bord avec m?triques agr?g?es |

---

## ??? Cuisine

### Fonctionnalit?s

- **Recettes** ? CRUD complet, import depuis URL/PDF, suggestions IA, versions, historique, retours utilisateur
- **Planning repas** ? Planification hebdomadaire, suggestions IA, templates semaine, g?n?ration liste courses
- **Courses** ? Listes collaboratives (WebSocket temps r?el), scan code-barres, mod?les r?utilisables
- **Inventaire** ? Gestion stock alimentaire, alertes p?remption, lookup OpenFoodFacts
- **Batch cooking** ? Sessions de pr?paration group?e, ?tapes, pr?parations
- **Anti-gaspillage** ? Score anti-gaspi, suggestions valorisation, actions

### Architecture

| Couche | Chemin |
| -------- | -------- |
| Routes API | `src/api/routes/recettes.py`, `courses.py`, `inventaire.py`, `planning.py`, `batch_cooking.py`, `anti_gaspillage.py` |
| Sch?mas | `src/api/schemas/recettes.py`, `courses.py`, `inventaire.py`, `planning.py` |
| Services | `src/services/cuisine/` (service, importer, suggestions), `src/services/planning/`, `src/services/inventaire/` |
| Mod?les ORM | `src/core/models/recettes.py`, `courses.py`, `batch_cooking.py`, `planning.py` |
| Frontend | `frontend/src/app/(app)/cuisine/` (recettes, planning, courses, inventaire, batch-cooking, anti-gaspillage) |
| API Client | `frontend/src/bibliotheque/api/recettes.ts`, `courses.ts`, `inventaire.ts`, `planning.ts` |

### Endpoints principaux

| M?thode | Route | Description |
| --------- | ------- | ------------- |
| GET/POST | `/api/v1/recettes` | Liste pagin?e / Cr?er recette |
| POST | `/api/v1/recettes/import-url` | Import depuis URL |
| GET/POST | `/api/v1/courses` | Listes de courses |
| WS | `/ws/courses/{liste_id}` | Collaboration temps r?el |
| GET/POST | `/api/v1/inventaire` | Stock alimentaire |
| GET/POST | `/api/v1/planning` | Planning repas |
| POST | `/api/v1/suggestions` | Suggestions IA |
| GET/POST | `/api/v1/batch-cooking` | Sessions batch cooking |
| GET | `/api/v1/anti-gaspillage/score` | Score anti-gaspillage |

---

## ???????? Famille

### Fonctionnalit?s

- **Jules** ? Suivi d?veloppement enfant : jalons, bien-?tre, courbes croissance, vaccins, rendez-vous m?dicaux
- **Activit?s** ? Activit?s familiales, planification, historique
- **Routines** ? Routines quotidiennes (matin/soir), t?ches
- **Budget famille** ? Achats familiaux, suivi d?penses, cat?gories
- **Weekend** ? Suggestions activit?s weekend IA, planification
- **Anniversaires** ? Suivi anniversaires, rappels
- **Contacts** ? Carnet contacts famille
- **Documents** ? Documents familiaux (upload, partage)
- **Journal** ? Journal de bord familial

### Architecture

| Couche | Chemin |
| -------- | -------- |
| Routes API | `src/api/routes/famille.py` |
| Sch?mas | `src/api/schemas/famille.py` |
| Services | `src/services/famille/` (service, jules_ai, weekend_ai) |
| Mod?les ORM | `src/core/models/famille.py`, `contacts.py`, `documents.py`, `carnet_sante.py`, `users.py` |
| Frontend | `frontend/src/app/(app)/famille/` (jules, activites, routines, budget, weekend, anniversaires, contacts, documents, journal) |

### Endpoints principaux

| M?thode | Route | Description |
| --------- | ------- | ------------- |
| GET/POST | `/api/v1/famille/enfants` | Profils enfants |
| GET/POST | `/api/v1/famille/activites` | Activit?s familiales |
| GET/POST | `/api/v1/famille/routines` | Routines quotidiennes |
| GET/POST | `/api/v1/famille/budget` | Budget / achats |
| GET | `/api/v1/famille/weekend/suggestions` | Suggestions IA weekend |

---

## ?? Maison

### Fonctionnalit?s

- **Projets** ? Gestion projets maison (t?ches, timeline, budget, ROI)
- **Charges** ? Contrats, factures, comparatifs
- **D?penses** ? Suivi d?penses maison par cat?gorie
- **?nergie** ? Relev?s compteurs, consommation, pr?visions IA
- **Entretien** ? T?ches entretien, entretiens saisonniers, artisans
- **Jardin** ? Plantes, zones, plans, r?coltes, objectifs autonomie, m?t?o
- **Stocks** ? Stock maison (non-alimentaire)
- **Cellier** ? Articles cellier (cave, r?serves)
- **Artisans** ? Carnet adresses professionnels, interventions
- **Contrats** ? Assurances, abonnements, r?siliation
- **Garanties** ? Garanties appareils, SAV, incidents
- **Diagnostics** ? DPE, amiante, estimations immobili?res

### Architecture

| Couche | Chemin |
| -------- | -------- |
| Routes API | `src/api/routes/maison.py` |
| Sch?mas | `src/api/schemas/maison.py` |
| Services | `src/services/maison/` (service) |
| Mod?les ORM | `src/core/models/maison.py`, `habitat.py`, `maison_extensions.py`, `contrats_artisans.py`, `jardin.py`, `temps_entretien.py` |
| Frontend | `frontend/src/app/(app)/maison/` (projets, charges, depenses, energie, entretien, jardin, stocks + cellier, artisans, contrats, garanties, diagnostics) |

---

## ?? Planning

### Fonctionnalit?s

- **Hub planning** ? Vue d'ensemble plannings actifs et prochains ?v?nements
- **Timeline** ? Vue timeline des repas et ?v?nements

### Architecture

| Couche | Chemin |
| -------- | -------- |
| Routes API | `src/api/routes/planning.py`, `calendriers.py` |
| Services | `src/services/planning/` (service, nutrition, agregation, formatters, validators, prompts) |
| Mod?les ORM | `src/core/models/planning.py`, `calendrier.py` |
| Frontend | `frontend/src/app/(app)/planning/` (page, timeline) |

---

## ?? Jeux

### Fonctionnalit?s

- **Paris sportifs** ? Suivi paris, ?quipes, matchs, cotes, value betting, s?ries
- **Loto** ? Tirages, grilles (4 strat?gies g?n?ration), statistiques, historique
- **EuroMillions** ? Tirages, grilles, statistiques sp?cifiques

### Architecture

| Couche | Chemin |
| -------- | -------- |
| Routes API | `src/api/routes/jeux.py` |
| Sch?mas | `src/api/schemas/jeux.py` |
| Services | `src/services/jeux/` (service) |
| Mod?les ORM | `src/core/models/jeux.py` (15 classes) |
| Frontend | `frontend/src/app/(app)/jeux/` (paris, loto, euromillions) |

---

## ??? Outils

### Fonctionnalit?s

- **Chat IA** ? Conversation libre Mistral avec contexte familial, streaming SSE
- **M?t?o** ? M?t?o actuelle + 7 jours, alertes, conseils jardin
- **Convertisseur** ? Volumes, poids, temp?ratures, devises
- **Minuteur** ? Compte ? rebours, chronom?tre, notifications push (Service Worker)
- **Notes** ? Prise de notes, tags, ?pinglage, recherche full-text

### Architecture

| Couche | Chemin |
| -------- | -------- |
| Routes API | `src/api/routes/utilitaires.py` |
| Services | `src/services/utilitaires/`, `src/services/integrations/weather/` |
| Mod?les ORM | `src/core/models/utilitaires.py` |
| Frontend | `frontend/src/app/(app)/outils/` (chat-ia, meteo, convertisseur, minuteur, notes) |

---

## ?? Dashboard

### Fonctionnalit?s

- M?triques agr?g?es tous modules
- Widgets : repas du jour, courses en attente, t?ches en retard, anniversaires proches, m?t?o, budget mensuel
- Raccourcis vers les actions fr?quentes

### Architecture

| Couche | Chemin |
| -------- | -------- |
| Routes API | `src/api/routes/dashboard.py` |
| Services | `src/services/dashboard/service.py` |
| Frontend | `frontend/src/app/(app)/page.tsx` |

---

## Modules transversaux

| Module | Route API | Description |
| -------- | ----------- | ------------- |
| Auth | `/api/v1/auth` | Login, refresh, me (JWT Bearer) |
| Export PDF | `/api/v1/export` | Export recettes, planning, courses, budget en PDF |
| Pr?f?rences | `/api/v1/preferences` | Pr?f?rences utilisateur (cuisine, UI, IA) |
| Documents | `/api/v1/documents` | Upload et gestion documents |
| Push | `/api/v1/push` | Notifications push (VAPID) |
| Webhooks | `/api/v1/webhooks` | Webhooks externes (HTTP POST sur ?v?nements) |
| Upload | `/api/v1/upload` | Upload fichiers et images |

