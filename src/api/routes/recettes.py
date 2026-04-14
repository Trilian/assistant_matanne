"""
Routes API pour les recettes.

CRUD complet pour les recettes avec pagination, filtres par catÃ©gorie,
recherche par nom et documentation OpenAPI enrichie.
"""

from datetime import date
from difflib import SequenceMatcher
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas import (
    MessageResponse,
    RecetteCreate,
    RecettePatch,
    RecetteResponse,
    ReponsePaginee,
    normaliser_categorie,
)
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_IA,
    REPONSES_LISTE,
)
from src.api.schemas.ia_transverses import (
    IdeeRepasSoirRequest,
    PatternsAlimentairesResponse,
    SuggestionRepasSoirResponse,
)
from src.api.utils import (
    construire_reponse_paginee,
    executer_async,
    executer_avec_session,
    gerer_exception_api,
)
from src.services.cuisine.service_ia import obtenir_service_innovations_cuisine

router = APIRouter(prefix="/api/v1/recettes", tags=["Recettes"])


@router.post("/idee-repas", response_model=SuggestionRepasSoirResponse, responses=REPONSES_IA)
@gerer_exception_api
async def idee_repas_soir(
    body: IdeeRepasSoirRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
) -> SuggestionRepasSoirResponse:
    """Alias métier de la suggestion dîner express historiquement exposée via /innovations."""
    service = obtenir_service_innovations_cuisine()
    result = service.suggerer_repas_ce_soir(
        temps_disponible_min=body.temps_disponible_min,
        humeur=body.humeur,
    )
    return result or SuggestionRepasSoirResponse()


@router.post("/mange-ce-soir", response_model=SuggestionRepasSoirResponse, responses=REPONSES_IA)
@gerer_exception_api
async def mange_ce_soir(
    body: IdeeRepasSoirRequest,
    user: dict[str, Any] = Depends(require_auth),
    _rate: dict[str, Any] = Depends(verifier_limite_debit_ia),
) -> SuggestionRepasSoirResponse:
    """Alias métier pour suggestion dîner rapide ce soir."""
    service = obtenir_service_innovations_cuisine()
    result = service.suggerer_repas_ce_soir(
        temps_disponible_min=body.temps_disponible_min,
        humeur=body.humeur,
    )
    return result or SuggestionRepasSoirResponse()


@router.get(
    "/patterns-alimentaires", response_model=PatternsAlimentairesResponse, responses=REPONSES_IA
)
@gerer_exception_api
async def obtenir_patterns_alimentaires(
    periode_jours: int = Query(90, ge=30, le=365),
    user: dict[str, Any] = Depends(require_auth),
) -> PatternsAlimentairesResponse:
    """Alias métier pour l'analyse des habitudes alimentaires."""
    service = obtenir_service_innovations_cuisine()
    result = service.analyser_patterns_alimentaires(periode_jours=periode_jours)
    return result or PatternsAlimentairesResponse()


@router.get(
    "/garmin-repas-adaptatif", response_model=SuggestionRepasSoirResponse, responses=REPONSES_IA
)
@gerer_exception_api
async def obtenir_repas_adaptatif_garmin(
    user: dict[str, Any] = Depends(require_auth),
) -> SuggestionRepasSoirResponse:
    """Alias métier pour l'adaptation des repas à la dépense Garmin."""
    service = obtenir_service_innovations_cuisine()
    user_id_raw = user.get("id")
    user_id = (
        int(user_id_raw)
        if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit()
        else None
    )
    result = service.proposer_repas_adapte_garmin(user_id=user_id)
    return result or SuggestionRepasSoirResponse()


