# 📅 Guide Module Planning

> Ce guide couvre le module de planification dans MaTanne : planning familial, timeline, gestion des conflits et rappels.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Hub Planning](#hub-planning)
3. [Timeline](#timeline)
4. [Gestion des conflits](#gestion-des-conflits)
5. [Rappels](#rappels)
6. [Intégration avec les autres modules](#intégration)
7. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Planning** est le calendrier centralisé de toute la vie familiale. Il agrège les événements en provenance de tous les autres modules (cuisines, famille, maison) dans une vue unifiée.

**URL** : `/planning`  
**Service backend** : `src/services/planning/`  
**Route API** : `src/api/routes/planning.py` (`/api/v1/planning`)

---

## Hub Planning

### Fonctionnalités

- Vue hebdomadaire de tous les événements familiaux
- Création rapide d'événements depuis le hub
- Filtrage par catégorie (cuisine, famille, maison, santé…)
- Indicateurs visuels par membre de la famille

### Usage

```
/planning
```

---

## Timeline

### Fonctionnalités

- Vue chronologique linéaire de tous les événements
- Zoom avant/arrière (jour / semaine / mois)
- Glisser-déposer pour repositionner les événements
- Indicateurs de jalons importants (anniversaires, rendez-vous médicaux…)

### Usage

```
/planning/timeline
```

### Composant frontend

La timeline utilise un composant custom qui agrège les données de plusieurs endpoints :

```typescript
// Exemple de requête combinée
const { data: planning } = utiliserRequete(
  ["planning", semaine],
  () => listerPlanningHebdo(semaine)
)
```

---

## Gestion des conflits

Le service détecte automatiquement les conflits de planning (chevauchements d'événements pour un même membre).

```python
from src.services.planning.conflits import ServiceConflitPlanning
service = ServiceConflitPlanning()
conflits = service.detecter_conflits(user_id=1, date_debut=..., date_fin=...)
```

Réponse s'il y a conflit :
```json
{
  "conflit": true,
  "evenements_concurrents": [
    {"id": 42, "titre": "Médecin Jules", "debut": "2026-03-26T14:00"}
  ]
}
```

---

## Rappels

Le service de rappels envoie des notifications push avant les événements.

- **J-1** : rappel la veille pour les RDV importants
- **H-1** : rappel 1h avant l'heure
- Canal de livraison : notifications push (Web Push via `src/api/routes/push.py`)

```python
from src.services.planning.rappels import ServiceRappels
service = ServiceRappels()
service.planifier_rappel(evenement_id=42, delai_minutes=60)
```

---

## Intégration

Le module Planning s'alimente des événements générés par les autres modules :

| Module  | Événements injectés                              |
|---------|--------------------------------------------------|
| Cuisine | Repas planifiés, dates batch-cooking             |
| Famille | Activités, RDV médicaux Jules, anniversaires     |
| Maison  | Tâches d'entretien, rendez-vous artisans         |
| Jeux    | Tirages loto/euromillions à ne pas rater         |

---

## API Reference

### Endpoints principaux

| Méthode | URL                              | Description                      |
|--------|----------------------------------|----------------------------------|
| GET    | `/api/v1/planning`               | Événements de la semaine courante |
| POST   | `/api/v1/planning`               | Créer un événement               |
| PUT    | `/api/v1/planning/{id}`          | Modifier un événement            |
| DELETE | `/api/v1/planning/{id}`          | Supprimer un événement           |
| GET    | `/api/v1/planning/conflits`      | Détecter les conflits            |
| POST   | `/api/v1/planning/rappels`       | Créer un rappel                  |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète.
