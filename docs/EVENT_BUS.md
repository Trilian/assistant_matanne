# Event Bus

> Reference du bus d'evenements domaine au 1er avril 2026.

---

## Vue d'ensemble

| Propriete | Valeur |
| --- | --- |
| Implementation | `src/services/core/events/bus.py` |
| Types d'evenements | 32 types domaines enregistres |
| Subscribers | 51 handlers enregistres au bootstrap |
| Thread-safe | Oui, verrou interne sur le registre |
| Wildcards | Oui, patterns du type `module.*` |
| Historique | 100 derniers evenements gardes en memoire |
| Metriques | emissions, erreurs, duree, repartition par type |

## Types d'evenements

### Recettes

`recette.planifiee`, `recette.importee`, `recette.creee`, `recette.feedback`

### Stock et courses

`stock.modifie`, `courses.generees`, `courses.modifiees`, `inventaire.modification_importante`

### Planning et batch cooking

`planning.modifie`, `batch_cooking.termine`

### Maison

`entretien.routine_creee`, `entretien.semaine_optimisee`, `depenses.modifiee`, `jardin.modifie`, `jardin.recolte`, `projets.modifie`, `meubles.modifie`, `eco_tips.modifie`, `energie.anomalie`, `contrat.renouvellement`

### Famille

`activites.modifiee`, `routines.modifiee`, `weekend.modifie`, `achats.modifie`, `food_log.ajoute`

### Budget et sante

`budget.modifie`, `budget.depassement`, `sante.modifie`

### Jeux

`loto.modifie`, `paris.modifie`, `jeux.sync_terminee`

### Systeme

`service.error`

## Groupes de subscribers

### Invalidation cache

| Handler | Pattern |
| --- | --- |
| `_invalider_cache_recettes()` | `recette.*` |
| `_invalider_cache_stock()` | `stock.*` |
| `_invalider_cache_courses()` | `courses.*` |
| `_invalider_cache_planning()` | `planning.*` |
| `_invalider_cache_batch_cooking()` | `batch_cooking.*` |
| `_invalider_cache_entretien()` | `entretien.*` |
| `_invalider_cache_activites()` | `activites.*` |
| `_invalider_cache_routines()` | `routines.*` |
| `_invalider_cache_weekend()` | `weekend.*` |
| `_invalider_cache_achats()` | `achats.*` |
| `_invalider_cache_food_log()` | `food_log.*` |
| `_invalider_cache_depenses()` | `depenses.*`, `budget.*` |
| `_invalider_cache_jardin()` | `jardin.*` |
| `_invalider_cache_projets()` | `projets.*` |
| `_invalider_cache_jeux()` | `jeux.*` |
| `_invalider_cache_sante()` | `sante.*` |

### Reactions metier

- anniversaires et echeances proches
- invalidation de suggestions lors de changements de preferences
- synchronisations inter-modules branchees via les services enregistres

### Notifications

- expiration de document vers ntfy et push
- depassement budget en haute priorite
- peremption proche vers anti-gaspillage
- fin de batch cooking avec retour utilisateur
- anomalies energie vers canal admin

### Monitoring et audit

- collecteur central de metriques
- suivi des erreurs service
- comptage des handlers et de la latence
- journalisation des evenements sensibles

### Webhooks sortants

- livraison best-effort vers integrations externes

## Exemples de flux reactifs

| Evenement | Reaction automatique |
| --- | --- |
| `jardin.recolte` | invalide les caches recettes, planning et suggestions |
| `energie.anomalie` | cree une tache entretien ou une alerte admin |
| `budget.depassement` | invalide le dashboard et declenche l'agent proactif |
| `document.echeance_proche` | pousse une notification utilisateur |
| `batch_cooking.termine` | deduit l'inventaire et notifie le resultat |
| `stock.modifie` | invalide les caches courses et verifie les seuils |

## API admin

```http
GET /api/v1/admin/events?limite=30&type_evenement=recette.*

POST /api/v1/admin/events/trigger
{
  "type_evenement": "jardin.recolte",
  "source": "admin",
  "payload": {"element_id": 5, "nom": "tomates"}
}
```

## Demarrage

Les subscribers sont enregistres au bootstrap via `enregistrer_subscribers()`.
L'operation est idempotente et peut etre relancee sans doublonner le registre.

## Bonnes pratiques

- emettre des evenements metier explicites sous la forme `module.action`
- garder les handlers resilients et non bloquants
- utiliser les wildcards pour les besoins transverses
- deplacer les actions lourdes en tache asynchrone ou en job planifie
- conserver les priorites implicites cache > metier > audit
