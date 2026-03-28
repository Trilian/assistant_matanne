"""
Routes API pour l'inventaire.

Gestion du stock alimentaire : suivi des quantités, dates de péremption,
alertes de stock bas et recherche par code-barres.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.schemas import (
    ArticleConsolideResponse,
    InventaireItemCreate,
    InventaireItemResponse,
    InventaireItemUpdate,
    MessageResponse,
    ReponsePaginee,
    ScanBatchRequest,
    ScanBatchResponse,
)
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/inventaire", tags=["Inventaire"])


@router.get("/emplacements")
async def lister_emplacements() -> list[str]:
    """Retourne la liste des emplacements de stockage normalisés."""
    from src.core.constants import EMPLACEMENTS_INVENTAIRE

    return EMPLACEMENTS_INVENTAIRE


@router.get("/consolide", response_model=list[ArticleConsolideResponse], responses=REPONSES_LISTE)
@gerer_exception_api
async def inventaire_consolide(
    user: dict[str, Any] = Depends(require_auth),
) -> list[dict[str, Any]]:
    """Fusionne inventaire cuisine + cellier en vue unifiée."""

    def _normaliser_nom(nom: str) -> str:
        n = (nom or "").strip().lower()
        for old, new in (("é", "e"), ("è", "e"), ("ê", "e"), ("à", "a"), ("ù", "u")):
            n = n.replace(old, new)
        return " ".join(n.split())

    def _query():
        from src.core.models import ArticleInventaire
        from src.core.models.maison_extensions import ArticleCellier

        with executer_avec_session() as session:
            fusion: dict[str, dict[str, Any]] = {}

            # Source cuisine (inventaire)
            rows_cuisine = session.query(ArticleInventaire).all()
            for a in rows_cuisine:
                nom = a.nom or f"ingredient_{a.ingredient_id}"
                cle = _normaliser_nom(nom)
                unite = a.unite or "pcs"
                entree = fusion.setdefault(
                    cle,
                    {
                        "nom": nom,
                        "nom_normalise": cle,
                        "quantite_totale": 0.0,
                        "unite": unite,
                        "categories": [],
                        "emplacements": [],
                        "sources": [],
                        "details_sources": [],
                    },
                )
                entree["quantite_totale"] += float(a.quantite or 0)
                if a.categorie and a.categorie not in entree["categories"]:
                    entree["categories"].append(a.categorie)
                if a.emplacement and a.emplacement not in entree["emplacements"]:
                    entree["emplacements"].append(a.emplacement)
                if "cuisine" not in entree["sources"]:
                    entree["sources"].append("cuisine")
                entree["details_sources"].append(
                    {
                        "source": "cuisine",
                        "id": a.id,
                        "quantite": float(a.quantite or 0),
                        "unite": unite,
                    }
                )

            # Source cellier (maison)
            rows_cellier = session.query(ArticleCellier).all()
            for a in rows_cellier:
                nom = a.nom or f"cellier_{a.id}"
                cle = _normaliser_nom(nom)
                unite = a.unite or "unité"
                entree = fusion.setdefault(
                    cle,
                    {
                        "nom": nom,
                        "nom_normalise": cle,
                        "quantite_totale": 0.0,
                        "unite": unite,
                        "categories": [],
                        "emplacements": [],
                        "sources": [],
                        "details_sources": [],
                    },
                )
                entree["quantite_totale"] += float(a.quantite or 0)
                if a.categorie and a.categorie not in entree["categories"]:
                    entree["categories"].append(a.categorie)
                if a.emplacement and a.emplacement not in entree["emplacements"]:
                    entree["emplacements"].append(a.emplacement)
                if "cellier" not in entree["sources"]:
                    entree["sources"].append("cellier")
                entree["details_sources"].append(
                    {
                        "source": "cellier",
                        "id": a.id,
                        "quantite": float(a.quantite or 0),
                        "unite": unite,
                    }
                )

            return sorted(fusion.values(), key=lambda x: x["nom_normalise"])

    return await executer_async(_query)


@router.get("", response_model=ReponsePaginee[InventaireItemResponse], responses=REPONSES_LISTE)
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
    from src.core.models.user_preferences import OpenFoodFactsCache

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

            # Enrichir avec données OpenFoodFacts si code-barres présent
            codes = [i.code_barres for i in items if i.code_barres]
            off_map: dict[str, OpenFoodFactsCache] = {}
            if codes:
                off_rows = (
                    session.query(OpenFoodFactsCache)
                    .filter(OpenFoodFactsCache.code_barres.in_(codes))
                    .all()
                )
                off_map = {r.code_barres: r for r in off_rows}

            result_items = []
            for i in items:
                data = InventaireItemResponse.model_validate(i).model_dump()
                off = off_map.get(i.code_barres) if i.code_barres else None
                if off:
                    data["nutriscore"] = off.nutriscore
                    data["ecoscore"] = off.ecoscore
                    data["nova_group"] = off.nova_group
                result_items.append(data)

            return {
                "items": result_items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size,
            }

    return await executer_async(_query)


@router.post("", response_model=InventaireItemResponse, responses=REPONSES_CRUD_CREATION)
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


@router.get(
    "/barcode/{code}", response_model=InventaireItemResponse, responses=REPONSES_CRUD_LECTURE
)
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


@router.post(
    "/barcode/batch",
    response_model=ScanBatchResponse,
    responses=REPONSES_CRUD_LECTURE,
)
@gerer_exception_api
async def scanner_codes_batch(
    request: ScanBatchRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Résout un lot de codes-barres en articles d'inventaire.

    Utilisé par le scanner multi-codes : une seule requête pour identifier
    plusieurs articles scannés en une passe caméra.

    Args:
        request: Liste de codes-barres (à scanner, max 50)

    Returns:
        ``trouves``: articles trouvés avec leur détail
        ``inconnus``: codes-barres sans article correspondant

    Example:
        ```
        POST /api/v1/inventaire/barcode/batch
        {"codes": ["3017620422003", "9999999999999"]}

        Response:
        {
            "trouves": [{"code": "3017620422003", "article": {...}}],
            "inconnus": ["9999999999999"]
        }
        ```
    """
    from sqlalchemy.orm import joinedload

    from src.core.models import ArticleInventaire

    def _query():
        with executer_avec_session() as session:
            articles = (
                session.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
                .filter(ArticleInventaire.code_barres.in_(request.codes))
                .all()
            )

            code_map = {a.code_barres: a for a in articles if a.code_barres}

            trouves = []
            inconnus = []
            vus = set()
            for code in request.codes:
                if code in vus:
                    continue
                vus.add(code)
                if code in code_map:
                    trouves.append({
                        "code": code,
                        "article": InventaireItemResponse.model_validate(code_map[code]),
                    })
                else:
                    inconnus.append(code)

            return {"trouves": trouves, "inconnus": inconnus}

    return await executer_async(_query)


