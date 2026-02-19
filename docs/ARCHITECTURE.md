# 🏗️ Architecture Technique - Assistant Matanne

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Accueil  │ │ Cuisine  │ │ Famille  │ │ Planning │ ...       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                   │
│       └────────────┴─────┬──────┴────────────┘                  │
│                          │                                       │
│                    OptimizedRouter (lazy loading)                │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                     SERVICES LAYER                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ RecettesSvc│ │ BudgetSvc  │ │ WeatherSvc │ │ BackupSvc  │   │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘   │
│         │              │              │              │           │
│         └──────────────┴──────┬───────┴──────────────┘          │
│                               │                                  │
│                       BaseAIService                              │
│                    (rate limit, cache IA)                        │
└───────────────────────────────┼──────────────────────────────────┘
                                │
┌───────────────────────────────┼──────────────────────────────────┐
│                          CORE LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Database │  │ Models   │  │   AI     │  │  Cache   │        │
│  │ (Pool)   │  │ (ORM)    │  │ (Mistral)│  │ (Redis)  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────────┐ ┌─────────┐ ┌───────────┐ ┌─────────┐
│   Supabase    │ │  SQLAlch│ │  Mistral  │ │  Redis  │
│  PostgreSQL   │ │  ORM    │ │    API    │ │ (opt.)  │
└───────────────┘ └─────────┘ └───────────┘ └─────────┘
```

## Modules Core (src/core/)

### config.py
```python
# Pydantic BaseSettings avec chargement en cascade
# .env.local → .env → st.secrets → constantes
from src.core.config import obtenir_parametres
config = obtenir_parametres()
```

### db/ (Base de données)
```python
# Connexion avec QueuePool (5 connexions, max 10)
from src.core.db import obtenir_contexte_db

with obtenir_contexte_db() as session:
    result = session.query(Recette).all()
```

### decorators.py
```python
@with_db_session      # Injecte automatiquement Session
@with_cache(ttl=300)  # Cache Streamlit 5 min
@with_error_handling  # Gestion erreurs unifiée
```

### models/ (SQLAlchemy 2.0 ORM)
| Fichier | Modèles |
|---------|---------|
| recettes.py | Recette, Ingredient, EtapeRecette, RecetteIngredient |
| inventaire.py | ArticleInventaire, HistoriqueInventaire |
| courses.py | ArticleCourses, ModeleCourses |
| planning.py | Planning, Repas, CalendarEvent |
| famille.py | ChildProfile, Milestone, FamilyActivity, FamilyBudget |
| sante.py | HealthRoutine, HealthObjective, HealthEntry |
| maison.py | Project, Routine, GardenItem |
| nouveaux.py | Depense, BudgetMensuelDB, AlerteMeteo, ConfigMeteo, Backup, CalendrierExterne, PushSubscription |

### ai/ (Intelligence Artificielle)
```python
from src.core.ai import ClientIA, AnalyseurIA, CacheIA

# Utilisation via BaseAIService (recommandé)
class MonService(BaseAIService):
    def suggest(self, prompt: str) -> list:
        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=MonModel
        )
```

## Services (src/services/)

| Service | Description | Modèle DB |
|---------|-------------|-----------|
| recettes.py | CRUD recettes, suggestions IA | Recette, Ingredient |
| budget.py | Dépenses, budgets mensuels | FamilyBudget, Depense* |
| weather.py | Alertes météo jardin | AlerteMeteo*, ConfigMeteo* |
| backup.py | Sauvegarde/restauration | Backup* |
| calendar_sync.py | Sync Google/Apple | CalendrierExterne* |
| push_notifications.py | Web Push | PushSubscription* |
| pdf_export.py | Export PDF | - |

*Nouveaux modèles dans `nouveaux.py`

## Lazy Loading (OptimizedRouter)

```python
# src/app.py
MODULE_REGISTRY = {
    "accueil": "src.modules.accueil",
    "cuisine": "src.modules.cuisine",
    "famille": "src.modules.famille",
    ...
}

# Chaque module exporte app()
def app():
    """Point d'entrée module"""
    st.title("Mon Module")
```

**Performance**: ~60% d'accélération au démarrage

## Sécurité

### Row Level Security (RLS)
```sql
-- Supabase: chaque utilisateur voit ses données
CREATE POLICY depenses_user_policy ON depenses
    FOR ALL USING (user_id = auth.uid());
```

### Multi-tenant

> **Note**: Le module multi-tenant (`multi_tenant.py`) a été supprimé car inutilisé en production.
> L'isolation des données se fait via les politiques RLS de Supabase (voir ci-dessus).

## Cache

### Architecture multi-niveaux (src/core/caching/)
1. **L1**: `CacheMemoireN1` — dict Python en mémoire (ultra rapide, volatile)
2. **L2**: `CacheSessionN2` — st.session_state (persistant pendant la session)
3. **L3**: `CacheFichierN3` — pickle sur disque (persistant entre sessions)

```python
from src.core.caching import avec_cache_multi, obtenir_cache

# Décorateur
@avec_cache_multi(ttl=300, niveaux=["L1", "L2"])
def get_recettes():
    ...

# Cache orchestrateur
cache = obtenir_cache()
cache.set("clé", valeur, ttl=600)
```

### Cache Redis (optionnel)
```python
from src.core.redis_cache import redis_cached

@redis_cached(ttl=3600, tags=["recettes"])
def get_recettes():
    ...
```

### Cache sémantique IA
```python
from src.core.ai import CacheIA
# Cache les réponses IA par similarité sémantique
```

## Conventions

### Nommage (Français)
- Variables: `obtenir_recettes()`, `liste_courses`
- Classes: `GestionnaireMigrations`, `ArticleInventaire`
- Constantes: `CATEGORIES_DEPENSE`, `TYPES_REPAS`

### Structure fichiers
```python
"""
Docstring module
"""
import ...

# Types et schémas
class MonSchema(BaseModel): ...

# Service principal
class MonService:
    def methode(self): ...

# Factory (export)
def get_mon_service() -> MonService:
    return MonService()
```
