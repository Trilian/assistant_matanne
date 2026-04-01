# ?? Guide Module Planning

> Ce guide couvre le module de planification dans MaTanne : planning familial, timeline, gestion des conflits et rappels.

## Table des mati?res

1. [Vue d'ensemble](#vue-densemble)
2. [Hub Planning](#hub-planning)
3. [Timeline](#timeline)
4. [Gestion des conflits](#gestion-des-conflits)
5. [Rappels](#rappels)
6. [Int?gration avec les autres modules](#int?gration)
7. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Planning** est le calendrier centralis? de toute la vie familiale. Il agr?ge les ?v?nements en provenance de tous les autres modules (cuisines, famille, maison) dans une vue unifi?e.

**URL** : `/planning`  
**Service backend** : `src/services/planning/`  
**Route API** : `src/api/routes/planning.py` (`/api/v1/planning`)

---

## Hub Planning

### Fonctionnalit?s

- Vue hebdomadaire de tous les ?v?nements familiaux
- Cr?ation rapide d'?v?nements depuis le hub
- Filtrage par cat?gorie (cuisine, famille, maison, sant?)
- Indicateurs visuels par membre de la famille

### Usage

```
/planning
```

---

## Timeline

### Fonctionnalit?s

- Vue chronologique lin?aire de tous les ?v?nements
- Zoom avant/arri?re (jour / semaine / mois)
- Glisser-d?poser pour repositionner les ?v?nements
- Indicateurs de jalons importants (anniversaires, rendez-vous m?dicaux?)

### Usage

```
/planning/timeline
```

### Composant frontend

La timeline utilise un composant custom qui agr?ge les donn?es de plusieurs endpoints :

```typescript
// Exemple de requ?te combin?e
const { data: planning } = utiliserRequete(
  ["planning", semaine],
  () => listerPlanningHebdo(semaine)
)
```

---

## Gestion des conflits

Le service d?tecte automatiquement les conflits de planning (chevauchements d'?v?nements pour un m?me membre).

```python
from src.services.planning.conflits import ServiceConflitPlanning
service = ServiceConflitPlanning()
conflits = service.detecter_conflits(user_id=1, date_debut=..., date_fin=...)
```

R?ponse s'il y a conflit :
```json
{
  "conflit": true,
  "evenements_concurrents": [
    {"id": 42, "titre": "M?decin Jules", "debut": "2026-03-26T14:00"}
  ]
}
```

---

## Rappels

Le service de rappels envoie des notifications push avant les ?v?nements.

- **J-1** : rappel la veille pour les RDV importants
- **H-1** : rappel 1h avant l'heure
- Canal de livraison : notifications push (Web Push via `src/api/routes/push.py`)

```python
from src.services.planning.rappels import ServiceRappels
service = ServiceRappels()
service.planifier_rappel(evenement_id=42, delai_minutes=60)
```

---

## Int?gration

Le module Planning s'alimente des ?v?nements g?n?r?s par les autres modules :

| Module  | ?v?nements inject?s                              |
| --------- | -------------------------------------------------- |
| Cuisine | Repas planifi?s, dates batch-cooking             |
| Famille | Activit?s, RDV m?dicaux Jules, anniversaires     |
| Maison  | T?ches d'entretien, rendez-vous artisans         |
| Jeux    | Tirages loto/euromillions ? ne pas rater         |

---

## API Reference

### Endpoints principaux

| M?thode | URL                              | Description                      |
| -------- | ---------------------------------- | ---------------------------------- |
| GET    | `/api/v1/planning`               | ?v?nements de la semaine courante |
| POST   | `/api/v1/planning`               | Cr?er un ?v?nement               |
| PUT    | `/api/v1/planning/{id}`          | Modifier un ?v?nement            |
| DELETE | `/api/v1/planning/{id}`          | Supprimer un ?v?nement           |
| GET    | `/api/v1/planning/conflits`      | D?tecter les conflits            |
| POST   | `/api/v1/planning/rappels`       | Cr?er un rappel                  |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation compl?te.
