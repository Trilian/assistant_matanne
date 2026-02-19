"""
Routes API pour l'inventaire.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas import InventaireItemCreate, InventaireItemResponse, MessageResponse
from src.api.utils import executer_avec_session

router = APIRouter(prefix="/api/v1/inventaire", tags=["Inventaire"])


@router.get("")
async def list_inventaire(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    categorie: str | None = None,
    emplacement: str | None = None,
    stock_bas: bool = False,
    peremption_proche: bool = False,
) -> dict[str, Any]:
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
async def create_inventaire_item(
    item: InventaireItemCreate, user: dict[str, Any] = Depends(require_auth)
):
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
    item_id: int, item: InventaireItemCreate, user: dict[str, Any] = Depends(require_auth)
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
async def delete_inventaire_item(item_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Supprime un article d'inventaire."""
    from src.core.models import ArticleInventaire

    with executer_avec_session() as session:
        db_item = session.query(ArticleInventaire).filter(ArticleInventaire.id == item_id).first()

        if not db_item:
            raise HTTPException(status_code=404, detail="Article non trouvé")

        session.delete(db_item)
        session.commit()

        return MessageResponse(message="Article supprimé", id=item_id)
