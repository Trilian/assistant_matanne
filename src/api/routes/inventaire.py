"""
Routes API pour l'inventaire.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator

from src.api.dependencies import require_auth
from src.api.schemas import MessageResponse
from src.api.utils import executer_avec_session

router = APIRouter(prefix="/api/v1/inventaire", tags=["Inventaire"])


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class InventaireItemBase(BaseModel):
    """Schéma de base pour un article d'inventaire."""

    nom: str
    quantite: float = 1.0
    unite: str | None = None
    categorie: str | None = None
    date_peremption: datetime | None = None

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
        if v == 0:
            raise ValueError("La quantité doit être supérieure à 0")
        return v


class InventaireItemCreate(InventaireItemBase):
    """Schéma pour créer un article."""

    code_barres: str | None = None
    emplacement: str | None = None


class InventaireItemResponse(InventaireItemBase):
    """Schéma de réponse pour un article."""

    id: int
    code_barres: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════


@router.get("")
async def list_inventaire(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    categorie: str | None = None,
    emplacement: str | None = None,
    stock_bas: bool = False,
    peremption_proche: bool = False,
):
    """Liste les articles d'inventaire avec filtres."""
    from datetime import timedelta

    from src.core.models import ArticleInventaire

    with executer_avec_session() as session:
        query = session.query(ArticleInventaire)

        if categorie:
            # categorie via relation ingredient
            from src.core.models import Ingredient

            query = query.join(Ingredient).filter(Ingredient.categorie == categorie)

        if emplacement:
            query = query.filter(ArticleInventaire.emplacement == emplacement)

        if stock_bas:
            query = query.filter(ArticleInventaire.quantite <= ArticleInventaire.quantite_min)

        if peremption_proche:
            seuil = datetime.now() + timedelta(days=7)
            query = query.filter(ArticleInventaire.date_peremption <= seuil)

        total = query.count()

        items = (
            query.order_by(ArticleInventaire.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [
                {
                    "id": i.id,
                    "nom": i.ingredient.nom if i.ingredient else f"Article #{i.id}",
                    "quantite": i.quantite,
                    "unite": i.ingredient.unite if i.ingredient else None,
                    "categorie": i.ingredient.categorie if i.ingredient else None,
                    "date_peremption": i.date_peremption,
                    "code_barres": i.code_barres,
                    "created_at": i.derniere_maj,
                }
                for i in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        }


@router.post("", response_model=InventaireItemResponse)
async def create_inventaire_item(item: InventaireItemCreate, user: dict = Depends(require_auth)):
    """Crée un nouvel article d'inventaire."""
    from src.core.models import ArticleInventaire

    with executer_avec_session() as session:
        db_item = ArticleInventaire(
            nom=item.nom,
            quantite=item.quantite,
            unite=item.unite,
            categorie=item.categorie,
            date_peremption=item.date_peremption,
            code_barres=item.code_barres,
            emplacement=item.emplacement,
        )
        session.add(db_item)
        session.commit()
        session.refresh(db_item)

        return InventaireItemResponse.model_validate(db_item)


@router.get("/barcode/{code}")
async def get_by_barcode(code: str):
    """Récupère un article par son code-barres."""
    from src.core.models import ArticleInventaire

    with executer_avec_session() as session:
        item = (
            session.query(ArticleInventaire).filter(ArticleInventaire.code_barres == code).first()
        )

        if not item:
            raise HTTPException(status_code=404, detail="Article non trouvé")

        return InventaireItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=InventaireItemResponse)
async def get_inventaire_item(item_id: int):
    """Récupère un article par son ID."""
    from src.core.models import ArticleInventaire

    with executer_avec_session() as session:
        item = session.query(ArticleInventaire).filter(ArticleInventaire.id == item_id).first()

        if not item:
            raise HTTPException(status_code=404, detail="Article non trouvé")

        return InventaireItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=InventaireItemResponse)
async def update_inventaire_item(
    item_id: int, item: InventaireItemCreate, user: dict = Depends(require_auth)
):
    """Met à jour un article d'inventaire."""
    from src.core.models import ArticleInventaire

    with executer_avec_session() as session:
        db_item = session.query(ArticleInventaire).filter(ArticleInventaire.id == item_id).first()

        if not db_item:
            raise HTTPException(status_code=404, detail="Article non trouvé")

        db_item.quantite = item.quantite
        if item.date_peremption:
            db_item.date_peremption = item.date_peremption
        if item.code_barres:
            db_item.code_barres = item.code_barres
        if item.emplacement:
            db_item.emplacement = item.emplacement

        session.commit()
        session.refresh(db_item)

        return InventaireItemResponse.model_validate(db_item)


@router.delete("/{item_id}", response_model=MessageResponse)
async def delete_inventaire_item(item_id: int, user: dict = Depends(require_auth)):
    """Supprime un article d'inventaire."""
    from src.core.models import ArticleInventaire

    with executer_avec_session() as session:
        db_item = session.query(ArticleInventaire).filter(ArticleInventaire.id == item_id).first()

        if not db_item:
            raise HTTPException(status_code=404, detail="Article non trouvé")

        session.delete(db_item)
        session.commit()

        return MessageResponse(message="Article supprimé", id=item_id)
