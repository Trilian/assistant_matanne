# ðŸ¡ Guide Module Maison

> Ce guide couvre la gestion complÃ¨te de la maison dans MaTanne : projets, entretien, jardin, Ã©nergie, artisans, stocks, contrats, diagnostics.

## Table des matiÃ¨res

1. [Vue d'ensemble](#vue-densemble)
2. [Projets](#projets)
3. [Entretien & Maintenance](#entretien--maintenance)
4. [Jardin](#jardin)
5. [Ã‰nergie](#Ã©nergie)
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

### CapacitÃ©s rÃ©centes Ã  connaÃ®tre

- notifications maison et rappels pÃ©riodiques
- rapport maison mensuel planifiÃ©
- gestion avancÃ©e des contrats, garanties, diagnostics, meubles et relevÃ©s
- vue de contexte maison et catalogue d'entretien enrichi

---

## Projets

### FonctionnalitÃ©s

- CrÃ©er et suivre des projets de travaux (rÃ©novation, amÃ©nagement)
- Suivre l'avancement (statuts : `planifiÃ©`, `en_cours`, `terminÃ©`, `annulÃ©`)
- Calculer la ROI des investissements
- Suggestions IA pour planifier les travaux (prioritÃ©, budget, timing)
- Visualiser l'impact sur la valeur du bien
- synthÃ¨se maison mensuelle via job dÃ©diÃ©

### Usage

```
/maison/projets
```

### Champs clÃ©s

| Champ           | Type     | Description                        |
| ---------------- | ---------- | ------------------------------------ |
| `nom`           | string   | Nom du projet                      |
| `statut`        | enum     | `planifiÃ©` / `en_cours` / `terminÃ©` |
| `budget_estime` | decimal  | Budget prÃ©visionnel                |
| `budget_reel`   | decimal  | CoÃ»t rÃ©el                          |
| `date_debut`    | date     | Date de dÃ©marrage                  |
| `date_fin`      | date     | Date de fin prÃ©vue/rÃ©elle          |
| `priorite`      | 1-5      | Niveau de prioritÃ©                 |

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

### FonctionnalitÃ©s

- Calendrier des tÃ¢ches d'entretien rÃ©currentes (chaudiÃ¨re, VMC, gouttiÃ¨resâ€¦)
- Alertes pour les tÃ¢ches en retard ou Ã  venir
- Historique des interventions
- Catalogue de tÃ¢ches prÃ©remplies avec frÃ©quences recommandÃ©es
- intÃ©gration avec les jobs d'entretien et de contrÃ´le de garanties

### Usage

```
/maison/entretien
```

### Catalogue des tÃ¢ches types

Le fichier `data/reference/entretien_catalogue.json` contient 50+ tÃ¢ches d'entretien classiques avec frÃ©quences suggÃ©rÃ©es.

```python
from src.services.maison.entretien_service import EntretienService
service = EntretienService()
taches_urgentes = service.get_taches_urgentes(horizon_jours=30)
```

---

## Jardin

### FonctionnalitÃ©s

- Catalogue de plantes avec fiches dÃ©taillÃ©es (arrosage, ensoleillement, saison)
- Planning d'arrosage dynamique (ajustÃ© par mÃ©tÃ©o en temps rÃ©el)
- Journal des semis et rÃ©coltes
- Conseils IA saisonniers basÃ©s sur la mÃ©tÃ©o locale
- Gestion des espaces (potager, massifs, pelouse)
- rapport jardin hebdomadaire cÃ´tÃ© cron

### Usage

```
/maison/jardin
```

### IntÃ©grations

- **MÃ©tÃ©o** : `src/services/integrations/weather/` â€” ajustement automatique des arrosages
- **Catalogue plantes** : `data/reference/plantes_catalogue.json` â€” 200+ espÃ¨ces documentÃ©es

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

## Ã‰nergie

### FonctionnalitÃ©s

- Saisie et suivi des index de consommation (Ã©lectricitÃ©, gaz, eau)
- Graphiques de consommation mensuelle/annuelle
- Comparaison avec les pÃ©riodes prÃ©cÃ©dentes
- Eco-tips personnalisÃ©s pour rÃ©duire la consommation
- zone encore prÃ©vue pour les anomalies IA de consommation

### Usage

```
/maison/energie`  
`/maison/eco-tips
```

### ModÃ¨le de donnÃ©es

```python
# src/core/models/habitat.py
class ReleveEnergie(Base):
    type_energie: str       # "electricite" | "gaz" | "eau"
    index_valeur: float     # Valeur du compteur
    date_releve: date
    consommation: float     # (index actuel - index prÃ©cÃ©dent)
```

---

## Artisans

### FonctionnalitÃ©s

- Carnet d'adresses des artisans (plombier, Ã©lectricien, maÃ§onâ€¦)
- Notes et Ã©valuations aprÃ¨s intervention
- Historique des interventions par artisan
- Devis et factures associÃ©s

### Usage

```
/maison/artisans
```

---

## Stocks & Cellier

### FonctionnalitÃ©s

- Inventaire des consommables maison (produits d'entretien, ampoules, filtresâ€¦)
- Gestion des quantitÃ©s et seuils d'alerte
- Historique des achats
- IntÃ©gration avec les listes de courses

### Usage

```
/maison/stocks  
/maison/cellier
```

---

## Contrats & Garanties

### FonctionnalitÃ©s

- Archivage des contrats (assurance, Ã©nergie, internet, abonnements)
- Dates d'Ã©chÃ©ance avec alertes de renouvellement J-30
- Garanties Ã©quipements avec dates d'expiration
- Export PDF des rÃ©capitulatifs

### Usage

```
/maison/contrats  
/maison/garanties
```

---

## Diagnostics

### FonctionnalitÃ©s

- Suivi des diagnostics immobiliers (DPE, amiante, plomb, Ã©lectricitÃ©â€¦)
- Dates de validitÃ© et alertes d'expiration
- Documents associÃ©s

### Usage

```
/maison/diagnostics
```

---

## API Reference

### Endpoints principaux

| MÃ©thode | URL                             | Description                    |
| -------- | --------------------------------- | -------------------------------- |
| GET    | `/api/v1/maison/projets`        | Lister les projets             |
| POST   | `/api/v1/maison/projets`        | CrÃ©er un projet                |
| PUT    | `/api/v1/maison/projets/{id}`   | Modifier un projet             |
| GET    | `/api/v1/maison/entretien`      | TÃ¢ches d'entretien             |
| POST   | `/api/v1/maison/entretien`      | Ajouter une tÃ¢che              |
| GET    | `/api/v1/maison/jardin/plantes` | Liste des plantes du jardin    |
| GET    | `/api/v1/maison/energie`        | RelevÃ©s d'Ã©nergie              |
| POST   | `/api/v1/maison/energie`        | Nouveau relevÃ©                 |
| GET    | `/api/v1/maison/artisans`       | Liste des artisans             |
| GET    | `/api/v1/maison/contrats`       | Contrats en cours              |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complÃ¨te.
