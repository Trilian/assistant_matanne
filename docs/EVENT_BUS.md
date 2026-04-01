# Event Bus

> RÃ©fÃ©rence du bus d'Ã©vÃ©nements domaine â€” 32 types, 51 subscribers, patterns et bonnes pratiques.
>
> **DerniÃ¨re mise Ã  jour** : 1er avril 2026

---

## Vue d'ensemble

| PropriÃ©tÃ© | Valeur |
| ----------- | -------- |
| **ImplÃ©mentation** | `src/services/core/events/bus.py` |
| **Types d'Ã©vÃ©nements** | 32 (`REGISTRE_EVENEMENTS`) |
| **Subscribers enregistrÃ©s** | 51 (`enregistrer_subscribers()`) |
| **Thread-safe** | Oui (`threading.Lock`) |
| **Wildcards** | Oui (`module.*` matche `module.action`) |
| **Historique** | 100 derniers Ã©vÃ©nements en mÃ©moire |
| **MÃ©triques** | Ã‰missions, handlers, erreurs, durÃ©e par type |

---

## Types d'Ã©vÃ©nements (32)

### Recettes
`recette.planifiee`, `recette.importee`, `recette.creee`, `recette.feedback`

### Stock / Courses
`stock.modifie`, `courses.generees`, `courses.modifiees`, `inventaire.modification_importante`

### Planning / Batch
`planning.modifie`, `batch_cooking.termine`

### Maison
`entretien.routine_creee`, `entretien.semaine_optimisee`, `depenses.modifiee`, `jardin.modifie`, `jardin.recolte`, `projets.modifie`, `meubles.modifie`, `eco_tips.modifie`, `energie.anomalie`, `contrat.renouvellement`

### Famille
`activites.modifiee`, `routines.modifiee`, `weekend.modifie`, `achats.modifie`, `food_log.ajoute`

### Budget / SantÃ©
`budget.modifie`, `budget.depassement`, `sante.modifie`

### Jeux
`loto.modifie`, `paris.modifie`, `jeux.sync_terminee`

### SystÃ¨me
`service.error`

---

## Groupes de subscribers (51)

### Invalidation cache (16 subscribers)

| Handler | Ã‰vÃ©nement pattern |
| --------- | ------------------- |
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

### RÃ©actions mÃ©tier (12+ subscribers)

- Checklist anniversaire proche (J-30/14/7/1)
- Invalidation suggestions achats sur changement prÃ©fÃ©rences
- Syncs inter-modules enregistrÃ©s via `@service_factory`

### Notifications (7+ subscribers)

- Document expiration â†’ ntfy/push
- Anomalie budget â†’ alertes haute prioritÃ©
- PÃ©remption J-48h â†’ suggestions anti-gaspillage
- Batch cooking terminÃ© â†’ notification rÃ©sultat
- Anomalie Ã©nergie â†’ alerte admin

### Monitoring (8+ subscribers)

- Collecteur mÃ©triques global
- Suivi erreurs services
- Compteurs performance
- DÃ©tection anomalies

### Audit (6+ subscribers)

- Logging structurÃ© des Ã©vÃ©nements
- Suivi actions par domaine
- Enregistrement Ã©vÃ©nements sÃ©curitÃ©

### Webhooks sortants

- Livraison best-effort via service d'intÃ©gration

---

## Exemples de flux rÃ©actifs

| Ã‰vÃ©nement | RÃ©action automatique |
| ----------- | --------------------- |
| `jardin.recolte` | Invalidation cache recettes/planning/suggestions |
| `energie.anomalie` | CrÃ©ation tÃ¢che entretien |
| `budget.depassement` | Invalidation dashboard + dÃ©clenchement agent proactif |
| `document.echeance_proche` | Notification ntfy |
| `batch_cooking.termine` | DÃ©duction inventaire + notification |
| `stock.modifie` | Invalidation cache courses + vÃ©rification seuil |

---

## API admin

```http
# Consulter les derniers Ã©vÃ©nements
GET /api/v1/admin/events?limite=30&type_evenement=recette.*

# DÃ©clencher un Ã©vÃ©nement manuellement (test)
POST /api/v1/admin/events/trigger
{
  "type_evenement": "jardin.recolte",
  "source": "admin",
  "payload": {"element_id": 5, "nom": "tomates"}
}
```

---

## DÃ©marrage

Les subscribers sont enregistrÃ©s au bootstrap via `enregistrer_subscribers()`.
La fonction est idempotente.

---

## Bonnes pratiques

- Ã‰mettre des Ã©vÃ©nements mÃ©tier explicites (`module.action`)
- Garder les handlers rÃ©silients (never fail the bus â€” tout wrappÃ© en `try/except`)
- Utiliser des wildcard patterns (`budget.*`) pour les comportements transverses
- Mettre les actions lourdes en asynchrone ou en job planifiÃ©
- PrioritÃ©s : cache invalidation (10) > mÃ©tier (5) > audit (0)