@router.post(
    "/barcode/{code}/enrichir",
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def enrichir_par_code_barres(
    code: str,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Enrichit un article d'inventaire via OpenFoodFacts à partir de son code-barres.

    Récupère nom, nutrition (nutriscore, ecoscore, nova), marque, catégories
    et met à jour l'article en base.

    Args:
        code: Code-barres (EAN-13, UPC, etc.)

    Returns:
        Données enrichies du produit
    """
    from src.core.models import ArticleInventaire
    from src.services.integrations.produit import OpenFoodFactsService

    off_service = OpenFoodFactsService()
    produit = off_service.rechercher_produit(code)

    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé sur OpenFoodFacts")

    def _update():
        with executer_avec_session() as session:
            article = (
                session.query(ArticleInventaire)
                .filter(ArticleInventaire.code_barres == code)
                .first()
            )

            enrichment = {
                "nom_produit": produit.nom,
                "marque": produit.marque,
                "categories": produit.categories,
                "image_url": produit.image_url,
                "labels": produit.labels,
            }

            if produit.nutrition:
                enrichment["nutriscore"] = produit.nutrition.nutriscore
                enrichment["ecoscore"] = produit.nutrition.ecoscore
                enrichment["nova_group"] = produit.nutrition.nova_group
                enrichment["calories_100g"] = produit.nutrition.energie_kcal
                enrichment["proteines_100g"] = produit.nutrition.proteines_g
                enrichment["glucides_100g"] = produit.nutrition.glucides_g
                enrichment["lipides_100g"] = produit.nutrition.lipides_g

            if article:
                # Mettre à jour les champs disponibles sur le modèle
                for attr in ("nutriscore", "ecoscore", "nova_group"):
                    if hasattr(article, attr) and enrichment.get(attr):
                        setattr(article, attr, enrichment[attr])
                session.commit()
                enrichment["article_id"] = article.id
                enrichment["article_mis_a_jour"] = True
            else:
                enrichment["article_id"] = None
                enrichment["article_mis_a_jour"] = False

            return enrichment

    return await executer_async(_update)


@router.get("/{item_id}", response_model=InventaireItemResponse, responses=REPONSES_CRUD_LECTURE)
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


@router.put("/{item_id}", response_model=InventaireItemResponse, responses=REPONSES_CRUD_ECRITURE)
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


@router.delete("/{item_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
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


@router.post(
    "/bulk",
    response_model=MessageResponse,
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def ajouter_articles_bulk(
    articles: list[dict[str, Any]],
    emplacement: str = Query("frigo", description="Emplacement par défaut"),
    user: dict[str, Any] = Depends(require_auth),
):
    """Ajoute plusieurs articles à l'inventaire en une seule requête (import photo-frigo).

    Chaque article doit avoir au minimum: nom (str), quantite (float).
    Champs optionnels: unite (str), categorie (str).
    Si l'ingrédient existe déjà, la quantité est cumulée.
    """
    from src.core.models import ArticleInventaire, Ingredient

    if not articles:
        raise HTTPException(status_code=422, detail="Liste d'articles vide")

    def _bulk():
        with executer_avec_session() as session:
            crees = 0
            maj = 0
            for art in articles[:50]:  # Limiter à 50 par appel
                nom = (art.get("nom") or "").strip()
                if not nom:
                    continue
                quantite = float(art.get("quantite") or 1.0)

                # Trouver ou créer l'ingrédient
                ingredient = session.query(Ingredient).filter(
                    Ingredient.nom == nom
                ).first()
                if not ingredient:
                    ingredient = Ingredient(
                        nom=nom,
                        categorie=art.get("categorie", "Autre"),
                        unite=art.get("unite", "pcs") or "pcs",
                    )
                    session.add(ingredient)
                    session.flush()

                # Trouver ou créer l'article inventaire
                inv = session.query(ArticleInventaire).filter(
                    ArticleInventaire.ingredient_id == ingredient.id
                ).first()
                if inv:
                    inv.quantite = float(inv.quantite or 0) + quantite
                    if emplacement and not inv.emplacement:
                        inv.emplacement = emplacement
                    maj += 1
                else:
                    session.add(ArticleInventaire(
                        ingredient_id=ingredient.id,
                        quantite=quantite,
                        quantite_min=1.0,
                        emplacement=emplacement,
                    ))
                    crees += 1

            session.commit()
            return MessageResponse(
                message=f"{crees} créés, {maj} mis à jour",
                id=0,
            )

    return await executer_async(_bulk)


@router.post("/ocr-photo-frigo", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def ocr_photo_frigo(
    photo: UploadFile = File(..., description="Photo du réfrigérateur (jpg/png, max 10 Mo)"),
    emplacement: str = Query("frigo", description="Emplacement par défaut pour les articles créés"),
    importer: bool = Query(True, alias="import", description="Si False, détecte sans importer (mode preview)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse une photo de frigo via IA vision et importe les aliments détectés dans l'inventaire.

    Avec `import=false`, retourne les articles détectés sans les sauvegarder (mode preview pour checkboxes).
    Retourne la liste des articles créés/mis à jour.
    """
    # Valider le type de fichier
    if photo.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=422, detail="Seuls les formats JPEG, PNG et WebP sont acceptés")

    # Lire les bytes (limite 10 Mo)
    image_bytes = await photo.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image trop volumineuse (max 10 Mo)")

    from src.services.integrations.multimodal import get_multimodal_service

    service = get_multimodal_service()
    articles_detectes = await service.analyser_frigo(image_bytes)

    if not articles_detectes:
        return {"articles": [], "total": 0, "crees": 0, "mis_a_jour": 0, "message": "Aucun aliment détecté dans la photo"}

    # Mode preview : retourner les articles détectés sans importer
    if not importer:
        return {
            "articles": articles_detectes,
            "total": len(articles_detectes),
            "crees": 0,
            "mis_a_jour": 0,
            "message": f"{len(articles_detectes)} aliment(s) détecté(s) — en attente de confirmation",
        }

    # Importer dans l'inventaire via le bulk
    from src.core.models import ArticleInventaire, Ingredient

    def _bulk():
        with executer_avec_session() as session:
            crees = 0
            maj = 0
            for art in articles_detectes[:50]:
                nom = art.get("nom", "").strip()
                if not nom:
                    continue
                quantite = float(art.get("quantite") or 1.0)

                ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()
                if not ingredient:
                    ingredient = Ingredient(
                        nom=nom,
                        categorie=art.get("categorie", "Autre"),
                        unite=art.get("unite", "pcs") or "pcs",
                    )
                    session.add(ingredient)
                    session.flush()

                inv = session.query(ArticleInventaire).filter(
                    ArticleInventaire.ingredient_id == ingredient.id
                ).first()
                if inv:
                    inv.quantite = float(inv.quantite or 0) + quantite
                    if emplacement and not inv.emplacement:
                        inv.emplacement = emplacement
                    maj += 1
                else:
                    session.add(ArticleInventaire(
                        ingredient_id=ingredient.id,
                        quantite=quantite,
                        quantite_min=1.0,
                        emplacement=emplacement,
                    ))
                    crees += 1

            session.commit()
            return {"articles": articles_detectes, "total": len(articles_detectes), "crees": crees, "mis_a_jour": maj}

    return await executer_async(_bulk)


# ═══════════════════════════════════════════════════════════
# QR CODE — ÉTIQUETAGE INVENTAIRE
# ═══════════════════════════════════════════════════════════


@router.get(
    "/articles/{article_id}/qr",
    responses=REPONSES_CRUD_LECTURE,
    summary="Générer un QR code PNG pour un article",
)
@gerer_exception_api
async def generer_qr_article(
    article_id: int,
    user: dict[str, Any] = Depends(require_auth),
):
    """Génère un QR code PNG contenant les infos de l'article pour étiquetage.

    Le QR code encode un JSON compact : id, nom, emplacement, péremption.
    """
    import io
    import json as json_mod

    import qrcode
    from fastapi.responses import StreamingResponse

    from src.core.models import ArticleInventaire

    def _gen():
        with executer_avec_session() as session:
            article = session.query(ArticleInventaire).filter(ArticleInventaire.id == article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail="Article non trouvé")

            data = {
                "id": article.id,
                "nom": article.nom,
                "emplacement": article.emplacement,
                "peremption": str(article.date_peremption) if article.date_peremption else None,
            }
            return json_mod.dumps(data, ensure_ascii=False)

    qr_data = await executer_async(_gen)

    # Générer le QR code en mémoire
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=qr_article_{article_id}.png"},
    )


