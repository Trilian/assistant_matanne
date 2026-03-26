"""
Routes API pour les courses.
"""

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile

# ─── Idempotency cache (TTL 5 min, single-instance) ───────────────────────────
_IDEMPOTENCY_CACHE: dict[str, tuple[float, Any]] = {}
_IDEMPOTENCY_TTL = 300  # secondes


def _check_idempotency(key: str | None) -> Any | None:
    """Retourne le résultat mis en cache si la clé a déjà été traitée récemment."""
    if not key:
        return None
    now = time.time()
    expired = [k for k, (ts, _) in _IDEMPOTENCY_CACHE.items() if now - ts > _IDEMPOTENCY_TTL]
    for k in expired:
        del _IDEMPOTENCY_CACHE[k]
    entry = _IDEMPOTENCY_CACHE.get(key)
    return entry[1] if entry else None


def _store_idempotency(key: str | None, result: Any) -> None:
    """Enregistre un résultat pour éviter les doublons d'idempotency."""
    if key:
        _IDEMPOTENCY_CACHE[key] = (time.time(), result)


from src.api.dependencies import require_auth
from src.api.schemas import (
    CourseItemBase,
    CourseListCreate,
    CheckoutCoursesResponse,
    CheckoutCoursesRequest,
    GenererCoursesRequest,
    GenererCoursesResponse,
    ListeCoursesResponse,
    ListeCoursesResume,
    MessageResponse,
    ReponsePaginee,
    ScanBarcodeCheckoutRequest,
    ScanBarcodeCheckoutResponse,
)
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


@router.get("", response_model=ReponsePaginee[ListeCoursesResume], responses=REPONSES_LISTE)
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


@router.post("", response_model=MessageResponse, status_code=201, responses=REPONSES_CRUD_CREATION)
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


@router.post(
    "/{liste_id}/items",
    response_model=MessageResponse,
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
)
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


@router.get("/{liste_id}", response_model=ListeCoursesResponse, responses=REPONSES_CRUD_LECTURE)
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


@router.get("/{liste_id}/export")
@gerer_exception_api
async def exporter_liste_texte(
    liste_id: int,
    group_by: str = Query(
        "categorie",
        pattern="^(categorie|simple)$",
        description="Regroupement du texte exporté",
    ),
    user: dict[str, Any] = Depends(require_auth),
):
    """Exporte une liste de courses en texte brut (optimisé mobile/partage)."""
    from datetime import datetime

    from src.core.models import ListeCourses

    def _export():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            articles = [a for a in (liste.articles or []) if not a.achete]

            lignes = [
                f"LISTE DE COURSES - {liste.nom}",
                f"Generee le {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                "",
            ]

            if group_by == "simple":
                for a in sorted(articles, key=lambda x: (x.ingredient.nom if x.ingredient else "")):
                    nom = a.ingredient.nom if a.ingredient else "Article"
                    unite = (a.ingredient.unite if a.ingredient else "") or ""
                    qty = f"{a.quantite_necessaire:g} {unite}".strip()
                    lignes.append(f"- [ ] {nom} ({qty})")
            else:
                groupes: dict[str, list] = {}
                for a in articles:
                    categorie = a.rayon_magasin or "Autre"
                    groupes.setdefault(categorie, []).append(a)

                for categorie in sorted(groupes.keys()):
                    lignes.append(f"\n[{categorie}]")
                    for a in sorted(
                        groupes[categorie], key=lambda x: (x.ingredient.nom if x.ingredient else "")
                    ):
                        nom = a.ingredient.nom if a.ingredient else "Article"
                        unite = (a.ingredient.unite if a.ingredient else "") or ""
                        qty = f"{a.quantite_necessaire:g} {unite}".strip()
                        lignes.append(f"- [ ] {nom} ({qty})")

            contenu = "\n".join(lignes).strip() + "\n"
            return Response(content=contenu, media_type="text/plain; charset=utf-8")

    return await executer_async(_export)


@router.put("/{liste_id}", response_model=MessageResponse, responses=REPONSES_CRUD_ECRITURE)
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


@router.put(
    "/{liste_id}/items/{item_id}", response_model=MessageResponse, responses=REPONSES_CRUD_ECRITURE
)
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


