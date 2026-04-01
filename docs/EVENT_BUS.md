# Event Bus

> Référence du bus d'événements domaine — 32 types, 51 subscribers, patterns et bonnes pratiques.
>
> **Dernière mise à jour** : 1er avril 2026

---

## Vue d'ensemble

| Propriété | Valeur |
|-----------|--------|
| **Implémentation** | `src/services/core/events/bus.py` |
| **Types d'événements** | 32 (`REGISTRE_EVENEMENTS`) |
| **Subscribers enregistrés** | 51 (`enregistrer_subscribers()`) |
| **Thread-safe** | Oui (`threading.Lock`) |
| **Wildcards** | Oui (`module.*` matche `module.action`) |
| **Historique** | 100 derniers événements en mémoire |
| **Métriques** | Émissions, handlers, erreurs, durée par type |

---

## Types d'événements (32)

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

### Budget / Santé
`budget.modifie`, `budget.depassement`, `sante.modifie`

### Jeux
`loto.modifie`, `paris.modifie`, `jeux.sync_terminee`

### Système
`service.error`

---

## Groupes de subscribers (51)

### Invalidation cache (16 subscribers)

| Handler | Événement pattern |
|---------|-------------------|
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

### Réactions métier (12+ subscribers)

- Checklist anniversaire proche (J-30/14/7/1)
- Invalidation suggestions achats sur changement préférences
- Syncs inter-modules enregistrés via `@service_factory`

### Notifications (7+ subscribers)

- Document expiration → ntfy/push
- Anomalie budget → alertes haute priorité
- Péremption J-48h → suggestions anti-gaspillage
- Batch cooking terminé → notification résultat
- Anomalie énergie → alerte admin

### Monitoring (8+ subscribers)

- Collecteur métriques global
- Suivi erreurs services
- Compteurs performance
- Détection anomalies

### Audit (6+ subscribers)

- Logging structuré des événements
- Suivi actions par domaine
- Enregistrement événements sécurité

### Webhooks sortants

- Livraison best-effort via service d'intégration

---

## Exemples de flux réactifs

| Événement | Réaction automatique |
|-----------|---------------------|
| `jardin.recolte` | Invalidation cache recettes/planning/suggestions |
| `energie.anomalie` | Création tâche entretien |
| `budget.depassement` | Invalidation dashboard + déclenchement agent proactif |
| `document.echeance_proche` | Notification ntfy |
| `batch_cooking.termine` | Déduction inventaire + notification |
| `stock.modifie` | Invalidation cache courses + vérification seuil |

---

## API admin

```http
# Consulter les derniers événements
GET /api/v1/admin/events?limite=30&type_evenement=recette.*

# Déclencher un événement manuellement (test)
POST /api/v1/admin/events/trigger
{
  "type_evenement": "jardin.recolte",
  "source": "admin",
  "payload": {"element_id": 5, "nom": "tomates"}
}
```

---

## Démarrage

Les subscribers sont enregistrés au bootstrap via `enregistrer_subscribers()`.
La fonction est idempotente.

---

## Bonnes pratiques

- Émettre des événements métier explicites (`module.action`)
- Garder les handlers résilients (never fail the bus — tout wrappé en `try/except`)
- Utiliser des wildcard patterns (`budget.*`) pour les comportements transverses
- Mettre les actions lourdes en asynchrone ou en job planifié
- Priorités : cache invalidation (10) > métier (5) > audit (0)
