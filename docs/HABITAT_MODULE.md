# Module Habitat ? Documentation

> **Derni?re mise ? jour** : 30 mars 2026 ? Phase 10

## Vue d'ensemble

Le module **Habitat** g?re les fonctionnalit?s li?es ? l'immobilier, la d?coration int?rieure, les plans de maison et les sc?narios de vie (rester/d?m?nager). Il int?gre des services IA pour les plans 2D/3D et les suggestions d?co.

## Architecture

```
src/services/habitat/
+-- service.py           # Service principal HabitatService
+-- plans_ia.py          # G?n?ration plans IA (2D, optimisations)
+-- deco_ia.py           # Suggestions d?coration IA
+-- veille_immo.py       # Veille immobili?re (scraping, alertes)

src/api/routes/
+-- habitat.py           # Routes API habitat

src/core/models/
+-- habitat.py           # Mod?les ORM (BienImmo, ScenarioHabitat, PlanMaison, etc.)

frontend/src/app/(app)/habitat/
+-- page.tsx             # Hub habitat
+-- scenarios/           # Comparaison sc?narios (rester vs partir)
+-- veille-immo/         # Veille immobili?re
+-- marche/              # Donn?es march? immobilier
+-- plans/               # Plans de maison IA
+-- deco/                # Suggestions d?co IA
+-- jardin/              # Jardin (partag? avec maison)
```

## Mod?les de donn?es

| Mod?le | Table | Description |
| -------- | ------- | ------------- |
| `BienImmo` | `biens_immobiliers` | Bien immobilier (localisation, surface, prix) |
| `ScenarioHabitat` | `scenarios_habitat` | Sc?nario de vie (rester, d?m?nager, acheter) |
| `PlanMaison` | `plans_maison` | Plan de maison (pi?ces, dimensions) |
| `TacheEntretien` | `taches_entretien` | T?che d'entretien de la maison |
| `DecoSuggestion` | `suggestions_deco` | Suggestion d?co IA |

## Endpoints API

| M?thode | Route | Description |
| --------- | ------- | ------------- |
| GET | `/api/v1/habitat/biens` | Lister les biens immobiliers |
| POST | `/api/v1/habitat/biens` | Ajouter un bien |
| GET | `/api/v1/habitat/scenarios` | Lister les sc?narios |
| POST | `/api/v1/habitat/scenarios/comparer` | Comparer deux sc?narios |
| POST | `/api/v1/habitat/plans/generer` | G?n?rer un plan IA |
| POST | `/api/v1/habitat/deco/suggestions` | Suggestions d?co IA |
| GET | `/api/v1/habitat/veille` | R?sultats veille immobili?re |

## Veille emploi (Phase 10)

Le module Habitat int?gre d?sormais la **veille emploi** via les innovations Phase 10 :

- **Endpoint** : `POST /api/v1/innovations/veille-emploi`
- **CRON** : `veille_emploi` ? scan quotidien ? 7h00
- **Crit?res configurables** : domaine, mots-cl?s, type contrat, mode travail, rayon g?ographique
- **Alertes** : Push + Email si nouvelles offres d?tect?es

Cette fonctionnalit? impacte directement les sc?narios Habitat (d?cision de rester/partir bas?e sur les opportunit?s professionnelles).

## Configuration

Variables d'environnement optionnelles :

| Variable | Description | D?faut |
| ---------- | ------------- | -------- |
| `VEILLE_IMMO_ENABLED` | Activer la veille immobili?re | `true` |
| `VEILLE_EMPLOI_DOMAINE` | Domaine par d?faut pour la veille emploi | `RH` |

## Relations inter-modules

- **Habitat ? Budget** : Sc?narios int?grent les projections financi?res
- **Habitat ? Maison** : Partage des donn?es d'entretien et ?quipements
- **Habitat ? Veille Emploi** : Impact sur les sc?narios rester/d?m?nager
