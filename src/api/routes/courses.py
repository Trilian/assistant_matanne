"""
Routes API pour les courses.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

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
        from src.core.database import get_db_context
        from src.core.models import ListeCourses
        
        with get_db_context() as session:
            query = session.query(ListeCourses)
            
            if active_only:
                query = query.filter(ListeCourses.archivee == False)
            
            total = query.count()
            
            items = (
                query
                .order_by(ListeCourses.created_at.desc())
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_liste(data: CourseListCreate):
    """Crée une nouvelle liste de courses."""
    try:
        from src.core.database import get_db_context
        from src.core.models import ListeCourses
        
        with get_db_context() as session:
            liste = ListeCourses(nom=data.nom, archivee=False)
            session.add(liste)
            session.commit()
            session.refresh(liste)
            
            return {"id": liste.id, "nom": liste.nom, "message": "Liste créée"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{liste_id}/items")
async def add_item(liste_id: int, item: CourseItemBase):
    """Ajoute un article à une liste."""
    try:
        from src.core.database import get_db_context
        from src.core.models import ListeCourses, ArticleCourses, Ingredient
        
        with get_db_context() as session:
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
        raise HTTPException(status_code=500, detail=str(e))
