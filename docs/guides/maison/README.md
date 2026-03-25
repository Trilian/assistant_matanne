# 🏡 Guide Module Maison

> Ce guide couvre la gestion complète de la maison dans MaTanne : projets, entretien, jardin, énergie, artisans, stocks, contrats, diagnostics.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Projets](#projets)
3. [Entretien & Maintenance](#entretien--maintenance)
4. [Jardin](#jardin)
5. [Énergie](#énergie)
6. [Artisans](#artisans)
7. [Stocks & Cellier](#stocks--cellier)
8. [Contrats & Garanties](#contrats--garanties)
9. [Diagnostics](#diagnostics)
10. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Maison** centralise tout ce qui concerne la gestion physique et administrative du foyer.

**URL** : `/maison`  
**Service backend** : `src/services/maison/`  
**Route API** : `src/api/routes/maison.py` (`/api/v1/maison`)

---

## Projets

### Fonctionnalités

- Créer et suivre des projets de travaux (rénovation, aménagement)
- Suivre l'avancement (statuts : `planifié`, `en_cours`, `terminé`, `annulé`)
- Calculer la ROI des investissements
- Suggestions IA pour planifier les travaux (priorité, budget, timing)
- Visualiser l'impact sur la valeur du bien

### Usage

```
/maison/projets
```

### Champs clés

| Champ           | Type     | Description                        |
|----------------|----------|------------------------------------|
| `nom`           | string   | Nom du projet                      |
| `statut`        | enum     | `planifié` / `en_cours` / `terminé` |
| `budget_estime` | decimal  | Budget prévisionnel                |
| `budget_reel`   | decimal  | Coût réel                          |
| `date_debut`    | date     | Date de démarrage                  |
| `date_fin`      | date     | Date de fin prévue/réelle          |
| `priorite`      | 1-5      | Niveau de priorité                 |

### Services

```python
from src.services.maison.projets_service import ProjetsMaisonService

service = ProjetsMaisonService()
# Lister projets en cours
projets = service.lister_projets(statut="en_cours")
# Suggestions IA
suggestions = service.suggerer_projets_ia(budget=5000)
```

---

## Entretien & Maintenance

### Fonctionnalités

- Calendrier des tâches d'entretien récurrentes (chaudière, VMC, gouttières…)
- Alertes pour les tâches en retard ou à venir
- Historique des interventions
- Catalogue de tâches préremplies avec fréquences recommandées

### Usage

```
/maison/entretien
```

### Catalogue des tâches types

Le fichier `data/entretien_catalogue.json` contient 50+ tâches d'entretien classiques avec fréquences suggérées.

```python
from src.services.maison.entretien_service import EntretienService
service = EntretienService()
taches_urgentes = service.get_taches_urgentes(horizon_jours=30)
```

---

## Jardin

### Fonctionnalités

- Catalogue de plantes avec fiches détaillées (arrosage, ensoleillement, saison)
- Planning d'arrosage dynamique (ajusté par météo en temps réel)
- Journal des semis et récoltes
- Conseils IA saisonniers basés sur la météo locale
- Gestion des espaces (potager, massifs, pelouse)

### Usage

```
/maison/jardin
```

### Intégrations

- **Météo** : `src/services/integrations/weather/` — ajustement automatique des arrosages
- **Catalogue plantes** : `data/plantes_catalogue.json` — 200+ espèces documentées

### Services

```python
from src.services.maison.jardin_service import JardinService
service = JardinService()
# Planning arrosage de la semaine
planning = service.get_planning_arrosage_semaine()
# Conseils IA jardin
conseils = service.obtenir_conseils_ia(saison="printemps")
```

---

## Énergie

### Fonctionnalités

- Saisie et suivi des index de consommation (électricité, gaz, eau)
- Graphiques de consommation mensuelle/annuelle
- Comparaison avec les périodes précédentes
- Eco-tips personnalisés pour réduire la consommation

### Usage

```
/maison/energie`  
`/maison/eco-tips
```

### Modèle de données

```python
# src/core/models/habitat.py
class ReleveEnergie(Base):
    type_energie: str       # "electricite" | "gaz" | "eau"
    index_valeur: float     # Valeur du compteur
    date_releve: date
    consommation: float     # (index actuel - index précédent)
```

---

## Artisans

### Fonctionnalités

- Carnet d'adresses des artisans (plombier, électricien, maçon…)
- Notes et évaluations après intervention
- Historique des interventions par artisan
- Devis et factures associés

### Usage

```
/maison/artisans
```

---

## Stocks & Cellier

### Fonctionnalités

- Inventaire des consommables maison (produits d'entretien, ampoules, filtres…)
- Gestion des quantités et seuils d'alerte
- Historique des achats
- Intégration avec les listes de courses

### Usage

```
/maison/stocks  
/maison/cellier
```

---

## Contrats & Garanties

### Fonctionnalités

- Archivage des contrats (assurance, énergie, internet, abonnements)
- Dates d'échéance avec alertes de renouvellement J-30
- Garanties équipements avec dates d'expiration
- Export PDF des récapitulatifs

### Usage

```
/maison/contrats  
/maison/garanties
```

---

## Diagnostics

### Fonctionnalités

- Suivi des diagnostics immobiliers (DPE, amiante, plomb, électricité…)
- Dates de validité et alertes d'expiration
- Documents associés

### Usage

```
/maison/diagnostics
```

---

## API Reference

### Endpoints principaux

| Méthode | URL                             | Description                    |
|--------|---------------------------------|--------------------------------|
| GET    | `/api/v1/maison/projets`        | Lister les projets             |
| POST   | `/api/v1/maison/projets`        | Créer un projet                |
| PUT    | `/api/v1/maison/projets/{id}`   | Modifier un projet             |
| GET    | `/api/v1/maison/entretien`      | Tâches d'entretien             |
| POST   | `/api/v1/maison/entretien`      | Ajouter une tâche              |
| GET    | `/api/v1/maison/jardin/plantes` | Liste des plantes du jardin    |
| GET    | `/api/v1/maison/energie`        | Relevés d'énergie              |
| POST   | `/api/v1/maison/energie`        | Nouveau relevé                 |
| GET    | `/api/v1/maison/artisans`       | Liste des artisans             |
| GET    | `/api/v1/maison/contrats`       | Contrats en cours              |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète.
