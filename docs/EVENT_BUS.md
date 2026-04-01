# Event Bus

Reference du bus d'evenements domaine.

## Vue d'ensemble

- Implementation: `src/services/core/events/bus.py`
- Types d'evenements metier: 32 (`REGISTRE_EVENEMENTS`)
- Souscriptions enregistrees au bootstrap: 51 (`enregistrer_subscribers`)
- Enregistrement: `src/services/core/events/subscribers.py`

## Types d'evenements (REGISTRE_EVENEMENTS)

- Recettes: `recette.planifiee`, `recette.importee`, `recette.creee`, `recette.feedback`
- Stock/courses: `stock.modifie`, `courses.generees`, `courses.modifiees`, `inventaire.modification_importante`
- Planning/batch: `planning.modifie`, `batch_cooking.termine`
- Maison: `entretien.routine_creee`, `entretien.semaine_optimisee`, `depenses.modifiee`, `jardin.modifie`, `jardin.recolte`, `projets.modifie`, `meubles.modifie`, `eco_tips.modifie`, `energie.anomalie`, `contrat.renouvellement`
- Famille: `activites.modifiee`, `routines.modifiee`, `weekend.modifie`, `achats.modifie`, `food_log.ajoute`
- Budget/sante: `budget.modifie`, `budget.depassement`, `sante.modifie`
- Jeux: `loto.modifie`, `paris.modifie`, `jeux.sync_terminee`
- Systeme: `service.error`

## Groupes de subscribers

- Invalidation cache: recettes, stock, courses, planning, budget, jeux, etc.
- Reactions metier: checklist anniversaire, suggestions activites, sync inter-modules.
- Monitoring: metriques globales + erreurs services.
- Audit: journalisation structuree de tous les evenements.
- Webhooks sortants: livraison best-effort via service d'integration.

## Exemples de flux

- `jardin.recolte` -> invalidation cache recettes/planning/suggestions.
- `energie.anomalie` -> creation tache entretien.
- `budget.depassement` -> invalidation dashboard + declenchement agent proactif.
- `document.echeance_proche` -> notification ntfy.

## Demarrage

Les subscribers sont enregistres au bootstrap via `enregistrer_subscribers()`.
La fonction est idempotente.

## Bonnes pratiques

- Emettre des evenements metier explicites (`module.action`).
- Garder les handlers resilients (never fail the bus).
- Utiliser des wildcard patterns (`budget.*`) pour les comportements transverses.
- Mettre les actions lourdes en asynchrone ou en job planifie si necessaire.
