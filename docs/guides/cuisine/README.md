# ðŸ½ï¸ Guide Module Cuisine

> Recettes, planning repas, courses, inventaire, batch cooking, anti-gaspillage et enrichissements IA.

## Table des matiÃ¨res

1. [Vue d'ensemble](#vue-densemble)
2. [Recettes](#recettes)
3. [Planning repas](#planning-repas)
4. [Courses](#courses)
5. [Inventaire](#inventaire)
6. [Batch cooking](#batch-cooking)
7. [Anti-gaspillage](#anti-gaspillage)
8. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Cuisine** couvre toute la chaÃ®ne alimentaire du foyer : recettes, planning repas, courses, inventaire, batch cooking et rÃ©duction du gaspillage.

**URL** : `/cuisine`
**Services backend** : `src/services/cuisine/`, `src/services/planning/`, `src/services/inventaire/`
**Routes API** : `src/api/routes/recettes.py`, `src/api/routes/courses.py`, `src/api/routes/inventaire.py`, `src/api/routes/planning.py`, `src/api/routes/batch_cooking.py`, `src/api/routes/anti_gaspillage.py`

### CapacitÃ©s rÃ©centes Ã  connaÃ®tre

- suggestions IA de recettes et de planning
- prÃ©diction de courses
- prÃ©diction / priorisation de pÃ©remption
- rappel repas du soir via cron
- stock bas -> ajout automatique Ã  la liste de courses

---

## Recettes

### FonctionnalitÃ©s

- CRUD complet (crÃ©er, lire, modifier, supprimer)
- Import depuis URL (parsing automatique du contenu web)
- Import depuis PDF
- Suggestions IA via Mistral (type repas, nombre de personnes, temps max)
- Gestion des ingrÃ©dients et Ã©tapes
- Versioning des recettes (historique des modifications)
- Retours utilisateur (like/dislike)
- Filtrage par catÃ©gorie, temps de prÃ©paration, compatibilitÃ© (batch, cookeo, rapide)

### Pages frontend

| Page | URL | Description |
| ------ | ----- | ------------- |
| Liste recettes | `/cuisine/recettes` | Catalogue filtrable |
| DÃ©tail recette | `/cuisine/recettes/[id]` | Recette complÃ¨te (ingrÃ©dients, Ã©tapes) |
| Modifier recette | `/cuisine/recettes/[id]/modifier` | Ã‰dition |
| Nouvelle recette | `/cuisine/recettes/nouveau` | Formulaire crÃ©ation |

---

## Planning repas

### FonctionnalitÃ©s

- Planification hebdomadaire (dÃ©jeuner, dÃ®ner, petit-dÃ©jeuner)
- Suggestions IA de menus Ã©quilibrÃ©s
- Templates de semaine rÃ©utilisables
- GÃ©nÃ©ration automatique de liste de courses depuis le planning
- VÃ©rification nutritionnelle (Ã©quilibre protÃ©ines/lÃ©gumes/fÃ©culents)
- Rappel du repas du soir via job planifiÃ©

### Pages frontend

| Page | URL | Description |
| ------ | ----- | ------------- |
| Planning repas | `/cuisine/planning` | Grille semaine avec drag & drop |

---

## Courses

### FonctionnalitÃ©s

- Listes de courses avec articles (nom, quantitÃ©, catÃ©gorie, fait/pas fait)
- Collaboration temps rÃ©el via WebSocket (plusieurs utilisateurs simultanÃ©s)
- ModÃ¨les de courses rÃ©utilisables
- GÃ©nÃ©ration automatique depuis planning repas
- Scan code-barres (camÃ©ra WebRTC)
- Enrichissement automatique possible depuis les jobs de stock bas

### Pages frontend

| Page | URL | Description |
| ------ | ----- | ------------- |
| Courses | `/cuisine/courses` | Listes et articles |

### WebSocket

```
ws://localhost:8000/ws/courses/{liste_id}
```

Ã‰vÃ©nements : article ajoutÃ©, article cochÃ©, article supprimÃ©, liste mise Ã  jour.

---

## Inventaire

### FonctionnalitÃ©s

- Suivi stock alimentaire (nom, quantitÃ©, unitÃ©, catÃ©gorie, date pÃ©remption)
- Alertes produits expirant bientÃ´t (configurable : 3, 7, 14 jours)
- Recherche par code-barres via OpenFoodFacts
- Historique des mouvements (ajout, consommation)
- Import CSV en masse
- Alertes anti-gaspillage alimentÃ©es par les jobs planifiÃ©s

### Pages frontend

| Page | URL | Description |
| ------ | ----- | ------------- |
| Inventaire | `/cuisine/inventaire` | Stock avec filtres et alertes |

---

## Batch cooking

### FonctionnalitÃ©s

- Sessions de batch cooking (sÃ©lection de recettes, planning)
- Ã‰tapes de prÃ©paration groupÃ©e
- PrÃ©parations et stockage (dates de pÃ©remption)
- Configuration batch (nombre de portions, durÃ©e max)
- Archivage automatique des prÃ©parations expirÃ©es via cron

### Pages frontend

| Page | URL | Description |
| ------ | ----- | ------------- |
| Batch cooking | `/cuisine/batch-cooking` | Sessions et prÃ©parations |

---

## Anti-gaspillage

### FonctionnalitÃ©s

- Score anti-gaspillage (basÃ© sur pÃ©remptions, consommation, pertes)
- Suggestions de recettes pour valoriser les produits proches pÃ©remption
- Actions pour rÃ©duire le gaspillage
- Statistiques et tendances
- Base de travail pour les futures interactions pÃ©remption -> recettes automatiques

### Pages frontend

| Page | URL | Description |
| ------ | ----- | ------------- |
| Anti-gaspillage | `/cuisine/anti-gaspillage` | Score, suggestions, actions |

---

## API Reference

### Recettes

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/recettes` | Liste paginÃ©e (filtres : catÃ©gorie, temps, recherche) |
| POST | `/api/v1/recettes` | CrÃ©er une recette |
| GET | `/api/v1/recettes/{id}` | DÃ©tail d'une recette |
| PUT | `/api/v1/recettes/{id}` | Modifier une recette |
| DELETE | `/api/v1/recettes/{id}` | Supprimer une recette |
| POST | `/api/v1/recettes/import-url` | Import depuis URL |

### Courses

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/courses` | Listes de courses |
| POST | `/api/v1/courses` | CrÃ©er une liste |
| POST | `/api/v1/courses/{id}/articles` | Ajouter un article |
| PATCH | `/api/v1/courses/articles/{id}` | Modifier / cocher article |

### Inventaire

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/inventaire` | Stock complet |
| POST | `/api/v1/inventaire` | Ajouter au stock |
| GET | `/api/v1/inventaire/barcode/{code}` | Recherche OpenFoodFacts |
| GET | `/api/v1/inventaire/expirant` | Articles expirant bientÃ´t |

### Planning

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/planning` | Planning semaine |
| POST | `/api/v1/planning/repas` | Ajouter un repas |
| POST | `/api/v1/suggestions` | Suggestions IA repas |

### Batch cooking

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/batch-cooking/sessions` | Sessions |
| POST | `/api/v1/batch-cooking/sessions` | CrÃ©er session |
| GET | `/api/v1/batch-cooking/config` | Configuration |

### Anti-gaspillage

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/anti-gaspillage/score` | Score global |
| GET | `/api/v1/anti-gaspillage/suggestions` | Suggestions recettes |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complÃ¨te de tous les endpoints.
