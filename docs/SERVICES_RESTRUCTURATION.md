# Architecture des Services - Guide de Restructuration

## Vue d'ensemble

Le dossier `src/services/` a été réorganisé en modules de façade pour améliorer l'organisation logique du code tout en maintenant la compatibilité avec les imports existants.

## Nouvelle Structure

### 1. `cuisine/` - Services de cuisine et alimentation
Regroupe tous les services liés à la gestion alimentaire:

```python
from src.services.cuisine import (
    # Recettes
    RecetteService, get_recette_service,
    RecipeImportService, get_recipe_import_service,
    # Inventaire
    InventaireService, get_inventaire_service,
    # Courses
    CoursesService, get_courses_service,
    # Batch cooking
    BatchCookingService, get_batch_cooking_service,
    # Suggestions IA
    ServiceSuggestions, obtenir_service_suggestions,
)
```

### 2. `infrastructure/` - Services techniques transversaux
Services d'infrastructure et support:

```python
from src.services.infrastructure import (
    # Notifications
    NotificationService, obtenir_service_notifications,
    PushNotificationService, get_push_notification_service,
    # Rapports PDF
    PDFExportService, get_pdf_export_service,
    RapportsPDFService, get_rapports_pdf_service,
    # Backup
    BackupService, get_backup_service,
    # Utilisateur
    AuthService, get_auth_service,
    ActionHistoryService, get_action_history_service,
    UserPreferenceService, get_user_preference_service,
)
```

### 3. `integrations/meteo/` - Service météo transversal
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
1. Utiliser les nouveaux chemins de façade (`services.cuisine`, `services.infrastructure`)
2. Placer tout code UI dans `src/ui/views/`
3. Les services ne doivent JAMAIS importer `streamlit`

### Migration progressive:
Les fichiers physiques n'ont pas été déplacés pour éviter de casser les imports existants. Une migration complète pourra être effectuée ultérieurement avec:
1. Mise à jour de tous les imports dans le projet
2. Déplacement physique des fichiers
3. Suppression des anciens chemins

## Tests de validation

```bash
# Tester les nouveaux modules:
python -c "from src.services.cuisine import *; print('OK')"
python -c "from src.services.infrastructure import *; print('OK')"
python -c "from src.services.integrations.meteo import *; print('OK')"

# Tester l'UI extraite:
python -c "from src.ui.views import *; print('OK')"

# Test complet de l'application:
python -c "from src.app import *; print('App OK')"
```
