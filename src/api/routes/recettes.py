"""
Routes API pour les recettes.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from src.api.dependencies import require_auth

router = APIRouter(prefix="/api/v1/recettes", tags=["Recettes"])


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class RecetteBase(BaseModel):
    """Schéma de base pour une recette."""

    nom: str
    description: str | None = None
    temps_preparation: int = Field(15, description="Minutes", ge=0)
    temps_cuisson: int = Field(0, description="Minutes", ge=0)
    portions: int = Field(4, ge=1)
    difficulte: str = "moyen"
    categorie: str | None = None

    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()


class RecetteCreate(RecetteBase):
    """Schéma pour créer une recette."""

    ingredients: list[dict] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RecetteResponse(RecetteBase):
    """Schéma de réponse pour une recette."""

    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════


@router.get("")
async def list_recettes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    categorie: str | None = None,
    search: str | None = None,
):
    """Liste les recettes avec pagination et filtres."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette

        with obtenir_contexte_db() as session:
            query = session.query(Recette)

            if categorie:
                query = query.filter(Recette.categorie == categorie)

            if search:
                query = query.filter(Recette.nom.ilike(f"%{search}%"))

            total = query.count()

            items = (
                query.order_by(Recette.nom).offset((page - 1) * page_size).limit(page_size).all()
            )

            return {
                "items": [RecetteResponse.model_validate(r).model_dump() for r in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{recette_id}", response_model=RecetteResponse)
async def get_recette(recette_id: int):
    """Récupère une recette par son ID."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette

        with obtenir_contexte_db() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            return RecetteResponse.model_validate(recette)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("", response_model=RecetteResponse)
async def create_recette(recette: RecetteCreate, user: dict = Depends(require_auth)):
    """Crée une nouvelle recette."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette

        with obtenir_contexte_db() as session:
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{recette_id}", response_model=RecetteResponse)
async def update_recette(
    recette_id: int, recette: RecetteCreate, user: dict = Depends(require_auth)
):
    """Met à jour une recette."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette

        with obtenir_contexte_db() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            for key, value in recette.model_dump(exclude_unset=True).items():
                if hasattr(db_recette, key):
                    setattr(db_recette, key, value)

            session.commit()
            session.refresh(db_recette)

            return RecetteResponse.model_validate(db_recette)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{recette_id}")
async def delete_recette(recette_id: int, user: dict = Depends(require_auth)):
    """Supprime une recette."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import Recette

        with obtenir_contexte_db() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            session.delete(db_recette)
            session.commit()

            return {"message": f"Recette {recette_id} supprimée"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
