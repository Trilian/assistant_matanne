# 🏠 Module Maison - Documentation complète

## Vue d'ensemble

Module complet pour la **gestion domestique** avec 3 sous-modules intégrés et IA intelligente:

- 🏗️ **Projets** : Rénovations, aménagements, projets maison
- 🌿 **Jardin** : Gestion des plantes, arrosage, récoltes
- 🧹 **Entretien** : Routines ménagères, tâches quotidiennes

## Architecture

```
src/modules/maison/
├── __init__.py ..................... Hub d'accueil + navigation
├── helpers.py ....................... Fonctions partagées en cache
├── jardin.py ......................... Module Jardin + JardinService (IA)
├── projets.py ........................ Module Projets + ProjetsService (IA)
└── entretien.py ...................... Module Entretien + EntretienService (IA)
```

## Modèles de base de données utilisés

### Projets
- **Project** : nom, description, statut, priorité, dates
- **ProjectTask** : tâches avec statut, priorité, assignation

### Jardin
- **GardenItem** : plante, type, localisation, dates plantation/récolte
- **GardenLog** : journal (arrosage, désherbage, etc.)

### Entretien
- **Routine** : routine quotidienne/hebdomadaire/mensuelle
- **RoutineTask** : tâches de la routine avec heure et completion

## Fonctionnalités par module

### 🏗️ Projets
| Feature | IA | Description |
|---------|-----|------------|
| **Suggérer tâches** | ✅ | IA génère 5-7 tâches pour un projet |
| **Estimer durée** | ✅ | Prédiction basée sur complexité |
| **Prioriser tâches** | ✅ | Réordonne tâches par ordre logique |
| **Analyser risques** | ✅ | Identifie blocages potentiels |
| **Suivi progression** | ❌ | Barre % + nombre tâches |
| **Alertes urgentes** | ❌ | Projets en retard / haute priorité |

**Points clés:**
- Cache des plantes par type/arrosage
- Détection automatique des projets urgents
- Templates (rénovation, potager, peinture)
- Graphiques de progression Plotly

### 🌿 Jardin
| Feature | IA | Description |
|---------|-----|------------|
| **Conseils saison** | ✅ | 3-4 conseils pratiques par saison |
| **Plantes recommandées** | ✅ | Quoi planter maintenant |
| **Conseil arrosage** | ✅ | Fréquence, quantité, moment |
| **Arrosage intelligent** | ❌ | Détecte quand arroser |
| **Récoltes prévues** | ❌ | Alertes récoltes proches |
| **Journal d'entretien** | ❌ | Log de toutes les actions |

**Points clés:**
- Détection automatique saison (Printemps/Été/Automne/Hiver)
- Cache des plantes à arroser
- Statuts plantes (actif/inactif/mort)
- Log avec date/action/notes
- Suggestions rapides (tomates, basilic, etc.)

### 🧹 Entretien
| Feature | IA | Description |
|---------|-----|------------|
| **Créer routine** | ✅ | IA suggère 5-8 tâches |
| **Optimiser semaine** | ✅ | Distribution Lun-Dim équilibrée |
| **Estimer temps** | ✅ | Durée min/max + fréquence idéale |
| **Astuces efficacité** | ✅ | 5 conseils pratiques |
| **Checklist quotidienne** | ❌ | Tâches du jour avec progression |
| **Routines récurrentes** | ❌ | Quotidien/hebdo/mensuel |

**Points clés:**
- Catégories (Cuisine, Salle de bain, Chambres, Salon, Extérieur)
- Fréquences configurables
- Checklist avec completion % 
- Templates pré-définis
- Heure prévue par tâche (optionnel)

## Services IA

### JardinService
```python
class JardinService(BaseAIService):
    async def generer_conseils_saison(saison: str) -> str
    async def suggerer_plantes_saison(saison: str, climat: str) -> str
    async def conseil_arrosage(nom_plante: str, saison: str) -> str
```

### ProjetsService
```python
class ProjetsService(BaseAIService):
    async def suggerer_taches(nom_projet: str, description: str) -> str
    async def estimer_duree(nom_projet: str, complexite: str) -> str
    async def prioriser_taches(nom_projet: str, taches_texte: str) -> str
    async def conseil_blocages(nom_projet: str, description: str) -> str
```

