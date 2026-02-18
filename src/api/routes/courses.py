"""
Routes API pour les courses.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from src.api.dependencies import require_auth

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class CourseItemBase(BaseModel):
    """Schéma pour un article de liste de courses."""

    nom: str
    quantite: float = 1.0
    unite: str | None = None
    categorie: str | None = None
    coche: bool = False

    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()

    @field_validator("quantite")
    @classmethod
    def validate_quantite(cls, v: float) -> float:
        if v < 0:
            raise ValueError("La quantité ne peut pas être négative")
        return v


class CourseListCreate(BaseModel):
    """Schéma pour créer une liste de courses."""

    nom: str = Field("Liste de courses", min_length=1)

    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()


class ListeCoursesResponse(BaseModel):
    """Réponse pour une liste de courses."""

    id: int
    nom: str
    items: list[CourseItemBase]
    created_at: datetime | None = None


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════


@router.get("")
async def list_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    active_only: bool = True,
):
    """Liste les listes de courses."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ListeCourses

        with obtenir_contexte_db() as session:
            query = session.query(ListeCourses)

            if active_only:
                query = query.filter(ListeCourses.archivee == False)

            total = query.count()

            items = (
                query.order_by(ListeCourses.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": liste.id,
                        "nom": liste.nom,
                        "items_count": len(liste.articles) if liste.articles else 0,
                        "created_at": liste.created_at,
                    }
                    for liste in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("")
async def create_liste(data: CourseListCreate, user: dict = Depends(require_auth)):
    """Crée une nouvelle liste de courses."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ListeCourses

        with obtenir_contexte_db() as session:
            liste = ListeCourses(nom=data.nom, archivee=False)
            session.add(liste)
            session.commit()
            session.refresh(liste)

            return {"id": liste.id, "nom": liste.nom, "message": "Liste créée"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{liste_id}/items")
async def add_item(liste_id: int, item: CourseItemBase, user: dict = Depends(require_auth)):
    """Ajoute un article à une liste."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleCourses, Ingredient, ListeCourses

        with obtenir_contexte_db() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            # Trouver ou créer l'ingrédient
            ingredient = session.query(Ingredient).filter(Ingredient.nom == item.nom).first()
            if not ingredient:
                ingredient = Ingredient(nom=item.nom, unite=item.unite or "pcs")
                session.add(ingredient)
                session.flush()

            article = ArticleCourses(
                liste_id=liste_id,
                ingredient_id=ingredient.id,
                quantite_necessaire=item.quantite or 1.0,
                priorite="moyenne",
                rayon_magasin=item.categorie,
            )
            session.add(article)
            session.commit()

            return {"message": "Article ajouté", "item_id": article.id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{liste_id}")
async def get_liste(liste_id: int):
    """Récupère une liste de courses avec ses articles."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ListeCourses

        with obtenir_contexte_db() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            return {
                "id": liste.id,
                "nom": liste.nom,
                "archivee": liste.archivee,
                "created_at": liste.created_at,
                "items": [
                    {
                        "id": a.id,
                        "nom": a.ingredient.nom if a.ingredient else "Article",
                        "quantite": a.quantite_necessaire,
                        "coche": a.achete,
                        "categorie": a.rayon_magasin,
                    }
                    for a in (liste.articles or [])
                ],
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{liste_id}")
async def update_liste(liste_id: int, data: CourseListCreate, user: dict = Depends(require_auth)):
    """Met à jour une liste de courses."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ListeCourses

        with obtenir_contexte_db() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            liste.nom = data.nom
            session.commit()
            session.refresh(liste)

            return {"id": liste.id, "nom": liste.nom, "message": "Liste mise à jour"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{liste_id}/items/{item_id}")
async def update_item(
    liste_id: int, item_id: int, item: CourseItemBase, user: dict = Depends(require_auth)
):
    """Met à jour un article d'une liste."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleCourses

        with obtenir_contexte_db() as session:
            article = (
                session.query(ArticleCourses)
                .filter(ArticleCourses.id == item_id, ArticleCourses.liste_id == liste_id)
                .first()
            )

            if not article:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            article.quantite_necessaire = item.quantite or 1.0
            article.achete = item.coche
            if item.categorie:
                article.rayon_magasin = item.categorie
            session.commit()

            return {"message": "Article mis à jour", "id": item_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{liste_id}")
async def delete_liste(liste_id: int, user: dict = Depends(require_auth)):
    """Supprime une liste de courses."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ListeCourses

        with obtenir_contexte_db() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            session.delete(liste)
            session.commit()

            return {"message": "Liste supprimée", "id": liste_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{liste_id}/items/{item_id}")
async def delete_item(liste_id: int, item_id: int, user: dict = Depends(require_auth)):
    """Supprime un article d'une liste."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleCourses

        with obtenir_contexte_db() as session:
            article = (
                session.query(ArticleCourses)
                .filter(ArticleCourses.id == item_id, ArticleCourses.liste_id == liste_id)
                .first()
            )

            if not article:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            session.delete(article)
            session.commit()

            return {"message": "Article supprimé", "id": item_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
