"""
Routes API pour l'inventaire.

Gestion du stock alimentaire : suivi des quantités, dates de péremption,
alertes de stock bas et recherche par code-barres.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas import (
    InventaireItemCreate,
    InventaireItemResponse,
    InventaireItemUpdate,
    MessageResponse,
    ReponsePaginee,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/inventaire", tags=["Inventaire"])


@router.get("", response_model=ReponsePaginee[InventaireItemResponse])
@gerer_exception_api
async def lister_inventaire(
    page: int = Query(1, ge=1, description="Numéro de page (1-indexé)"),
    page_size: int = Query(50, ge=1, le=200, description="Nombre d'éléments par page (max 200)"),
    categorie: str | None = Query(None, description="Filtrer par catégorie d'ingrédient"),
    emplacement: str | None = Query(
        None, description="Filtrer par emplacement (frigo, placard...)"
    ),
    stock_bas: bool = Query(False, description="Afficher uniquement les articles en stock bas"),
    peremption_proche: bool = Query(
        False, description="Afficher uniquement les articles expirant sous 7 jours"
    ),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les articles d'inventaire avec pagination et filtres avancés.

    Permet de surveiller le stock alimentaire avec des filtres combinables
    pour identifier rapidement les articles à racheter ou à consommer.

    Args:
        page: Numéro de page (défaut: 1)
        page_size: Taille de page (défaut: 50, max: 200)
        categorie: Filtre par catégorie d'ingrédient (ex: "produits laitiers")
        emplacement: Filtre par lieu de stockage (frigo, placard, congélateur)
        stock_bas: Si True, ne montre que les articles sous le seuil minimum
        peremption_proche: Si True, ne montre que les articles expirant sous 7 jours

    Returns:
        Réponse paginée avec items, total, page, page_size, pages

    Example:
        ```
        GET /api/v1/inventaire?stock_bas=true&page_size=10

        Response:
        {
            "items": [{"id": 1, "nom": "Lait", "quantite": 0.5, "unite": "L", ...}],
            "total": 3,
            "page": 1,
            "page_size": 10,
            "pages": 1
        }
        ```
    """
    from datetime import timedelta

    from sqlalchemy.orm import joinedload

    from src.core.models import ArticleInventaire, Ingredient

    def _query():
        with executer_avec_session() as session:
            query = session.query(ArticleInventaire).options(
                joinedload(ArticleInventaire.ingredient)
            )

            if categorie:
                query = query.join(Ingredient).filter(Ingredient.categorie == categorie)

            if emplacement:
                query = query.filter(ArticleInventaire.emplacement == emplacement)

            if stock_bas:
                query = query.filter(ArticleInventaire.quantite <= ArticleInventaire.quantite_min)

            if peremption_proche:
                seuil = datetime.now(UTC) + timedelta(days=7)
                query = query.filter(ArticleInventaire.date_peremption <= seuil)

            total = query.count()

            items = (
                query.order_by(ArticleInventaire.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [InventaireItemResponse.model_validate(i) for i in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size,
            }

    return await executer_async(_query)


@router.post("", response_model=InventaireItemResponse)
@gerer_exception_api
async def creer_article_inventaire(
    item: InventaireItemCreate, user: dict[str, Any] = Depends(require_auth)
):
    """
    Crée un nouvel article d'inventaire.

    Nécessite une authentification. L'article est ajouté au stock
    avec la quantité et les métadonnées spécifiées.

    Args:
        item: Données de l'article (nom, quantité, unité, catégorie, etc.)

    Returns:
        L'article créé avec son ID

    Raises:
        401: Non authentifié
        422: Données invalides

    Example:
        ```
        POST /api/v1/inventaire
        Authorization: Bearer <token>

        Body:
        {
            "nom": "Lait demi-écrémé",
            "quantite": 2.0,
            "unite": "L",
            "categorie": "Produits laitiers",
            "emplacement": "frigo",
            "date_peremption": "2026-03-01"
        }
        ```
    """
    from sqlalchemy.orm import joinedload

    from src.core.models import ArticleInventaire, Ingredient

    def _create():
        with executer_avec_session() as session:
            # Vérifier que l'ingrédient existe
            ingredient = (
                session.query(Ingredient).filter(Ingredient.id == item.ingredient_id).first()
            )
            if not ingredient:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ingrédient #{item.ingredient_id} non trouvé",
                )

            db_item = ArticleInventaire(
                ingredient_id=item.ingredient_id,
                quantite=item.quantite,
                quantite_min=item.quantite_min,
                emplacement=item.emplacement,
                date_peremption=item.date_peremption,
                code_barres=item.code_barres,
                prix_unitaire=item.prix_unitaire,
            )
            session.add(db_item)
            session.commit()

            # Recharger avec la relation ingredient pour la réponse
            db_item = (
                session.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
                .filter(ArticleInventaire.id == db_item.id)
                .one()
            )

            return InventaireItemResponse.model_validate(db_item)

    return await executer_async(_create)


@router.get("/barcode/{code}", response_model=InventaireItemResponse)
@gerer_exception_api
async def obtenir_par_code_barres(code: str, user: dict[str, Any] = Depends(require_auth)):
    """
    Récupère un article par son code-barres.

    Utilisé par le scanner de codes-barres pour identifier un article
    dans l'inventaire. Le code peut être un EAN-13 ou tout autre format.

    Args:
        code: Code-barres de l'article (EAN-13, UPC, etc.)

    Returns:
        Détail de l'article correspondant

    Raises:
        404: Aucun article avec ce code-barres

    Example:
        ```
        GET /api/v1/inventaire/barcode/3017620422003

        Response:
        {
            "id": 42,
            "nom": "Nutella 400g",
            "quantite": 1.0,
            "code_barres": "3017620422003"
        }
        ```
    """
    from sqlalchemy.orm import joinedload

    from src.core.models import ArticleInventaire

    def _query():
        with executer_avec_session() as session:
            item = (
                session.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
                .filter(ArticleInventaire.code_barres == code)
                .first()
            )

            if not item:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            return InventaireItemResponse.model_validate(item)

    return await executer_async(_query)


@router.get("/{item_id}", response_model=InventaireItemResponse)
@gerer_exception_api
async def obtenir_article_inventaire(item_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    Récupère un article d'inventaire par son ID.

    Args:
        item_id: Identifiant unique de l'article

    Returns:
        Détail complet de l'article

    Raises:
        404: Article non trouvé

    Example:
        ```
        GET /api/v1/inventaire/42

        Response:
        {
            "id": 42,
            "nom": "Farine T55",
            "quantite": 1.5,
            "unite": "kg",
            "categorie": "Épicerie",
            "emplacement": "placard",
            "date_peremption": "2026-06-15"
        }
        ```
    """
    from sqlalchemy.orm import joinedload

    from src.core.models import ArticleInventaire

    def _query():
        with executer_avec_session() as session:
            item = (
                session.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
                .filter(ArticleInventaire.id == item_id)
                .first()
            )

            if not item:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            return InventaireItemResponse.model_validate(item)

    return await executer_async(_query)


@router.put("/{item_id}", response_model=InventaireItemResponse)
@gerer_exception_api
async def modifier_article_inventaire(
    item_id: int, item: InventaireItemUpdate, user: dict[str, Any] = Depends(require_auth)
):
    """
    Met à jour un article d'inventaire (PATCH partiel).

    Seuls les champs fournis dans le body sont modifiés.
    Permet de modifier tous les champs : ingredient_id, quantité,
    quantité min, emplacement, date de péremption, code-barres, prix.

    Args:
        item_id: ID de l'article à modifier
        item: Champs à mettre à jour (seuls les champs présents sont appliqués)

    Returns:
        L'article mis à jour

    Raises:
        401: Non authentifié
        404: Article non trouvé

    Example:
        ```
        PUT /api/v1/inventaire/42
        Authorization: Bearer <token>

        Body: {"quantite": 0.5, "emplacement": "placard"}

        Response:
        {"id": 42, "ingredient_id": 7, "nom": "Farine T55", "quantite": 0.5, ...}
        ```
    """
    from sqlalchemy.orm import joinedload

    from src.core.models import ArticleInventaire, Ingredient

    def _update():
        with executer_avec_session() as session:
            db_item = (
                session.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
                .filter(ArticleInventaire.id == item_id)
                .first()
            )

            if not db_item:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            # Appliquer uniquement les champs fournis (exclude_unset)
            update_data = item.model_dump(exclude_unset=True)

            # Si ingredient_id est modifié, vérifier qu'il existe
            if "ingredient_id" in update_data:
                ingredient = (
                    session.query(Ingredient)
                    .filter(Ingredient.id == update_data["ingredient_id"])
                    .first()
                )
                if not ingredient:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Ingrédient #{update_data['ingredient_id']} non trouvé",
                    )

            for field, value in update_data.items():
                setattr(db_item, field, value)

            session.commit()

            # Recharger avec la relation ingredient pour la réponse
            db_item = (
                session.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
                .filter(ArticleInventaire.id == db_item.id)
                .one()
            )

            return InventaireItemResponse.model_validate(db_item)

    return await executer_async(_update)


@router.delete("/{item_id}", response_model=MessageResponse)
@gerer_exception_api
async def supprimer_article_inventaire(item_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    Supprime un article d'inventaire.

    Args:
        item_id: ID de l'article à supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Article non trouvé

    Example:
        ```
        DELETE /api/v1/inventaire/42
        Authorization: Bearer <token>

        Response:
        {"message": "Article supprimé", "id": 42}
        ```
    """
    from src.core.models import ArticleInventaire

    def _delete():
        with executer_avec_session() as session:
            db_item = (
                session.query(ArticleInventaire).filter(ArticleInventaire.id == item_id).first()
            )

            if not db_item:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            session.delete(db_item)
            session.commit()

            return MessageResponse(message="Article supprimé", id=item_id)

    return await executer_async(_delete)