@router.get(
    "/qr/scan",
    responses=REPONSES_CRUD_LECTURE,
    summary="Retrouver un article par son QR code",
)
@gerer_exception_api
async def scanner_qr_article(
    article_id: int = Query(..., description="ID de l'article encodé dans le QR code"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retrouve un article depuis les données scannées du QR code.

    Le frontend scanne le QR, extrait l'ID, et appelle cet endpoint.
    Retourne l'article complet + actions rapides disponibles.
    """
    from src.core.models import ArticleInventaire

    def _scan():
        with executer_avec_session() as session:
            article = session.query(ArticleInventaire).filter(ArticleInventaire.id == article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail="Article non trouvé via QR code")

            jours_peremption = None
            if article.date_peremption:
                from datetime import date

                delta = (article.date_peremption - date.today()).days
                jours_peremption = delta

            return {
                "article": {
                    "id": article.id,
                    "nom": article.nom,
                    "quantite": float(article.quantite) if article.quantite else 0,
                    "unite": article.unite,
                    "emplacement": article.emplacement,
                    "date_peremption": str(article.date_peremption) if article.date_peremption else None,
                    "jours_avant_peremption": jours_peremption,
                },
                "actions": [
                    {"label": "Consommer", "method": "PATCH", "url": f"/api/v1/inventaire/articles/{article_id}"},
                    {"label": "Supprimer", "method": "DELETE", "url": f"/api/v1/inventaire/articles/{article_id}"},
                ],
            }

    return await executer_async(_scan)
