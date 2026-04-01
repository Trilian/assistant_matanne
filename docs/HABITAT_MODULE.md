# Module Habitat â€” Documentation

> **DerniÃ¨re mise Ã  jour** : 30 mars 2026 â€” Phase 10

## Vue d'ensemble

Le module **Habitat** gÃ¨re les fonctionnalitÃ©s liÃ©es Ã  l'immobilier, la dÃ©coration intÃ©rieure, les plans de maison et les scÃ©narios de vie (rester/dÃ©mÃ©nager). Il intÃ¨gre des services IA pour les plans 2D/3D et les suggestions dÃ©co.

## Architecture

```
src/services/habitat/
â”œâ”€â”€ service.py           # Service principal HabitatService
â”œâ”€â”€ plans_ia.py          # GÃ©nÃ©ration plans IA (2D, optimisations)
â”œâ”€â”€ deco_ia.py           # Suggestions dÃ©coration IA
â””â”€â”€ veille_immo.py       # Veille immobiliÃ¨re (scraping, alertes)

src/api/routes/
â”œâ”€â”€ habitat.py           # Routes API habitat

src/core/models/
â”œâ”€â”€ habitat.py           # ModÃ¨les ORM (BienImmo, ScenarioHabitat, PlanMaison, etc.)

frontend/src/app/(app)/habitat/
â”œâ”€â”€ page.tsx             # Hub habitat
â”œâ”€â”€ scenarios/           # Comparaison scÃ©narios (rester vs partir)
â”œâ”€â”€ veille-immo/         # Veille immobiliÃ¨re
â”œâ”€â”€ marche/              # DonnÃ©es marchÃ© immobilier
â”œâ”€â”€ plans/               # Plans de maison IA
â”œâ”€â”€ deco/                # Suggestions dÃ©co IA
â””â”€â”€ jardin/              # Jardin (partagÃ© avec maison)
```

## ModÃ¨les de donnÃ©es

| ModÃ¨le | Table | Description |
| -------- | ------- | ------------- |
| `BienImmo` | `biens_immobiliers` | Bien immobilier (localisation, surface, prix) |
| `ScenarioHabitat` | `scenarios_habitat` | ScÃ©nario de vie (rester, dÃ©mÃ©nager, acheter) |
| `PlanMaison` | `plans_maison` | Plan de maison (piÃ¨ces, dimensions) |
| `TacheEntretien` | `taches_entretien` | TÃ¢che d'entretien de la maison |
| `DecoSuggestion` | `suggestions_deco` | Suggestion dÃ©co IA |

## Endpoints API

| MÃ©thode | Route | Description |
| --------- | ------- | ------------- |
| GET | `/api/v1/habitat/biens` | Lister les biens immobiliers |
| POST | `/api/v1/habitat/biens` | Ajouter un bien |
| GET | `/api/v1/habitat/scenarios` | Lister les scÃ©narios |
| POST | `/api/v1/habitat/scenarios/comparer` | Comparer deux scÃ©narios |
| POST | `/api/v1/habitat/plans/generer` | GÃ©nÃ©rer un plan IA |
| POST | `/api/v1/habitat/deco/suggestions` | Suggestions dÃ©co IA |
| GET | `/api/v1/habitat/veille` | RÃ©sultats veille immobiliÃ¨re |

## Veille emploi (Phase 10)

Le module Habitat intÃ¨gre dÃ©sormais la **veille emploi** via les innovations Phase 10 :

- **Endpoint** : `POST /api/v1/innovations/veille-emploi`
- **CRON** : `veille_emploi` â€” scan quotidien Ã  7h00
- **CritÃ¨res configurables** : domaine, mots-clÃ©s, type contrat, mode travail, rayon gÃ©ographique
- **Alertes** : Push + Email si nouvelles offres dÃ©tectÃ©es

Cette fonctionnalitÃ© impacte directement les scÃ©narios Habitat (dÃ©cision de rester/partir basÃ©e sur les opportunitÃ©s professionnelles).

## Configuration

Variables d'environnement optionnelles :

| Variable | Description | DÃ©faut |
| ---------- | ------------- | -------- |
| `VEILLE_IMMO_ENABLED` | Activer la veille immobiliÃ¨re | `true` |
| `VEILLE_EMPLOI_DOMAINE` | Domaine par dÃ©faut pour la veille emploi | `RH` |

## Relations inter-modules

- **Habitat â†’ Budget** : ScÃ©narios intÃ¨grent les projections financiÃ¨res
- **Habitat â†’ Maison** : Partage des donnÃ©es d'entretien et Ã©quipements
- **Habitat â†’ Veille Emploi** : Impact sur les scÃ©narios rester/dÃ©mÃ©nager
