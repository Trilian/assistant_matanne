"""
Routes API pour les recettes.

CRUD complet pour les recettes avec pagination, filtres par catégorie,
recherche par nom et documentation OpenAPI enrichie.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas import (
    MessageResponse,
    RecetteCreate,
    RecettePatch,
    RecetteResponse,
    ReponsePaginee,
)
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import (
    construire_reponse_paginee,
    executer_async,
    executer_avec_session,
    gerer_exception_api,
)

router = APIRouter(prefix="/api/v1/recettes", tags=["Recettes"])


@router.get("", response_model=ReponsePaginee[RecetteResponse], responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_recettes(
    page: int = Query(1, ge=1, description="Numéro de page (1-indexé)"),
    page_size: int = Query(20, ge=1, le=100, description="Nombre d'éléments par page"),
    categorie: str | None = Query(
        None, description="Filtrer par catégorie (plat, dessert, entrée...)"
    ),
    search: str | None = Query(None, description="Recherche dans le nom de la recette"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les recettes avec pagination et filtres.

    Retourne une liste paginée de recettes avec possibilité de filtrer
    par catégorie ou de rechercher par nom.

    Args:
        page: Numéro de page (défaut: 1)
        page_size: Taille de page (défaut: 20, max: 100)
        categorie: Filtre optionnel par catégorie
        search: Recherche partielle dans le nom

    Returns:
        Réponse paginée avec items, total, pages

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

    def _query():
        with executer_avec_session() as session:
            query = session.query(Recette)

            if categorie:
                query = query.filter(Recette.categorie == categorie)

            if search:
                # Échapper les caractères spéciaux SQL wildcard pour éviter l'injection
                safe_search = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(Recette.nom.ilike(f"%{safe_search}%"))

            total = query.count()
            items = (
                query.order_by(Recette.nom).offset((page - 1) * page_size).limit(page_size).all()
            )

            return construire_reponse_paginee(items, total, page, page_size, RecetteResponse)

    return await executer_async(_query)


@router.get("/{recette_id}", response_model=RecetteResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_recette(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    Récupère une recette par son ID.

    Args:
        recette_id: Identifiant unique de la recette

    Returns:
        Détail complet de la recette

    Raises:
        404: Recette non trouvée

    Example:
        ```
        GET /api/v1/recettes/42

        Response:
        {
            "id": 42,
            "nom": "Poulet rôti",
            "description": "Un classique familial",
            "temps_preparation": 15,
            "temps_cuisson": 60,
            "portions": 4,
            "difficulte": "facile",
            "categorie": "plat"
        }
        ```
    """
    from src.core.models import Recette

    def _query():
        with executer_avec_session() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            return RecetteResponse.model_validate(recette)

    return await executer_async(_query)


