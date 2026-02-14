# 📡 API Reference - Assistant Matanne

Documentation complète de l'API REST FastAPI.

## Vue d'ensemble

| Attribut | Valeur |
|----------|--------|
| **Base URL** | `http://localhost:8000` |
| **Documentation** | `/docs` (Swagger), `/redoc` (ReDoc) |
| **Version** | 1.0.0 |
| **Authentification** | JWT Bearer Token |

## 🔐 Authentification

```bash
# Header requis
Authorization: Bearer <token>

# Mode développement (sans token)
# Utilisateur par défaut automatique
```

## 📖 Endpoints

### Santé & Informations

#### `GET /`
Informations sur l'API.

**Réponse:**
```json
{
    "nom": "Assistant Matanne API",
    "version": "1.0.0",
    "status": "active"
}
```

#### `GET /health`
Vérifie l'état de l'API et de la base de données.

**Réponse:**
```json
{
    "status": "healthy",
    "database": true,
    "timestamp": "2025-01-18T10:00:00"
}
```

---

### 🍽️ Recettes

#### `GET /api/v1/recettes`
Liste paginée des recettes.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `page` | int | 1 | Numéro de page |
| `page_size` | int | 20 | Taille de page (max: 100) |
| `categorie` | str | - | Filtrer par catégorie |
| `search` | str | - | Recherche par nom |

**Réponse:**
```json
{
    "items": [
        {
            "id": 1,
            "nom": "Tarte aux pommes",
            "temps_preparation": 30,
            "temps_cuisson": 45,
            "portions": 8,
            "categorie": "dessert"
        }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
}
```

#### `GET /api/v1/recettes/{id}`
Détails d'une recette avec ingrédients et instructions.

**Réponse:**
```json
{
    "id": 1,
    "nom": "Tarte aux pommes",
    "description": "Délicieuse tarte traditionnelle",
    "temps_preparation": 30,
    "temps_cuisson": 45,
    "portions": 8,
    "categorie": "dessert",
    "ingredients": [
        {"nom": "Pommes", "quantite": 6, "unite": "pièces"}
    ],
    "instructions": ["Préchauffer le four...", "..."]
}
```

#### `POST /api/v1/recettes`
Créer une nouvelle recette.

**Corps de requête:**
```json
{
    "nom": "Ma recette",
    "temps_preparation": 20,
    "temps_cuisson": 30,
    "portions": 4,
    "categorie": "plat",
    "ingredients": [
        {"nom": "Ingrédient", "quantite": 100, "unite": "g"}
    ],
    "instructions": ["Étape 1", "Étape 2"]
}
```

#### `PUT /api/v1/recettes/{id}`
Mettre à jour une recette existante.

#### `DELETE /api/v1/recettes/{id}`
Supprimer une recette.

---

### 📦 Inventaire

#### `GET /api/v1/inventaire`
Liste de l'inventaire.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `expiring_soon` | bool | Filtrer articles expirant dans 7 jours |

**Réponse:**
```json
{
    "items": [
        {
            "id": 1,
            "nom": "Lait",
            "quantite": 2,
            "unite": "L",
            "code_barres": "3017760000000",
            "date_peremption": "2025-01-25"
        }
    ],
    "total": 50
}
```

#### `POST /api/v1/inventaire`
Ajouter un article à l'inventaire.

**Corps de requête:**
```json
{
    "nom": "Yaourts",
    "quantite": 4,
    "unite": "pièces",
    "code_barres": "3017760000123",
    "date_peremption": "2025-02-01"
}
```

#### `GET /api/v1/inventaire/barcode/{code}`
Rechercher un article par code-barres.

**Réponse (trouvé):**
```json
{
    "found": true,
    "id": 42,
    "nom": "Nutella",
    "quantite": 1,
    "date_peremption": "2025-06-15"
}
```

**Réponse (non trouvé):**
```json
{
    "found": false,
    "code": "3017760000999"
}
```

---

### 🛒 Courses

#### `GET /api/v1/courses`
Liste des listes de courses.

**Réponse:**
```json
{
    "items": [
        {
            "id": 1,
            "nom": "Courses de la semaine",
            "date_creation": "2025-01-18",
            "nb_articles": 15,
            "nb_faits": 8
        }
    ]
}
```

#### `POST /api/v1/courses`
Créer une nouvelle liste de courses.

**Corps de requête:**
```json
{
    "nom": "Courses samedi"
}
```

#### `POST /api/v1/courses/{id}/items`
Ajouter un article à une liste.

**Corps de requête:**
```json
{
    "nom": "Pain",
    "quantite": 2,
    "categorie": "boulangerie"
}
```

---

### 📅 Planning

#### `GET /api/v1/planning/semaine`
Planning de la semaine.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `date_debut` | str | Date de début (YYYY-MM-DD), défaut: lundi courant |

**Réponse:**
```json
{
    "semaine": "2025-W03",
    "date_debut": "2025-01-13",
    "date_fin": "2025-01-19",
    "repas": [
        {
            "date": "2025-01-13",
            "type": "diner",
            "recette_id": 42,
            "recette_nom": "Lasagnes"
        }
    ]
}
```

#### `POST /api/v1/planning/repas`
Ajouter un repas au planning.

**Corps de requête:**
```json
{
    "date": "2025-01-20",
    "type": "diner",
    "recette_id": 15
}
```

---

### 🤖 Suggestions IA

#### `GET /api/v1/suggestions/recettes`
Obtenir des suggestions de recettes intelligentes basées sur l'inventaire et l'historique.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `type_repas` | str | "petit-dejeuner", "dejeuner", "diner", "gouter" |
| `personnes` | int | Nombre de personnes |
| `temps_max` | int | Temps de préparation max (minutes) |

**Réponse:**
```json
{
    "suggestions": [
        {
            "id": 12,
            "nom": "Omelette aux champignons",
            "score": 0.95,
            "raison": "Ingrédients disponibles, rapide"
        }
    ]
}
```

---

## 📦 Codes de réponse

| Code | Description |
|------|-------------|
| `200` | Succès |
| `201` | Créé avec succès |
| `400` | Requête invalide |
| `401` | Non authentifié |
| `403` | Non autorisé |
| `404` | Ressource non trouvée |
| `422` | Erreur de validation |
| `429` | Trop de requêtes (rate limit) |
| `500` | Erreur serveur |

## 🔒 Rate Limiting

L'API implémente une limitation de débit:

| Type | Limite |
|------|--------|
| Par IP | 100 req/min |
| Par utilisateur | 1000 req/min |
| Endpoints IA | 20 req/min |

**Headers de réponse:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705579200
```

## 🧪 Tests

```bash
# Tests API complets
pytest tests/api/ -v

# Avec couverture
pytest tests/api/ --cov=src/api --cov-report=html
```

## 📚 Voir aussi

- [README API](../src/api/README.md) - Documentation rapide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Architecture technique
- [FONCTIONNALITES.md](./FONCTIONNALITES.md) - Fonctionnalités complètes
