# API REST Assistant Matanne

API REST FastAPI pour l'accÃ¨s programmatique aux fonctionnalitÃ©s de l'Assistant Matanne.

## ðŸš€ DÃ©marrage rapide

### PrÃ©requis

```bash
# Installer les dÃ©pendances
pip install fastapi uvicorn[standard]
```

### Lancer le serveur

```bash
# Mode dÃ©veloppement avec rechargement automatique
uvicorn src.api.main:app --reload --port 8000

# Mode production
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Documentation interactive

Une fois le serveur lancÃ©:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ðŸ“š Endpoints disponibles

### SantÃ©

| MÃ©thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/` | Information sur l'API |
| GET | `/health` | VÃ©rifie l'Ã©tat de l'API et de la base de donnÃ©es |

### Recettes

| MÃ©thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/recettes` | Liste paginÃ©e des recettes |
| GET | `/api/v1/recettes/{id}` | DÃ©tails d'une recette |
| POST | `/api/v1/recettes` | CrÃ©er une recette |
| PUT | `/api/v1/recettes/{id}` | Mettre Ã  jour une recette |
| DELETE | `/api/v1/recettes/{id}` | Supprimer une recette |

**ParamÃ¨tres de filtrage:**
- `page`: NumÃ©ro de page (dÃ©faut: 1)
- `page_size`: Taille de page (dÃ©faut: 20, max: 100)
- `categorie`: Filtrer par catÃ©gorie
- `search`: Recherche par nom

### Inventaire

| MÃ©thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/inventaire` | Liste de l'inventaire |
| POST | `/api/v1/inventaire` | Ajouter un article |
| GET | `/api/v1/inventaire/barcode/{code}` | Rechercher par code-barres |

**ParamÃ¨tres:**
- `expiring_soon`: Filtrer les articles qui expirent dans 7 jours

### Courses

| MÃ©thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/courses` | Listes de courses |
| POST | `/api/v1/courses` | CrÃ©er une liste |
| POST | `/api/v1/courses/{id}/items` | Ajouter un article Ã  une liste |

### Planning

| MÃ©thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/planning/semaine` | Planning de la semaine |
| POST | `/api/v1/planning/repas` | Ajouter un repas |

### Suggestions IA

| MÃ©thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/suggestions/recettes` | Suggestions basÃ©es sur l'inventaire et l'historique |

## ðŸ” Authentification

L'API utilise des tokens JWT (JSON Web Tokens) pour l'authentification.

### Mode dÃ©veloppement
En mode dÃ©veloppement, un utilisateur par dÃ©faut est utilisÃ© si aucun token n'est fourni.

### Mode production
Ajoutez le header `Authorization` avec un token Bearer:

```bash
curl -H "Authorization: Bearer <votre-token>" \
     http://localhost:8000/api/v1/recettes
```

## ðŸ“– Exemples d'utilisation

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

# CrÃ©er une recette
nouvelle_recette = {
    "nom": "Tarte aux pommes",
    "temps_preparation": 30,
    "temps_cuisson": 45,
    "portions": 8,
    "categorie": "dessert",
    "ingredients": [
        {"nom": "Pommes", "quantite": 6, "unite": "piÃ¨ces"},
        {"nom": "PÃ¢te feuilletÃ©e", "quantite": 1, "unite": "rouleau"},
        {"nom": "Sucre", "quantite": 100, "unite": "g"}
    ],
    "instructions": [
        "PrÃ©chauffer le four Ã  180Â°C",
        "Ã‰plucher et couper les pommes",
        "Disposer sur la pÃ¢te",
        "Enfourner 45 minutes"
    ]
}
response = requests.post(f"{BASE_URL}/recettes", json=nouvelle_recette)
print(f"Recette crÃ©Ã©e: {response.json()}")

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

    console.log(`${data.total} articles expirent bientÃ´t:`);
    data.items.forEach(item => {
        console.log(`- ${item.nom}: ${item.date_peremption}`);
    });
}

// Rechercher par code-barres
async function searchBarcode(code) {
    const response = await fetch(`${BASE_URL}/inventaire/barcode/${code}`);
    const data = await response.json();

    if (data.found !== false) {
        console.log(`TrouvÃ©: ${data.nom}`);
    } else {
        console.log("Article non trouvÃ©");
    }
}
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Liste des recettes
curl "http://localhost:8000/api/v1/recettes?page=1&page_size=10"

# CrÃ©er une recette
curl -X POST http://localhost:8000/api/v1/recettes \
     -H "Content-Type: application/json" \
     -d '{"nom": "Salade", "temps_preparation": 10, "portions": 2}'

# Planning de la semaine
curl http://localhost:8000/api/v1/planning/semaine

# Suggestions IA
curl "http://localhost:8000/api/v1/suggestions/recettes?type_repas=dejeuner&personnes=4"
```

## ðŸ§ª Tests

```bash
# Lancer les tests de l'API
pytest tests/test_api.py -v

# Avec couverture
pytest tests/test_api.py --cov=src.api --cov-report=html
```

## ðŸ“¦ Structure des rÃ©ponses

### RÃ©ponse paginÃ©e
```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
}
```

### RÃ©ponse d'erreur
```json
{
    "detail": "Message d'erreur"
}
```

### Codes HTTP
- `200`: SuccÃ¨s
- `201`: CrÃ©Ã©
- `400`: RequÃªte invalide
- `401`: Non authentifiÃ©
- `403`: Non autorisÃ©
- `404`: Non trouvÃ©
- `422`: Erreur de validation
- `500`: Erreur serveur

## ðŸ”§ Configuration

Variables d'environnement:
- `DATABASE_URL`: URL de connexion PostgreSQL
- `SUPABASE_URL`: URL du projet Supabase
- `SUPABASE_ANON_KEY`: ClÃ© anonyme Supabase

## ðŸ“ Notes

- L'API utilise la mÃªme base de donnÃ©es que l'application frontend
- Les modifications sont reflÃ©tÃ©es en temps rÃ©el
- Utilisez les endpoints de suggestions pour des recommandations intelligentes basÃ©es sur votre historique
