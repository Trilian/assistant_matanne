"""
Routes API pour les courses.
"""

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field

# â”€â”€â”€ Idempotency cache (TTL 5 min, single-instance) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_IDEMPOTENCY_CACHE: dict[str, tuple[float, Any]] = {}
_IDEMPOTENCY_TTL = 300  # secondes


def _check_idempotency(key: str | None) -> Any | None:
    """Retourne le rÃ©sultat mis en cache si la clÃ© a dÃ©jÃ  Ã©tÃ© traitÃ©e rÃ©cemment."""
    if not key:
        return None
    now = time.time()
    expired = [k for k, (ts, _) in _IDEMPOTENCY_CACHE.items() if now - ts > _IDEMPOTENCY_TTL]
    for k in expired:
        del _IDEMPOTENCY_CACHE[k]
    entry = _IDEMPOTENCY_CACHE.get(key)
    return entry[1] if entry else None


def _store_idempotency(key: str | None, result: Any) -> None:
    """Enregistre un rÃ©sultat pour Ã©viter les doublons d'idempotency."""
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


class FeedbackPredictionCoursesRequest(BaseModel):
    """Feedback utilisateur sur une suggestion d'article habituel."""

    article_nom: str = Field(..., min_length=1, max_length=200)
    accepte: bool = Field(..., description="True si l'article a ete ajoute, False sinon")