### EntretienService
```python
class EntretienService(BaseAIService):
    async def creer_routine(nom: str, description: str) -> str
    async def optimiser_semaine(types_taches: str) -> str
    async def conseil_temps_estime(tache: str) -> str
    async def conseil_efficacite() -> str
```

## Helpers (Fonctions partagées)

### Projets
- `charger_projets(statut)` : Charge + calcule progression
- `get_projets_urgents()` : Détecte retards + haute priorité
- `get_stats_projets()` : Total/en cours/terminés + moyenne

### Jardin
- `charger_plantes()` : Charge avec détection besoin arrosage
- `get_plantes_a_arroser()` : Liste plantes qui en ont besoin
- `get_recoltes_proches()` : Récoltes dans les 7 prochains jours
- `get_saison()` : Détermine saison (basée sur mois)

### Entretien
- `charger_routines()` : Charge + calcule completion du jour
- `get_taches_today()` : Tâches à faire aujourd'hui
- `get_stats_entretien()` : Routines/tâches + completion %

## Patterns d'utilisation

### Décorateurs utilisés
```python
@with_db_session          # Injection Session automatique
@st.cache_data(ttl=1800)  # Cache Streamlit 30min
@gerer_erreurs            # Gestion erreurs unifiée
```

### Appels IA
```python
import asyncio

service = get_jardin_service()
result = asyncio.run(service.generer_conseils_saison("Printemps"))
# Automatiquement: rate limiting + cache sémantique + gestion erreurs
```

### Gestion du cache
```python
from src.modules.maison.helpers import clear_maison_cache

# Après modification de données
clear_maison_cache()  # Invalide tout le cache Streamlit
st.rerun()
```

## Structure des données retournées

### Projets
```python
{
    "id": int,
    "nom": str,
    "description": str,
    "statut": str,  # "en_cours", "terminé", "annulé"
    "priorite": str,  # "basse", "moyenne", "haute", "urgente"
    "progress": float,  # 0-100
    "jours_restants": int | None,
    "taches_count": int
}
```

### Plantes
```python
{
    "id": int,
    "nom": str,
    "type": str,  # "Légume", "Fruit", "Herbe aromatique", etc.
    "location": str,
    "plantation": date,
    "recolte": date | None,
    "a_arroser": bool,
    "jours_depuis_arrosage": int | None,
    "notes": str
}
```

### Routines
```python
{
    "id": int,
    "nom": str,
    "categorie": str,
    "frequence": str,  # "quotidien", "hebdomadaire", etc.
    "tasks_count": int,
    "tasks_aujourd_hui": int,
    "completion": float,  # 0-100
    "description": str
}
```

## Point d'entrée principal

```python
# Dans app.py principal
from src.modules.maison import app

# Chargement différé via OptimizedRouter
module_maison.app()
```

## Intégration avec autres modules

- **Cuisine** : Synchronisation possible liste courses (future)
- **Famille** : Budget partagé si ajout fonction tracker
- **Planning** : Affichage projets urgents dans calendrier

## Améliorations futures

- [ ] Sync liste courses Cuisine → Jardin/Projets
- [ ] Notifications push pour tâches urgentes
- [ ] Graphiques Gantt pour projets
- [ ] Intégration données météo API réelle
- [ ] Récurrence automatique tâches (repeating)
- [ ] Assignation par personne
- [ ] Historique photos avant/après projets
- [ ] Intégration calendrier planning

## Testing

```bash
# Tester les imports
pytest tests/test_maison.py -v

# Ou manuellement
python -c "from src.modules.maison import app; app()"
```

## FAQ

**Q: Pourquoi cache_data au lieu de cache_resource?**  
A: Cache des données (DataFrames, listes) qui changent souvent (1800s). Les ressources longues vivraient plus longtemps.

**Q: Comment ajouter une nouvelle IA feature?**  
A: Ajouter `async def` à la classe `*Service`, utiliser `self.call_with_cache()`.

**Q: Où modifier les templates de projets?**  
A: Dans `projets.py`, fonction `app()`, variable `templates`.

**Q: Comment intégrer une vraie API météo?**  
A: Remplacer `get_meteo_mock()` par vrai appel API, adapter `generer_conseils_saison()`.

---

**Version** : 1.0  
**Date** : 25 Janvier 2026  
**Status** : Production-ready ✅
