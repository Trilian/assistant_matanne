"""Routes publiques de partage (sans authentification)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/share", tags=["Partage"])


@router.get("/recette/{token}")
@gerer_exception_api
async def obtenir_recette_partagee(token: str) -> dict:
    """Retourne une recette publique via token temporaire."""
    from src.core.models import Recette
    from src.services.cuisine.partage_recettes import obtenir_recette_partagee as _resolver_token

    recette_id = _resolver_token(token)
    if not recette_id:
        raise HTTPException(status_code=404, detail="Lien de partage invalide ou expiré")

    def _query() -> dict:
        with executer_avec_session() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            ingredients = [
                {
                    "nom": ri.ingredient.nom if ri.ingredient else "",
                    "quantite": ri.quantite,
                    "unite": ri.unite,
                }
                for ri in getattr(recette, "ingredients", [])
            ]
            instructions = [
                e.description
                for e in sorted(getattr(recette, "etapes", []), key=lambda x: x.ordre)
                if getattr(e, "description", None)
            ]

            return {
                "id": recette.id,
                "nom": recette.nom,
                "description": recette.description,
                "temps_preparation": recette.temps_preparation,
                "temps_cuisson": recette.temps_cuisson,
                "portions": recette.portions,
                "difficulte": recette.difficulte,
                "categorie": recette.categorie,
                "ingredients": ingredients,
                "instructions": "\n".join(instructions),
            }

    return await executer_async(_query)
