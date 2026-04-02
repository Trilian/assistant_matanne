# Guide Inter-Modules

## Objectif

Ce guide explique comment creer un nouveau bridge inter-module dans Assistant Matanne, du design a la validation test.

## Quand creer un bridge

Creer un bridge quand:
- une information d un module doit piloter une action dans un autre module
- la logique ne doit pas etre dupliquee dans plusieurs services
- le flux doit etre testable de facon isolee

Eviter un bridge quand:
- le besoin peut etre couvert par une simple requete locale
- le couplage cree une dependance forte et fragile

## Pattern recommande

1. Produire un service de pont dans `src/services/inter_modules/`
2. Exposer une factory `get_{nom}_service()` avec `@service_factory`
3. Utiliser des types de retour stables (`dict` serialisable)
4. Ajouter des tests dans `tests/inter_modules/`
5. Si necessaire, publier des evenements via le bus

## Exemple minimal

```python
from src.services.core.registry import service_factory
from src.core.decorators import avec_session_db

class InventaireBudgetBridgeService:
    """Bridge lecture inventaire -> projection budget alimentation."""

    @avec_session_db
    def calculer_projection(self, semaine_iso: str, db=None) -> dict:
        lignes = []  # recuperation et agregation SQLAlchemy
        total = sum(ligne["montant"] for ligne in lignes)
        return {
            "semaine_iso": semaine_iso,
            "total_estime": total,
            "lignes": lignes,
        }

@service_factory("inventaire_budget_bridge", tags={"inter_modules", "cuisine", "famille"})
def get_inventaire_budget_bridge_service() -> InventaireBudgetBridgeService:
    return InventaireBudgetBridgeService()
```

## Publication d evenement (optionnel)

```python
from src.services.core.events import get_event_bus

bus = get_event_bus()
bus.publish(
    "cuisine.inventaire.projection_budget_calculee",
    {"semaine_iso": "2026-W14", "total_estime": 82.4},
)
```

## Contrat de test recommande

- Test unitaire du service bridge
- Test de schema de la reponse (cles obligatoires)
- Test de non-regression sur les valeurs calculees

Exemple:

```python
def test_projection_budget_retourne_schema_valide():
    service = get_inventaire_budget_bridge_service()
    resultat = service.calculer_projection("2026-W14")

    assert "semaine_iso" in resultat
    assert "total_estime" in resultat
    assert isinstance(resultat["lignes"], list)
```

## Checklist avant merge

- [ ] Nom de bridge explicite
- [ ] Factory enregistree
- [ ] Test unitaire present
- [ ] Documentation du flux mise a jour
- [ ] Aucun couplage direct route -> route
