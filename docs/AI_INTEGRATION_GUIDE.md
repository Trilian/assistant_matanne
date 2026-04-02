# Guide Integration IA

## Objectif

Ce guide decrit la creation d un nouveau service IA en respectant le pattern `BaseAIService` deja utilise dans le backend.

## Pattern standard

1. Creer un service dans `src/services/{module}/`
2. Heriter de `BaseAIService`
3. Exposer une factory `@service_factory`
4. Ajouter des tests unitaires avec mock du client IA

## Exemple de service

```python
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

class PlanningAIService(BaseAIService):
    """Optimisation nutritionnelle et variete des menus."""

    def analyser_variete(self, repas: list[dict]) -> dict:
        prompt = f"Analyse la variete de ces repas: {repas}"
        return self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt=(
                "Tu es un nutritionniste familial. "
                "Retourne un JSON strict avec score_variete et recommandations."
            ),
        )

@service_factory("planning_ai", tags={"planning", "ia"})
def get_planning_ai_service() -> PlanningAIService:
    return PlanningAIService()
```

## Bonnes pratiques

- Toujours imposer un format de sortie strict (JSON)
- Definir un `system_prompt` court et cible
- Utiliser les methodes de parsing de `BaseAIService`
- Journaliser uniquement les metadonnees, jamais les secrets

## Test unitaire type

```python
def test_planning_ai_retourne_structure_attendue(mocker):
    service = get_planning_ai_service()
    mocker.patch.object(
        service,
        "call_with_dict_parsing_sync",
        return_value={"score_variete": 8, "recommandations": ["Ajouter legumes verts"]},
    )

    resultat = service.analyser_variete([{"nom": "pates"}])

    assert resultat["score_variete"] == 8
    assert isinstance(resultat["recommandations"], list)
```

## Observabilite minimale

- Nombre d appels IA
- Taux d erreur
- Temps moyen de reponse
- Taux de fallback

## Checklist avant merge

- [ ] Service herite de `BaseAIService`
- [ ] Factory `@service_factory` ajoutee
- [ ] Tests unitaires presents
- [ ] Prompt et schema de sortie documentes
- [ ] Endpoint API (si expose) documente dans API_REFERENCE
