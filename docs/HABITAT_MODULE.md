# Module Habitat — Documentation

> **Dernière mise à jour** : 30 mars 2026 — Phase 10

## Vue d'ensemble

Le module **Habitat** gère les fonctionnalités liées à l'immobilier, la décoration intérieure, les plans de maison et les scénarios de vie (rester/déménager). Il intègre des services IA pour les plans 2D/3D et les suggestions déco.

## Architecture

```
src/services/habitat/
├── service.py           # Service principal HabitatService
├── plans_ia.py          # Génération plans IA (2D, optimisations)
├── deco_ia.py           # Suggestions décoration IA
└── veille_immo.py       # Veille immobilière (scraping, alertes)

src/api/routes/
├── habitat.py           # Routes API habitat

src/core/models/
├── habitat.py           # Modèles ORM (BienImmo, ScenarioHabitat, PlanMaison, etc.)

frontend/src/app/(app)/habitat/
├── page.tsx             # Hub habitat
├── scenarios/           # Comparaison scénarios (rester vs partir)
├── veille-immo/         # Veille immobilière
├── marche/              # Données marché immobilier
├── plans/               # Plans de maison IA
├── deco/                # Suggestions déco IA
└── jardin/              # Jardin (partagé avec maison)
```

## Modèles de données

| Modèle | Table | Description |
|--------|-------|-------------|
| `BienImmo` | `biens_immobiliers` | Bien immobilier (localisation, surface, prix) |
| `ScenarioHabitat` | `scenarios_habitat` | Scénario de vie (rester, déménager, acheter) |
| `PlanMaison` | `plans_maison` | Plan de maison (pièces, dimensions) |
| `TacheEntretien` | `taches_entretien` | Tâche d'entretien de la maison |
| `DecoSuggestion` | `suggestions_deco` | Suggestion déco IA |

## Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/habitat/biens` | Lister les biens immobiliers |
| POST | `/api/v1/habitat/biens` | Ajouter un bien |
| GET | `/api/v1/habitat/scenarios` | Lister les scénarios |
| POST | `/api/v1/habitat/scenarios/comparer` | Comparer deux scénarios |
| POST | `/api/v1/habitat/plans/generer` | Générer un plan IA |
| POST | `/api/v1/habitat/deco/suggestions` | Suggestions déco IA |
| GET | `/api/v1/habitat/veille` | Résultats veille immobilière |

## Veille emploi (Phase 10)

Le module Habitat intègre désormais la **veille emploi** via les innovations Phase 10 :

- **Endpoint** : `POST /api/v1/innovations/veille-emploi`
- **CRON** : `veille_emploi` — scan quotidien à 7h00
- **Critères configurables** : domaine, mots-clés, type contrat, mode travail, rayon géographique
- **Alertes** : Push + Email si nouvelles offres détectées

Cette fonctionnalité impacte directement les scénarios Habitat (décision de rester/partir basée sur les opportunités professionnelles).

## Configuration

Variables d'environnement optionnelles :

| Variable | Description | Défaut |
|----------|-------------|--------|
| `VEILLE_IMMO_ENABLED` | Activer la veille immobilière | `true` |
| `VEILLE_EMPLOI_DOMAINE` | Domaine par défaut pour la veille emploi | `RH` |

## Relations inter-modules

- **Habitat → Budget** : Scénarios intègrent les projections financières
- **Habitat → Maison** : Partage des données d'entretien et équipements
- **Habitat → Veille Emploi** : Impact sur les scénarios rester/déménager
