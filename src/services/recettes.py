"""
Service Recettes Unifié (REFACTORING PHASE 2)

✅ Utilise @with_db_session et @with_cache (Phase 1)
✅ Validation Pydantic centralisée (RecetteInput, etc.)
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit

Service complet pour les recettes fusionnant :
- recette_service.py (CRUD + recherche)
- recette_ai_service.py (Génération IA)
- recette_io_service.py (Import/Export)
- recette_version_service.py (Versions bébé/batch)
"""

import csv
import json
import logging
from io import StringIO

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.errors_base import ErreurNonTrouve, ErreurValidation
from src.core.models import (
    EtapeRecette,
    Ingredient,
    Recette,
    RecetteIngredient,
    VersionRecette,
)
from src.core.validators_pydantic import RecetteInput, IngredientInput, EtapeInput
from src.services.base_ai_service import BaseAIService, RecipeAIMixin
from src.services.types import BaseService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC (Validation IA)
# ═══════════════════════════════════════════════════════════


class RecetteSuggestion(BaseModel):
    """Recette suggérée par l'IA"""

    nom: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(4, gt=0, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    type_repas: str
    saison: str = "toute_année"
    ingredients: list[dict]
    etapes: list[dict]


class VersionBebeGeneree(BaseModel):
    """Version bébé générée"""

    instructions_modifiees: str
    notes_bebe: str
    age_minimum_mois: int = Field(6, ge=6, le=36)


# ═══════════════════════════════════════════════════════════
# SERVICE RECETTES UNIFIÉ (AVEC HÉRITAGE MULTIPLE)
# ═══════════════════════════════════════════════════════════


class RecetteService(BaseService[Recette], BaseAIService, RecipeAIMixin):
    """
    Service complet pour les recettes.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - RecipeAIMixin → Contextes métier recettes

    Fonctionnalités :
    - CRUD optimisé avec cache
    - Génération IA (rate limiting + cache AUTO)
    - Import/Export (CSV, JSON)
    - Recherche avancée
    - Statistiques
    """

    def __init__(self):
        # Initialisation CRUD
        BaseService.__init__(self, Recette, cache_ttl=3600)

        # Initialisation IA (rate limiting + cache auto)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="recettes",
            default_ttl=3600,
            default_temperature=0.8,  # Plus créatif pour recettes
            service_name="recettes",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : CRUD OPTIMISÉ
    # ═══════════════════════════════════════════════════════════

    @with_cache(ttl=3600, key_func=lambda self, recette_id: f"recette_full_{recette_id}")
    @with_db_session
    def get_by_id_full(self, recette_id: int, db: Session) -> Recette | None:
        """Récupère une recette avec toutes ses relations (avec cache)."""
        try:
            recette = (
                db.query(Recette)
                .options(
                    joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                    joinedload(Recette.etapes),
                    joinedload(Recette.versions),
                )
                .filter(Recette.id == recette_id)
                .first()
            )
            
            if not recette:
                return None
                
            return recette
        except Exception as e:
            logger.error(f"Erreur récupération recette {recette_id}: {e}")
            return None

    @with_db_session
    def get_by_type(self, type_repas: str, db: Session) -> list[Recette]:
        """Récupère les recettes d'un type donné."""
        try:
            return (
                db.query(Recette)
                .filter(Recette.type_repas == type_repas)
                .all()
            )
        except Exception as e:
            logger.error(f"Erreur récupération recettes par type {type_repas}: {e}")
            return []

    @with_error_handling(default_return=None, afficher_erreur=True)
    @with_db_session
    def create_complete(self, data: dict, db: Session) -> Recette:
        """
        Crée une recette complète (recette + ingrédients + étapes).
        
        Args:
            data: Dict avec clés: nom, description, temps_prep, temps_cuisson, 
                  portions, ingredients[], etapes[]
            db: Session DB injectée
            
        Returns:
            Recette créée avec relations
        """
        # Validation avec Pydantic
        try:
            validated = RecetteInput(**data)
        except Exception as e:
            raise ErreurValidation(f"Données invalides: {str(e)}")
        
        # Créer recette
        recette = Recette(**validated.model_dump(exclude={"ingredients", "etapes"}))
        db.add(recette)
        db.flush()

        # Créer ingrédients
        for ing_data in validated.ingredients or []:
            ingredient = self._find_or_create_ingredient(db, ing_data.nom)
            recette_ing = RecetteIngredient(
                recette_id=recette.id,
                ingredient_id=ingredient.id,
                quantite=ing_data.quantite,
                unite=ing_data.unite,
            )
            db.add(recette_ing)

        # Créer étapes
        for idx, etape_data in enumerate(validated.etapes or []):
            etape = EtapeRecette(
                recette_id=recette.id,
                ordre=idx + 1,
                description=etape_data.description,
                duree=etape_data.duree,
            )
            db.add(etape)

        db.commit()
        db.refresh(recette)

        # Invalider cache
        Cache.invalider(pattern="recettes")

        logger.info(f"✅ Recette créée : {recette.nom} (ID: {recette.id})")
        return recette

    @with_db_session
    def search_advanced(
        self,
        term: str | None = None,
        type_repas: str | None = None,
        saison: str | None = None,
        difficulte: str | None = None,
        temps_max: int | None = None,
        compatible_bebe: bool | None = None,
        limit: int = 100,
        db: Session | None = None,
    ) -> list[Recette]:
        """
        Recherche avancée multi-critères.
        
        Args:
            term: Terme de recherche (nom/description)
            type_repas: Type de repas (petit_déjeuner, déjeuner, dîner, goûter)
            saison: Saison (printemps, été, automne, hiver)
            difficulte: Niveau (facile, moyen, difficile)
            temps_max: Temps préparation max en minutes
            compatible_bebe: Compatible pour bébé
            limit: Nombre de résultats max
            db: Session DB injectée
            
        Returns:
            Liste des recettes trouvées
        """
        filters: dict = {}
        if type_repas:
            filters["type_repas"] = type_repas
        if saison:
            filters["saison"] = saison
        if difficulte:
            filters["difficulte"] = difficulte
        if compatible_bebe is not None:
            filters["compatible_bebe"] = compatible_bebe
        if temps_max:
            filters["temps_preparation"] = {"lte": temps_max}

        search_fields = ["nom", "description"] if term else None

        return self.advanced_search(
            search_term=term,
            search_fields=search_fields,
            filters=filters,
            sort_by="nom",
            limit=limit,
            db=db,
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : GÉNÉRATION IA (AVEC CACHE ET VALIDATION)
    # ═══════════════════════════════════════════════════════════

    @with_cache(
        ttl=21600,
        key_func=lambda self, type_repas, saison, difficulte, ingredients_dispo: (
            f"recettes_ia_{type_repas}_{saison}_{difficulte}_"
            f"{hash(tuple(ingredients_dispo or []))}"
        ),
    )
    @with_error_handling(default_return=[])
    def generer_recettes_ia(
        self,
        type_repas: str,
        saison: str,
        difficulte: str = "moyen",
        ingredients_dispo: list[str] | None = None,
        nb_recettes: int = 3,
    ) -> list[RecetteSuggestion]:
        """Génère des suggestions de recettes avec l'IA.

        Uses Mistral AI to suggest recipes based on meal type, season,
        difficulty, and available ingredients. Results cached for 6 hours.

        Args:
            type_repas: Type de repas (petit_déjeuner, déjeuner, dîner, goûter)
            saison: Season (printemps, été, automne, hiver)
            difficulte: Difficulty level (facile, moyen, difficile)
            ingredients_dispo: List of available ingredient names
            nb_recettes: Number of suggestions to generate

        Returns:
            List of RecetteSuggestion objects, empty list on error
        """
        # Construire contexte métier
        context = self.build_recipe_context(
            filters={
                "type_repas": type_repas,
                "saison": saison,
                "difficulte": difficulte,
                "is_quick": False,
            },
            ingredients_dispo=ingredients_dispo,
            nb_recettes=nb_recettes,
        )

        # Prompt avec instructions JSON
        prompt = self.build_json_prompt(
            context=context,
            task=f"Generate {nb_recettes} complete recipes",
            json_schema='[{"nom": str, "description": str, "temps_preparation": int, ...}]',
            constraints=[
                "Each recipe must be complete with all ingredients",
                "Include precise quantities and units",
                "Detail all preparation steps",
                "Respect season constraints",
            ],
        )

        logger.info(f"🤖 Generating {nb_recettes} recipe suggestions")

        # IA call with auto rate limiting & parsing
        recettes = self.call_with_list_parsing(
            prompt=prompt,
            item_model=RecetteSuggestion,
            system_prompt=self.build_system_prompt(
                role="Expert chef and nutritionist",
                expertise=[
                    "French and international cuisine",
                    "Nutritional balance",
                    "Seasonal adaptation",
                    "Culinary creativity",
                ],
                rules=[
                    "Prioritize seasonal ingredients",
                    "Respect preparation times",
                    "Propose achievable recipes",
                ],
            ),
            max_items=nb_recettes,
        )

        logger.info(f"✅ Generated {len(recettes)} recipe suggestions")
        return recettes

    @with_cache(ttl=3600, key_func=lambda self, rid: f"version_bebe_{rid}")
    @with_error_handling(default_return=None)
    @with_db_session
    def generer_version_bebe(self, recette_id: int, db: Session) -> VersionRecette | None:
        """Génère une version bébé sécurisée de la recette avec l'IA.

        Adapts recipe for babies (12+ months). Creates version in DB.
        Includes safety notes and age recommendations.

        Args:
            recette_id: ID of recipe to adapt
            db: Database session (injected by @with_db_session)

        Returns:
            VersionRecette object or None if generation fails
        """
        # Récupérer la recette
        recette = (
            db.query(Recette)
            .options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                joinedload(Recette.etapes),
            )
            .filter(Recette.id == recette_id)
            .first()
        )
        if not recette:
            raise ErreurNonTrouve(f"Recipe {recette_id} not found")

        # Vérifier si version existe déjà
        existing = (
            db.query(VersionRecette)
            .filter(
                VersionRecette.recette_base_id == recette_id,
                VersionRecette.type_version == "bébé",
            )
            .first()
        )
        if existing:
            logger.info(f"📦 Baby version already exists for recipe {recette_id}")
            return existing

        logger.info(f"🤖 Generating baby-safe version for recipe {recette_id}")

        # Construire contexte avec recette complète
        ingredients_str = "\n".join(
            [f"- {ri.quantite} {ri.unite} {ri.ingredient.nom}" for ri in recette.ingredients]
        )
        etapes_str = "\n".join(
            [f"{e.ordre}. {e.description}" for e in sorted(recette.etapes, key=lambda x: x.ordre)]
        )

        context = f"""Recipe: {recette.nom}

Ingredients:
{ingredients_str}

Steps:
{etapes_str}"""

        # Prompt pour adaptation bébé
        prompt = self.build_json_prompt(
            context=context,
            task="Adapt this recipe for a 12-month-old baby",
            json_schema='{"instructions_modifiees": str, "notes_bebe": str, "age_minimum_mois": int}',
            constraints=[
                "Appropriate texture (no hard chunks)",
                "No major allergens",
                "Reduced quantities",
                "Food safety instructions",
            ],
        )

        # Appel IA avec parsing auto
        version_data = self.call_with_parsing(
            prompt=prompt,
            response_model=VersionBebeGeneree,
            system_prompt=self.build_system_prompt(
                role="Pediatric nutritionist specialist in infant feeding",
                expertise=[
                    "Food diversification",
                    "Food allergies",
                    "Baby nutritional needs",
                    "Food safety",
                ],
                rules=[
                    "Ensure age-appropriate safety",
                    "No salt, sugar, or honey",
                    "Soft, easy-to-chew texture",
                ],
            ),
        )

        if not version_data:
            logger.warning(f"⚠️ Failed to generate baby version for recipe {recette_id}")
            raise ErreurValidation("Invalid IA response format for baby version")

        # Créer version en DB
        version = VersionRecette(
            recette_base_id=recette_id,
            type_version="bébé",
            instructions_modifiees=version_data.instructions_modifiees,
            notes_bebe=version_data.notes_bebe,
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        logger.info(f"✅ Baby version created for recipe {recette_id}")
        return version

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : IMPORT/EXPORT (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    def export_to_csv(self, recettes: list[Recette], separator: str = ",") -> str:
        """Exporte des recettes en CSV.
        
        Args:
            recettes: List of Recette objects to export
            separator: CSV separator character
            
        Returns:
            CSV string with recipe data
        """
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "nom",
                "description",
                "temps_preparation",
                "temps_cuisson",
                "portions",
                "difficulte",
                "type_repas",
                "saison",
            ],
            delimiter=separator,
        )

        writer.writeheader()
        for r in recettes:
            writer.writerow(
                {
                    "nom": r.nom,
                    "description": r.description or "",
                    "temps_preparation": r.temps_preparation,
                    "temps_cuisson": r.temps_cuisson,
                    "portions": r.portions,
                    "difficulte": r.difficulte,
                    "type_repas": r.type_repas,
                    "saison": r.saison,
                }
            )

        logger.info(f"✅ Exported {len(recettes)} recipes to CSV")
        return output.getvalue()

    def export_to_json(self, recettes: list[Recette], indent: int = 2) -> str:
        """Exporte des recettes en JSON.
        
        Args:
            recettes: List of Recette objects to export
            indent: JSON indentation level
            
        Returns:
            JSON string with recipe data
        """
        data = []
        for r in recettes:
            data.append(
                {
                    "nom": r.nom,
                    "description": r.description,
                    "temps_preparation": r.temps_preparation,
                    "temps_cuisson": r.temps_cuisson,
                    "portions": r.portions,
                    "difficulte": r.difficulte,
                    "type_repas": r.type_repas,
                    "saison": r.saison,
                    "ingredients": [
                        {"nom": ri.ingredient.nom, "quantite": ri.quantite, "unite": ri.unite}
                        for ri in r.ingredients
                    ],
                    "etapes": [{"ordre": e.ordre, "description": e.description} for e in r.etapes],
                }
            )

        logger.info(f"✅ Exported {len(recettes)} recipes to JSON")
        return json.dumps(data, indent=indent, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════
    # SECTION 4 : HELPERS PRIVÉS (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    def _find_or_create_ingredient(self, db: Session, nom: str) -> Ingredient:
        """Finds or creates an ingredient.
        
        Args:
            db: Database session
            nom: Ingredient name
            
        Returns:
            Ingredient object (existing or newly created)
        """
        ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()
        if not ingredient:
            ingredient = Ingredient(nom=nom, unite="pcs")
            db.add(ingredient)
            db.flush()
            logger.debug(f"Created ingredient: {nom}")
        return ingredient


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON - LAZY LOADING
# ═══════════════════════════════════════════════════════════

_recette_service = None

def get_recette_service() -> RecetteService:
    """Get or create the global RecetteService instance."""
    global _recette_service
    if _recette_service is None:
        _recette_service = RecetteService()
    return _recette_service

recette_service = None


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "RecetteService",
    "recette_service",
    "RecetteSuggestion",
    "VersionBebeGeneree",
    "get_recette_service",
]