@router.get("", response_model=ReponsePaginee[ListeCoursesResume], responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_courses(
    page: int = Query(1, ge=1, description="NumÃ©ro de page (1-indexÃ©)"),
    page_size: int = Query(20, ge=1, le=100, description="Nombre d'Ã©lÃ©ments par page"),
    active_only: bool = Query(True, description="Afficher uniquement les listes non archivÃ©es"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les listes de courses avec pagination.

    Retourne les listes de courses triÃ©es par date de crÃ©ation dÃ©croissante.
    Par dÃ©faut, seules les listes actives (non archivÃ©es) sont affichÃ©es.

    Args:
        page: NumÃ©ro de page (dÃ©faut: 1)
        page_size: Taille de page (dÃ©faut: 20, max: 100)
        active_only: Filtrer les listes archivÃ©es (dÃ©faut: True)

    Returns:
        RÃ©ponse paginÃ©e avec items, total, page, page_size

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
    CrÃ©e une nouvelle liste de courses.

    NÃ©cessite une authentification. La liste est crÃ©Ã©e vide,
    les articles peuvent Ãªtre ajoutÃ©s ensuite via POST /{id}/items.

    Args:
        data: DonnÃ©es de la liste (nom requis)

    Returns:
        Message de confirmation avec l'ID de la liste crÃ©Ã©e

    Raises:
        401: Non authentifiÃ©
        422: DonnÃ©es invalides (nom vide)

    Example:
        ```
        POST /api/v1/courses
        Authorization: Bearer <token>

        Body: {"nom": "Courses du weekend"}

        Response (201):
        {"message": "Liste crÃ©Ã©e", "id": 5}
        ```
    """
    from src.core.models import ListeCourses

    def _create():
        with executer_avec_session() as session:
            liste = ListeCourses(nom=data.nom, archivee=False)
            session.add(liste)
            session.commit()
            session.refresh(liste)
            return MessageResponse(message="Liste crÃ©Ã©e", id=liste.id)

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
    Ajoute un article Ã  une liste de courses.

    CrÃ©e automatiquement l'ingrÃ©dient s'il n'existe pas encore en base.

    Args:
        liste_id: ID de la liste de courses
        item: DonnÃ©es de l'article (nom, quantitÃ©, unitÃ©, catÃ©gorie)

    Returns:
        Message de confirmation avec l'ID de l'article crÃ©Ã©

    Raises:
        401: Non authentifiÃ©
        404: Liste non trouvÃ©e
        422: DonnÃ©es invalides

    Example:
        ```
        POST /api/v1/courses/5/items
        Authorization: Bearer <token>

        Body: {"nom": "Tomates", "quantite": 2.0, "unite": "kg", "categorie": "Fruits et lÃ©gumes"}

        Response (201):
        {"message": "Article ajoutÃ©", "id": 12}
        ```
    """
    from src.core.models import ArticleCourses, Ingredient, ListeCourses

    def _add():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

            # Trouver ou crÃ©er l'ingrÃ©dient
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

            return MessageResponse(message="Article ajoutÃ©", id=article.id)

    return await executer_async(_add)


@router.get("/{liste_id}", response_model=ListeCoursesResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_liste(liste_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    RÃ©cupÃ¨re une liste de courses avec ses articles dÃ©taillÃ©s.

    Args:
        liste_id: ID de la liste de courses

    Returns:
        DÃ©tail de la liste avec tous ses articles

    Raises:
        404: Liste non trouvÃ©e

    Example:
        ```
        GET /api/v1/courses/5

        Response:
        {
            "id": 5,
            "nom": "Courses semaine",
            "archivee": false,
            "items": [
                {"id": 12, "nom": "Tomates", "quantite": 2.0, "coche": false, "categorie": "Fruits et lÃ©gumes"}
            ]
        }
        ```
    """
    from src.core.models import ListeCourses

    def _get():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

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
        description="Regroupement du texte exportÃ©",
    ),
    user: dict[str, Any] = Depends(require_auth),
):
    """Exporte une liste de courses en texte brut (optimisÃ© mobile/partage)."""
    from datetime import datetime

    from src.core.models import ListeCourses

    def _export():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

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


@router.get("/{liste_id}/share-qr")
@gerer_exception_api
async def generer_qr_partage_liste(
    liste_id: int,
    include_checked: bool = Query(False, description="Inclure les articles dÃ©jÃ  cochÃ©s"),
    user: dict[str, Any] = Depends(require_auth),
):
    """GÃ©nÃ¨re un QR code PNG contenant une version texte de la liste."""
    from io import BytesIO

    import qrcode

    from src.core.models import ListeCourses

    def _build_payload() -> str:
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

            articles = [
                a
                for a in (liste.articles or [])
                if include_checked or not a.achete
            ]
            lignes = [f"Courses - {liste.nom}"]
            for article in articles:
                nom = article.ingredient.nom if article.ingredient else "Article"
                unite = (article.ingredient.unite if article.ingredient else "") or ""
                qty = f"{article.quantite_necessaire:g} {unite}".strip()
                lignes.append(f"- {nom} ({qty})")
            return "\n".join(lignes)

    contenu = await executer_async(_build_payload)

    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(contenu)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return Response(content=buffer.getvalue(), media_type="image/png")


@router.put("/{liste_id}", response_model=MessageResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_liste(
    liste_id: int, data: CourseListCreate, user: dict[str, Any] = Depends(require_auth)
):
    """
    Met Ã  jour le nom d'une liste de courses.

    Args:
        liste_id: ID de la liste Ã  modifier
        data: Nouvelles donnÃ©es (nom)

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifiÃ©
        404: Liste non trouvÃ©e

    Example:
        ```
        PUT /api/v1/courses/5
        Authorization: Bearer <token>

        Body: {"nom": "Courses marchÃ©"}

        Response:
        {"message": "Liste mise Ã  jour", "id": 5}
        ```
    """
    from src.core.models import ListeCourses

    def _update():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

            liste.nom = data.nom
            session.commit()
            session.refresh(liste)

            return MessageResponse(message="Liste mise Ã  jour", id=liste.id)

    return await executer_async(_update)


@router.put(
    "/{liste_id}/items/{item_id}", response_model=MessageResponse, responses=REPONSES_CRUD_ECRITURE
)
@gerer_exception_api
async def modifier_article(
    liste_id: int, item_id: int, item: CourseItemBase, user: dict[str, Any] = Depends(require_auth)
):
    """
    Met Ã  jour un article d'une liste de courses.

    Permet de modifier la quantitÃ©, cocher/dÃ©cocher l'article, ou changer sa catÃ©gorie.

    Args:
        liste_id: ID de la liste contenant l'article
        item_id: ID de l'article Ã  modifier
        item: Nouvelles donnÃ©es de l'article

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifiÃ©
        404: Article non trouvÃ© dans cette liste

    Example:
        ```
        PUT /api/v1/courses/5/items/12
        Authorization: Bearer <token>

        Body: {"nom": "Tomates", "quantite": 3.0, "coche": true}

        Response:
        {"message": "Article mis Ã  jour", "id": 12}
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
                raise HTTPException(status_code=404, detail="Article non trouvÃ©")

            article.quantite_necessaire = item.quantite or 1.0
            article.achete = item.coche
            if item.categorie:
                article.rayon_magasin = item.categorie
            session.commit()

            return MessageResponse(message="Article mis Ã  jour", id=item_id)

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
    """Checkout batch: marque des articles courses comme achetÃ©s et met Ã  jour l'inventaire.

    Transaction unique par requÃªte:
    - coche l'article de courses (achete=True, achete_le)
    - incrÃ©mente (ou crÃ©e) la ligne inventaire associÃ©e Ã  l'ingrÃ©dient
    - enregistre l'historique inventaire
    """
    # Idempotency: mÃªme clÃ© = mÃªme rÃ©ponse (anti double-scan)
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
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

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

                # 2) Met Ã  jour l'inventaire
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
    - rÃ©sout le code-barres vers un article inventaire (ingredient_id)
    - trouve l'article courses non achetÃ© correspondant dans la liste
    - coche l'article et incrÃ©mente l'inventaire
    """
    # Idempotency: mÃªme clÃ© = mÃªme rÃ©ponse (anti double-scan)
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
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

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
    """GÃ©nÃ¨re une liste de courses depuis le planning de la semaine.

    1. RÃ©cupÃ¨re tous les Repas de la semaine avec recette_id
    2. Extrait et agrÃ¨ge les ingrÃ©dients via RecetteIngredient
    3. Soustrait le stock existant si demandÃ©
    4. CrÃ©e une ListeCourses avec les ArticleCourses
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
            # 1) RÃ©cupÃ©rer tous les repas de la semaine avec une recette liÃ©e
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
                    detail="Aucun repas avec recette trouvÃ© pour cette semaine",
                )

            # Collecter tous les recette_ids (plat + entrÃ©e + desserts)
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

            # 2) Extraire les ingrÃ©dients de toutes les recettes
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

            # 3) AgrÃ©ger les ingrÃ©dients identiques
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

            # 5) CrÃ©er la ListeCourses + ArticleCourses
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
        liste_id: ID de la liste Ã  supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifiÃ©
        404: Liste non trouvÃ©e

    Example:
        ```
        DELETE /api/v1/courses/5
        Authorization: Bearer <token>

        Response:
        {"message": "Liste supprimÃ©e", "id": 5}
        ```
    """
    from src.core.models import ListeCourses

    def _delete():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

            session.delete(liste)
            session.commit()

            return MessageResponse(message="Liste supprimÃ©e", id=liste_id)

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
        item_id: ID de l'article Ã  supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifiÃ©
        404: Article non trouvÃ© dans cette liste

    Example:
        ```
        DELETE /api/v1/courses/5/items/12
        Authorization: Bearer <token>

        Response:
        {"message": "Article supprimÃ©", "id": 12}
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
                raise HTTPException(status_code=404, detail="Article non trouvÃ©")

            session.delete(article)
            session.commit()

            return MessageResponse(message="Article supprimÃ©", id=item_id)

    return await executer_async(_delete)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION COURSES â†’ SYNC INVENTAIRE + HISTORIQUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post(
    "/{liste_id}/valider",
    response_model=MessageResponse,
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def valider_courses(
    liste_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Valide une liste de courses : incrÃ©mente l'inventaire + met Ã  jour l'historique d'achats.

    Pour chaque article cochÃ© :
    - IncrÃ©mente l'article correspondant dans l'inventaire (ou le crÃ©e)
    - Met Ã  jour la table historique_achats (frÃ©quence d'achat pour l'IA)

    Puis archive la liste.
    """
    from datetime import datetime, UTC

    from src.core.models import ArticleInventaire
    from src.core.models.courses import ArticleCourses, HistoriqueAchats, ListeCourses
    from src.core.models.recettes import Ingredient

    def _valider():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

            articles_achetes = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste_id,
                    ArticleCourses.achete == True,  # noqa: E712
                )
                .all()
            )

            articles_sync = 0
            now = datetime.now(UTC)

            for art in articles_achetes:
                # IncrÃ©menter l'inventaire
                inv = (
                    session.query(ArticleInventaire)
                    .filter(ArticleInventaire.ingredient_id == art.ingredient_id)
                    .first()
                )
                if inv:
                    inv.quantite = float(inv.quantite or 0) + float(art.quantite_necessaire or 1)
                else:
                    session.add(
                        ArticleInventaire(
                            ingredient_id=art.ingredient_id,
                            quantite=float(art.quantite_necessaire or 1),
                            quantite_min=1.0,
                        )
                    )
                articles_sync += 1

                # Mettre Ã  jour l'historique d'achats
                ingredient = (
                    session.query(Ingredient).filter(Ingredient.id == art.ingredient_id).first()
                )
                if ingredient:
                    hist = (
                        session.query(HistoriqueAchats)
                        .filter(HistoriqueAchats.article_nom == ingredient.nom)
                        .first()
                    )
                    if hist:
                        # Calculer la frÃ©quence
                        if hist.derniere_achat:
                            delta = (now - hist.derniere_achat).days
                            if delta > 0:
                                ancien_freq = hist.frequence_jours or delta
                                hist.frequence_jours = round(
                                    (ancien_freq * hist.nb_achats + delta) / (hist.nb_achats + 1)
                                )
                        hist.nb_achats += 1
                        hist.derniere_achat = now
                    else:
                        session.add(
                            HistoriqueAchats(
                                article_nom=ingredient.nom,
                                categorie=ingredient.categorie,
                                rayon_magasin=art.rayon_magasin,
                                derniere_achat=now,
                                nb_achats=1,
                            )
                        )

            # Archiver la liste
            liste.archivee = True
            session.commit()

            return MessageResponse(
                message=f"Courses validÃ©es : {articles_sync} articles synchronisÃ©s avec l'inventaire",
                id=liste_id,
            )

    return await executer_async(_valider)


@router.get(
    "/{liste_id}/bio-local",
    responses=REPONSES_LISTE,
)
@gerer_exception_api
async def obtenir_suggestions_bio_local(
    liste_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse les articles de la liste et retourne des suggestions bio/local/saison.

    Pour chaque article :
    - VÃ©rifie si un producteur local est disponible
    - VÃ©rifie si le produit est de saison
    - Propose des alternatives bio si pertinent
    """
    import json
    from pathlib import Path

    from src.core.models.courses import ArticleCourses, ListeCourses

    def _analyse():
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

            articles = (
                session.query(ArticleCourses)
                .filter(ArticleCourses.liste_id == liste_id)
                .all()
            )

            # Charger les donnÃ©es de saison
            saison_path = Path("data/reference/produits_de_saison.json")
            produits_saison: dict = {}
            if saison_path.exists():
                produits_saison = json.loads(saison_path.read_text(encoding="utf-8"))

            from datetime import date
            mois_actuel = date.today().month
            mois_noms = [
                "", "janvier", "fÃ©vrier", "mars", "avril", "mai", "juin",
                "juillet", "aoÃ»t", "septembre", "octobre", "novembre", "dÃ©cembre",
            ]
            mois_str = mois_noms[mois_actuel]

            suggestions = []
            for art in articles:
                nom = art.ingredient.nom.lower() if art.ingredient else ""
                info: dict[str, Any] = {
                    "article_id": art.id,
                    "nom": art.ingredient.nom if art.ingredient else "?",
                    "en_saison": False,
                    "bio_disponible": False,
                    "local_disponible": False,
                    "producteur": None,
                    "alternative_bio": None,
                }

                # VÃ©rifier saisonnalitÃ©
                if isinstance(produits_saison, dict):
                    for categorie, produits in produits_saison.items():
                        if isinstance(produits, list):
                            for p in produits:
                                if isinstance(p, dict) and nom in p.get("nom", "").lower():
                                    mois_dispo = p.get("mois", [])
                                    if mois_str in mois_dispo or mois_actuel in mois_dispo:
                                        info["en_saison"] = True

                suggestions.append(info)

            return {
                "liste_id": liste_id,
                "mois": mois_str,
                "suggestions": suggestions,
                "nb_en_saison": sum(1 for s in suggestions if s["en_saison"]),
            }

    return await executer_async(_analyse)


@router.get(
    "/recurrents-suggeres",
    responses=REPONSES_LISTE,
)
@gerer_exception_api
async def obtenir_recurrents_suggeres(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les articles rÃ©currents dont la frÃ©quence d'achat est dÃ©passÃ©e.

    Se base sur l'historique d'achats pour suggÃ©rer les articles que l'utilisateur
    achÃ¨te habituellement Ã  une certaine frÃ©quence.
    """
    from datetime import datetime, UTC

    from src.core.models.courses import HistoriqueAchats

    def _recurrents():
        with executer_avec_session() as session:
            now = datetime.now(UTC)

            # Articles avec frÃ©quence connue
            historiques = (
                session.query(HistoriqueAchats)
                .filter(
                    HistoriqueAchats.frequence_jours.isnot(None),
                    HistoriqueAchats.nb_achats >= 2,
                )
                .all()
            )

            suggestions = []
            for h in historiques:
                if not h.derniere_achat or not h.frequence_jours:
                    continue
                jours_depuis = (now - h.derniere_achat).days
                if jours_depuis >= h.frequence_jours:
                    suggestions.append({
                        "article_nom": h.article_nom,
                        "categorie": h.categorie,
                        "frequence_jours": h.frequence_jours,
                        "jours_depuis_dernier_achat": jours_depuis,
                        "retard_jours": jours_depuis - h.frequence_jours,
                        "nb_achats_total": h.nb_achats,
                    })

            # Trier par retard dÃ©croissant
            suggestions.sort(key=lambda x: x["retard_jours"], reverse=True)

            return {
                "suggestions": suggestions[:20],
                "total": len(suggestions),
            }

    return await executer_async(_recurrents)


@router.get(
    "/optimiser-budget-ia",
    responses=REPONSES_LISTE,
    summary="Optimiser le budget courses avec l'IA",
)
@gerer_exception_api
async def optimiser_budget_courses_ia(
    budget_cible: float = Query(120.0, ge=10, le=2000, description="Budget cible de la liste"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse la liste active et propose des optimisations budget (IA + heuristiques)."""
    from src.core.models import ArticleCourses, ListeCourses

    estimation_par_rayon = {
        "fruits": 2.4,
        "lÃ©gumes": 2.1,
        "legumes": 2.1,
        "viandes": 6.5,
        "poissons": 7.0,
        "produits laitiers": 2.2,
        "boissons": 1.8,
        "Ã©picerie": 2.7,
        "epicerie": 2.7,
        "boulangerie": 1.6,
        "autre": 2.5,
    }

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.archivee.is_(False))
                .order_by(ListeCourses.cree_le.desc())
                .first()
            )
            if liste is None:
                raise HTTPException(status_code=404, detail="Aucune liste de courses active")

            articles = (
                session.query(ArticleCourses)
                .filter(ArticleCourses.liste_id == liste.id, ArticleCourses.achete.is_(False))
                .all()
            )

            priorites: list[dict[str, Any]] = []
            articles_ia: list[dict[str, Any]] = []
            estimation_totale = 0.0

            for article in articles:
                nom = article.ingredient.nom if getattr(article, "ingredient", None) else "Article"
                rayon = (article.rayon_magasin or getattr(article.ingredient, "categorie", "Autre") or "Autre")
                rayon_key = str(rayon).lower()
                cout_unitaire = estimation_par_rayon.get(rayon_key, estimation_par_rayon["autre"])
                quantite = float(article.quantite_necessaire or 1.0)
                cout_estime = round(cout_unitaire * max(quantite, 0.25), 2)
                estimation_totale += cout_estime

                priorite_txt = (article.priorite or "moyenne").lower()
                priorite_int = {"haute": 1, "moyenne": 2, "basse": 3}.get(priorite_txt, 2)

                priorites.append(
                    {
                        "nom": nom,
                        "rayon": rayon,
                        "quantite": quantite,
                        "cout_estime": cout_estime,
                        "indispensable": priorite_int == 1,
                    }
                )

                articles_ia.append(
                    {
                        "nom": nom,
                        "quantite": quantite,
                        "unite": getattr(article.ingredient, "unite", "pcs") or "pcs",
                        "rayon": rayon,
                        "priorite": priorite_int,
                    }
                )

            priorites.sort(key=lambda i: (not i["indispensable"], -i["cout_estime"]))

            return {
                "liste_id": liste.id,
                "nom_liste": liste.nom,
                "priorites": priorites,
                "articles_ia": articles_ia,
                "estimation_totale": round(estimation_totale, 2),
            }

    donnees = await executer_async(_query)

    substitutions: list[dict[str, Any]] = []
    try:
        from src.services.cuisine.courses.suggestion import obtenir_service_courses_intelligentes
        from src.services.cuisine.courses.types import ArticleCourse

        service = obtenir_service_courses_intelligentes()
        articles_service = [ArticleCourse(**a) for a in donnees["articles_ia"]]
        suggestions = await service.suggerer_substitutions(articles_service)
        substitutions = [s.model_dump() for s in suggestions]
    except Exception:
        substitutions = []

    estimation = float(donnees["estimation_totale"])
    economie_potentielle = round(max(0.0, estimation - budget_cible), 2)

    if estimation <= budget_cible:
        niveau_alerte = "ok"
        message = "Votre liste est dans le budget cible."
    elif estimation <= budget_cible * 1.15:
        niveau_alerte = "attention"
        message = "Budget lÃ©gÃ¨rement dÃ©passÃ©, appliquez 1 ou 2 substitutions."
    else:
        niveau_alerte = "critique"
        message = "Budget nettement dÃ©passÃ©, priorisez les indispensables et substitutions IA."

    return {
        "liste_id": donnees["liste_id"],
        "nom_liste": donnees["nom_liste"],
        "budget_cible": round(budget_cible, 2),
        "estimation_totale": estimation,
        "economie_potentielle": economie_potentielle,
        "niveau_alerte": niveau_alerte,
        "substitutions": substitutions,
        "priorites": donnees["priorites"][:20],
        "message": message,
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# OCR TICKET DE CAISSE â†’ IMPORT COURSES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post(
    "/ocr-ticket-caisse",
    responses={**REPONSES_CRUD_CREATION, **REPONSES_CRUD_LECTURE},
    summary="OCR ticket de caisse â†’ import courses",
)
@gerer_exception_api
async def importer_ticket_caisse(
    file: UploadFile,
    liste_id: int | None = Query(
        None,
        description="ID de la liste oÃ¹ importer les articles (sans = extraction seule)",
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
    4. Retourne les donnÃ©es OCR brutes + articles importÃ©s

    **ParamÃ¨tres**:
    - `file`: Photo du ticket (max 10 Mo)
    - `liste_id` (optionnel): ID de la liste cible ; sans â†’ mode aperÃ§u seul

    **Retour**:
    ```json
    {
      "success": true,
      "message": "12 articles importÃ©s",
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
            detail=f"Type non supportÃ©: {file.content_type}. Utilisez JPEG, PNG ou WebP.",
        )

    contenu = await file.read()
    if len(contenu) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 10 Mo)")

    from src.services.integrations.multimodal import obtenir_multimodal_service

    service = obtenir_multimodal_service()
    resultat = service.extraire_facture_sync(contenu)

    if not resultat:
        return {
            "success": False,
            "message": "Impossible d'extraire les donnÃ©es. Essayez avec une image plus nette.",
            "donnees_ocr": None,
            "articles_importes": [],
            "articles_non_importes": [],
            "liste_id": liste_id,
        }

    # Construire les donnÃ©es OCR normalisÃ©es
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

    # Mode aperÃ§u : retourner sans importer
    if liste_id is None:
        return {
            "success": True,
            "message": f"{len(articles_ocr)} article(s) dÃ©tectÃ©(s) â€” fournir liste_id pour importer",
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
                raise HTTPException(status_code=404, detail="Liste non trouvÃ©e")

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

                # Trouver ou crÃ©er l'ingrÃ©dient
                ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()
                if not ingredient:
                    ingredient = Ingredient(nom=nom, unite="unitÃ©", categorie="Autre")
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
        "message": f"{len(importes)} article(s) importÃ©(s) dans la liste Â« {liste_id} Â»",
        "donnees_ocr": donnees_ocr,
        "articles_importes": importes,
        "articles_non_importes": ignores,
        "liste_id": liste_id,
    }


@router.get(
    "/predictions",
    responses=REPONSES_LISTE,
    summary="Predictions d'articles habituels",
)
@gerer_exception_api
async def obtenir_predictions_courses(
    limite: int = Query(25, ge=1, le=100),
    inclure_deja_sur_liste: bool = Query(False),
    nb_invites: int = Query(0, ge=0, le=20, description="Nombre d'invites prevus"),
    evenements: list[str] | None = Query(None, description="Evenements contextuels (repetable)"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne une liste pre-completee d'articles habituels avec score de confiance."""

    def _query() -> dict[str, Any]:
        from src.services.cuisine.prediction_courses import obtenir_service_prediction_courses

        service = obtenir_service_prediction_courses()
        items = service.predire_articles(
            limite=limite,
            inclure_deja_sur_liste=inclure_deja_sur_liste,
            evenements=evenements,
            nb_invites=nb_invites,
        )
        return {
            "items": items,
            "total": len(items),
            "meta": {
                "source": "historique_achats",
                "scoring": "retard_frequence + fiabilite_historique + contexte_evenementiel",
                "contexte": {
                    "nb_invites": nb_invites,
                    "evenements": evenements or [],
                },
            },
        }

    return await executer_async(_query)


@router.post(
    "/predictions/feedback",
    responses=REPONSES_CRUD_ECRITURE,
    summary="Feedback prediction courses",
)
@gerer_exception_api
async def enregistrer_feedback_prediction_courses(
    payload: FeedbackPredictionCoursesRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ameliore progressivement les predictions via feedback utilisateur (ajout/refus)."""

    def _query() -> dict[str, Any]:
        from src.services.cuisine.prediction_courses import obtenir_service_prediction_courses

        service = obtenir_service_prediction_courses()
        ok = service.enregistrer_feedback(
            article_nom=payload.article_nom,
            accepte=payload.accepte,
        )
        if not ok:
            raise HTTPException(status_code=404, detail="Article historique introuvable")

        return {
            "message": "Feedback enregistre",
            "article_nom": payload.article_nom,
            "accepte": payload.accepte,
        }

    return await executer_async(_query)

