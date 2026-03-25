# 🍽️ Guide Module Cuisine

> Recettes, planning repas, courses, inventaire, batch cooking et anti-gaspillage.

## Table des matières

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

Le module **Cuisine** est le plus complet de l'application. Il couvre toute la chaîne : trouver des recettes → planifier les repas → générer les courses → suivre le stock → réduire le gaspillage.

**URL** : `/cuisine`  
**Services backend** : `src/services/cuisine/`, `src/services/planning/`, `src/services/inventaire/`  
**Routes API** : `src/api/routes/recettes.py`, `courses.py`, `inventaire.py`, `planning.py`, `batch_cooking.py`, `anti_gaspillage.py`

---

## Recettes

### Fonctionnalités

- CRUD complet (créer, lire, modifier, supprimer)
- Import depuis URL (parsing automatique du contenu web)
- Import depuis PDF
- Suggestions IA via Mistral (type repas, nombre de personnes, temps max)
- Gestion des ingrédients et étapes
- Versioning des recettes (historique des modifications)
- Retours utilisateur (like/dislike)
- Filtrage par catégorie, temps de préparation, compatibilité (batch, cookeo, rapide)

### Pages frontend

| Page | URL | Description |
|------|-----|-------------|
| Liste recettes | `/cuisine/recettes` | Catalogue filtrable |
| Détail recette | `/cuisine/recettes/[id]` | Recette complète (ingrédients, étapes) |
| Modifier recette | `/cuisine/recettes/[id]/modifier` | Édition |
| Nouvelle recette | `/cuisine/recettes/nouveau` | Formulaire création |

---

## Planning repas

### Fonctionnalités

- Planification hebdomadaire (déjeuner, dîner, petit-déjeuner)
- Suggestions IA de menus équilibrés
- Templates de semaine réutilisables
- Génération automatique de liste de courses depuis le planning
- Vérification nutritionnelle (équilibre protéines/légumes/féculents)

### Pages frontend

| Page | URL | Description |
|------|-----|-------------|
| Planning repas | `/cuisine/planning` | Grille semaine avec drag & drop |

---

## Courses

### Fonctionnalités

- Listes de courses avec articles (nom, quantité, catégorie, fait/pas fait)
- Collaboration temps réel via WebSocket (plusieurs utilisateurs simultanés)
- Modèles de courses réutilisables
- Génération automatique depuis planning repas
- Scan code-barres (caméra WebRTC)

### Pages frontend

| Page | URL | Description |
|------|-----|-------------|
| Courses | `/cuisine/courses` | Listes et articles |

### WebSocket

```
ws://localhost:8000/ws/courses/{liste_id}
```

Événements : article ajouté, article coché, article supprimé, liste mise à jour.

---

## Inventaire

### Fonctionnalités

- Suivi stock alimentaire (nom, quantité, unité, catégorie, date péremption)
- Alertes produits expirant bientôt (configurable : 3, 7, 14 jours)
- Recherche par code-barres via OpenFoodFacts
- Historique des mouvements (ajout, consommation)
- Import CSV en masse

### Pages frontend

| Page | URL | Description |
|------|-----|-------------|
| Inventaire | `/cuisine/inventaire` | Stock avec filtres et alertes |

---

## Batch cooking

### Fonctionnalités

- Sessions de batch cooking (sélection de recettes, planning)
- Étapes de préparation groupée
- Préparations et stockage (dates de péremption)
- Configuration batch (nombre de portions, durée max)

### Pages frontend

| Page | URL | Description |
|------|-----|-------------|
| Batch cooking | `/cuisine/batch-cooking` | Sessions et préparations |

---

## Anti-gaspillage

### Fonctionnalités

- Score anti-gaspillage (basé sur péremptions, consommation, pertes)
- Suggestions de recettes pour valoriser les produits proches péremption
- Actions pour réduire le gaspillage
- Statistiques et tendances

### Pages frontend

| Page | URL | Description |
|------|-----|-------------|
| Anti-gaspillage | `/cuisine/anti-gaspillage` | Score, suggestions, actions |

---

## API Reference

### Recettes

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/recettes` | Liste paginée (filtres : catégorie, temps, recherche) |
| POST | `/api/v1/recettes` | Créer une recette |
| GET | `/api/v1/recettes/{id}` | Détail d'une recette |
| PUT | `/api/v1/recettes/{id}` | Modifier une recette |
| DELETE | `/api/v1/recettes/{id}` | Supprimer une recette |
| POST | `/api/v1/recettes/import-url` | Import depuis URL |

### Courses

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/courses` | Listes de courses |
| POST | `/api/v1/courses` | Créer une liste |
| POST | `/api/v1/courses/{id}/articles` | Ajouter un article |
| PATCH | `/api/v1/courses/articles/{id}` | Modifier / cocher article |

### Inventaire

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/inventaire` | Stock complet |
| POST | `/api/v1/inventaire` | Ajouter au stock |
| GET | `/api/v1/inventaire/barcode/{code}` | Recherche OpenFoodFacts |
| GET | `/api/v1/inventaire/expirant` | Articles expirant bientôt |

### Planning

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/planning` | Planning semaine |
| POST | `/api/v1/planning/repas` | Ajouter un repas |
| POST | `/api/v1/suggestions` | Suggestions IA repas |

### Batch cooking

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/batch-cooking/sessions` | Sessions |
| POST | `/api/v1/batch-cooking/sessions` | Créer session |
| GET | `/api/v1/batch-cooking/config` | Configuration |

### Anti-gaspillage

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/anti-gaspillage/score` | Score global |
| GET | `/api/v1/anti-gaspillage/suggestions` | Suggestions recettes |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète de tous les endpoints.
