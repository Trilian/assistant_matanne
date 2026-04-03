# ?? Guide Module Maison

> Ce guide couvre la gestion compl?te de la maison dans MaTanne : projets, entretien, jardin, ?nergie, artisans, stocks, contrats, diagnostics.

## Table des mati?res

1. [Vue d'ensemble](#vue-densemble)
2. [Projets](#projets)
3. [Entretien & Maintenance](#entretien--maintenance)
4. [Jardin](#jardin)
5. [?nergie](#?nergie)
6. [Artisans](#artisans)
7. [Stocks & Cellier](#stocks--cellier)
8. [Abonnements](#abonnements)
9. [Diagnostics](#diagnostics)
10. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Maison** centralise tout ce qui concerne la gestion physique et administrative du foyer.

**URL** : `/maison`
**Service backend** : `src/services/maison/`
**Route API** : `src/api/routes/maison.py` (`/api/v1/maison`)

### Capacit?s r?centes ? conna?tre

- notifications maison et rappels p?riodiques
- rapport maison mensuel planifi?
- gestion avanc?e des contrats, garanties, diagnostics, meubles et relev?s
- vue de contexte maison et catalogue d'entretien enrichi

---

## Projets

### Fonctionnalit?s

- Cr?er et suivre des projets de travaux (r?novation, am?nagement)
- Suivre l'avancement (statuts : `planifi?`, `en_cours`, `termin?`, `annul?`)
- Calculer la ROI des investissements
- Suggestions IA pour planifier les travaux (priorit?, budget, timing)
- Visualiser l'impact sur la valeur du bien
- synth?se maison mensuelle via job d?di?

### Usage

```
/maison/projets
```

### Champs cl?s

| Champ           | Type     | Description                        |
| ---------------- | ---------- | ------------------------------------ |
| `nom`           | string   | Nom du projet                      |
| `statut`        | enum     | `planifi?` / `en_cours` / `termin?` |
| `budget_estime` | decimal  | Budget pr?visionnel                |
| `budget_reel`   | decimal  | Co?t r?el                          |
| `date_debut`    | date     | Date de d?marrage                  |
| `date_fin`      | date     | Date de fin pr?vue/r?elle          |
| `priorite`      | 1-5      | Niveau de priorit?                 |

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

### Fonctionnalit?s

- Calendrier des t?ches d'entretien r?currentes (chaudi?re, VMC, goutti?res?)
- Alertes pour les t?ches en retard ou ? venir
- Historique des interventions
- Catalogue de t?ches pr?remplies avec fr?quences recommand?es
- int?gration avec les jobs d'entretien et de contr?le de garanties

### Usage

```
/maison/entretien
```

### Catalogue des t?ches types

Le fichier `data/reference/entretien_catalogue.json` contient 50+ t?ches d'entretien classiques avec fr?quences sugg?r?es.

```python
from src.services.maison.entretien_service import EntretienService
service = EntretienService()
taches_urgentes = service.get_taches_urgentes(horizon_jours=30)
```

---

## Jardin

### Fonctionnalit?s

- Catalogue de plantes avec fiches d?taill?es (arrosage, ensoleillement, saison)
- Planning d'arrosage dynamique (ajust? par m?t?o en temps r?el)
- Journal des semis et r?coltes
- Conseils IA saisonniers bas?s sur la m?t?o locale
- Gestion des espaces (potager, massifs, pelouse)
- rapport jardin hebdomadaire c?t? cron

### Usage

```
/maison/jardin
```

### Int?grations

- **M?t?o** : `src/services/integrations/weather/` ? ajustement automatique des arrosages
- **Catalogue plantes** : `data/reference/plantes_catalogue.json` ? 200+ esp?ces document?es

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

## ?nergie

### Fonctionnalit?s

- Saisie et suivi des index de consommation (?lectricit?, gaz, eau)
- Graphiques de consommation mensuelle/annuelle
- Comparaison avec les p?riodes pr?c?dentes
- Eco-tips personnalis?s pour r?duire la consommation
- zone encore pr?vue pour les anomalies IA de consommation

### Usage

```
/maison/energie`  
`/maison/eco-tips
```

### Mod?le de donn?es

```python
# src/core/models/habitat.py
class ReleveEnergie(Base):
    type_energie: str       # "electricite" | "gaz" | "eau"
    index_valeur: float     # Valeur du compteur
    date_releve: date
    consommation: float     # (index actuel - index pr?c?dent)
```

---

## Artisans

### Fonctionnalit?s

- Carnet d'adresses des artisans (plombier, ?lectricien, ma?on?)
- Notes et ?valuations apr?s intervention
- Historique des interventions par artisan
- Devis et factures associ?s

### Usage

```
/maison/artisans
```

---

## Stocks & Cellier

### Fonctionnalit?s

- Inventaire des consommables maison (produits d'entretien, ampoules, filtres?)
- Gestion des quantit?s et seuils d'alerte
- Historique des achats
- Int?gration avec les listes de courses

### Usage

```
/maison/stocks  
/maison/cellier
```

---

## Abonnements

### Fonctionnalités

- Comparateur d'abonnements (eau, électricité, gaz, assurances, téléphone, internet)
- Coût total mensuel et annuel
- Date fin engagement avec rappel J-30
- Garanties équipements : badge "Sous garantie ✅ / Hors garantie ❌" sur fiche équipement

### Usage

```
/maison/abonnements
/maison/equipements  (badge garantie sur chaque objet)
```

---

## Diagnostics

### Fonctionnalit?s

- Suivi des diagnostics immobiliers (DPE, amiante, plomb, ?lectricit?)
- Dates de validit? et alertes d'expiration
- Documents associ?s

### Usage

```
/maison/diagnostics
```

---

## API Reference

### Endpoints principaux

| M?thode | URL                             | Description                    |
| -------- | --------------------------------- | -------------------------------- |
| GET    | `/api/v1/maison/projets`        | Lister les projets             |
| POST   | `/api/v1/maison/projets`        | Cr?er un projet                |
| PUT    | `/api/v1/maison/projets/{id}`   | Modifier un projet             |
| GET    | `/api/v1/maison/entretien`      | T?ches d'entretien             |
| POST   | `/api/v1/maison/entretien`      | Ajouter une t?che              |
| GET    | `/api/v1/maison/jardin/plantes` | Liste des plantes du jardin    |
| GET    | `/api/v1/maison/energie`        | Relev?s d'?nergie              |
| POST   | `/api/v1/maison/energie`        | Nouveau relev?                 |
| GET    | `/api/v1/maison/artisans`       | Liste des artisans             |
| GET    | `/api/v1/maison/contrats`       | Contrats en cours              |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation compl?te.