@router.post(
    "/{liste_id}/checkout-items",
    response_model=CheckoutCoursesResponse,
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def checkout_articles(
    liste_id: int,
    payload: CheckoutCoursesRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    """Checkout batch: marque des articles courses comme achetés et met à jour l'inventaire.

    Transaction unique par requête:
    - coche l'article de courses (achete=True, achete_le)
    - incrémente (ou crée) la ligne inventaire associée à l'ingrédient
    - enregistre l'historique inventaire
    """
    # Idempotency: même clé = même réponse (anti double-scan)
    cached = _check_idempotency(payload.idempotency_key)
    if cached is not None:
        return cached

    from datetime import datetime

    from src.core.models import (
        ArticleCourses,
        ArticleInventaire,
        HistoriqueInventaire,
        ListeCourses,
    )

    def _checkout():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            results: list[dict[str, Any]] = []
            total_maj = 0

            for requested in payload.articles:
                item_id = requested.item_id
                article = (
                    session.query(ArticleCourses)
                    .filter(ArticleCourses.id == item_id, ArticleCourses.liste_id == liste_id)
                    .first()
                )

                if not article:
                    results.append(
                        {
                            "item_id": item_id,
                            "ingredient_nom": "Inconnu",
                            "statut": "non_trouve",
                            "quantite_ajoutee": 0,
                            "inventaire_article_id": None,
                            "coche": False,
                        }
                    )
                    continue

                ingredient_nom = article.ingredient.nom if article.ingredient else "Article"

                if article.achete:
                    results.append(
                        {
                            "item_id": item_id,
                            "ingredient_nom": ingredient_nom,
                            "statut": "deja_achete",
                            "quantite_ajoutee": 0,
                            "inventaire_article_id": None,
                            "coche": True,
                        }
                    )
                    continue

                quantite_checkout = requested.quantite_achetee or article.quantite_necessaire or 1.0

                # 1) Coche l'article courses
                article.achete = True
                article.achete_le = datetime.now()

                # 2) Met à jour l'inventaire
                inv = (
                    session.query(ArticleInventaire)
                    .filter(ArticleInventaire.ingredient_id == article.ingredient_id)
                    .first()
                )

                if inv:
                    quantite_avant = inv.quantite
                    inv.quantite = float(inv.quantite or 0) + float(quantite_checkout)
                    if not inv.emplacement and payload.emplacement_defaut:
                        inv.emplacement = payload.emplacement_defaut

                    session.add(
                        HistoriqueInventaire(
                            article_id=inv.id,
                            ingredient_id=inv.ingredient_id,
                            type_modification="modification",
                            quantite_avant=quantite_avant,
                            quantite_apres=inv.quantite,
                            notes=f"Checkout courses liste {liste_id}",
                        )
                    )
                    inv_id = inv.id
                else:
                    inv = ArticleInventaire(
                        ingredient_id=article.ingredient_id,
                        quantite=float(quantite_checkout),
                        quantite_min=1.0,
                        emplacement=payload.emplacement_defaut,
                    )
                    session.add(inv)
                    session.flush()

                    session.add(
                        HistoriqueInventaire(
                            article_id=inv.id,
                            ingredient_id=inv.ingredient_id,
                            type_modification="ajout",
                            quantite_avant=0,
                            quantite_apres=inv.quantite,
                            notes=f"Checkout courses liste {liste_id}",
                        )
                    )
                    inv_id = inv.id

                total_maj += 1
                results.append(
                    {
                        "item_id": item_id,
                        "ingredient_nom": ingredient_nom,
                        "statut": "traite",
                        "quantite_ajoutee": float(quantite_checkout),
                        "inventaire_article_id": inv_id,
                        "coche": True,
                    }
                )

            session.commit()

            return {
                "liste_id": liste_id,
                "total_demandes": len(payload.articles),
                "total_traites": len([r for r in results if r["statut"] == "traite"]),
                "total_inventaire_maj": total_maj,
                "articles": results,
            }

    result = await executer_async(_checkout)
    _store_idempotency(payload.idempotency_key, result)
    return result


@router.post(
    "/{liste_id}/scan-barcode-checkout",
    response_model=ScanBarcodeCheckoutResponse,
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def scan_barcode_checkout(
    liste_id: int,
    payload: ScanBarcodeCheckoutRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    """Checkout rapide en magasin via code-barres.

    Workflow:
    - résout le code-barres vers un article inventaire (ingredient_id)
    - trouve l'article courses non acheté correspondant dans la liste
    - coche l'article et incrémente l'inventaire
    """
    # Idempotency: même clé = même réponse (anti double-scan)
    cached = _check_idempotency(payload.idempotency_key)
    if cached is not None:
        return cached

    from datetime import datetime

    from src.core.models import (
        ArticleCourses,
        ArticleInventaire,
        HistoriqueInventaire,
        ListeCourses,
    )

    def _scan_checkout():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            inventaire = (
                session.query(ArticleInventaire)
                .filter(ArticleInventaire.code_barres == payload.barcode)
                .first()
            )
            if not inventaire:
                return {
                    "liste_id": liste_id,
                    "barcode": payload.barcode,
                    "item_id": None,
                    "ingredient_nom": None,
                    "statut": "barcode_inconnu",
                    "quantite_ajoutee": 0,
                    "inventaire_article_id": None,
                }

            article_courses = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste_id,
                    ArticleCourses.ingredient_id == inventaire.ingredient_id,
                    ArticleCourses.achete.is_(False),
                )
                .order_by(ArticleCourses.id.asc())
                .first()
            )

            ingredient_nom = inventaire.ingredient.nom if inventaire.ingredient else "Article"

            if not article_courses:
                return {
                    "liste_id": liste_id,
                    "barcode": payload.barcode,
                    "item_id": None,
                    "ingredient_nom": ingredient_nom,
                    "statut": "hors_liste",
                    "quantite_ajoutee": 0,
                    "inventaire_article_id": inventaire.id,
                }

            # Checkout + stock
            article_courses.achete = True
            article_courses.achete_le = datetime.now()

            quantite_avant = inventaire.quantite
            inventaire.quantite = float(inventaire.quantite or 0) + float(payload.quantite_achetee)

            session.add(
                HistoriqueInventaire(
                    article_id=inventaire.id,
                    ingredient_id=inventaire.ingredient_id,
                    type_modification="modification",
                    quantite_avant=quantite_avant,
                    quantite_apres=inventaire.quantite,
                    notes=f"Scan checkout liste {liste_id} ({payload.barcode})",
                )
            )

            session.commit()

            return {
                "liste_id": liste_id,
                "barcode": payload.barcode,
                "item_id": article_courses.id,
                "ingredient_nom": ingredient_nom,
                "statut": "traite",
                "quantite_ajoutee": float(payload.quantite_achetee),
                "inventaire_article_id": inventaire.id,
            }

    result = await executer_async(_scan_checkout)
    _store_idempotency(payload.idempotency_key, result)
    return result


@router.post(
    "/generer-depuis-planning",
    response_model=GenererCoursesResponse,
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def generer_depuis_planning(
    data: GenererCoursesRequest,
    user: dict[str, Any] = Depends(require_auth),
):
    """Génère une liste de courses depuis le planning de la semaine.

    1. Récupère tous les Repas de la semaine avec recette_id
    2. Extrait et agrège les ingrédients via RecetteIngredient
    3. Soustrait le stock existant si demandé
    4. Crée une ListeCourses avec les ArticleCourses
    """
    from datetime import timedelta

    from sqlalchemy import func

    from src.core.models import (
        ArticleCourses,
        ArticleInventaire,
        Ingredient,
        ListeCourses,
        Recette,
        RecetteIngredient,
    )
    from src.core.models.planning import Repas
    from src.services.cuisine.planning.agregation import (
        aggregate_ingredients,
        sort_ingredients_by_rayon,
    )

    semaine_debut = data.semaine_debut
    semaine_fin = semaine_debut + timedelta(days=6)

    def _generate():
        with executer_avec_session() as session:
            # 1) Récupérer tous les repas de la semaine avec une recette liée
            repas_list = (
                session.query(Repas)
                .filter(
                    Repas.date_repas >= semaine_debut,
                    Repas.date_repas <= semaine_fin,
                    Repas.recette_id.isnot(None),
                )
                .all()
            )

            if not repas_list:
                raise HTTPException(
                    status_code=404,
                    detail="Aucun repas avec recette trouvé pour cette semaine",
                )

            # Collecter tous les recette_ids (plat + entrée + desserts)
            recette_ids: set[int] = set()
            for r in repas_list:
                if r.recette_id:
                    recette_ids.add(r.recette_id)
                if r.entree_recette_id:
                    recette_ids.add(r.entree_recette_id)
                if r.dessert_recette_id:
                    recette_ids.add(r.dessert_recette_id)
                if r.dessert_jules_recette_id:
                    recette_ids.add(r.dessert_jules_recette_id)

            # 2) Extraire les ingrédients de toutes les recettes
            rows = (
                session.query(
                    Ingredient.nom,
                    func.sum(RecetteIngredient.quantite).label("total_qty"),
                    RecetteIngredient.unite,
                    Ingredient.categorie,
                )
                .join(RecetteIngredient, RecetteIngredient.ingredient_id == Ingredient.id)
                .filter(RecetteIngredient.recette_id.in_(recette_ids))
                .group_by(Ingredient.nom, RecetteIngredient.unite, Ingredient.categorie)
                .all()
            )

            ingredients_list = [
                {
                    "nom": row.nom,
                    "quantite": float(row.total_qty or 1),
                    "unite": row.unite or "",
                    "rayon": row.categorie or "Autre",
                }
                for row in rows
            ]

            # 3) Agréger les ingrédients identiques
            aggregated = aggregate_ingredients(ingredients_list)
            sorted_ings = sort_ingredients_by_rayon(aggregated)

            # 4) Soustraire le stock
            articles_en_stock = 0
            articles_a_acheter = []

            for ing in sorted_ings:
                nom = ing["nom"]
                besoin = ing["quantite"]
                en_stock = 0.0

                if data.soustraire_stock:
                    inv = (
                        session.query(ArticleInventaire)
                        .join(Ingredient, Ingredient.id == ArticleInventaire.ingredient_id)
                        .filter(func.lower(Ingredient.nom) == func.lower(nom))
                        .first()
                    )
                    if inv and inv.quantite:
                        en_stock = float(inv.quantite)

                if en_stock >= besoin:
                    articles_en_stock += 1
                    continue

                quantite_a_acheter = besoin - en_stock
                articles_a_acheter.append({
                    **ing,
                    "quantite": quantite_a_acheter,
                    "en_stock": en_stock,
                })

            # 5) Créer la ListeCourses + ArticleCourses
            liste = ListeCourses(nom=data.nom_liste, archivee=False)
            session.add(liste)
            session.flush()

            for art in articles_a_acheter:
                ingredient = (
                    session.query(Ingredient)
                    .filter(func.lower(Ingredient.nom) == func.lower(art["nom"]))
                    .first()
                )
                if not ingredient:
                    ingredient = Ingredient(
                        nom=art["nom"],
                        categorie=art.get("rayon", "Autre"),
                        unite=art.get("unite", "pcs") or "pcs",
                    )
                    session.add(ingredient)
                    session.flush()

                session.add(
                    ArticleCourses(
                        liste_id=liste.id,
                        ingredient_id=ingredient.id,
                        quantite_necessaire=art["quantite"],
                        rayon_magasin=art.get("rayon", "Autre"),
                        priorite="moyenne",
                        suggere_par_ia=False,
                    )
                )

            session.commit()

            # Compter par rayon
            par_rayon: dict[str, int] = {}
            for art in articles_a_acheter:
                rayon = art.get("rayon", "Autre")
                par_rayon[rayon] = par_rayon.get(rayon, 0) + 1

            return {
                "liste_id": liste.id,
                "nom": liste.nom,
                "total_articles": len(articles_a_acheter),
                "articles_en_stock": articles_en_stock,
                "articles": [
                    {
                        "nom": a["nom"],
                        "quantite": a["quantite"],
                        "unite": a.get("unite", ""),
                        "rayon": a.get("rayon", "Autre"),
                        "en_stock": a.get("en_stock", 0),
                    }
                    for a in articles_a_acheter
                ],
                "par_rayon": par_rayon,
            }

    return await executer_async(_generate)


@router.delete("/{liste_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
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


@router.delete(
    "/{liste_id}/items/{item_id}",
    response_model=MessageResponse,
    responses=REPONSES_CRUD_SUPPRESSION,
)
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


# ═══════════════════════════════════════════════════════════
# OCR TICKET DE CAISSE → IMPORT COURSES
# ═══════════════════════════════════════════════════════════


@router.post(
    "/ocr-ticket-caisse",
    responses={**REPONSES_CRUD_CREATION, **REPONSES_CRUD_LECTURE},
    summary="OCR ticket de caisse → import courses",
)
@gerer_exception_api
async def importer_ticket_caisse(
    file: UploadFile,
    liste_id: int | None = Query(
        None,
        description="ID de la liste où importer les articles (sans = extraction seule)",
    ),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Analyse un ticket de caisse alimentaire par OCR et importe les articles
    dans une liste de courses.

    **Workflow**:
    1. Upload d'une photo du ticket (JPEG/PNG/WebP)
    2. Extraction OCR via Mistral vision
    3. Si `liste_id` fourni : import automatique dans la liste
    4. Retourne les données OCR brutes + articles importés

    **Paramètres**:
    - `file`: Photo du ticket (max 10 Mo)
    - `liste_id` (optionnel): ID de la liste cible ; sans → mode aperçu seul

    **Retour**:
    ```json
    {
      "success": true,
      "message": "12 articles importés",
      "donnees_ocr": { "magasin": "Carrefour", "date": "...", "total": 45.30, "articles": [...] },
      "articles_importes": [{ "nom": "Tomates", "quantite": 1.0, "article_id": 42 }],
      "articles_non_importes": [],
      "liste_id": 5
    }
    ```
    """
    TYPES_AUTORISES = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in TYPES_AUTORISES:
        raise HTTPException(
            status_code=422,
            detail=f"Type non supporté: {file.content_type}. Utilisez JPEG, PNG ou WebP.",
        )

    contenu = await file.read()
    if len(contenu) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 10 Mo)")

    from src.services.integrations.multimodal import get_multimodal_service

    service = get_multimodal_service()
    resultat = service.extraire_facture_sync(contenu)

    if not resultat:
        return {
            "success": False,
            "message": "Impossible d'extraire les données. Essayez avec une image plus nette.",
            "donnees_ocr": None,
            "articles_importes": [],
            "articles_non_importes": [],
            "liste_id": liste_id,
        }

    # Construire les données OCR normalisées
    articles_ocr = [
        {
            "description": ligne.description,
            "quantite": ligne.quantite,
            "prix_unitaire": ligne.prix_unitaire,
            "prix_total": ligne.prix_total,
        }
        for ligne in (resultat.lignes or [])
    ]

    donnees_ocr = {
        "magasin": resultat.magasin,
        "date": resultat.date,
        "articles": articles_ocr,
        "sous_total": resultat.sous_total,
        "tva": resultat.tva,
        "total": resultat.total,
        "mode_paiement": resultat.mode_paiement,
    }

    # Mode aperçu : retourner sans importer
    if liste_id is None:
        return {
            "success": True,
            "message": f"{len(articles_ocr)} article(s) détecté(s) — fournir liste_id pour importer",
            "donnees_ocr": donnees_ocr,
            "articles_importes": [],
            "articles_non_importes": articles_ocr,
            "liste_id": None,
        }

    # Import dans la liste
    from src.core.models import ArticleCourses, Ingredient, ListeCourses

    def _import():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")

            importes = []
            ignores = []

            for art in articles_ocr:
                nom = (art["description"] or "").strip()
                if not nom:
                    ignores.append(art)
                    continue

                # Tronquer les noms trop longs (max 120 chars)
                nom = nom[:120]
                quantite = float(art["quantite"] or 1.0)

                # Trouver ou créer l'ingrédient
                ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()
                if not ingredient:
                    ingredient = Ingredient(nom=nom, unite="unité", categorie="Autre")
                    session.add(ingredient)
                    session.flush()

                article = ArticleCourses(
                    liste_id=liste_id,
                    ingredient_id=ingredient.id,
                    quantite_necessaire=quantite,
                    priorite="moyenne",
                    rayon_magasin="Autre",
                )
                session.add(article)
                session.flush()

                importes.append({
                    "nom": nom,
                    "quantite": quantite,
                    "article_id": article.id,
                })

            session.commit()
            return importes, ignores

    importes, ignores = await executer_async(_import)

    return {
        "success": True,
        "message": f"{len(importes)} article(s) importé(s) dans la liste « {liste_id} »",
        "donnees_ocr": donnees_ocr,
        "articles_importes": importes,
        "articles_non_importes": ignores,
        "liste_id": liste_id,
    }