@router.post("", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_recette(recette: RecetteCreate, user: dict[str, Any] = Depends(require_auth)):
    """
    Crée une nouvelle recette.

    Nécessite une authentification. La recette est créée avec les données
    fournies et un ID est automatiquement généré.

    Args:
        recette: Données de la recette à créer

    Returns:
        La recette créée avec son ID

    Raises:
        401: Non authentifié
        422: Données invalides

    Example:
        ```
        POST /api/v1/recettes
        Authorization: Bearer <token>

        Body:
        {
            "nom": "Gratin dauphinois",
            "description": "Pommes de terre gratinees",
            "temps_preparation": 20,
            "temps_cuisson": 45,
            "portions": 6,
            "difficulte": "facile",
            "categorie": "accompagnement"
        }
        ```
    """
    from src.core.models import Recette

    def _create():
        with executer_avec_session() as session:
            db_recette = Recette(
                nom=recette.nom,
                description=recette.description,
                temps_preparation=recette.temps_preparation,
                temps_cuisson=recette.temps_cuisson,
                portions=recette.portions,
                difficulte=recette.difficulte,
                categorie=recette.categorie,
            )
            session.add(db_recette)
            session.commit()
            session.refresh(db_recette)

            return RecetteResponse.model_validate(db_recette)

    return await executer_async(_create)


@router.put("/{recette_id}", response_model=RecetteResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_recette(
    recette_id: int, recette: RecetteCreate, user: dict[str, Any] = Depends(require_auth)
):
    """Met à jour une recette complètement (remplacement total).

    Remplace tous les champs de la recette par les valeurs fournies.
    Pour une mise à jour partielle, utiliser PATCH.

    Args:
        recette_id: ID de la recette à modifier
        recette: Tous les champs de la recette (remplacement complet)

    Returns:
        La recette mise à jour

    Raises:
        401: Non authentifié
        404: Recette non trouvée
        422: Données invalides

    Example:
        ```
        PUT /api/v1/recettes/42
        Authorization: Bearer <token>

        Body: {"nom": "Poulet rôti aux herbes", "temps_cuisson": 75}

        Response:
        {"id": 42, "nom": "Poulet rôti aux herbes", "temps_cuisson": 75, ...}
        ```
    """
    from src.core.models import Recette

    def _update():
        with executer_avec_session() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            # PUT = remplacement complet (A9: ne pas utiliser exclude_unset)
            # Exclure les champs relationnels gérés séparément
            for key, value in recette.model_dump(
                exclude={"ingredients", "instructions", "tags"}
            ).items():
                if hasattr(db_recette, key):
                    setattr(db_recette, key, value)

            session.commit()
            session.refresh(db_recette)

            return RecetteResponse.model_validate(db_recette)

    return await executer_async(_update)


@router.patch("/{recette_id}", response_model=RecetteResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_partiellement_recette(
    recette_id: int, patch: RecettePatch, user: dict[str, Any] = Depends(require_auth)
):
    """Mise à jour partielle d'une recette.

    Seuls les champs fournis dans le body sont modifiés.
    Les champs absents ou ``null`` restent inchangés.

    Args:
        recette_id: ID de la recette à modifier
        patch: Champs à mettre à jour (tous optionnels)

    Returns:
        La recette mise à jour

    Raises:
        401: Non authentifié
        404: Recette non trouvée
        422: Données invalides

    Example:
        ```
        PATCH /api/v1/recettes/42
        Authorization: Bearer <token>

        Body: {"nom": "Poulet rôti aux herbes", "temps_cuisson": 75}

        Response:
        {"id": 42, "nom": "Poulet rôti aux herbes", "temps_cuisson": 75, ...}
        ```
    """
    from src.core.models import Recette

    def _patch():
        with executer_avec_session() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            # Seuls les champs explicitement fournis sont mis à jour
            donnees = patch.model_dump(exclude_unset=True)
            if not donnees:
                raise HTTPException(
                    status_code=422,
                    detail="Aucun champ à mettre à jour fourni",
                )

            for key, value in donnees.items():
                if hasattr(db_recette, key):
                    setattr(db_recette, key, value)

            session.commit()
            session.refresh(db_recette)

            return RecetteResponse.model_validate(db_recette)

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


# ─────────────────────────────────────────────────────────
# PLANIFICATION "CETTE SEMAINE"
# ─────────────────────────────────────────────────────────


@router.get("/planifiees-semaine", response_model=list[RecetteResponse])
@gerer_exception_api
async def lister_recettes_semaine(user: dict[str, Any] = Depends(require_auth)):
    """Liste les recettes marquées 'à faire cette semaine'."""
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
            return [RecetteResponse.model_validate(r) for r in rows]

    return await executer_async(_query)


@router.post("/{recette_id}/planifier-semaine", response_model=MessageResponse)
@gerer_exception_api
async def planifier_recette_semaine(recette_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Marque une recette comme 'à faire cette semaine'."""
    from datetime import datetime

    from src.core.models import Recette
    from src.core.models.user_preferences import RetourRecette

    def _upsert():
        with executer_avec_session() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

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
            return MessageResponse(message=f"Recette {recette_id} planifiée cette semaine")

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
            return MessageResponse(message=f"Recette {recette_id} retirée de cette semaine")

    return await executer_async(_clear)


# ═══════════════════════════════════════════════════════════
# IMPORT DE RECETTES
# ═══════════════════════════════════════════════════════════


@router.post("/import-url", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def importer_recette_url(
    url: str = Query(..., description="URL de la recette à importer"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Importe une recette depuis une URL.
    
    Supporte les sites populaires (Marmiton, CuisineAZ, etc.) ainsi que
    les pages génériques via extraction IA.
    
    Args:
        url: URL complète de la recette
        user: Utilisateur authentifié
    
    Returns:
        Recette créée avec données importées
    
    Raises:
        HTTPException 422: URL invalide ou recette non trouvée
        HTTPException 500: Erreur lors de l'import
    """
    from src.core.models import Recette, Ingredient, EtapeRecette
    from src.services.cuisine.recettes.import_url import get_recipe_import_service
    
    def _import():
        # Import via service
        import_service = get_recipe_import_service()
        result = import_service.import_from_url(url, use_ai_fallback=True)
        
        if not result.success:
            raise HTTPException(
                status_code=422,
                detail=f"Impossible d'importer la recette: {result.error}"
            )
        
        recipe_data = result.recipe
        
        # Créer la recette en DB
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            
            # Créer recette principale
            recette = Recette(
                nom=recipe_data.nom,
                description=recipe_data.description,
                temps_preparation=recipe_data.temps_preparation,
                temps_cuisson=recipe_data.temps_cuisson,
                temps_total=recipe_data.temps_total,
                portions=recipe_data.portions or 4,
                niveau=recipe_data.niveau or "moyen",
                categorie=recipe_data.categorie or "plat",
                saison="toutes_saisons",
                tags=recipe_data.tags or [],
                url_source=url,
                cree_par=user_id,
            )
            session.add(recette)
            session.flush()  # Get ID
            
            # Ajouter ingrédients
            for idx, ing_data in enumerate(recipe_data.ingredients or [], start=1):
                ingredient = Ingredient(
                    recette_id=recette.id,
                    ordre=idx,
                    quantite=ing_data.quantite,
                    unite=ing_data.unite,
                    nom=ing_data.nom,
                )
                session.add(ingredient)
            
            # Ajouter étapes
            for idx, step in enumerate(recipe_data.etapes or [], start=1):
                etape = EtapeRecette(
                    recette_id=recette.id,
                    ordre=idx,
                    description=step,
                )
                session.add(etape)
            
            session.commit()
            session.refresh(recette)
            
            return {
                "id": recette.id,
                "nom": recette.nom,
                "description": recette.description,
                "temps_preparation": recette.temps_preparation,
                "temps_cuisson": recette.temps_cuisson,
                "portions": recette.portions,
                "categorie": recette.categorie,
                "url_source": recette.url_source,
            }
    
    return await executer_async(_import)


@router.post("/import-pdf", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def importer_recette_pdf(
    file: "UploadFile",
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Importe une recette depuis un fichier PDF.
    
    Utilise l'OCR et l'IA pour extraire le contenu du PDF et créer une recette.
    
    Args:
        file: Fichier PDF uploadé
        user: Utilisateur authentifié
    
    Returns:
        Recette créée avec données extraites
    
    Raises:
        HTTPException 422: Fichier invalide
        HTTPException 500: Erreur lors de l'extraction OCR
    """
    from fastapi import UploadFile
    
    # Import PDF non implémenté dans le service actuellement
    # Placeholder pour future implémentation
    raise HTTPException(
        status_code=501,
        detail="Import PDF pas encore implémenté. Utilisez import-url pour le moment."
    )

