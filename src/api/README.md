# API REST Assistant Matanne

API REST FastAPI pour l'accès programmatique aux fonctionnalités de l'Assistant Matanne.

## 🚀 Démarrage rapide

### Prérequis

```bash
# Installer les dépendances
pip install fastapi uvicorn[standard]
```

### Lancer le serveur

```bash
# Mode développement avec rechargement automatique
uvicorn src.api.main:app --reload --port 8000

# Mode production
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Documentation interactive

Une fois le serveur lancé:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Endpoints disponibles

### Santé

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Information sur l'API |
| GET | `/health` | Vérifie l'état de l'API et de la base de données |

### Recettes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/recettes` | Liste paginée des recettes |
| GET | `/api/v1/recettes/{id}` | Détails d'une recette |
| POST | `/api/v1/recettes` | Créer une recette |
| PUT | `/api/v1/recettes/{id}` | Mettre à jour une recette |
| DELETE | `/api/v1/recettes/{id}` | Supprimer une recette |

**Paramètres de filtrage:**
- `page`: Numéro de page (défaut: 1)
- `page_size`: Taille de page (défaut: 20, max: 100)
- `categorie`: Filtrer par catégorie
- `search`: Recherche par nom

### Inventaire

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/inventaire` | Liste de l'inventaire |
| POST | `/api/v1/inventaire` | Ajouter un article |
| GET | `/api/v1/inventaire/barcode/{code}` | Rechercher par code-barres |

**Paramètres:**
- `expiring_soon`: Filtrer les articles qui expirent dans 7 jours

### Courses

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/courses` | Listes de courses |
| POST | `/api/v1/courses` | Créer une liste |
| POST | `/api/v1/courses/{id}/items` | Ajouter un article à une liste |

### Planning

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/planning/semaine` | Planning de la semaine |
| POST | `/api/v1/planning/repas` | Ajouter un repas |

### Suggestions IA

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/suggestions/recettes` | Suggestions basées sur l'inventaire et l'historique |

## 🔐 Authentification

L'API utilise des tokens JWT (JSON Web Tokens) pour l'authentification.

### Mode développement
En mode développement, un utilisateur par défaut est utilisé si aucun token n'est fourni.

### Mode production
Ajoutez le header `Authorization` avec un token Bearer:

```bash
curl -H "Authorization: Bearer <votre-token>" \
     http://localhost:8000/api/v1/recettes
```

## 📖 Exemples d'utilisation

### Python avec requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Lister les recettes
response = requests.get(f"{BASE_URL}/recettes", params={
    "page": 1,
    "page_size": 10,
    "categorie": "dessert"
})
recettes = response.json()
print(f"Total: {recettes['total']} recettes")

# Créer une recette
nouvelle_recette = {
    "nom": "Tarte aux pommes",
    "temps_preparation": 30,
    "temps_cuisson": 45,
    "portions": 8,
    "categorie": "dessert",
    "ingredients": [
        {"nom": "Pommes", "quantite": 6, "unite": "pièces"},
        {"nom": "Pâte feuilletée", "quantite": 1, "unite": "rouleau"},
        {"nom": "Sucre", "quantite": 100, "unite": "g"}
    ],
    "instructions": [
        "Préchauffer le four à 180°C",
        "Éplucher et couper les pommes",
        "Disposer sur la pâte",
        "Enfourner 45 minutes"
    ]
}
response = requests.post(f"{BASE_URL}/recettes", json=nouvelle_recette)
print(f"Recette créée: {response.json()}")

# Obtenir des suggestions
response = requests.get(f"{BASE_URL}/suggestions/recettes", params={
    "type_repas": "diner",
    "personnes": 4,
    "temps_max": 30
})
suggestions = response.json()
for s in suggestions["suggestions"]:
    print(f"- {s['nom']} (score: {s['score']})")
```

### JavaScript avec fetch

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Lister l'inventaire avec items qui expirent
async function getExpiringItems() {
    const response = await fetch(`${BASE_URL}/inventaire?expiring_soon=true`);
    const data = await response.json();

    console.log(`${data.total} articles expirent bientôt:`);
    data.items.forEach(item => {
        console.log(`- ${item.nom}: ${item.date_peremption}`);
    });
}

// Rechercher par code-barres
async function searchBarcode(code) {
    const response = await fetch(`${BASE_URL}/inventaire/barcode/${code}`);
    const data = await response.json();

    if (data.found !== false) {
        console.log(`Trouvé: ${data.nom}`);
    } else {
        console.log("Article non trouvé");
    }
}
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Liste des recettes
curl "http://localhost:8000/api/v1/recettes?page=1&page_size=10"

# Créer une recette
curl -X POST http://localhost:8000/api/v1/recettes \
     -H "Content-Type: application/json" \
     -d '{"nom": "Salade", "temps_preparation": 10, "portions": 2}'

# Planning de la semaine
curl http://localhost:8000/api/v1/planning/semaine

# Suggestions IA
curl "http://localhost:8000/api/v1/suggestions/recettes?type_repas=dejeuner&personnes=4"
```

## 🧪 Tests

```bash
# Lancer les tests de l'API
pytest tests/test_api.py -v

# Avec couverture
pytest tests/test_api.py --cov=src.api --cov-report=html
```

## 📦 Structure des réponses

### Réponse paginée
```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
}
```

### Réponse d'erreur
```json
{
    "detail": "Message d'erreur"
}
```

### Codes HTTP
- `200`: Succès
- `201`: Créé
- `400`: Requête invalide
- `401`: Non authentifié
- `403`: Non autorisé
- `404`: Non trouvé
- `422`: Erreur de validation
- `500`: Erreur serveur

## 🔧 Configuration

Variables d'environnement:
- `DATABASE_URL`: URL de connexion PostgreSQL
- `SUPABASE_URL`: URL du projet Supabase
- `SUPABASE_ANON_KEY`: Clé anonyme Supabase

## 📝 Notes

- L'API utilise la même base de données que l'application frontend
- Les modifications sont reflétées en temps réel
- Utilisez les endpoints de suggestions pour des recommandations intelligentes basées sur votre historique
