"""
Routes API pour les courses.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas import (
    CourseItemBase,
    CourseListCreate,
    ListeCoursesResponse,
    ListeCoursesResume,
    MessageResponse,
    ReponsePaginee,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


@router.get("", response_model=ReponsePaginee[ListeCoursesResume])
@gerer_exception_api
async def lister_courses(
    page: int = Query(1, ge=1, description="Numéro de page (1-indexé)"),
    page_size: int = Query(20, ge=1, le=100, description="Nombre d'éléments par page"),
    active_only: bool = Query(True, description="Afficher uniquement les listes non archivées"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les listes de courses avec pagination.

    Retourne les listes de courses triées par date de création décroissante.
    Par défaut, seules les listes actives (non archivées) sont affichées.

    Args:
        page: Numéro de page (défaut: 1)
        page_size: Taille de page (défaut: 20, max: 100)
        active_only: Filtrer les listes archivées (défaut: True)

    Returns:
        Réponse paginée avec items, total, page, page_size

    Example:
        ```
        GET /api/v1/courses?active_only=true&page_size=10

        Response:
        {
            "items": [{"id": 1, "nom": "Courses semaine", "items_count": 12, ...}],
            "total": 3,
            "page": 1,
            "page_size": 10
        }
        ```
    """
    from src.core.models import ListeCourses

    def _query():
        with executer_avec_session() as session:
            query = session.query(ListeCourses)

            if active_only:
                query = query.filter(ListeCourses.archivee.is_(False))

            total = query.count()

            items = (
                query.order_by(ListeCourses.cree_le.desc())
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
                        "created_at": liste.cree_le,
                    }
                    for liste in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.post("", response_model=MessageResponse, status_code=201)
@gerer_exception_api
async def creer_liste(data: CourseListCreate, user: dict[str, Any] = Depends(require_auth)):
    """
    Crée une nouvelle liste de courses.

    Nécessite une authentification. La liste est créée vide,
    les articles peuvent être ajoutés ensuite via POST /{id}/items.

    Args:
        data: Données de la liste (nom requis)

    Returns:
        Message de confirmation avec l'ID de la liste créée

    Raises:
        401: Non authentifié
        422: Données invalides (nom vide)

    Example:
        ```
        POST /api/v1/courses
        Authorization: Bearer <token>

        Body: {"nom": "Courses du weekend"}

        Response (201):
        {"message": "Liste créée", "id": 5}
        ```
    """
    from src.core.models import ListeCourses

    def _create():
        with executer_avec_session() as session:
            liste = ListeCourses(nom=data.nom, archivee=False)
            session.add(liste)
            session.commit()
            session.refresh(liste)
            return MessageResponse(message="Liste créée", id=liste.id)

    return await executer_async(_create)


@router.post("/{liste_id}/items", response_model=MessageResponse, status_code=201)
@gerer_exception_api
async def ajouter_article(
    liste_id: int, item: CourseItemBase, user: dict[str, Any] = Depends(require_auth)
):
    """
    Ajoute un article à une liste de courses.

    Crée automatiquement l'ingrédient s'il n'existe pas encore en base.

    Args:
        liste_id: ID de la liste de courses
        item: Données de l'article (nom, quantité, unité, catégorie)

    Returns:
        Message de confirmation avec l'ID de l'article créé

    Raises:
        401: Non authentifié
        404: Liste non trouvée
        422: Données invalides

    Example:
        ```
        POST /api/v1/courses/5/items
        Authorization: Bearer <token>

        Body: {"nom": "Tomates", "quantite": 2.0, "unite": "kg", "categorie": "Fruits et légumes"}

        Response (201):
        {"message": "Article ajouté", "id": 12}
        ```
    """
    from src.core.models import ArticleCourses, Ingredient, ListeCourses

    def _add():
        with executer_avec_session() as session:
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

            return MessageResponse(message="Article ajouté", id=article.id)

    return await executer_async(_add)