@router.post("/fusionner", response_model=RecetteResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def fusionner_recettes(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> Any:
    """Fusionne deux recettes similaires en une seule.

    La recette à garder est conservée (avec son historique, ses ingrédients, ses étapes).
    L'historique de cuisson et les feedbacks de la recette à supprimer sont transférés.
    Les entrées de planning et de batch cooking sont mises à jour.
    La recette à supprimer est ensuite effacée.
    """
    from src.core.models import Recette
    from src.core.models.recettes import HistoriqueRecette
    from src.core.models.planning import Repas
    from src.core.models.batch_cooking import EtapeBatchCooking, PreparationBatch, BatchCookingCongelation
    from src.core.models.user_preferences import RetourRecette

    id_a_garder: int | None = payload.get("id_a_garder")
    id_a_supprimer: int | None = payload.get("id_a_supprimer")
    nouveau_nom: str | None = payload.get("nouveau_nom")

    if not id_a_garder or not id_a_supprimer:
        raise HTTPException(status_code=422, detail="id_a_garder et id_a_supprimer sont obligatoires.")
    if id_a_garder == id_a_supprimer:
        raise HTTPException(status_code=422, detail="Les deux recettes doivent être différentes.")

    def _fusionner() -> dict[str, Any]:
        with executer_avec_session() as session:
            recette_garde = session.get(Recette, id_a_garder)
            recette_supprime = session.get(Recette, id_a_supprimer)

            if not recette_garde:
                raise HTTPException(status_code=404, detail=f"Recette {id_a_garder} introuvable.")
            if not recette_supprime:
                raise HTTPException(status_code=404, detail=f"Recette {id_a_supprimer} introuvable.")

            if nouveau_nom:
                recette_garde.nom = nouveau_nom.strip()

            # 1. Transférer l'historique de cuisson
            session.query(HistoriqueRecette).filter(
                HistoriqueRecette.recette_id == id_a_supprimer
            ).update({"recette_id": id_a_garder}, synchronize_session=False)

            # 2. Transférer les feedbacks (éviter les doublons : on supprime ceux qui existent déjà sur la recette gardée)
            ids_feedbacks_gardes = {
                r.user_id
                for r in session.query(RetourRecette).filter(
                    RetourRecette.recette_id == id_a_garder
                ).all()
            }
            feedbacks_a_transferer = session.query(RetourRecette).filter(
                RetourRecette.recette_id == id_a_supprimer
            ).all()
            for fb in feedbacks_a_transferer:
                if fb.user_id not in ids_feedbacks_gardes:
                    fb.recette_id = id_a_garder
                else:
                    session.delete(fb)

            # 3. Mettre à jour les plannings (4 colonnes nullable)
            for col in ("recette_id", "entree_recette_id", "dessert_recette_id", "dessert_jules_recette_id"):
                session.query(Repas).filter(
                    getattr(Repas, col) == id_a_supprimer
                ).update({col: id_a_garder}, synchronize_session=False)

            # 4. Mettre à jour le batch cooking
            for model in (EtapeBatchCooking, PreparationBatch, BatchCookingCongelation):
                session.query(model).filter(
                    model.recette_id == id_a_supprimer
                ).update({"recette_id": id_a_garder}, synchronize_session=False)

            # 5. Supprimer la recette doublon (CASCADE supprime ses ingrédients, étapes, versions)
            session.delete(recette_supprime)
            session.flush()

            # Invalider le cache du service
            try:
                from src.services.cuisine.recettes.service import obtenir_service_recettes
                svc = obtenir_service_recettes()
                svc._cache.invalider(f"recette_{id_a_garder}")
                svc._cache.invalider(f"recette_{id_a_supprimer}")
            except Exception:
                pass

            session.refresh(recette_garde)

            # Construire la réponse minimale (RecetteResponse)
            ingredients_out = []
            for ri in (recette_garde.ingredients or []):
                if ri.ingredient:
                    ingredients_out.append({
                        "id": ri.ingredient.id,
                        "nom": ri.ingredient.nom,
                        "quantite": ri.quantite,
                        "unite": ri.unite or ri.ingredient.unite,
                        "optionnel": ri.optionnel,
                    })
            etapes_out = [
                {
                    "id": e.id,
                    "ordre": e.ordre,
                    "titre": e.titre,
                    "description": e.description,
                    "duree": e.duree,
                }
                for e in sorted(recette_garde.etapes or [], key=lambda x: x.ordre)
            ]
            return {
                "id": recette_garde.id,
                "nom": recette_garde.nom,
                "description": recette_garde.description,
                "temps_preparation": recette_garde.temps_preparation,
                "temps_cuisson": recette_garde.temps_cuisson,
                "portions": recette_garde.portions,
                "difficulte": recette_garde.difficulte,
                "categorie": recette_garde.categorie,
                "ingredients": ingredients_out,
                "etapes": etapes_out,
                "est_favori": False,
                "url_source": recette_garde.url_source,
                "compatible_cookeo": recette_garde.compatible_cookeo,
                "compatible_airfryer": recette_garde.compatible_airfryer,
                "compatible_monsieur_cuisine": recette_garde.compatible_monsieur_cuisine,
                "jours_depuis_derniere_cuisson": None,
                "calories": recette_garde.calories,
                "proteines": recette_garde.proteines,
                "lipides": recette_garde.lipides,
                "glucides": recette_garde.glucides,
            }

    return await executer_async(_fusionner)


@router.get("/doublons", responses=REPONSES_LISTE)
@gerer_exception_api
async def detecter_doublons_recettes(
    seuil: float = Query(0.72, ge=0.3, le=1.0),
    limite: int = Query(12, ge=1, le=50),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détecte les recettes potentiellement très proches pour éviter les doublons dans la collection."""
    from src.core.models import Recette

    def _normaliser(valeur: str | None) -> str:
        return " ".join((valeur or "").strip().lower().replace("-", " ").split())

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            recettes = session.query(Recette).all()
            doublons: list[dict[str, Any]] = []

            for index, recette_source in enumerate(recettes):
                ingredients_source = {
                    _normaliser(getattr(item.ingredient, "nom", None))
                    for item in (recette_source.ingredients or [])
                    if getattr(item, "ingredient", None)
                    and _normaliser(getattr(item.ingredient, "nom", None))
                }
                nom_source = _normaliser(recette_source.nom)

                for recette_proche in recettes[index + 1 :]:
                    nom_proche = _normaliser(recette_proche.nom)
                    ingredients_proches = {
                        _normaliser(getattr(item.ingredient, "nom", None))
                        for item in (recette_proche.ingredients or [])
                        if getattr(item, "ingredient", None)
                        and _normaliser(getattr(item.ingredient, "nom", None))
                    }

                    score_nom = SequenceMatcher(None, nom_source, nom_proche).ratio()
                    union = ingredients_source | ingredients_proches
                    intersection = ingredients_source & ingredients_proches
                    score_ingredients = (len(intersection) / len(union)) if union else 0.0
                    score = round((score_nom * 0.68) + (score_ingredients * 0.32), 2)

                    if score < seuil:
                        continue

                    raisons: list[str] = []
                    if score_nom >= 0.78:
                        raisons.append("Nom très proche")
                    if len(intersection) >= 2 or score_ingredients >= 0.45:
                        raisons.append("Base d'ingrédients similaire")
                    if not raisons:
                        raisons.append("Structure globale voisine")

                    doublons.append(
                        {
                            "recette_source": {"id": recette_source.id, "nom": recette_source.nom},
                            "recette_proche": {"id": recette_proche.id, "nom": recette_proche.nom},
                            "score_similarite": score,
                            "raisons": raisons,
                            "ingredients_communs": sorted(intersection)[:5],
                        }
                    )

            doublons = sorted(
                doublons,
                key=lambda item: (
                    item.get("score_similarite", 0),
                    item.get("recette_source", {}).get("nom", ""),
                ),
                reverse=True,
            )
            return {"items": doublons[:limite], "total": len(doublons), "seuil": seuil}

    return await executer_async(_query)


@router.get("/{recette_id:int}/export-pdf", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def exporter_recette_pdf(
    recette_id: int,
    user: dict[str, Any] = Depends(require_auth),
):
    """Exporte une recette en PDF."""
    from src.services.rapports.export import obtenir_service_export_pdf

    def _generate():
        service = obtenir_service_export_pdf()
        return service.exporter_recette(recette_id)

    buffer = await executer_async(_generate)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="recette_{recette_id}.pdf"',
        },
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPERS INTERNES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _sauvegarder_ingredients(session, recette_id: int, ingredients: list) -> None:
    """Persiste les RecetteIngredient en trouvant/crÃ©ant les Ingredient de rÃ©fÃ©rence."""
    from src.core.models import Ingredient, RecetteIngredient

    for idx, ing in enumerate(ingredients, start=1):
        nom = ing.nom.strip()
        if not nom:
            continue

        # Find or create l'ingrÃ©dient de rÃ©fÃ©rence
        db_ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()
        if not db_ingredient:
            db_ingredient = Ingredient(nom=nom, unite=ing.unite or "piÃ¨ce")
            session.add(db_ingredient)
            session.flush()

        session.add(
            RecetteIngredient(
                recette_id=recette_id,
                ingredient_id=db_ingredient.id,
                quantite=ing.quantite or 1,
                unite=ing.unite or db_ingredient.unite,
            )
        )


def _sauvegarder_etapes(session, recette_id: int, instructions: list[str]) -> None:
    """Persiste les EtapeRecette depuis une liste de descriptions."""
    from src.core.models import EtapeRecette

    for idx, text in enumerate(instructions, start=1):
        text = text.strip()
        if not text:
            continue
        session.add(
            EtapeRecette(
                recette_id=recette_id,
                ordre=idx,
                description=text,
            )
        )


def _serialiser_recette(db_recette, session, user: dict) -> RecetteResponse:
    """SÃ©rialise une Recette ORM en RecetteResponse avec relations."""
    from sqlalchemy import func as sql_func

    from src.core.models import HistoriqueRecette, RecetteIngredient
    from src.core.models.user_preferences import RetourRecette

    # Charger ingrÃ©dients avec le nom depuis la table Ingredient
    ingredients_resp = []
    for ri in db_recette.ingredients:
        ingredients_resp.append(
            {
                "id": ri.id,
                "nom": ri.ingredient.nom if ri.ingredient else "?",
                "quantite": ri.quantite,
                "unite": ri.unite,
                "optionnel": ri.optionnel,
            }
        )

    # Charger Ã©tapes
    etapes_resp = [
        {
            "id": e.id,
            "ordre": e.ordre,
            "description": e.description,
            "titre": e.titre,
            "duree": e.duree,
        }
        for e in sorted(db_recette.etapes, key=lambda e: e.ordre)
    ]

    # VÃ©rifier favori (feedback == 'like' dans RetourRecette)
    user_id = user.get("sub", user.get("id", "dev"))
    retour = (
        session.query(RetourRecette)
        .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == db_recette.id)
        .first()
    )
    est_favori = retour.feedback == "like" if retour else False

    derniere_cuisson = (
        session.query(sql_func.max(HistoriqueRecette.date_preparation))
        .filter(HistoriqueRecette.recette_id == db_recette.id)
        .scalar()
    )
    jours_depuis_derniere_cuisson = None
    if derniere_cuisson:
        jours_depuis_derniere_cuisson = (date.today() - derniere_cuisson).days

    return RecetteResponse(
        id=db_recette.id,
        nom=db_recette.nom,
        description=db_recette.description,
        temps_preparation=db_recette.temps_preparation,
        temps_cuisson=db_recette.temps_cuisson,
        portions=db_recette.portions,
        difficulte=db_recette.difficulte,
        categorie=db_recette.categorie,
        ingredients=ingredients_resp,
        etapes=etapes_resp,
        est_favori=est_favori,
        genere_par_ia=getattr(db_recette, "genere_par_ia", False) or False,
        url_source=getattr(db_recette, "url_source", None),
        image_url=getattr(db_recette, "url_image", None),
        compatible_cookeo=db_recette.compatible_cookeo,
        compatible_monsieur_cuisine=db_recette.compatible_monsieur_cuisine,
        compatible_airfryer=db_recette.compatible_airfryer,
        instructions_cookeo=db_recette.instructions_cookeo,
        instructions_monsieur_cuisine=db_recette.instructions_monsieur_cuisine,
        instructions_airfryer=db_recette.instructions_airfryer,
        jours_depuis_derniere_cuisson=jours_depuis_derniere_cuisson,
        calories=getattr(db_recette, "calories", None),
        proteines=getattr(db_recette, "proteines", None),
        lipides=getattr(db_recette, "lipides", None),
        glucides=getattr(db_recette, "glucides", None),
    )


@router.get("", response_model=ReponsePaginee[RecetteResponse], responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_recettes(
    page: int = Query(1, ge=1, description="NumÃ©ro de page (1-indexÃ©)"),
    page_size: int = Query(20, ge=1, le=100, description="Nombre d'Ã©lÃ©ments par page"),
    categorie: str | None = Query(
        None, description="Filtrer par catÃ©gorie (plat, dessert, entrÃ©e...)"
    ),
    search: str | None = Query(None, description="Recherche dans le nom de la recette"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les recettes avec pagination et filtres.

    Retourne une liste paginÃ©e de recettes avec possibilitÃ© de filtrer
    par catÃ©gorie ou de rechercher par nom.

    Args:
        page: NumÃ©ro de page (dÃ©faut: 1)
        page_size: Taille de page (dÃ©faut: 20, max: 100)
        categorie: Filtre optionnel par catÃ©gorie
        search: Recherche partielle dans le nom

    Returns:
        RÃ©ponse paginÃ©e avec items, total, pages

    Example:
        ```
        GET /api/v1/recettes?categorie=dessert&page_size=10

        Response:
        {
            "items": [{"id": 1, "nom": "Tarte aux pommes", ...}],
            "total": 42,
            "page": 1,
            "page_size": 10,
            "pages": 5
        }
        ```
    """

    from src.core.models import Recette
    from src.core.models.recettes import HistoriqueRecette

    def _query():
        with executer_avec_session() as session:
            query = session.query(Recette)

            if categorie:
                query = query.filter(func.lower(Recette.categorie) == categorie.lower())

            if search:
                # Ã‰chapper les caractÃ¨res spÃ©ciaux SQL wildcard pour Ã©viter l'injection
                safe_search = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(Recette.nom.ilike(f"%{safe_search}%"))

            total = query.count()
            items = (
                query.order_by(Recette.nom).offset((page - 1) * page_size).limit(page_size).all()
            )

            historiques = (
                session.query(
                    HistoriqueRecette.recette_id,
                    func.max(HistoriqueRecette.date_preparation).label("derniere_cuisson"),
                )
                .group_by(HistoriqueRecette.recette_id)
                .all()
            )
            historique_par_recette = {
                recette_id: derniere_cuisson for recette_id, derniere_cuisson in historiques
            }

            # Favoris de l'utilisateur courant (une seule requête IN)
            from src.core.models.user_preferences import RetourRecette

            user_id = user.get("sub", user.get("id", "dev"))
            ids_items = [r.id for r in items]
            favoris_ids: set[int] = set()
            if ids_items:
                retours = (
                    session.query(RetourRecette.recette_id)
                    .filter(
                        RetourRecette.user_id == user_id,
                        RetourRecette.recette_id.in_(ids_items),
                        RetourRecette.feedback == "like",
                    )
                    .all()
                )
                favoris_ids = {row.recette_id for row in retours}

            # Sérialisation basique (sans relations) pour la liste
            items_dicts = [
                {
                    "id": r.id,
                    "nom": r.nom,
                    "description": r.description,
                    "temps_preparation": r.temps_preparation,
                    "temps_cuisson": r.temps_cuisson,
                    "portions": r.portions,
                    "difficulte": r.difficulte,
                    "categorie": r.categorie,
                    "est_favori": r.id in favoris_ids,
                    "genere_par_ia": getattr(r, "genere_par_ia", False) or False,
                    "compatible_cookeo": r.compatible_cookeo,
                    "compatible_monsieur_cuisine": r.compatible_monsieur_cuisine,
                    "compatible_airfryer": r.compatible_airfryer,
                    "jours_depuis_derniere_cuisson": (
                        (date.today() - historique_par_recette[r.id]).days
                        if historique_par_recette.get(r.id)
                        else None
                    ),
                }
                for r in items
            ]

            return construire_reponse_paginee(items_dicts, total, page, page_size)

    return await executer_async(_query)


@router.get("/{recette_id:int}", response_model=RecetteResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_recette(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    RÃ©cupÃ¨re une recette par son ID.

    Args:
        recette_id: Identifiant unique de la recette

    Returns:
        DÃ©tail complet de la recette

    Raises:
        404: Recette non trouvÃ©e

    Example:
        ```
        GET /api/v1/recettes/42

        Response:
        {
            "id": 42,
            "nom": "Poulet rÃ´ti",
            "description": "Un classique familial",
            "temps_preparation": 15,
            "temps_cuisson": 60,
            "portions": 4,
            "difficulte": "facile",
            "categorie": "plat"
        }
        ```
    """
    from sqlalchemy.orm import joinedload

    from src.core.models import Recette

    def _query():
        with executer_avec_session() as session:
            recette = (
                session.query(Recette)
                .options(
                    joinedload(Recette.ingredients),
                    joinedload(Recette.etapes),
                )
                .filter(Recette.id == recette_id)
                .first()
            )

            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            return _serialiser_recette(recette, session, user)

    return await executer_async(_query)


@router.post("", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_recette(donnees: RecetteCreate, user: dict[str, Any] = Depends(require_auth)):
    """
    CrÃ©e une nouvelle recette avec ses ingrÃ©dients et Ã©tapes.

    Args:
        recette: DonnÃ©es de la recette (nom, ingrÃ©dients, instructions...)

    Returns:
        La recette crÃ©Ã©e avec ses ingrÃ©dients et Ã©tapes

    Example:
        ```
        POST /api/v1/recettes
        Body:
        {
            "nom": "Gratin dauphinois",
            "description": "Pommes de terre gratinÃ©es",
            "temps_preparation": 20,
            "temps_cuisson": 45,
            "portions": 6,
            "difficulte": "facile",
            "categorie": "accompagnement",
            "ingredients": [
                {"nom": "Pommes de terre", "quantite": 1, "unite": "kg"},
                {"nom": "CrÃ¨me fraÃ®che", "quantite": 30, "unite": "cl"}
            ],
            "instructions": ["Ã‰plucher les pommes de terre", "PrÃ©chauffer le four Ã  180Â°C"]
        }
        ```
    """
    from src.core.models import EtapeRecette, Ingredient, Recette, RecetteIngredient

    def _create():
        with executer_avec_session() as session:
            db_recette = Recette(
                nom=donnees.nom,
                description=donnees.description,
                temps_preparation=donnees.temps_preparation,
                temps_cuisson=donnees.temps_cuisson,
                portions=donnees.portions,
                difficulte=donnees.difficulte,
                categorie=donnees.categorie,
            )
            session.add(db_recette)
            session.flush()

            _sauvegarder_ingredients(session, db_recette.id, donnees.ingredients)
            _sauvegarder_etapes(session, db_recette.id, donnees.instructions)

            session.commit()
            session.refresh(db_recette)

            return _serialiser_recette(db_recette, session, user)

    return await executer_async(_create)


@router.put("/{recette_id}", response_model=RecetteResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_recette(
    recette_id: int, donnees: RecetteCreate, user: dict[str, Any] = Depends(require_auth)
):
    """Met Ã  jour une recette complÃ¨tement (remplacement total).

    Remplace tous les champs de la recette par les valeurs fournies.
    Pour une mise Ã  jour partielle, utiliser PATCH.

    Args:
        recette_id: ID de la recette Ã  modifier
        recette: Tous les champs de la recette (remplacement complet)

    Returns:
        La recette mise Ã  jour

    Raises:
        401: Non authentifiÃ©
        404: Recette non trouvÃ©e
        422: DonnÃ©es invalides

    Example:
        ```
        PUT /api/v1/recettes/42
        Authorization: Bearer <token>

        Body: {"nom": "Poulet rÃ´ti aux herbes", "temps_cuisson": 75}

        Response:
        {"id": 42, "nom": "Poulet rÃ´ti aux herbes", "temps_cuisson": 75, ...}
        ```
    """
    from src.core.models import EtapeRecette, Recette, RecetteIngredient

    def _update():
        with executer_avec_session() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvÃ©e")

            for key, value in donnees.model_dump(
                exclude={"ingredients", "instructions", "tags"}
            ).items():
                if hasattr(db_recette, key):
                    setattr(db_recette, key, value)

            # Remplacer ingrÃ©dients et Ã©tapes
            session.query(RecetteIngredient).filter(
                RecetteIngredient.recette_id == recette_id
            ).delete()
            session.query(EtapeRecette).filter(EtapeRecette.recette_id == recette_id).delete()

            _sauvegarder_ingredients(session, recette_id, donnees.ingredients)
            _sauvegarder_etapes(session, recette_id, donnees.instructions)

            session.commit()
            session.refresh(db_recette)

            return _serialiser_recette(db_recette, session, user)

    return await executer_async(_update)


@router.patch("/{recette_id}", response_model=RecetteResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_partiellement_recette(
    recette_id: int, maj: RecettePatch, user: dict[str, Any] = Depends(require_auth)
):
    """Mise Ã  jour partielle d'une recette.

    Seuls les champs fournis dans le body sont modifiÃ©s.
    Les champs absents ou ``null`` restent inchangÃ©s.

    Args:
        recette_id: ID de la recette Ã  modifier
        patch: Champs Ã  mettre Ã  jour (tous optionnels)

    Returns:
        La recette mise Ã  jour

    Raises:
        401: Non authentifiÃ©
        404: Recette non trouvÃ©e
        422: DonnÃ©es invalides

    Example:
        ```
        PATCH /api/v1/recettes/42
        Authorization: Bearer <token>

        Body: {"nom": "Poulet rÃ´ti aux herbes", "temps_cuisson": 75}

        Response:
        {"id": 42, "nom": "Poulet rÃ´ti aux herbes", "temps_cuisson": 75, ...}
        ```
    """
    from src.core.models import EtapeRecette, Recette, RecetteIngredient

    def _patch():
        with executer_avec_session() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvÃ©e")

            donnees = maj.model_dump(exclude_unset=True)
            if not donnees:
                raise HTTPException(
                    status_code=422,
                    detail="Aucun champ à mettre à jour fourni",
                )

            ingredients_data = donnees.pop("ingredients", None)
            instructions_data = donnees.pop("instructions", None)
            donnees.pop("tags", None)

            for key, value in donnees.items():
                if hasattr(db_recette, key):
                    setattr(db_recette, key, value)

            if ingredients_data is not None:
                session.query(RecetteIngredient).filter(
                    RecetteIngredient.recette_id == recette_id
                ).delete()
                from src.api.schemas.recettes import IngredientItem

                items = [
                    IngredientItem(**i) if isinstance(i, dict) else i for i in ingredients_data
                ]
                _sauvegarder_ingredients(session, recette_id, items)

            if instructions_data is not None:
                session.query(EtapeRecette).filter(EtapeRecette.recette_id == recette_id).delete()
                _sauvegarder_etapes(session, recette_id, instructions_data)

            session.commit()
            session.refresh(db_recette)

            return _serialiser_recette(db_recette, session, user)

    return await executer_async(_patch)


@router.delete("/{recette_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_recette(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Supprime une recette.

    Args:
        recette_id: ID de la recette à supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Recette non trouvée

    Example:
        ```
        DELETE /api/v1/recettes/42
        Authorization: Bearer <token>

        Response:
        {"message": "Recette 42 supprimée", "id": 42}
        ```
    """
    from src.core.models import Recette

    def _delete():
        with executer_avec_session() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            session.delete(db_recette)
            session.commit()

            return MessageResponse(message=f"Recette {recette_id} supprimée", id=recette_id)

    return await executer_async(_delete)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PLANIFICATION "CETTE SEMAINE"
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@router.get("/planifiees-semaine", response_model=list[RecetteResponse])
@gerer_exception_api
async def lister_recettes_semaine(user: dict[str, Any] = Depends(require_auth)):
    """Liste les recettes marquÃ©es 'Ã  faire cette semaine'."""
    from src.core.models import Recette
    from src.core.models.user_preferences import RetourRecette

    def _query():
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            rows = (
                session.query(Recette)
                .join(RetourRecette, RetourRecette.recette_id == Recette.id)
                .filter(
                    RetourRecette.user_id == user_id,
                    RetourRecette.planifie_cette_semaine.is_(True),
                )
                .all()
            )
            return [_serialiser_recette(r, session, user) for r in rows]

    return await executer_async(_query)


@router.get("/saisonnieres", responses=REPONSES_LISTE)
@gerer_exception_api
async def recettes_saisonnieres(
    mois: int = Query(0, ge=0, le=12, description="Mois (1-12). 0 = mois courant"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les recettes dont les ingrédients principaux sont de saison (11.5).

    Croise les ingrédients des recettes avec le calendrier saisonnier
    et retourne les recettes triées par score de saisonnalité.
    """
    import json
    from pathlib import Path

    from src.core.models.recettes import Recette, RecetteIngredient

    mois_cible = mois if mois > 0 else date.today().month
    fichier = Path(__file__).resolve().parents[3] / "data" / "reference" / "produits_de_saison.json"

    def _query():
        # Charger produits de saison
        produits_saison: set[str] = set()
        if fichier.exists():
            data = json.loads(fichier.read_text(encoding="utf-8"))
            for p in data.get("produits", []):
                if mois_cible in p.get("mois", []):
                    produits_saison.add(p["nom"].lower())

        with executer_avec_session() as session:
            recettes = session.query(Recette).all()
            scored: list[tuple[Any, int, int]] = []

            for r in recettes:
                ingredients = (
                    session.query(RecetteIngredient)
                    .filter(RecetteIngredient.recette_id == r.id)
                    .all()
                )
                nb_total = len(ingredients)
                if nb_total == 0:
                    continue
                nb_saison = sum(
                    1
                    for ing in ingredients
                    if any(ps in (ing.ingredient.nom or "").lower() for ps in produits_saison)
                )
                if nb_saison > 0:
                    scored.append((r, nb_saison, nb_total))

            # Trier par ratio saisonnier décroissant
            scored.sort(key=lambda x: x[1] / x[2], reverse=True)

            total = len(scored)
            start = (page - 1) * page_size
            page_items = scored[start : start + page_size]

            return {
                "items": [
                    {
                        **_serialiser_recette(r, session, user).model_dump(),
                        "nb_ingredients_saison": nb_s,
                        "nb_ingredients_total": nb_t,
                        "score_saison": round(nb_s / nb_t * 100),
                    }
                    for r, nb_s, nb_t in page_items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages_totales": (total + page_size - 1) // page_size,
                "mois": mois_cible,
                "produits_saison": sorted(produits_saison)[:20],
            }

    return await executer_async(_query)


@router.get("/calendrier-saisonnier", responses=REPONSES_LISTE)
@gerer_exception_api
async def calendrier_saisonnier() -> dict[str, Any]:
    """Calendrier visuel des produits de saison par mois (C1).

    Retourne le catalogue enrichi d'ingrédients de saison avec
    catégories, mois de pic, paires classiques et mois courant.
    """
    from src.services.cuisine.suggestions.saisons_enrichi import (
        INGREDIENTS_SAISON_ENRICHI,
        PAIRES_SAISON,
        obtenir_saison,
    )

    mois_courant = date.today().month
    saison_courante = obtenir_saison()

    # Construire la vue par mois (1-12)
    mois_noms = [
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]

    calendrier = []
    for mois in range(1, 13):
        ingredients_mois = []
        for _saison, items in INGREDIENTS_SAISON_ENRICHI.items():
            for ing in items:
                if mois in ing.pic_mois:
                    ingredients_mois.append(
                        {
                            "nom": ing.nom,
                            "categorie": ing.categorie,
                            "bio_local": ing.bio_local_courant,
                        }
                    )
        calendrier.append(
            {
                "mois": mois,
                "nom": mois_noms[mois],
                "ingredients": ingredients_mois,
            }
        )

    paires = [
        {
            "ingredients": p.ingredients,
            "description": p.description,
            "saison": p.saison,
        }
        for p in PAIRES_SAISON
    ]

    return {
        "mois_courant": mois_courant,
        "saison_courante": saison_courante,
        "calendrier": calendrier,
        "paires_saison": paires,
    }


@router.get("/depuis-jardin", response_model=dict, responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_recettes_depuis_jardin(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggère des recettes basées sur les récoltes disponibles du jardin (IM2).

    Récupère les récoltes proches du jardin et suggère des recettes qui utilisent
    ces ingrédients. Idéal pour cuisiner avec les produits frais disponibles.

    Returns:
        Dict avec liste des récoltes et recettes suggérées compatibles
    """
    from src.services.cuisine.suggestions import obtenir_service_suggestions
    from src.services.maison import obtenir_jardin_service

    def _get_suggestions():
        with executer_avec_session() as session:
            service_jardin = obtenir_jardin_service()
            recoltes = service_jardin.obtenir_recoltes_proches()

            ingredients_disponibles = [
                {
                    "nom": r.nom if hasattr(r, "nom") else str(r),
                    "date": str(getattr(r, "date_recolte_prevue", "")),
                    "quantite_kg": getattr(r, "quantite_disponible_kg", 1),
                }
                for r in recoltes
            ]

            service_suggestions = obtenir_service_suggestions()
            suggestions = service_suggestions.suggerer_recettes(
                contexte=None,
                nb_suggestions=5,
                session=session,
            )

            return {
                "recoltes": ingredients_disponibles,
                "recettes_suggerees": [
                    {
                        "id": s.recette_id,
                        "nom": s.nom,
                        "score": round(s.score, 2),
                        "raison": s.raison,
                        "temps_preparation": s.temps_preparation,
                    }
                    for s in suggestions[:5]
                ],
                "nb_recoltes": len(ingredients_disponibles),
                "nb_suggestions": min(5, len(suggestions)),
            }

    return await executer_async(_get_suggestions)


@router.post("/{recette_id}/planifier-semaine", response_model=MessageResponse)
@gerer_exception_api
async def planifier_recette_semaine(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Marque une recette comme 'Ã  faire cette semaine'."""
    from datetime import datetime

    from src.core.models import Recette
    from src.core.models.user_preferences import RetourRecette

    def _upsert():
        with executer_avec_session() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvÃ©e")

            user_id = user.get("sub", user.get("id", "dev"))
            retour = (
                session.query(RetourRecette)
                .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == recette_id)
                .first()
            )
            if retour:
                retour.planifie_cette_semaine = True
                retour.date_planifie = datetime.utcnow()
            else:
                retour = RetourRecette(
                    user_id=user_id,
                    recette_id=recette_id,
                    planifie_cette_semaine=True,
                    date_planifie=datetime.utcnow(),
                )
                session.add(retour)
            session.commit()
            return MessageResponse(message=f"Recette {recette_id} planifiÃ©e cette semaine")

    return await executer_async(_upsert)


@router.delete("/{recette_id}/planifier-semaine", response_model=MessageResponse)
@gerer_exception_api
async def deplanifier_recette_semaine(
    recette_id: int, user: dict[str, Any] = Depends(require_auth)
):
    """Retire une recette de la liste 'cette semaine'."""
    from src.core.models.user_preferences import RetourRecette

    def _clear():
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            retour = (
                session.query(RetourRecette)
                .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == recette_id)
                .first()
            )
            if retour:
                retour.planifie_cette_semaine = False
                retour.date_planifie = None
                session.commit()
            return MessageResponse(message=f"Recette {recette_id} retirÃ©e de cette semaine")

    return await executer_async(_clear)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# IMPORT DE RECETTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/import-url", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def importer_recette_url(
    url: str = Query(..., description="URL de la recette Ã  importer"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Importe une recette depuis une URL.

    Supporte les sites populaires (Marmiton, CuisineAZ, etc.) ainsi que
    les pages gÃ©nÃ©riques via extraction IA.

    Args:
        url: URL complÃ¨te de la recette
        user: Utilisateur authentifiÃ©

    Returns:
        Recette crÃ©Ã©e avec donnÃ©es importÃ©es

    Raises:
        HTTPException 422: URL invalide ou recette non trouvÃ©e
        HTTPException 500: Erreur lors de l'import
    """
    from src.core.models import Recette
    from src.services.cuisine.recettes.enrichers import (
        ImportedIngredient,
        ImportedRecipe,
        get_recipe_enricher,
    )
    from src.services.cuisine.recettes.import_url import obtenir_recipe_import_service

    def _import():
        # Import via service
        import_service = obtenir_recipe_import_service()
        result = import_service.import_from_url(url, use_ai_fallback=True)

        if not result.success:
            raise HTTPException(
                status_code=422, detail=f"Impossible d'importer la recette: {result.error}"
            )

        recipe_data = result.recipe

        # Convertir en ImportedRecipe pour enrichissement
        imported_recipe = ImportedRecipe(
            nom=recipe_data.nom,
            description=recipe_data.description or "",
            temps_preparation=recipe_data.temps_preparation or 0,
            temps_cuisson=recipe_data.temps_cuisson or 0,
            portions=recipe_data.portions or 4,
            ingredients=[
                ImportedIngredient(
                    nom=ing.nom,
                    quantite=ing.quantite,
                    unite=ing.unite,
                )
                for ing in (recipe_data.ingredients or [])
                if ing.nom
            ],
            etapes=recipe_data.etapes or [],
        )

        # Enrichir automatiquement
        enricher = get_recipe_enricher()
        enrichment = enricher.enrich(imported_recipe)

        # CrÃ©er la recette en DB
        with executer_avec_session() as session:
            # CrÃ©er recette principale avec enrichissement
            recette = Recette(
                nom=recipe_data.nom,
                description=recipe_data.description,
                temps_preparation=recipe_data.temps_preparation or 0,
                temps_cuisson=recipe_data.temps_cuisson or 0,
                portions=recipe_data.portions or 4,
                difficulte=getattr(recipe_data, "niveau", "moyen") or "moyen",
                categorie=normaliser_categorie(recipe_data.categorie),
                saison="toute_annÃ©e",
                genere_par_ia=True,
                # Enrichissement nutrition
                calories=enrichment.calories,
                proteines=enrichment.proteines,
                lipides=enrichment.lipides,
                glucides=enrichment.glucides,
                # Tags bio/local
                est_bio=enrichment.est_bio,
                est_local=enrichment.est_local,
                # Tags auto
                est_rapide=enrichment.est_rapide,
                compatible_batch=enrichment.compatible_batch,
                congelable=enrichment.congelable,
                compatible_bebe=enrichment.compatible_bebe,
                # Robots
                compatible_cookeo=enrichment.compatible_cookeo,
                compatible_airfryer=enrichment.compatible_airfryer,
                compatible_monsieur_cuisine=enrichment.compatible_monsieur_cuisine,
                # Source et image
                url_source=recipe_data.source_url or None,
                url_image=recipe_data.image_url or None,
            )
            session.add(recette)
            session.flush()

            # Ajouter ingrÃ©dients via helper (find-or-create Ingredient + RecetteIngredient)
            from src.api.schemas.recettes import IngredientItem

            ing_items = [
                IngredientItem(
                    nom=ing_data.nom,
                    quantite=ing_data.quantite or 1,
                    unite=ing_data.unite or "pièce",
                )
                for ing_data in (recipe_data.ingredients or [])
                if ing_data.nom
            ]
            _sauvegarder_ingredients(session, recette.id, ing_items)

            # Ajouter Ã©tapes
            _sauvegarder_etapes(session, recette.id, recipe_data.etapes or [])

            session.commit()
            session.refresh(recette)

            return _serialiser_recette(recette, session, user)

    return await executer_async(_import)


@router.post("/import-lot", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def importer_recettes_lot(
    urls: list[str] = Query(..., description="Liste d'URLs de recettes à importer"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Importe plusieurs recettes en lot depuis une liste d'URLs."""

    resultats = []
    for url in urls[:10]:
        try:
            recette = await importer_recette_url(url=url, user=user)
            resultats.append(
                {
                    "url": url,
                    "succes": True,
                    "recette_id": recette.id,
                    "nom": recette.nom,
                }
            )
        except HTTPException as exc:
            resultats.append(
                {
                    "url": url,
                    "succes": False,
                    "erreur": exc.detail,
                }
            )

    return {
        "total": len(resultats),
        "importees": sum(1 for r in resultats if r["succes"]),
        "echouees": sum(1 for r in resultats if not r["succes"]),
        "resultats": resultats,
    }


@router.post("/import-pdf", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def importer_recette_pdf(
    file: UploadFile,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Importe une recette depuis un fichier PDF.

    Utilise PyPDF2 pour extraire le texte et l'enrichit automatiquement
    (nutrition, bio/local, classification, robots).

    Args:
        file: Fichier PDF uploadÃ©
        user: Utilisateur authentifiÃ©

    Returns:
        Recette crÃ©Ã©e avec donnÃ©es extraites et enrichies

    Raises:
        HTTPException 422: Fichier invalide ou non PDF
        HTTPException 500: Erreur lors de l'extraction
    """
    import tempfile
    from pathlib import Path

    from src.core.models import Recette
    from src.services.cuisine.recettes.enrichers import (
        ImportedIngredient,
        ImportedRecipe,
        get_recipe_enricher,
    )
    from src.services.cuisine.recettes.importer import RecipeImporter

    def _import():
        # VÃ©rifier type de fichier
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=422, detail="Seuls les fichiers PDF sont acceptÃ©s")

        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        try:
            # Extraire avec PyPDF2
            raw_data = RecipeImporter.from_pdf(tmp_path)

            if not raw_data or not raw_data.get("nom"):
                raise HTTPException(
                    status_code=422, detail="Impossible d'extraire une recette du PDF"
                )

            # Convertir en ImportedRecipe pour l'enrichissement
            # Les ingrÃ©dients sont des strings simples, on parse basiquement
            imported_ingredients = []
            for ing_str in raw_data.get("ingredients", []):
                # Pattern simple: "250g farine" -> 250, g, farine
                import re

                match = re.match(r"(\d+(?:\.\d+)?)\s*([a-z]+)?\s*(.+)", ing_str.strip())
                if match:
                    qty, unit, name = match.groups()
                    imported_ingredients.append(
                        ImportedIngredient(
                            nom=name.strip(),
                            quantite=float(qty),
                            unite=unit or "piÃ¨ce",
                        )
                    )
                else:
                    # Pas de quantitÃ© dÃ©tectÃ©e, juste le nom
                    imported_ingredients.append(ImportedIngredient(nom=ing_str.strip()))

            recipe = ImportedRecipe(
                nom=raw_data.get("nom", "Recette PDF"),
                description=raw_data.get("description", ""),
                temps_preparation=raw_data.get("temps_preparation", 0),
                temps_cuisson=raw_data.get("temps_cuisson", 0),
                portions=raw_data.get("portions", 4),
                ingredients=imported_ingredients,
                etapes=raw_data.get("etapes", []),
            )

            # Enrichir la recette
            enricher = get_recipe_enricher()
            enrichment = enricher.enrich(recipe)

            # CrÃ©er en DB
            with executer_avec_session() as session:
                recette = Recette(
                    nom=recipe.nom,
                    description=recipe.description,
                    temps_preparation=recipe.temps_preparation,
                    temps_cuisson=recipe.temps_cuisson,
                    portions=recipe.portions,
                    difficulte="moyen",
                    categorie=normaliser_categorie(getattr(recipe, "categorie", None)),
                    saison="toute_annÃ©e",
                    genere_par_ia=False,
                    # Enrichissement nutrition
                    calories=enrichment.calories,
                    proteines=enrichment.proteines,
                    lipides=enrichment.lipides,
                    glucides=enrichment.glucides,
                    # Tags bio/local
                    est_bio=enrichment.est_bio,
                    est_local=enrichment.est_local,
                    # Tags auto
                    est_rapide=enrichment.est_rapide,
                    compatible_batch=enrichment.compatible_batch,
                    congelable=enrichment.congelable,
                    compatible_bebe=enrichment.compatible_bebe,
                    # Robots
                    compatible_cookeo=enrichment.compatible_cookeo,
                    compatible_airfryer=enrichment.compatible_airfryer,
                    compatible_monsieur_cuisine=enrichment.compatible_monsieur_cuisine,
                )
                session.add(recette)
                session.flush()

                # IngrÃ©dients
                from src.api.schemas.recettes import IngredientItem

                ing_items = [
                    IngredientItem(
                        nom=ing.nom,
                        quantite=ing.quantite or 1,
                        unite=ing.unite or "piÃ¨ce",
                    )
                    for ing in recipe.ingredients
                ]
                _sauvegarder_ingredients(session, recette.id, ing_items)

                # Ã‰tapes
                _sauvegarder_etapes(session, recette.id, recipe.etapes)

                session.commit()
                session.refresh(recette)

                return _serialiser_recette(recette, session, user)

        finally:
            # Nettoyer le fichier temporaire
            Path(tmp_path).unlink(missing_ok=True)

    return await executer_async(_import)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FAVORIS & NOTATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/{recette_id}/favori", response_model=MessageResponse)
@gerer_exception_api
async def ajouter_favori(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Ajoute une recette aux favoris (feedback = 'like')."""
    from src.core.models import Recette
    from src.core.models.user_preferences import RetourRecette

    def _upsert():
        with executer_avec_session() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvÃ©e")

            user_id = user.get("sub", user.get("id", "dev"))
            retour = (
                session.query(RetourRecette)
                .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == recette_id)
                .first()
            )
            if retour:
                retour.feedback = "like"
            else:
                retour = RetourRecette(user_id=user_id, recette_id=recette_id, feedback="like")
                session.add(retour)
            session.commit()
            from src.services.core.event_bus_mixin import emettre_evenement_simple

            emettre_evenement_simple(
                "recette.feedback",
                {
                    "recette_id": recette_id,
                    "user_id": str(user_id),
                    "feedback": "like",
                },
                source="api.recettes",
            )
            return MessageResponse(message=f"Recette {recette_id} ajoutÃ©e aux favoris")

    return await executer_async(_upsert)


@router.delete("/{recette_id}/favori", response_model=MessageResponse)
@gerer_exception_api
async def retirer_favori(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Retire une recette des favoris (feedback = 'neutral')."""
    from src.core.models.user_preferences import RetourRecette

    def _remove():
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            retour = (
                session.query(RetourRecette)
                .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == recette_id)
                .first()
            )
            if retour:
                retour.feedback = "neutral"
                session.commit()
                from src.services.core.event_bus_mixin import emettre_evenement_simple

                emettre_evenement_simple(
                    "recette.feedback",
                    {
                        "recette_id": recette_id,
                        "user_id": str(user_id),
                        "feedback": "neutral",
                    },
                    source="api.recettes",
                )
            return MessageResponse(message=f"Recette {recette_id} retirÃ©e des favoris")

    return await executer_async(_remove)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENRICHISSEMENT NUTRITIONNEL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/{recette_id}/enrichir-nutrition")
@gerer_exception_api
async def enrichir_nutrition_recette(
    recette_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enrichit une recette avec les donnÃ©es nutritionnelles via OpenFoodFacts."""
    from src.services.cuisine.nutrition import obtenir_service_nutrition

    def _enrichir():
        service = obtenir_service_nutrition()
        resultat = service.enrichir_recette(recette_id)
        if not resultat:
            raise HTTPException(
                status_code=404,
                detail="Impossible d'enrichir cette recette (ingrÃ©dients manquants ou non trouvÃ©s)",
            )
        return resultat

    return await executer_async(_enrichir)


@router.post("/enrichir-nutrition-batch")
@gerer_exception_api
async def enrichir_nutrition_batch(
    limite: int = Query(50, ge=1, le=200, description="Nombre max de recettes Ã  traiter"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enrichit en batch les recettes sans donnÃ©es nutritionnelles."""
    from src.services.cuisine.nutrition import obtenir_service_nutrition

    def _batch():
        service = obtenir_service_nutrition()
        return service.enrichir_batch(limite=limite)

    return await executer_async(_batch)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VERSION JULES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•



# ═══════════════════════════════════════════════════════════
# ENRICHISSEMENT DES INSTRUCTIONS (étapes + ingrédients via IA)
# ═══════════════════════════════════════════════════════════


@router.post("/{recette_id}/enrichir-instructions")
@gerer_exception_api
async def enrichir_instructions_recette(
    recette_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère via l'IA les étapes de préparation et les ingrédients d'une recette stub."""
    from src.services.cuisine.planning import obtenir_service_planning

    def _enrichir():
        service = obtenir_service_planning()
        count = service.enrichir_recettes_stubs_global(recette_ids=[recette_id])
        return {"enrichies": count, "recette_id": recette_id}

    return await executer_async(_enrichir)


@router.post("/enrichir-instructions-batch")
@gerer_exception_api
async def enrichir_instructions_batch(
    limite: int = Query(20, ge=1, le=50, description="Nombre max de recettes stubs à traiter"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enrichit en batch toutes les recettes sans étapes de préparation (stubs IA)."""
    from src.core.db import obtenir_contexte_db
    from src.core.models import EtapeRecette
    from src.core.models.recettes import Recette
    from src.services.cuisine.planning import obtenir_service_planning

    def _batch():
        with obtenir_contexte_db() as session:
            stub_ids: list[int] = []
            for (rid,) in session.query(Recette.id).all():
                if not session.query(EtapeRecette).filter(EtapeRecette.recette_id == rid).first():
                    stub_ids.append(rid)
                if len(stub_ids) >= limite:
                    break

        if not stub_ids:
            return {"enrichies": 0, "message": "Aucune recette stub trouvée"}

        service = obtenir_service_planning()
        count = service.enrichir_recettes_stubs_global(recette_ids=stub_ids)
        return {"enrichies": count, "traites": len(stub_ids)}

    return await executer_async(_batch)


@router.post("/{recette_id}/version-jules", response_model=dict)
@gerer_exception_api
async def generer_version_jules(
    recette_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """GÃ©nÃ¨re une version adaptÃ©e Ã  Jules (bÃ©bÃ©) pour une recette.

    Adapte les ingrÃ©dients et instructions selon l'Ã¢ge et les aliments exclus
    de Jules dÃ©finis dans les prÃ©fÃ©rences de l'utilisateur.

    Args:
        recette_id: ID de la recette source

    Returns:
        DonnÃ©es de la VersionRecette crÃ©Ã©e/mise Ã  jour
    """
    from src.core.models.user_preferences import PreferenceUtilisateur
    from src.services.famille.version_recette_jules import obtenir_version_recette_jules_service

    def _generate():
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            prefs = (
                session.query(PreferenceUtilisateur)
                .filter(PreferenceUtilisateur.user_id == user_id)
                .first()
            )
            profil_jules = {
                "age_mois": prefs.jules_age_mois if prefs else 19,
                "aliments_exclus_jules": prefs.aliments_exclus_jules if prefs else [],
            }

        service = obtenir_version_recette_jules_service()
        return service.generer_version_jules(recette_id, profil_jules)

    return await executer_async(_generate)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÃ‰NÃ‰RATION DEPUIS PHOTO (CT-06)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post(
    "/generer-depuis-photo", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION
)
@gerer_exception_api
async def generer_recette_depuis_photo(
    image: UploadFile = File(..., description="Photo du plat ou de la recette"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """GÃ©nÃ¨re une recette complÃ¨te depuis une photo via IA vision (CT-06).

    Analyse la photo avec Pixtral pour identifier les ingrÃ©dients et prÃ©parer
    une recette structurÃ©e, puis la persiste en base de donnÃ©es.

    Args:
        image: Image du plat (JPEG, PNG, WEBP)

    Returns:
        Recette crÃ©Ã©e avec ingrÃ©dients et Ã©tapes
    """
    import asyncio

    from src.core.models import Recette
    from src.services.integrations.multimodal import obtenir_multimodal_service

    image_bytes = await image.read()

    async def _generate_async():
        multimodal = obtenir_multimodal_service()
        recette_extraite = await multimodal.extraire_recette_image(image_bytes)

        if not recette_extraite:
            raise HTTPException(
                status_code=422,
                detail="Impossible d'identifier une recette dans cette image",
            )

        def _persist():
            with executer_avec_session() as session:
                db_recette = Recette(
                    nom=recette_extraite.nom,
                    description="Recette gÃ©nÃ©rÃ©e depuis photo",
                    temps_preparation=_parse_minutes(recette_extraite.temps_preparation),
                    temps_cuisson=_parse_minutes(recette_extraite.temps_cuisson),
                    portions=4,
                    difficulte=(recette_extraite.difficulte or "moyen").lower(),
                    categorie=normaliser_categorie(recette_extraite.categorie),
                    genere_par_ia=True,
                )
                session.add(db_recette)
                session.flush()

                from src.api.schemas.recettes import IngredientItem

                ing_items = [
                    IngredientItem(
                        nom=ing.nom,
                        quantite=float(ing.quantite or 1),
                        unite=ing.unite or "piÃ¨ce",
                    )
                    for ing in recette_extraite.ingredients
                    if ing.nom
                ]
                _sauvegarder_ingredients(session, db_recette.id, ing_items)
                _sauvegarder_etapes(session, db_recette.id, recette_extraite.etapes)

                session.commit()
                session.refresh(db_recette)
                return _serialiser_recette(db_recette, session, user)

        return await executer_async(_persist)

    return await _generate_async()


def _parse_minutes(valeur: str | None) -> int:
    """Parse une chaÃ®ne '15 min', '1h30' etc. en nombre de minutes."""
    if not valeur:
        return 0
    import re

    valeur = valeur.lower()
    h = re.search(r"(\d+)\s*h", valeur)
    m = re.search(r"(\d+)\s*(?:min|mn|m\b)", valeur)
    total = 0
    if h:
        total += int(h.group(1)) * 60
    if m:
        total += int(m.group(1))
    if not h and not m:
        digits = re.search(r"(\d+)", valeur)
        if digits:
            total = int(digits.group(1))
    return total


@router.get("/surprise", response_model=RecetteResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def recette_surprise(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne une recette surprise adaptÃ©e Ã  la saison et aux stocks (QW-02)."""
    import random
    from datetime import date

    from src.core.models import Recette as RecetteORM
    from src.core.models.inventaire import ArticleInventaire

    def _query():
        with executer_avec_session() as session:
            # Saison courante (approximation par mois)
            mois = date.today().month
            if mois in (12, 1, 2):
                saison = "hiver"
            elif mois in (3, 4, 5):
                saison = "printemps"
            elif mois in (6, 7, 8):
                saison = "Ã©tÃ©"
            else:
                saison = "automne"

            # Articles en stock (noms normalisÃ©s)
            stocks = {a.nom.lower() for a in session.query(ArticleInventaire.nom).all()}

            # Toutes les recettes avec leurs ingrÃ©dients
            recettes = session.query(RecetteORM).all()
            if not recettes:
                raise HTTPException(status_code=404, detail="Aucune recette disponible")

            # Filtrer par saison si des tags existent
            candidates = [r for r in recettes if saison in (r.tags or []) or not r.tags] or recettes

            # PrÃ©fÃ©rer les recettes dont des ingrÃ©dients sont en stock
            def _score(r: RecetteORM) -> int:
                return sum(1 for ing in (r.ingredients or []) if ing.nom.lower() in stocks)

            candidates.sort(key=_score, reverse=True)
            # Prendre parmi le top 5 des meilleures correspondances
            top = candidates[:5]
            recette = random.choice(top)
            return _serialiser_recette(recette, session, user)

    return await executer_async(_query)
