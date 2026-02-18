# Architecture des Services - Guide de Restructuration

## Vue d'ensemble

Le dossier `src/services/` est organisé en modules par domaine métier avec des imports directs.

## Structure Actuelle

### Organisation par domaine

```
src/services/
├── base/               # Classes de base (BaseAIService, BaseService, async_utils)
├── recettes/           # Gestion des recettes
├── planning/           # Planning repas et activités
├── inventaire/         # Gestion des stocks
├── courses/            # Listes de courses
├── budget/             # Gestion budgétaire
├── batch_cooking/      # Préparation batch
├── suggestions/        # Suggestions IA
├── maison/             # Entretien, jardin, énergie
├── calendrier/         # Calendrier familial + Google Calendar
├── weather/            # Service météo
├── utilisateur/        # Auth, historique, préférences
├── notifications/      # Notifications push
├── integrations/       # APIs externes (codes-barres, météo)
├── jeux/               # Paris sportifs (isolé avec _internal/)
├── garmin/             # Intégration Garmin
├── rapports/           # Export PDF
├── backup/             # Backup/Restore
└── web/                # Services web/PWA
```

### Imports directs (recommandé)

```python
# Recettes
from src.services.recettes import RecetteService, get_recette_service

# Inventaire
from src.services.inventaire import InventaireService, get_inventaire_service

# Courses
from src.services.courses import CoursesService, get_courses_service

# Notifications
from src.services.notifications import NotificationService, obtenir_service_notifications

# Authentification
from src.services.utilisateur import AuthService, get_auth_service

# Météo
from src.services.weather import ServiceMeteo, get_weather_service
```

### Service météo transversal (`integrations/meteo/`)
Utilisé par `maison/jardin` ET `famille/activités`:

```python
from src.services.integrations.meteo import (
    ServiceMeteo, get_weather_service,
    MeteoJour, AlerteMeteo, ConseilJardin, PlanArrosage,
)

# Ou via le parent:
from src.services.integrations import (
    ServiceMeteo, get_weather_service,
)
```

## Phase 3 — Convention de nommage français

Toutes les 29 factory functions ont reçu des alias français (nom primaire) :

```python
# Exemple — le français est primaire, l'anglais est rétrocompatible
def obtenir_service_recettes() -> ServiceRecettes: ...
get_recette_service = obtenir_service_recettes  # alias rétrocompat
```

