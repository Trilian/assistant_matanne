# Plan de Division des Fichiers Volumineux (Phase 2)

Ce document détaille le plan de division des fichiers > 500 lignes.

## Priorité 1: Fichiers Critiques (> 1000 lignes)

### 1. `src/services/recettes.py` (1236 lignes)
**Division proposée:**
- `recettes/service.py` - Service principal CRUD (~300L)
- `recettes/ai_service.py` - Génération IA (~350L)
- `recettes/schemas.py` - Schémas Pydantic (~150L)
- `recettes/io_service.py` - Import/Export CSV/JSON (~200L)
- `recettes/version_service.py` - Versions bébé/batch (~200L)
- `recettes/__init__.py` - Re-exports

### 2. `src/services/rapports_pdf.py` (1161 lignes)
**Division proposée:**
- `rapports_pdf/service.py` - Service principal (~200L)
- `rapports_pdf/templates.py` - Templates HTML (~400L)
- `rapports_pdf/generators.py` - Générateurs par type (~400L)
- `rapports_pdf/styles.py` - Styles CSS (~100L)
- `rapports_pdf/__init__.py` - Re-exports

### 3. `src/services/inventaire.py` (1096 lignes)
**Division proposée:**
- `inventaire/service.py` - Service CRUD (~300L)
- `inventaire/ai_service.py` - Suggestions IA (~250L)
- `inventaire/schemas.py` - Schémas Pydantic (~150L)
- `inventaire/alerts.py` - Alertes stock/péremption (~200L)
- `inventaire/__init__.py` - Re-exports

## Priorité 2: Fichiers Importants (800-1000 lignes)

### 4. `src/api/main.py` (939 lignes)
**Division proposée:**
- `api/main.py` - App FastAPI + middleware (~150L)
- `api/routes/recettes.py` - Routes recettes (~200L)
- `api/routes/inventaire.py` - Routes inventaire (~150L)
- `api/routes/planning.py` - Routes planning (~150L)
- `api/routes/courses.py` - Routes courses (~150L)
- `api/schemas.py` - Schémas Pydantic API (~150L)

### 5. `src/services/push_notifications.py` (990 lignes)
**Division proposée:**
- `push_notifications/service.py` - Service principal (~300L)
- `push_notifications/providers.py` - Fournisseurs (FCM, APNS) (~350L)
- `push_notifications/templates.py` - Templates de messages (~150L)
- `push_notifications/scheduler.py` - Planification (~150L)

### 6. `src/services/calendar_sync/service.py` (961 lignes)
**Division proposée:**
- `calendar_sync/service.py` - Service principal (~250L)
- `calendar_sync/google.py` - Intégration Google Calendar (~300L)
- `calendar_sync/outlook.py` - Intégration Outlook (~200L)
- `calendar_sync/sync_engine.py` - Moteur de synchronisation (~200L)

## Priorité 3: Fichiers Volumineux (700-800 lignes)

### 7. `src/services/auth.py` (956 lignes)
**Division proposée:**
- `auth/service.py` - Service authentification (~300L)
- `auth/jwt.py` - Gestion tokens JWT (~200L)
- `auth/permissions.py` - Permissions et rôles (~200L)
- `auth/oauth.py` - OAuth providers (~200L)

### 8. `src/services/weather.py` (937 lignes)
**Division proposée:**
- `weather/service.py` - Service principal (~300L)
- `weather/providers.py` - Fournisseurs API (~300L)
- `weather/utils.py` - Utilitaires météo (~300L)

## Priorité 4: Autres Fichiers (500-700 lignes)

| Fichier | Lignes | Action Suggérée |
|---------|--------|-----------------|
| `src/services/recipe_import.py` | 895 | Merger avec recettes/io_service.py |
| `src/services/weather_utils.py` | 847 | Merger avec weather/ |
| `src/ui/tablet_mode.py` | 822 | Diviser par composant UI |
| `src/services/pwa.py` | 812 | Diviser service/manifest/sw |
| `src/services/batch_cooking.py` | 794 | Laisser ou diviser légèrement |
| `src/modules/planning/logic/calendrier_unifie_logic.py` | 786 | Diviser par fonctionnalité |
| `src/services/backup.py` | 779 | Diviser backup/restore |
| `src/services/budget/service.py` | 713 | Acceptable, légère division |
| `src/core/performance.py` | 697 | Diviser profiler/metrics |
| `src/core/cache_multi.py` | 693 | Acceptable pour un cache complexe |

## Recommandation d'Exécution

1. **Immédiat**: Diviser recettes.py, main.py (impact maximal)
2. **Court terme**: Diviser inventaire.py, auth.py, rapports_pdf.py
3. **Moyen terme**: Reste des fichiers > 700L
4. **Optionnel**: Fichiers 500-700L (selon besoins)

## Convention de Nommage Post-Division

Après division, utiliser des packages Python:
```
src/services/
├── recettes/
│   ├── __init__.py      # from .service import RecetteService
│   ├── service.py       # RecetteService (CRUD)
│   ├── ai_service.py    # RecetteAIService
│   ├── schemas.py       # Schémas Pydantic
│   └── io_service.py    # Import/Export
├── inventaire/
│   ├── __init__.py
│   ├── service.py
│   └── ...
```

## Script de Migration Automatique

Voir `scripts/divide_large_files.py` pour exécuter la division automatiquement.
