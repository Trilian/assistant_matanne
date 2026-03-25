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


# ═══════════════════════════════════════════════════════════
# HELPERS INTERNES
# ═══════════════════════════════════════════════════════════


def _sauvegarder_ingredients(session, recette_id: int, ingredients: list) -> None:
    """Persiste les RecetteIngredient en trouvant/créant les Ingredient de référence."""
    from src.core.models import Ingredient, RecetteIngredient

    for idx, ing in enumerate(ingredients, start=1):
        nom = ing.nom.strip()
        if not nom:
            continue

        # Find or create l'ingrédient de référence
        db_ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()
        if not db_ingredient:
            db_ingredient = Ingredient(nom=nom, unite=ing.unite or "pièce")
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
    """Sérialise une Recette ORM en RecetteResponse avec relations."""
    from src.core.models import RecetteIngredient
    from src.core.models.user_preferences import RetourRecette

    # Charger ingrédients avec le nom depuis la table Ingredient
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

    # Charger étapes
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

    # Vérifier favori (feedback == 'like' dans RetourRecette)
    user_id = user.get("sub", user.get("id", "dev"))
    retour = (
        session.query(RetourRecette)
        .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == db_recette.id)
        .first()
    )
    est_favori = retour.feedback == "like" if retour else False

    # Note moyenne
    from src.core.models.recettes import HistoriqueRecette
    from sqlalchemy import func

    note_avg = (
        session.query(func.avg(HistoriqueRecette.note))
        .filter(
            HistoriqueRecette.recette_id == db_recette.id,
            HistoriqueRecette.note.isnot(None),
        )
        .scalar()
    )

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
        note_moyenne=round(note_avg, 1) if note_avg else None,
        url_source=getattr(db_recette, "url_source", None),
    )


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
                }
                for r in items
            ]

            return construire_reponse_paginee(items_dicts, total, page, page_size)

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
    from sqlalchemy.orm import joinedload

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
async def creer_recette(recette: RecetteCreate, user: dict[str, Any] = Depends(require_auth)):
    """
    Crée une nouvelle recette avec ses ingrédients et étapes.

    Args:
        recette: Données de la recette (nom, ingrédients, instructions...)

    Returns:
        La recette créée avec ses ingrédients et étapes

    Example:
        ```
        POST /api/v1/recettes
        Body:
        {
            "nom": "Gratin dauphinois",
            "description": "Pommes de terre gratinées",
            "temps_preparation": 20,
            "temps_cuisson": 45,
            "portions": 6,
            "difficulte": "facile",
            "categorie": "accompagnement",
            "ingredients": [
                {"nom": "Pommes de terre", "quantite": 1, "unite": "kg"},
                {"nom": "Crème fraîche", "quantite": 30, "unite": "cl"}
            ],
            "instructions": ["Éplucher les pommes de terre", "Préchauffer le four à 180°C"]
        }
        ```
    """
    from src.core.models import EtapeRecette, Ingredient, Recette, RecetteIngredient

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
            session.flush()

            _sauvegarder_ingredients(session, db_recette.id, recette.ingredients)
            _sauvegarder_etapes(session, db_recette.id, recette.instructions)

            session.commit()
            session.refresh(db_recette)

            return _serialiser_recette(db_recette, session, user)

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
    from src.core.models import EtapeRecette, Recette, RecetteIngredient

    def _update():
        with executer_avec_session() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            for key, value in recette.model_dump(
                exclude={"ingredients", "instructions", "tags"}
            ).items():
                if hasattr(db_recette, key):
                    setattr(db_recette, key, value)

            # Remplacer ingrédients et étapes
            session.query(RecetteIngredient).filter(
                RecetteIngredient.recette_id == recette_id
            ).delete()
            session.query(EtapeRecette).filter(
                EtapeRecette.recette_id == recette_id
            ).delete()

            _sauvegarder_ingredients(session, recette_id, recette.ingredients)
            _sauvegarder_etapes(session, recette_id, recette.instructions)

            session.commit()
            session.refresh(db_recette)

            return _serialiser_recette(db_recette, session, user)

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
    from src.core.models import EtapeRecette, Recette, RecetteIngredient

    def _patch():
        with executer_avec_session() as session:
            db_recette = session.query(Recette).filter(Recette.id == recette_id).first()

            if not db_recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            donnees = patch.model_dump(exclude_unset=True)
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
                items = [IngredientItem(**i) if isinstance(i, dict) else i for i in ingredients_data]
                _sauvegarder_ingredients(session, recette_id, items)

            if instructions_data is not None:
                session.query(EtapeRecette).filter(
                    EtapeRecette.recette_id == recette_id
                ).delete()
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
            return [_serialiser_recette(r, session, user) for r in rows]

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
    from src.core.models import Recette
    from src.services.cuisine.recettes.import_url import get_recipe_import_service
    from src.services.cuisine.recettes.enrichers import (
        ImportedIngredient,
        ImportedRecipe,
        get_recipe_enricher,
    )
    
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
        
        # Créer la recette en DB
        with executer_avec_session() as session:
            # Créer recette principale avec enrichissement
            recette = Recette(
                nom=recipe_data.nom,
                description=recipe_data.description,
                temps_preparation=recipe_data.temps_preparation or 0,
                temps_cuisson=recipe_data.temps_cuisson or 0,
                portions=recipe_data.portions or 4,
                difficulte=getattr(recipe_data, "niveau", "moyen") or "moyen",
                categorie=recipe_data.categorie or "plat",
                saison="toute_année",
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
            )
            session.add(recette)
            session.flush()
            
            # Ajouter ingrédients via helper (find-or-create Ingredient + RecetteIngredient)
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
            
            # Ajouter étapes
            _sauvegarder_etapes(session, recette.id, recipe_data.etapes or [])
            
            session.commit()
            session.refresh(recette)
            
            return _serialiser_recette(recette, session, user)
    
    return await executer_async(_import)


