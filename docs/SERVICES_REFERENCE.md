# 🔧 Services Reference — Assistant MaTanne

> Documentation des services backend, leur architecture et leurs APIs internes.

---

## Architecture des services

```text
┌─────────────────────────────────────────────────────────┐
│              Frontend (Next.js / React)                  │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP / WebSocket
┌─────────────────────────▼───────────────────────────────┐
│              Routes API (src/api/routes/)                │
│       20 routeurs FastAPI — auth, CRUD, IA              │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                  Services Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Cuisine  │ │ Famille  │ │  Maison  │ │   Jeux   │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       └────────────┴─────┬──────┴────────────┘          │
│                   BaseAIService                          │
│            (rate limit, cache, parsing)                  │
└──────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    Core Layer                            │
│  Database │ Models │ AI Client │ Cache │ Config         │
└─────────────────────────────────────────────────────────┘
```

### Pattern singleton — `@service_factory`

Tous les services exposent une fonction factory décorée `@service_factory` qui garantit un singleton via le registre :

```python
from src.services.core.registry import service_factory

@service_factory("recettes", tags={"cuisine"})
def get_recette_service() -> RecetteService:
    return RecetteService()
```

### BaseAIService

Les services nécessitant l'IA héritent de `BaseAIService` (`src/services/core/base/ai_service.py`) qui fournit automatiquement :

- Limitation de débit (quotidien + horaire)
- Cache sémantique des requêtes
- Parsing JSON/Pydantic des réponses
- Gestion d'erreurs et fallback

---

## Services par domaine

### Recettes — `src/services/cuisine/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `service.py` | `RecetteService` | `get_recette_service()` | CRUD recettes + suggestions IA |
| `importer.py` | `ImporterRecette` | — | Import depuis URL / PDF |
| `suggestions.py` | `ServiceSuggestions(BaseAIService)` | `get_suggestions_service()` | Suggestions IA (repas, recettes) |

```python
from src.services.cuisine import get_recette_service

service = get_recette_service()
recette = service.creer_recette(data)
suggestions = service.suggerer_recettes(type_repas="diner", personnes=4)
recette = service.importer_depuis_url("https://...")
```

---

### Courses — `src/services/cuisine/` (via routes)

Gestion des listes de courses. Collaboration temps réel via WebSocket (`src/api/websocket_courses.py`).

```python
# Endpoints API principaux
GET  /api/v1/courses          # Lister les listes
POST /api/v1/courses          # Créer une liste
POST /api/v1/courses/{id}/articles  # Ajouter article
WS   /ws/courses/{liste_id}   # Collaboration temp réel
```

---

### Inventaire — `src/services/inventaire/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `service.py` | `InventaireService` | `get_inventaire_service()` | Stock alimentaire, code-barres, alertes péremption |

```python
from src.services.inventaire import get_inventaire_service

service = get_inventaire_service()
articles = service.lister_articles()
article = service.rechercher_barcode("3017760000123")  # OpenFoodFacts
expirant = service.articles_expirant_bientot(jours=7)
```

---

### Planning — `src/services/planning/`

Service modulaire divisé en sous-modules :

| Fichier | Description |
|---------|-------------|
| `service.py` | Service principal (planning semaine, repas, suggestions IA) |
| `nutrition.py` | Équilibre nutritionnel |
| `agregation.py` | Agrégation liste courses depuis planning |
| `formatters.py` | Formatage pour l'API |
| `validators.py` | Validation des plannings |
| `prompts.py` | Génération prompts IA |

```python
from src.services.planning import get_planning_service

service = get_planning_service()
semaine = service.planning_semaine("2026-W13")
suggestions = service.suggerer_repas_semaine()
```

---

### Famille — `src/services/famille/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `service.py` | `FamilleService` | `get_famille_service()` | CRUD enfants, activités, routines, budget |
| `jules_ai.py` | `JulesAIService(BaseAIService)` | `get_jules_ai_service()` | Suggestions développement Jules (streaming) |
| `weekend_ai.py` | `WeekendAIService(BaseAIService)` | `get_weekend_ai_service()` | Suggestions activités weekend IA |

---

### Maison — `src/services/maison/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `service.py` | `MaisonService` | `get_maison_service()` | Projets, entretien, jardin, énergie, stocks |

Sous-modules mixins (façade pattern) :
- `jardin_ia_mixin.py` / `jardin_crud_mixin.py` — Jardin IA + CRUD
- `projets_ia_mixin.py` / `projets_crud_mixin.py` — Projets IA + CRUD

---

### Jeux — `src/services/jeux/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `service.py` | `JeuxService` | `get_jeux_service()` | Paris sportifs, Loto, EuroMillions |

---

### Dashboard — `src/services/dashboard/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `service.py` | `DashboardService` | `get_dashboard_service()` | Agrégation métriques pour tableau de bord |

---

### Utilitaires — `src/services/utilitaires/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `service.py` | `UtilitairesService` | `get_utilitaires_service()` | Chat IA, notes, outils divers |

---

### Rapports — `src/services/rapports/`

| Fichier | Classe | Factory | Description |
|---------|--------|---------|-------------|
| `export.py` | `ServiceExportPDF` | `get_export_service()` | Export PDF (recettes, planning, courses, budget) |

---

### Intégrations — `src/services/integrations/`

| Fichier | Description |
|---------|-------------|
| `multimodal.py` | IA images (analyse, OCR) |
| `webhooks.py` | Envoi webhooks HTTP POST sur événements métier |
| `weather/` | Service météo (agrégation APIs, fallback) |

---

## Services transversaux (core)

### Registre — `src/services/core/registry.py`

Registre singleton avec décorateur `@service_factory`. Permet le lookup par nom et tags.

### Bus d'événements — `src/services/core/events/`

Bus pub/sub avec wildcards pour le découplage inter-services. 14 événements typés.

### Audit — `src/services/core/audit.py`

Trail d'audit transversal : souscription wildcard bus, buffer mémoire, persistence DB.

### Utilisateur — `src/services/core/utilisateur/profils.py`

CRUD profils utilisateurs.

---

## Référence rapide factories

```python
# Cuisine
from src.services.cuisine import get_recette_service
from src.services.inventaire import get_inventaire_service
from src.services.planning import get_planning_service

# Famille
from src.services.famille import get_famille_service

# Maison
from src.services.maison import get_maison_service

# Jeux
from src.services.jeux import get_jeux_service

# Dashboard
from src.services.dashboard import get_dashboard_service

# Utilitaires
from src.services.utilitaires import get_utilitaires_service

# Rapports
from src.services.rapports import get_export_service
```

