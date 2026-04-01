# Interactions Inter-Modules

> Cartographie compl?te des 21+ bridges en production, m?canismes de couplage et guide de cr?ation.
>
> **Derni?re mise ? jour** : 1er avril 2026

---

## M?canismes utilis?s

Les interactions cross-module reposent sur :

| M?canisme | Localisation | Usage |
| ----------- | ------------- | ------- |
| **Services inter-module** | `src/services/{module}/inter_module_*.py` | Logique m?tier cross-module |
| **Bus d'?v?nements** | `src/services/core/events/` | D?couplage pub/sub r?actif |
| **Jobs planifi?s** | `src/services/core/cron/jobs.py` | Synchronisations p?riodiques |
| **Agr?gations dashboard** | `src/services/dashboard/` | Donn?es consolid?es multi-modules |
| **Dispatcher notifications** | `src/services/core/notifications/` | Notifications cross-module |

---

## Bridges en production (21+)

### Cuisine (7 bridges)

| Bridge | Source ? Destination | M?thodes cl?s |
| -------- | --------------------- | --------------- |
| `inter_module_inventaire_planning.py` | Inventaire ? Planning recettes | `suggerer_recettes_selon_stock()`, `exclure_articles_surplus()`, `blocker_batch_jours()`, `analyser_equilibre_nutritionnel()`, `filtrer_recettes_mal_notees()` |
| `inter_module_jules_nutrition.py` | Croissance Jules ? Portions planning | `adapter_planning_nutrition_selon_croissance()`, `adapter_portions_recettes_planifiees()` |
| `inter_module_saison_menu.py` | Saisonnalit? ? Planning IA | `obtenir_contexte_saisonnier_planning()` |
| `inter_module_courses_budget.py` | Total courses ? Budget alimentation | `synchroniser_total_courses_vers_budget()`, `estimer_budget_courses_mensuel()` |
| `inter_module_batch_inventaire.py` | Batch cooking termin? ? D?duction stock | `deduire_ingredients_session_terminee()` |
| `inter_module_peremption_recettes.py` | P?remption ? Suggestions anti-gaspillage | D?clenche suggestions IA pour produits expirants |
| `inter_module_jardin_recettes.py` | R?colte jardin ? Recettes semaine suivante | `suggerer_recettes_depuis_recolte()` |

### Famille (6 bridges)

| Bridge | Source ? Destination | M?thodes cl?s |
| -------- | --------------------- | --------------- |
| `inter_module_meteo_activites.py` | M?t?o ? Activit?s famille | `suggerer_activites_selon_meteo()` (pluie = int?rieur, soleil = ext?rieur) |
| `inter_module_weekend_courses.py` | Activit?s weekend ? Courses | `suggerer_fournitures_weekend()` (mat?riel rando, pique-nique) |
| `inter_module_documents_calendrier.py` | Documents expirants ? Calendrier | `synchroniser_documents_vers_calendrier()` (rappel J-14) |
| `inter_module_budget_anomalie.py` | Anomalie budget ? Notifications | `detecter_et_notifier_anomalies()` (seuil: +30% vs mois pr?c?dent) |
| `inter_module_anniversaires_budget.py` | Anniversaire J-14 ? Budget pr?visionnel | `reserver_budget_previsionnel_j14()` |
| `inter_module_voyages_budget.py` | Voyages ? Budget sync | Sync d?penses voyage vers budget |

### Maison (3 bridges)

| Bridge | Source ? Destination | M?thodes cl?s |
| -------- | --------------------- | --------------- |
| `inter_module_entretien_courses.py` | T?ches entretien ? Courses | `suggerer_produits_entretien_pour_courses()` (produits m?nagers) |
| `inter_module_charges_energie.py` | Anomalie charges ? Analyse ?nergie | `detecter_hausse_et_declencher_analyse()` (seuil: +20% vs mois pr?c?dent) |
| `inter_module_jardin_entretien.py` | Saison jardin ? Entretien auto | `generer_taches_saisonnieres_depuis_plantes()` |

### Cross-module (2 bridges)