@router.post("/import-pdf", response_model=RecetteResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def importer_recette_pdf(
    file: "UploadFile",
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Importe une recette depuis un fichier PDF.
    
    Utilise PyPDF2 pour extraire le texte et l'enrichit automatiquement
    (nutrition, bio/local, classification, robots).
    
    Args:
        file: Fichier PDF uploadé
        user: Utilisateur authentifié
    
    Returns:
        Recette créée avec données extraites et enrichies
    
    Raises:
        HTTPException 422: Fichier invalide ou non PDF
        HTTPException 500: Erreur lors de l'extraction
    """
    import tempfile
    from pathlib import Path
    
    from fastapi import UploadFile
    
    from src.core.models import Recette
    from src.services.cuisine.recettes.importer import RecipeImporter
    from src.services.cuisine.recettes.enrichers import (
        ImportedIngredient,
        ImportedRecipe,
        get_recipe_enricher,
    )
    
    def _import():
        # Vérifier type de fichier
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=422,
                detail="Seuls les fichiers PDF sont acceptés"
            )
        
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        
        try:
            # Extraire avec PyPDF2
            raw_data = RecipeImporter.from_pdf(tmp_path)
            
            if not raw_data or not raw_data.get("nom"):
                raise HTTPException(
                    status_code=422,
                    detail="Impossible d'extraire une recette du PDF"
                )
            
            # Convertir en ImportedRecipe pour l'enrichissement
            # Les ingrédients sont des strings simples, on parse basiquement
            imported_ingredients = []
            for ing_str in raw_data.get("ingredients", []):
                # Pattern simple: "250g farine" -> 250, g, farine
                import re
                match = re.match(r'(\d+(?:\.\d+)?)\s*([a-z]+)?\s*(.+)', ing_str.strip())
                if match:
                    qty, unit, name = match.groups()
                    imported_ingredients.append(
                        ImportedIngredient(
                            nom=name.strip(),
                            quantite=float(qty),
                            unite=unit or "pièce",
                        )
                    )
                else:
                    # Pas de quantité détectée, juste le nom
                    imported_ingredients.append(
                        ImportedIngredient(nom=ing_str.strip())
                    )
            
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
            
            # Créer en DB
            with executer_avec_session() as session:
                recette = Recette(
                    nom=recipe.nom,
                    description=recipe.description,
                    temps_preparation=recipe.temps_preparation,
                    temps_cuisson=recipe.temps_cuisson,
                    portions=recipe.portions,
                    difficulte="moyen",
                    categorie="plat",
                    saison="toute_année",
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
                
                # Ingrédients
                from src.api.schemas.recettes import IngredientItem
                
                ing_items = [
                    IngredientItem(
                        nom=ing.nom,
                        quantite=ing.quantite or 1,
                        unite=ing.unite or "pièce",
                    )
                    for ing in recipe.ingredients
                ]
                _sauvegarder_ingredients(session, recette.id, ing_items)
                
                # Étapes
                _sauvegarder_etapes(session, recette.id, recipe.etapes)
                
                session.commit()
                session.refresh(recette)
                
                return _serialiser_recette(recette, session, user)
                
        finally:
            # Nettoyer le fichier temporaire
            Path(tmp_path).unlink(missing_ok=True)
    
    return await executer_async(_import)


# ═══════════════════════════════════════════════════════════
# FAVORIS & NOTATION
# ═══════════════════════════════════════════════════════════


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
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            user_id = user.get("sub", user.get("id", "dev"))
            retour = (
                session.query(RetourRecette)
                .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == recette_id)
                .first()
            )
            if retour:
                retour.feedback = "like"
            else:
                retour = RetourRecette(
                    user_id=user_id, recette_id=recette_id, feedback="like"
                )
                session.add(retour)
            session.commit()
            return MessageResponse(message=f"Recette {recette_id} ajoutée aux favoris")

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
            return MessageResponse(message=f"Recette {recette_id} retirée des favoris")

    return await executer_async(_remove)


@router.post("/{recette_id}/noter", response_model=MessageResponse)
@gerer_exception_api
async def noter_recette(
    recette_id: int,
    note: int = Query(..., ge=0, le=5, description="Note de 0 à 5"),
    avis: str | None = Query(None, description="Commentaire optionnel"),
    user: dict[str, Any] = Depends(require_auth),
):
    """Note une recette (0-5 étoiles) en créant une entrée dans l'historique."""
    from datetime import date

    from src.core.models import Recette
    from src.core.models.recettes import HistoriqueRecette

    def _noter():
        with executer_avec_session() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")

            historique = HistoriqueRecette(
                recette_id=recette_id,
                date_cuisson=date.today(),
                portions_cuisinees=recette.portions,
                note=note,
                avis=avis,
            )
            session.add(historique)
            session.commit()
            return MessageResponse(
                message=f"Recette {recette_id} notée {note}/5", id=historique.id
            )

    return await executer_async(_noter)


# ═══════════════════════════════════════════════════════════
# ENRICHISSEMENT NUTRITIONNEL
# ═══════════════════════════════════════════════════════════


@router.post("/{recette_id}/enrichir-nutrition")
@gerer_exception_api
async def enrichir_nutrition_recette(
    recette_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enrichit une recette avec les données nutritionnelles via OpenFoodFacts."""
    from src.services.cuisine.nutrition import obtenir_service_nutrition

    def _enrichir():
        service = obtenir_service_nutrition()
        resultat = service.enrichir_recette(recette_id)
        if not resultat:
            raise HTTPException(
                status_code=404,
                detail="Impossible d'enrichir cette recette (ingrédients manquants ou non trouvés)",
            )
        return resultat

    return await executer_async(_enrichir)


@router.post("/enrichir-nutrition-batch")
@gerer_exception_api
async def enrichir_nutrition_batch(
    limite: int = Query(50, ge=1, le=200, description="Nombre max de recettes à traiter"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Enrichit en batch les recettes sans données nutritionnelles."""
    from src.services.cuisine.nutrition import obtenir_service_nutrition

    def _batch():
        service = obtenir_service_nutrition()
        return service.enrichir_batch(limite=limite)

    return await executer_async(_batch)

