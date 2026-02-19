"""
Routes API pour les recettes.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas import MessageResponse, RecetteCreate, RecetteResponse
from src.api.utils import construire_reponse_paginee, executer_avec_session

router = APIRouter(prefix="/api/v1/recettes", tags=["Recettes"])


@router.get("")
async def list_recettes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    categorie: str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    """Liste les recettes avec pagination et filtres."""
    from src.core.models import Recette

    with executer_avec_session() as session:
        query = session.query(Recette)

        if categorie:
            query = query.filter(Recette.categorie == categorie)

        if search:
            query = query.filter(Recette.nom.ilike(f"%{search}%"))

        total = query.count()
        items = query.order_by(Recette.nom).offset((page - 1) * page_size).limit(page_size).all()

        return construire_reponse_paginee(items, total, page, page_size, RecetteResponse)


@router.get("/{recette_id}", response_model=RecetteResponse)
async def get_recette(recette_id: int):
    """Récupère une recette par son ID."""
    from src.core.models import Recette

    with executer_avec_session() as session:
        recette = session.query(Recette).filter(Recette.id == recette_id).first()

        if not recette:
            raise HTTPException(status_code=404, detail="Recette non trouvée")

        return RecetteResponse.model_validate(recette)


@router.post("", response_model=RecetteResponse)
async def create_recette(recette: RecetteCreate, user: dict[str, Any] = Depends(require_auth)):
    """Crée une nouvelle recette."""
    from src.core.models import Recette

    with executer_avec_session() as session:
        db_recette = Recette(
            nom=recette.nom,
            description=recette.description,
            temps_preparation=recette.temps_preparation,
            temps_cuisson=recette.temps_cuisson,
            portions=recette.portions,
            difficulte=recette.difficulte,
            categorie=recette.categorie,
        )
        session.add(db_recette)
        session.commit()
        session.refresh(db_recette)

        return RecetteResponse.model_validate(db_recette)


@router.put("/{recette_id}", response_model=RecetteResponse)
async def update_recette(
    recette_id: int, recette: RecetteCreate, user: dict[str, Any] = Depends(require_auth)
):
    """Met à jour une recette."""
    from src.core.models import Recette

    with executer_avec_session() as session:
        db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

        if not db_recette:
            raise HTTPException(status_code=404, detail="Recette non trouvée")

        for key, value in recette.model_dump(exclude_unset=True).items():
            if hasattr(db_recette, key):
                setattr(db_recette, key, value)

        session.commit()
        session.refresh(db_recette)

        return RecetteResponse.model_validate(db_recette)


@router.delete("/{recette_id}", response_model=MessageResponse)
async def delete_recette(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Supprime une recette."""
    from src.core.models import Recette

    with executer_avec_session() as session:
        db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

        if not db_recette:
            raise HTTPException(status_code=404, detail="Recette non trouvée")

        session.delete(db_recette)
        session.commit()

        return MessageResponse(message=f"Recette {recette_id} supprimée", id=recette_id)
