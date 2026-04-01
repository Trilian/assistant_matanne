# API REST Assistant Matanne

API REST FastAPI pour l'acc�s programmatique aux fonctionnalit�s de l'Assistant Matanne.

## ?? D�marrage rapide

### Pr�requis

```bash
# Installer les d�pendances
pip install fastapi uvicorn[standard]
```

### Lancer le serveur

```bash
# Mode d�veloppement avec rechargement automatique
uvicorn src.api.main:app --reload --port 8000

# Mode production
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Documentation interactive

Une fois le serveur lanc�:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ?? Endpoints disponibles

### Sant�

| M�thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/` | Information sur l'API |
| GET | `/health` | V�rifie l'�tat de l'API et de la base de donn�es |

### Recettes

| M�thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/recettes` | Liste pagin�e des recettes |
| GET | `/api/v1/recettes/{id}` | D�tails d'une recette |
| POST | `/api/v1/recettes` | Cr�er une recette |
| PUT | `/api/v1/recettes/{id}` | Mettre � jour une recette |
| DELETE | `/api/v1/recettes/{id}` | Supprimer une recette |

**Param�tres de filtrage:**
- `page`: Num�ro de page (d�faut: 1)
- `page_size`: Taille de page (d�faut: 20, max: 100)
- `categorie`: Filtrer par cat�gorie
- `search`: Recherche par nom

### Inventaire

| M�thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/inventaire` | Liste de l'inventaire |
| POST | `/api/v1/inventaire` | Ajouter un article |
| GET | `/api/v1/inventaire/barcode/{code}` | Rechercher par code-barres |

**Param�tres:**
- `expiring_soon`: Filtrer les articles qui expirent dans 7 jours

### Courses

| M�thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/courses` | Listes de courses |
| POST | `/api/v1/courses` | Cr�er une liste |
| POST | `/api/v1/courses/{id}/items` | Ajouter un article � une liste |

### Planning

| M�thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/planning/semaine` | Planning de la semaine |
| POST | `/api/v1/planning/repas` | Ajouter un repas |

### Suggestions IA

| M�thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| GET | `/api/v1/suggestions/recettes` | Suggestions bas�es sur l'inventaire et l'historique |

## ?? Authentification

L'API utilise des tokens JWT (JSON Web Tokens) pour l'authentification.

### Mode d�veloppement
En mode d�veloppement, un utilisateur par d�faut est utilis� si aucun token n'est fourni.

### Mode production
Ajoutez le header `Authorization` avec un token Bearer:

```bash
curl -H "Authorization: Bearer <votre-token>" \
     http://localhost:8000/api/v1/recettes
```

## ?? Exemples d'utilisation

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

# Cr�er une recette
nouvelle_recette = {
    "nom": "Tarte aux pommes",
    "temps_preparation": 30,
    "temps_cuisson": 45,
    "portions": 8,
    "categorie": "dessert",
    "ingredients": [
        {"nom": "Pommes", "quantite": 6, "unite": "pi�ces"},
        {"nom": "P�te feuillet�e", "quantite": 1, "unite": "rouleau"},
        {"nom": "Sucre", "quantite": 100, "unite": "g"}
    ],
    "instructions": [
        "Pr�chauffer le four � 180�C",
        "�plucher et couper les pommes",
        "Disposer sur la p�te",
        "Enfourner 45 minutes"
    ]
}
response = requests.post(f"{BASE_URL}/recettes", json=nouvelle_recette)
print(f"Recette cr��e: {response.json()}")

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

    console.log(`${data.total} articles expirent bient�t:`);
    data.items.forEach(item => {
        console.log(`- ${item.nom}: ${item.date_peremption}`);
    });
}

// Rechercher par code-barres
async function searchBarcode(code) {
    const response = await fetch(`${BASE_URL}/inventaire/barcode/${code}`);
    const data = await response.json();

    if (data.found !== false) {
        console.log(`Trouv�: ${data.nom}`);
    } else {
        console.log("Article non trouv�");
    }
}
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Liste des recettes
curl "http://localhost:8000/api/v1/recettes?page=1&page_size=10"

# Cr�er une recette
curl -X POST http://localhost:8000/api/v1/recettes \
     -H "Content-Type: application/json" \
     -d '{"nom": "Salade", "temps_preparation": 10, "portions": 2}'

# Planning de la semaine
curl http://localhost:8000/api/v1/planning/semaine

# Suggestions IA
curl "http://localhost:8000/api/v1/suggestions/recettes?type_repas=dejeuner&personnes=4"
```

## ?? Tests

```bash
# Lancer les tests de l'API
pytest tests/test_api.py -v

# Avec couverture
pytest tests/test_api.py --cov=src.api --cov-report=html
```

## ?? Structure des r�ponses

### R�ponse pagin�e
```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
}
```

### R�ponse d'erreur
```json
{
    "detail": "Message d'erreur"
}
```

### Codes HTTP
- `200`: Succ�s
- `201`: Cr��
- `400`: Requ�te invalide
- `401`: Non authentifi�
- `403`: Non autoris�
- `404`: Non trouv�
- `422`: Erreur de validation
- `500`: Erreur serveur

## ?? Configuration

Variables d'environnement:
- `DATABASE_URL`: URL de connexion PostgreSQL
- `SUPABASE_URL`: URL du projet Supabase
- `SUPABASE_ANON_KEY`: Cl� anonyme Supabase

## ?? Notes

- L'API utilise la m�me base de donn�es que l'application frontend
- Les modifications sont refl�t�es en temps r�el
- Utilisez les endpoints de suggestions pour des recommandations intelligentes bas�es sur votre historique