@router.get("/{liste_id}", response_model=ListeCoursesResponse)
@gerer_exception_api
async def obtenir_liste(liste_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    Récupère une liste de courses avec ses articles détaillés.

    Args:
        liste_id: ID de la liste de courses

    Returns:
        Détail de la liste avec tous ses articles

    Raises:
        404: Liste non trouvée

    Example:
        ```
        GET /api/v1/courses/5

        Response:
        {
            "id": 5,
            "nom": "Courses semaine",
            "archivee": false,
            "items": [
                {"id": 12, "nom": "Tomates", "quantite": 2.0, "coche": false, "categorie": "Fruits et légumes"}
            ]
        }
        ```
    """
    from src.core.models import ListeCourses

    def _get():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            return {
                "id": liste.id,
                "nom": liste.nom,
                "archivee": liste.archivee,
                "created_at": liste.cree_le,
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

    return await executer_async(_get)


@router.put("/{liste_id}", response_model=MessageResponse)
@gerer_exception_api
async def modifier_liste(
    liste_id: int, data: CourseListCreate, user: dict[str, Any] = Depends(require_auth)
):
    """
    Met à jour le nom d'une liste de courses.

    Args:
        liste_id: ID de la liste à modifier
        data: Nouvelles données (nom)

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Liste non trouvée

    Example:
        ```
        PUT /api/v1/courses/5
        Authorization: Bearer <token>

        Body: {"nom": "Courses marché"}

        Response:
        {"message": "Liste mise à jour", "id": 5}
        ```
    """
    from src.core.models import ListeCourses

    def _update():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            liste.nom = data.nom
            session.commit()
            session.refresh(liste)

            return MessageResponse(message="Liste mise à jour", id=liste.id)

    return await executer_async(_update)


@router.put("/{liste_id}/items/{item_id}", response_model=MessageResponse)
@gerer_exception_api
async def modifier_article(
    liste_id: int, item_id: int, item: CourseItemBase, user: dict[str, Any] = Depends(require_auth)
):
    """
    Met à jour un article d'une liste de courses.

    Permet de modifier la quantité, cocher/décocher l'article, ou changer sa catégorie.

    Args:
        liste_id: ID de la liste contenant l'article
        item_id: ID de l'article à modifier
        item: Nouvelles données de l'article

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Article non trouvé dans cette liste

    Example:
        ```
        PUT /api/v1/courses/5/items/12
        Authorization: Bearer <token>

        Body: {"nom": "Tomates", "quantite": 3.0, "coche": true}

        Response:
        {"message": "Article mis à jour", "id": 12}
        ```
    """
    from src.core.models import ArticleCourses

    def _update():
        with executer_avec_session() as session:
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

            return MessageResponse(message="Article mis à jour", id=item_id)

    return await executer_async(_update)


@router.delete("/{liste_id}", response_model=MessageResponse)
@gerer_exception_api
async def supprimer_liste(liste_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    Supprime une liste de courses et tous ses articles.

    Args:
        liste_id: ID de la liste à supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Liste non trouvée

    Example:
        ```
        DELETE /api/v1/courses/5
        Authorization: Bearer <token>

        Response:
        {"message": "Liste supprimée", "id": 5}
        ```
    """
    from src.core.models import ListeCourses

    def _delete():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            session.delete(liste)
            session.commit()

            return MessageResponse(message="Liste supprimée", id=liste_id)

    return await executer_async(_delete)


@router.delete("/{liste_id}/items/{item_id}", response_model=MessageResponse)
@gerer_exception_api
async def supprimer_article(
    liste_id: int, item_id: int, user: dict[str, Any] = Depends(require_auth)
):
    """
    Supprime un article d'une liste de courses.

    Args:
        liste_id: ID de la liste contenant l'article
        item_id: ID de l'article à supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Article non trouvé dans cette liste

    Example:
        ```
        DELETE /api/v1/courses/5/items/12
        Authorization: Bearer <token>

        Response:
        {"message": "Article supprimé", "id": 12}
        ```
    """
    from src.core.models import ArticleCourses

    def _delete():
        with executer_avec_session() as session:
            article = (
                session.query(ArticleCourses)
                .filter(ArticleCourses.id == item_id, ArticleCourses.liste_id == liste_id)
                .first()
            )

            if not article:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            session.delete(article)
            session.commit()

            return MessageResponse(message="Article supprimé", id=item_id)

    return await executer_async(_delete)
