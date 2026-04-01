# Interactions Inter-Modules

> Cartographie complète des 21+ bridges en production, mécanismes de couplage et guide de création.
>
> **Dernière mise à jour** : 1er avril 2026

---

## Mécanismes utilisés

Les interactions cross-module reposent sur :

| Mécanisme | Localisation | Usage |
| ----------- | ------------- | ------- |
| **Services inter-module** | `src/services/{module}/inter_module_*.py` | Logique métier cross-module |
| **Bus d'événements** | `src/services/core/events/` | Découplage pub/sub réactif |
| **Jobs planifiés** | `src/services/core/cron/jobs.py` | Synchronisations périodiques |
| **Agrégations dashboard** | `src/services/dashboard/` | Données consolidées multi-modules |
| **Dispatcher notifications** | `src/services/core/notifications/` | Notifications cross-module |

---

## Bridges en production (21+)

### Cuisine (7 bridges)

| Bridge | Source → Destination | Méthodes clés |
| -------- | --------------------- | --------------- |
| `inter_module_inventaire_planning.py` | Inventaire → Planning recettes | `suggerer_recettes_selon_stock()`, `exclure_articles_surplus()`, `blocker_batch_jours()`, `analyser_equilibre_nutritionnel()`, `filtrer_recettes_mal_notees()` |
| `inter_module_jules_nutrition.py` | Croissance Jules → Portions planning | `adapter_planning_nutrition_selon_croissance()`, `adapter_portions_recettes_planifiees()` |
| `inter_module_saison_menu.py` | Saisonnalité → Planning IA | `obtenir_contexte_saisonnier_planning()` |
| `inter_module_courses_budget.py` | Total courses → Budget alimentation | `synchroniser_total_courses_vers_budget()`, `estimer_budget_courses_mensuel()` |
| `inter_module_batch_inventaire.py` | Batch cooking terminé → Déduction stock | `deduire_ingredients_session_terminee()` |
| `inter_module_peremption_recettes.py` | Péremption → Suggestions anti-gaspillage | Déclenche suggestions IA pour produits expirants |
| `inter_module_jardin_recettes.py` | Récolte jardin → Recettes semaine suivante | `suggerer_recettes_depuis_recolte()` |

### Famille (6 bridges)

| Bridge | Source → Destination | Méthodes clés |
| -------- | --------------------- | --------------- |
| `inter_module_meteo_activites.py` | Météo → Activités famille | `suggerer_activites_selon_meteo()` (pluie = intérieur, soleil = extérieur) |
| `inter_module_weekend_courses.py` | Activités weekend → Courses | `suggerer_fournitures_weekend()` (matériel rando, pique-nique) |
| `inter_module_documents_calendrier.py` | Documents expirants → Calendrier | `synchroniser_documents_vers_calendrier()` (rappel J-14) |
| `inter_module_budget_anomalie.py` | Anomalie budget → Notifications | `detecter_et_notifier_anomalies()` (seuil: +30% vs mois précédent) |
| `inter_module_anniversaires_budget.py` | Anniversaire J-14 → Budget prévisionnel | `reserver_budget_previsionnel_j14()` |
| `inter_module_voyages_budget.py` | Voyages → Budget sync | Sync dépenses voyage vers budget |

### Maison (3 bridges)

| Bridge | Source → Destination | Méthodes clés |
| -------- | --------------------- | --------------- |
| `inter_module_entretien_courses.py` | Tâches entretien → Courses | `suggerer_produits_entretien_pour_courses()` (produits ménagers) |
| `inter_module_charges_energie.py` | Anomalie charges → Analyse énergie | `detecter_hausse_et_declencher_analyse()` (seuil: +20% vs mois précédent) |
| `inter_module_jardin_entretien.py` | Saison jardin → Entretien auto | `generer_taches_saisonnieres_depuis_plantes()` |

### Cross-module (2 bridges)

| Bridge | Source → Destination | Méthodes clés |
| -------- | --------------------- | --------------- |
| `inter_module_chat_contexte.py` | Multi-module → Chat IA | `collecter_contexte_complet()` (frigo, planning, courses, budget, anniversaires, documents, tâches) |
| `inter_module_diagnostics_ia.py` | Photo → Diagnostic IA → Artisans | `diagnostiquer_panne_photo()`, `creer_projet_maison_depuis_diagnostic()` |

### Interactions via jobs CRON

| Job | Source → Destination |
| ----- | --------------------- |
| `sync_recoltes_inventaire` | Récoltes jardin → Inventaire cuisine |
| `sync_jeux_budget` | Gains/pertes jeux → Budget famille |
| `sync_entretien_budget` | Coûts entretien → Dépenses |
| `sync_charges_dashboard` | Charges fixes → Métriques dashboard |
| `suggestions_activites_meteo` | Météo → Activités |
| `sync_routines_planning` | Routines → Planning quotidien |

### Interactions via event bus

| Événement | Réaction |
| ----------- | ---------- |
| `jardin.recolte` | Invalidation cache recettes/planning/suggestions |
| `energie.anomalie` | Création tâche entretien |
| `budget.depassement` | Invalidation dashboard + agent proactif |
| `document.echeance_proche` | Notification ntfy/push |
| `batch_cooking.termine` | Déduction stock + notification |
| `stock.modifie` | Invalidation cache courses |

---

## Observabilité des bridges

### Endpoint admin de statut

```http
GET /api/v1/admin/bridges/phase5/status?inclure_smoke=true
```

Retourne par bridge : `id`, `bridge`, `intitulé`, `vérification`, `statut`, `latence_ms`, `détails`.

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

## Guide de création d'un nouveau bridge

### Pattern 1 : Service inter-module avec événement

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

### Pattern 2 : Subscriber réactif via event bus

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

### Pattern 3 : Invalidation cache sur événement

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
bus.souscrire("module.*", _handler_module_action, priority=5)           # métier
bus.souscrire("*", audit_logger, priority=0)                            # audit
```

---

## Recommandations

- Privilégier le bus d'événements pour les réactions non bloquantes
- Garder les synchronisations lourdes dans les jobs CRON
- Éviter les appels directs entre services quand un événement suffit
- Documenter chaque nouveau flux ici lors de son ajout
- Chaque bridge doit être couvert par un smoke test admin