Services concernés : authentification, historique, preferences, synchronisation,
import_recettes, budget, calendrier, 7× maison/*, 9× jeux/*, 3× integrations/*.

## Phase 4 — Découpage des gros fichiers (mixins)

| Fichier original | Mixin extrait | Lignes extraites |
|------------------|---------------|------------------|
| `rapports/generation.py` (1047→885) | `rapports/planning_pdf.py` — `PlanningReportMixin` | ~160 |
| `recettes/service.py` (1153→548) | `recettes/recettes_ia_generation.py` — `RecettesIAGenerationMixin` | ~605 |
| `inventaire/service.py` (1094→752) | `inventaire/inventaire_io.py` — `InventaireIOMixin` | ~233 |
| | `inventaire/inventaire_stats.py` — `InventaireStatsMixin` | ~210 |
| `calendrier/service.py` (1020→506) | `calendrier/google_calendar.py` — `GoogleCalendarMixin` | ~494 |
| `weather/service.py` (983→794) | `weather/meteo_jardin.py` — `MeteoJardinMixin` | ~232 |

Les méthodes sont injectées via héritage coopératif (MRO Python) :
```python
class ServiceRecettes(BaseService[Recette], BaseAIService, RecipeAIMixin, RecettesIAGenerationMixin):
    # Les méthodes IA sont fournies par RecettesIAGenerationMixin
    pass
```

## Phase 5 — Isolation du module `jeux/`

Structure plugin avec `_internal/` :
```
jeux/
  __init__.py              # API publique (importe depuis _internal/)
  ai_service.py            # Stub rétrocompat → _internal/
  series_service.py        # Stub rétrocompat → _internal/
  ...                      # 9 stubs au total
  _internal/
    __init__.py
    ai_service.py          # Implémentation réelle
    series_service.py
    ...                    # 9 fichiers d'implémentation
```

Tous les imports existants restent fonctionnels via les stubs de rétrocompatibilité.

## Modules existants

- `planning/` - Planning repas et activités
- `maison/` - Entretien, jardin, énergie, projets
- `budget/` - Gestion budgétaire
- `calendrier/` - Calendrier familial (Google Calendar extrait en mixin)
- `jeux/` - Module paris sportifs (isolé avec `_internal/`)
- `garmin/` - Intégration Garmin
- `web/` - Services web/PWA

## Compatibilité

**Les anciens chemins d'import restent fonctionnels:**

```python
# Ces imports continuent de fonctionner:
from src.services.recettes import RecetteService
from src.services.inventaire import get_inventaire_service
from src.services.notifications import PushNotificationService
from src.services.weather import ServiceMeteo
```

## Interface UI extraite

L'interface utilisateur a été extraite vers `src/ui/views/`:

| Service original | UI extraite |
|------------------|-------------|
| `notifications/ui.py` | `ui/views/notifications.py` |
| `weather/service.py` (render_*) | `ui/views/meteo.py` |
| `backup/service.py` (render_*) | `ui/views/sauvegarde.py` |
| `utilisateur/authentification.py` | `ui/views/authentification.py` |
| `utilisateur/historique.py` | `ui/views/historique.py` |
| `recettes/import_url.py` | `ui/views/import_recettes.py` |
| `web/synchronisation.py` | `ui/views/synchronisation.py` |
| `jeux/notification_service.py` | `ui/views/jeux.py` |

Usage:
```python
from src.ui.views import (
    afficher_demande_permission_push,
    afficher_alertes_jardin,
    afficher_formulaire_backup,
    afficher_formulaire_connexion,
    afficher_timeline_activites,
    afficher_importation_recette_url,
    afficher_indicateur_presence,
    afficher_badge_notifications_jeux,
)
```

## Recommandations pour le futur

### Pour les nouveaux développements:
1. Utiliser les imports directs depuis les packages métier
2. Placer tout code UI dans `src/ui/views/`
3. Les services ne doivent JAMAIS importer `streamlit`
4. Utiliser `sync_wrapper` pour créer des versions sync des méthodes async

### Utilitaire async/sync
```python
from src.services.base import sync_wrapper

class MonService:
    async def call_api(self, prompt: str) -> str:
        ...

    # Crée automatiquement la version sync
    call_api_sync = sync_wrapper(call_api)
```

## Surveillance des gros packages

### `jeux/` — 22 fichiers (~4140 lignes)

| Fichier | Lignes | Domaine | Split possible? |
|---------|--------|---------|-----------------|
| `football_data.py` | 541 | Football | Extraire vers `jeux/football/` |
| `prediction_service.py` | 468 | Prédictions | OK |
| `backtest_service.py` | 451 | Backtesting | OK |
| `series_service.py` | 433 | Séries | OK |
| `loto_data.py` | 320 | Loto | Extraire vers `jeux/loto/` |

**Recommandation**: Surveiller. Si le module football grandit, considérer un split `jeux/football/` et `jeux/loto/`.

### `maison/` — 18 fichiers (~4855 lignes)

| Fichier | Lignes | Domaine | Split possible? |
|---------|--------|---------|-----------------|
| `plan_jardin_service.py` | 453 | Jardin | Extraire vers `maison/jardin/` |
| `assistant_ia.py` | 434 | IA | OK |
| `temps_entretien_service.py` | 430 | Entretien | OK |
| `energie_service.py` | 423 | Énergie | Extraire vers `maison/energie/` |
| `jardin_service.py` | 357 | Jardin | Extraire vers `maison/jardin/` |
| `entretien_service.py` | 336 | Entretien | OK |

**Recommandation**: Surveiller. Si le jardin grandit, considérer un split `maison/jardin/` et `maison/entretien/`.

### Seuils d'alerte

| Métrique | Seuil actuel | Seuil d'alerte | Action |
|----------|--------------|----------------|--------|
| Fichiers par package | 22 max | >30 | Split en sous-packages |
| Lignes par fichier | 541 max | >600 | Extraire en mixins |
| Lignes totales package | ~4855 | >6000 | Restructurer |

## Tests de validation

```bash
# Tester les imports de base:
python -c "from src.services.base import BaseAIService, sync_wrapper; print('OK')"
python -c "from src.services.recettes import get_recette_service; print('OK')"
python -c "from src.services.integrations.meteo import ServiceMeteo; print('OK')"

# Tester l'UI extraite:
python -c "from src.ui.views import *; print('OK')"

# Test complet de l'application:
python -c "from src.app import *; print('App OK')"
```
