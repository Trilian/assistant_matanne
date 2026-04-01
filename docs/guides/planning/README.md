# ðŸ“… Guide Module Planning

> Ce guide couvre le module de planification dans MaTanne : planning familial, timeline, gestion des conflits et rappels.

## Table des matiÃ¨res

1. [Vue d'ensemble](#vue-densemble)
2. [Hub Planning](#hub-planning)
3. [Timeline](#timeline)
4. [Gestion des conflits](#gestion-des-conflits)
5. [Rappels](#rappels)
6. [IntÃ©gration avec les autres modules](#intÃ©gration)
7. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Planning** est le calendrier centralisÃ© de toute la vie familiale. Il agrÃ¨ge les Ã©vÃ©nements en provenance de tous les autres modules (cuisines, famille, maison) dans une vue unifiÃ©e.

**URL** : `/planning`  
**Service backend** : `src/services/planning/`  
**Route API** : `src/api/routes/planning.py` (`/api/v1/planning`)

---

## Hub Planning

### FonctionnalitÃ©s

- Vue hebdomadaire de tous les Ã©vÃ©nements familiaux
- CrÃ©ation rapide d'Ã©vÃ©nements depuis le hub
- Filtrage par catÃ©gorie (cuisine, famille, maison, santÃ©â€¦)
- Indicateurs visuels par membre de la famille

### Usage

```
/planning
```

---

## Timeline

### FonctionnalitÃ©s

- Vue chronologique linÃ©aire de tous les Ã©vÃ©nements
- Zoom avant/arriÃ¨re (jour / semaine / mois)
- Glisser-dÃ©poser pour repositionner les Ã©vÃ©nements
- Indicateurs de jalons importants (anniversaires, rendez-vous mÃ©dicauxâ€¦)

### Usage

```
/planning/timeline
```

### Composant frontend

La timeline utilise un composant custom qui agrÃ¨ge les donnÃ©es de plusieurs endpoints :

```typescript
// Exemple de requÃªte combinÃ©e
const { data: planning } = utiliserRequete(
  ["planning", semaine],
  () => listerPlanningHebdo(semaine)
)
```

---

## Gestion des conflits

Le service dÃ©tecte automatiquement les conflits de planning (chevauchements d'Ã©vÃ©nements pour un mÃªme membre).

```python
from src.services.planning.conflits import ServiceConflitPlanning
service = ServiceConflitPlanning()
conflits = service.detecter_conflits(user_id=1, date_debut=..., date_fin=...)
```

RÃ©ponse s'il y a conflit :
```json
{
  "conflit": true,
  "evenements_concurrents": [
    {"id": 42, "titre": "MÃ©decin Jules", "debut": "2026-03-26T14:00"}
  ]
}
```

---

## Rappels

Le service de rappels envoie des notifications push avant les Ã©vÃ©nements.

- **J-1** : rappel la veille pour les RDV importants
- **H-1** : rappel 1h avant l'heure
- Canal de livraison : notifications push (Web Push via `src/api/routes/push.py`)

```python
from src.services.planning.rappels import ServiceRappels
service = ServiceRappels()
service.planifier_rappel(evenement_id=42, delai_minutes=60)
```

---

## IntÃ©gration

Le module Planning s'alimente des Ã©vÃ©nements gÃ©nÃ©rÃ©s par les autres modules :

| Module  | Ã‰vÃ©nements injectÃ©s                              |
| --------- | -------------------------------------------------- |
| Cuisine | Repas planifiÃ©s, dates batch-cooking             |
| Famille | ActivitÃ©s, RDV mÃ©dicaux Jules, anniversaires     |
| Maison  | TÃ¢ches d'entretien, rendez-vous artisans         |
| Jeux    | Tirages loto/euromillions Ã  ne pas rater         |

---

## API Reference

### Endpoints principaux

| MÃ©thode | URL                              | Description                      |
| -------- | ---------------------------------- | ---------------------------------- |
| GET    | `/api/v1/planning`               | Ã‰vÃ©nements de la semaine courante |
| POST   | `/api/v1/planning`               | CrÃ©er un Ã©vÃ©nement               |
| PUT    | `/api/v1/planning/{id}`          | Modifier un Ã©vÃ©nement            |
| DELETE | `/api/v1/planning/{id}`          | Supprimer un Ã©vÃ©nement           |
| GET    | `/api/v1/planning/conflits`      | DÃ©tecter les conflits            |
| POST   | `/api/v1/planning/rappels`       | CrÃ©er un rappel                  |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complÃ¨te.