| Bridge | Source ? Destination | M?thodes cl?s |
| -------- | --------------------- | --------------- |
| `inter_module_chat_contexte.py` | Multi-module ? Chat IA | `collecter_contexte_complet()` (frigo, planning, courses, budget, anniversaires, documents, t?ches) |
| `inter_module_diagnostics_ia.py` | Photo ? Diagnostic IA ? Artisans | `diagnostiquer_panne_photo()`, `creer_projet_maison_depuis_diagnostic()` |

### Interactions via jobs CRON

| Job | Source ? Destination |
| ----- | --------------------- |
| `sync_recoltes_inventaire` | R?coltes jardin ? Inventaire cuisine |
| `sync_jeux_budget` | Gains/pertes jeux ? Budget famille |
| `sync_entretien_budget` | Co?ts entretien ? D?penses |
| `sync_charges_dashboard` | Charges fixes ? M?triques dashboard |
| `suggestions_activites_meteo` | M?t?o ? Activit?s |
| `sync_routines_planning` | Routines ? Planning quotidien |

### Interactions via event bus

| ?v?nement | R?action |
| ----------- | ---------- |
| `jardin.recolte` | Invalidation cache recettes/planning/suggestions |
| `energie.anomalie` | Cr?ation t?che entretien |
| `budget.depassement` | Invalidation dashboard + agent proactif |
| `document.echeance_proche` | Notification ntfy/push |
| `batch_cooking.termine` | D?duction stock + notification |
| `stock.modifie` | Invalidation cache courses |

---

## Observabilit? des bridges

### Endpoint admin de statut

```http
GET /api/v1/admin/bridges/phase5/status?inclure_smoke=true
```

Retourne par bridge : `id`, `bridge`, `intitul?`, `v?rification`, `statut`, `latence_ms`, `d?tails`.

### Event bus inspection

```http
GET /api/v1/admin/events?limite=30&type_evenement=recette.*
```

### Trigger manuel (test)

```http
POST /api/v1/admin/events/trigger
{
  "type_evenement": "jardin.recolte",
  "source": "admin",
  "payload": {"element_id": 5, "nom": "tomates", "quantite": 10}
}
```

---

## Guide de cr?ation d'un nouveau bridge

### Pattern 1 : Service inter-module avec ?v?nement

```python
# src/services/{module}/inter_module_{source}_{dest}.py

from src.services.core.registry import service_factory
from src.core.decorators import avec_gestion_erreurs, avec_session_db

class SourceDestInteractionService:
    """Bridge de Source vers Dest."""
    
    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def action_name(self, *, db=None):
        result = self._process()
        
        from src.services.core.events import obtenir_bus
        obtenir_bus().emettre(
            "module.action_complete",
            {"data": result},
            source="source_module"
        )
        return result

@service_factory("source_dest_interaction", tags={"source", "dest"})
def obtenir_service_source_dest():
    return SourceDestInteractionService()
```

### Pattern 2 : Subscriber r?actif via event bus

```python
# Dans src/services/core/events/subscribers.py

def _handler_module_action(event: EvenementDomaine) -> None:
    try:
        from src.services.dest import obtenir_service_dest
        service = obtenir_service_dest()
        service.react_to_source_change(event.data, event.source)
    except Exception as e:
        logger.warning(f"Subscriber failed gracefully: {e}")
```

### Pattern 3 : Invalidation cache sur ?v?nement

```python
def _invalider_cache_module(event: EvenementDomaine) -> None:
    try:
        from src.core.caching import obtenir_cache
        nb = obtenir_cache().invalidate(pattern="module_*")
        logger.debug(f"Cache invalidated: {nb} entries on {event.type}")
    except Exception:
        logger.warning("Cache invalidation failed")
```

### Enregistrement des subscribers

Dans `enregistrer_subscribers()` :

```python
bus = obtenir_bus()
bus.souscrire("module.changed", _invalider_cache_module, priority=10)   # cache
bus.souscrire("module.*", _handler_module_action, priority=5)           # m?tier
bus.souscrire("*", audit_logger, priority=0)                            # audit
```

---

## Recommandations

- Privil?gier le bus d'?v?nements pour les r?actions non bloquantes
- Garder les synchronisations lourdes dans les jobs CRON
- ?viter les appels directs entre services quand un ?v?nement suffit
- Documenter chaque nouveau flux ici lors de son ajout
- Chaque bridge doit ?tre couvert par un smoke test admin
