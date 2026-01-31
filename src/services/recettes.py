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

import asyncio
import csv
import json
import logging
from io import StringIO

from pydantic import BaseModel, Field, ConfigDict, field_validator
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
    
    # Convertir automatiquement les floats en entiers (Mistral peut retourner 20.0)
    model_config = ConfigDict(coerce_numbers_to_str=False)

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
    
    @field_validator("temps_preparation", "temps_cuisson", "portions", mode="before")
    @classmethod
    def convert_float_to_int(cls, v):
        """Convertit les floats en entiers (Mistral peut retourner des floats)"""
        if isinstance(v, float):
            return int(v)
        return v


class VersionBebeGeneree(BaseModel):
    """Version bébé générée"""
    
    @field_validator("age_minimum_mois", mode="before")
    @classmethod
    def convert_float_to_int_age(cls, v):
        """Convertit les floats en entiers"""
        if isinstance(v, float):
            return int(v)
        return v

    instructions_modifiees: str
    notes_bebe: str
    age_minimum_mois: int = Field(6, ge=6, le=36)


class VersionBatchCookingGeneree(BaseModel):
    """Version batch cooking générée"""
    
    @field_validator("nombre_portions_recommande", mode="before")
    @classmethod
    def convert_float_to_int_portions(cls, v):
        """Convertit les floats en entiers"""
        if isinstance(v, float):
            return int(v)
        return v

    instructions_modifiees: str
    nombre_portions_recommande: int = Field(12, ge=4, le=100)
    temps_preparation_total_heures: float = Field(2.0, ge=0.5, le=12)
    conseils_conservation: str
    conseils_congelation: str
    calendrier_preparation: str


class VersionRobotGeneree(BaseModel):
    """Version adaptée pour robot de cuisine"""
    
    @field_validator("temps_cuisson_adapte_minutes", mode="before")
    @classmethod
    def convert_float_to_int_temps(cls, v):
        """Convertit les floats en entiers"""
        if isinstance(v, float):
            return int(v)
        return v

    instructions_modifiees: str
    reglages_robot: str
    temps_cuisson_adapte_minutes: int = Field(30, ge=5, le=300)
    conseils_preparation: str
    etapes_specifiques: list[str] = Field(default_factory=list)


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
            from sqlalchemy.orm import selectinload
            
            recette = (
                db.query(Recette)
                .options(
                    selectinload(Recette.ingredients).selectinload(RecetteIngredient.ingredient),
                    selectinload(Recette.etapes),
                    selectinload(Recette.versions),
                )
                .filter(Recette.id == recette_id)
                .first()
            )
            
            if not recette:
                return None
            
            # Force l'initialisation des collections lazy-loaded avant la fermeture de la session
            _ = recette.ingredients
            _ = recette.etapes
            _ = recette.versions
            
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
        from datetime import datetime
        
        # Validation avec Pydantic
        try:
            validated = RecetteInput(**data)
        except Exception as e:
            raise ErreurValidation(f"Données invalides: {str(e)}")
        
        # Créer recette avec updated_at
        recette_dict = validated.model_dump(exclude={"ingredients", "etapes"})
        recette_dict["updated_at"] = datetime.utcnow()  # ← Requis par le trigger PostgreSQL
        recette = Recette(**recette_dict)
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
        key_func=lambda self, type_repas, saison, difficulte, ingredients_dispo, nb_recettes: (
            f"recettes_ia_{type_repas}_{saison}_{difficulte}_{nb_recettes}_"
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
            json_schema='''{
    "items": [
        {
            "nom": "string (recipe name)",
            "description": "string (short description)",
            "temps_preparation": "integer (minutes)",
            "temps_cuisson": "integer (minutes)",
            "portions": "integer",
            "difficulte": "string (facile|moyen|difficile)",
            "type_repas": "string (meal type)",
            "saison": "string (season)",
            "ingredients": [{"nom": "string", "quantite": "number", "unite": "string"}],
            "etapes": [{"description": "string"}]
        }
    ]
}''',
            constraints=[
                "Each recipe must be complete with all ingredients",
                "Include precise quantities and units",
                "Detail all preparation steps",
                "Respect season constraints",
                "Return EXACTLY this JSON structure with 'items' key containing the recipes array",
            ],
        )

        logger.info(f"🤖 Generating {nb_recettes} recipe suggestions")

        # IA call with auto rate limiting & parsing
        recettes = self.call_with_list_parsing_sync(
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

    def generer_variantes_recette_ia(
        self,
        nom_recette: str,
        nb_variantes: int = 3,
    ) -> list[RecetteSuggestion]:
        """Génère plusieurs variantes d'une recette spécifique avec l'IA.

        Generates multiple variations of a specific recipe (e.g., "spaghetti bolognaise")
        with different ingredients, cooking methods, or cuisines.

        Args:
            nom_recette: Name of recipe to create variations for
            nb_variantes: Number of variations to generate (1-5)

        Returns:
            List of RecetteSuggestion objects with variations
        """
        # Build context for variations
        context = f"Créer {nb_variantes} variantes différentes et intéressantes de la recette: {nom_recette}"
        context += "\nChaque variante doit avoir une twist unique (ingrédient différent, cuisine différente, technique différente)"

        # Prompt pour générer les variantes
        prompt = self.build_json_prompt(
            context=context,
            task=f"Generate {nb_variantes} different variations of {nom_recette} recipe",
            json_schema='''{
    "items": [
        {
            "nom": "string (recipe name with variation)",
            "description": "string (what makes this variation unique)",
            "temps_preparation": "integer (minutes)",
            "temps_cuisson": "integer (minutes)",
            "portions": "integer",
            "difficulte": "string (facile|moyen|difficile)",
            "type_repas": "string (meal type)",
            "saison": "string (season)",
            "ingredients": [{"nom": "string", "quantite": "number", "unite": "string"}],
            "etapes": [{"description": "string"}]
        }
    ]
}''',
            constraints=[
                "Each variation must be significantly different from the others",
                "Include variations from different cuisines or cooking methods",
                "Each recipe must be complete with ingredients and steps",
                "Vary the ingredients while keeping the essence of the original",
                "Make sure each variation is practical and achievable",
                "Return EXACTLY this JSON structure with 'items' key containing the recipes array",
            ],
        )

        logger.info(f"🤖 Generating {nb_variantes} variations of '{nom_recette}'")

        # Call IA with auto rate limiting & parsing
        variations = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=RecetteSuggestion,
            system_prompt=self.build_system_prompt(
                role="Creative chef and culinary expert",
                expertise=[
                    "Recipe variations and adaptations",
                    "Different cooking methods",
                    "International cuisines",
                    "Ingredient substitutions",
                    "Culinary creativity",
                ],
                rules=[
                    "Create truly different variations, not just minor changes",
                    "Suggest creative twists (fusion, different cuisine, new cooking method)",
                    "Keep recipes practical and achievable",
                    "Respect seasonality where applicable",
                ],
            ),
            max_items=nb_variantes,
        )

        logger.info(f"✅ Generated {len(variations)} variations of '{nom_recette}'")
        return variations

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
        print(f"[generer_version_bebe] START: recette_id={recette_id}, db={type(db)}")
        
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
        print(f"[generer_version_bebe] recette found: {recette is not None}")
        if not recette:
            print(f"[generer_version_bebe] Recipe {recette_id} not found")
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
            print(f"[generer_version_bebe] Baby version already exists for recipe {recette_id}")
            logger.info(f"📦 Baby version already exists for recipe {recette_id}")
            return existing

        logger.info(f"🤖 Generating baby-safe version for recipe {recette_id}")
        print(f"[generer_version_bebe] Generating new baby version")

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
        print(f"[generer_version_bebe] Prompt built, calling IA...")

        # Appel IA avec parsing auto
        version_data = self.call_with_parsing_sync(
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
            print(f"[generer_version_bebe] version_data is None after IA call")
            logger.warning(f"⚠️ Failed to generate baby version for recipe {recette_id}")
            raise ErreurValidation("Invalid IA response format for baby version")

        print(f"[generer_version_bebe] version_data parsed successfully: {version_data}")

        # Créer version en DB
        version = VersionRecette(
            recette_base_id=recette_id,
            type_version="bébé",
            instructions_modifiees=version_data.instructions_modifiees,
            notes_bebe=version_data.notes_bebe,
        )
        print(f"[generer_version_bebe] VersionRecette object created")
        db.add(version)
        print(f"[generer_version_bebe] Version added to db session")
        db.commit()
        print(f"[generer_version_bebe] Version committed to db")
        db.refresh(version)
        print(f"[generer_version_bebe] Version refreshed, id={version.id}")

        logger.info(f"✅ Baby version created for recipe {recette_id}")
        print(f"[generer_version_bebe] END: Returning version {version.id}")
        return version

    @with_db_session
    def generer_version_batch_cooking(self, recette_id: int, db: Session) -> VersionRecette | None:
        """Génère une version batch cooking optimisée de la recette avec l'IA.

        Adapts recipe for batch cooking preparation. Creates version in DB.
        Includes storage, freezing, and preparation timeline advice.

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
                VersionRecette.type_version == "batch cooking",
            )
            .first()
        )
        if existing:
            logger.info(f"📦 Batch cooking version already exists for recipe {recette_id}")
            return existing

        logger.info(f"🤖 Generating batch cooking version for recipe {recette_id}")

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
{etapes_str}

Preparation time: {recette.temps_preparation} minutes
Cooking time: {recette.temps_cuisson} minutes
Difficulty: {recette.difficulte}"""

        # Prompt pour adaptation batch cooking
        prompt = self.build_json_prompt(
            context=context,
            task="Adapt this recipe for batch cooking preparation",
            json_schema='''{
                "instructions_modifiees": str,
                "nombre_portions_recommande": int,
                "temps_preparation_total_heures": float,
                "conseils_conservation": str,
                "conseils_congelation": str,
                "calendrier_preparation": str
            }''',
            constraints=[
                "Increase quantities for 12+ portions",
                "Simplify steps for batch preparation",
                "Include storage duration (days/weeks)",
                "Provide freezing instructions",
                "Detail preparation timeline for the week",
                "Consider food safety guidelines",
            ],
        )

        # Appel IA avec parsing auto
        version_data = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=VersionBatchCookingGeneree,
            system_prompt=self.build_system_prompt(
                role="Expert batch cooking coach",
                expertise=[
                    "Meal prep strategies",
                    "Food preservation",
                    "Freezing techniques",
                    "Time-efficient cooking",
                    "Food safety",
                ],
                rules=[
                    "Optimize for minimum active cooking time",
                    "Maximize freezer storage efficiency",
                    "Ensure food safety at every step",
                    "Suggest portion-friendly containers",
                    "Include reheating instructions",
                ],
            ),
        )

        if not version_data:
            logger.warning(f"⚠️ Failed to generate batch cooking version for recipe {recette_id}")
            raise ErreurValidation("Invalid IA response format for batch cooking version")

        # Créer version en DB
        version = VersionRecette(
            recette_base_id=recette_id,
            type_version="batch cooking",
            instructions_modifiees=version_data.instructions_modifiees,
            notes_bebe=f"""**Portions: {version_data.nombre_portions_recommande}**
⏱️ Temps total: {version_data.temps_preparation_total_heures}h

🧊 Conservation: {version_data.conseils_conservation}

❄️ Congélation: {version_data.conseils_congelation}

📅 Calendrier: {version_data.calendrier_preparation}""",
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        logger.info(f"✅ Batch cooking version created for recipe {recette_id}")
        return version

    @with_db_session
    def generer_version_robot(
        self, recette_id: int, robot_type: str, db: Session
    ) -> VersionRecette | None:
        """Génère une version adaptée pour un robot de cuisine.

        Adapts recipe for specific cooking robots (Cookeo, Monsieur Cuisine, Airfryer, Multicooker).

        Args:
            recette_id: ID of recipe to adapt
            robot_type: Type of robot (cookeo, monsieur_cuisine, airfryer, multicooker)
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
                VersionRecette.type_version == f"robot_{robot_type}",
            )
            .first()
        )
        if existing:
            logger.info(
                f"🤖 Robot version ({robot_type}) already exists for recipe {recette_id}"
            )
            return existing

        logger.info(f"🤖 Generating {robot_type} version for recipe {recette_id}")

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
{etapes_str}

Preparation time: {recette.temps_preparation} minutes
Cooking time: {recette.temps_cuisson} minutes
Difficulty: {recette.difficulte}"""

        # Robot-specific prompts
        robot_prompts = {
            "cookeo": {
                "role": "Cookeo expert",
                "task": "Adapt this recipe specifically for a Cookeo pressure cooker",
                "constraints": [
                    "Reduce cooking times by 30-40% due to pressure cooking",
                    "Specify Cookeo mode (high pressure, low pressure, browning, steaming)",
                    "Account for liquid reduction in pressure cooking",
                    "Ensure ingredients are cut appropriately for fast cooking",
                    "Include release pressure method instructions",
                ],
                "rules": [
                    "Specify which Cookeo program or mode to use",
                    "Calculate time reductions for pressure cooking",
                    "Include natural or quick pressure release advice",
                    "Note ingredient preparation requirements",
                ],
            },
            "monsieur_cuisine": {
                "role": "Monsieur Cuisine expert",
                "task": "Adapt this recipe specifically for a Monsieur Cuisine kitchen robot",
                "constraints": [
                    "Use Monsieur Cuisine program structure (mix, chop, steam, slow cook)",
                    "Optimize ingredient sizes for robot processing",
                    "Respect robot capacity limits",
                    "Account for robot-specific cooking times",
                    "Include timing for each phase",
                ],
                "rules": [
                    "Specify program sequence for automatic cooking",
                    "Suggest portion sizes for robot capacity",
                    "Include manual stirring points if needed",
                    "Note ingredient additions timing",
                ],
            },
            "airfryer": {
                "role": "Air fryer expert",
                "task": "Adapt this recipe specifically for an air fryer (deep fryer alternative)",
                "constraints": [
                    "Reduce cooking times by 20-30% compared to oven",
                    "Lower temperature by 20°C typically",
                    "Specify basket arrangement and stirring frequency",
                    "Account for reduced oil requirements",
                    "Include portion/batch information",
                ],
                "rules": [
                    "Specify temperature and exact cooking time",
                    "Note required preheating duration",
                    "Include shaking/stirring instructions",
                    "Suggest batch cooking if needed",
                    "Mention if food needs to be arranged in basket",
                ],
            },
            "multicooker": {
                "role": "Multicooker expert",
                "task": "Adapt this recipe specifically for a programmable multicooker",
                "constraints": [
                    "Optimize for available multicooker modes (slow cook, pressure, steam, sauté)",
                    "Calculate appropriate cooking times per mode",
                    "Plan ingredient sequence for cooking mode",
                    "Ensure proper heat distribution",
                ],
                "rules": [
                    "Specify cooking mode sequence",
                    "Include exact temperature and time settings",
                    "Note ingredient addition timing between modes",
                    "Include delay start programming tips if applicable",
                ],
            },
        }

        if robot_type not in robot_prompts:
            raise ValueError(f"Unknown robot type: {robot_type}")

        robot_config = robot_prompts[robot_type]

        # Prompt pour adaptation robot
        prompt = self.build_json_prompt(
            context=context,
            task=robot_config["task"],
            json_schema='''{
                "instructions_modifiees": str,
                "reglages_robot": str,
                "temps_cuisson_adapte_minutes": int,
                "conseils_preparation": str,
                "etapes_specifiques": list[str]
            }''',
            constraints=robot_config["constraints"],
        )

        # Appel IA avec parsing auto
        version_data = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=VersionRobotGeneree,
            system_prompt=self.build_system_prompt(
                role=robot_config["role"],
                expertise=[
                    f"Cooking with {robot_type}",
                    "Recipe adaptation",
                    "Cooking time optimization",
                    "Food quality maintenance",
                ],
                rules=robot_config["rules"],
            ),
        )

        if not version_data:
            logger.warning(f"⚠️ Failed to generate {robot_type} version for recipe {recette_id}")
            raise ErreurValidation(f"Invalid IA response format for {robot_type} version")

        # Créer version en DB
        version = VersionRecette(
            recette_base_id=recette_id,
            type_version=f"robot_{robot_type}",
            instructions_modifiees=version_data.instructions_modifiees,
            notes_bebe=f"""**Réglages {robot_type.capitalize()}:**
{version_data.reglages_robot}

⏱️ Temps de cuisson: {version_data.temps_cuisson_adapte_minutes} minutes

📋 Préparation: {version_data.conseils_preparation}

🔧 Étapes spécifiques:
{chr(10).join(f"• {etape}" for etape in version_data.etapes_specifiques)}""",
        )
        db.add(version)
        db.commit()
        db.refresh(version)

        logger.info(f"✅ {robot_type} version created for recipe {recette_id}")
        return version

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : HISTORIQUE & VERSIONS
    # ═══════════════════════════════════════════════════════════

    @with_db_session
    def enregistrer_cuisson(
        self,
        recette_id: int,
        portions: int = 1,
        note: int | None = None,
        avis: str | None = None,
        db: Session | None = None,
    ) -> bool:
        """Enregistre qu'une recette a été cuisinée.
        
        Args:
            recette_id: ID de la recette
            portions: Nombre de portions cuisinées
            note: Note de 0-5 (optionnel)
            avis: Avis personnel (optionnel)
            db: Session DB injectée
            
        Returns:
            True si succès, False sinon
        """
        try:
            from datetime import date
            from src.core.models import HistoriqueRecette
            
            historique = HistoriqueRecette(
                recette_id=recette_id,
                date_cuisson=date.today(),
                portions_cuisinees=portions,
                note=note,
                avis=avis,
            )
            db.add(historique)
            db.commit()
            logger.info(f"✅ Cuisson enregistrée pour recette {recette_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur enregistrement cuisson: {e}")
            return False

    @with_db_session
    def get_historique(
        self,
        recette_id: int,
        nb_dernieres: int = 10,
        db: Session | None = None,
    ) -> list:
        """Récupère l'historique d'utilisation d'une recette.
        
        Args:
            recette_id: ID de la recette
            nb_dernieres: Nombre d'entrées à retourner
            db: Session DB injectée
            
        Returns:
            Liste des entrées d'historique
        """
        try:
            from src.core.models import HistoriqueRecette
            
            return (
                db.query(HistoriqueRecette)
                .filter(HistoriqueRecette.recette_id == recette_id)
                .order_by(HistoriqueRecette.date_cuisson.desc())
                .limit(nb_dernieres)
                .all()
            )
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return []

    @with_db_session
    def get_stats_recette(self, recette_id: int, db: Session | None = None) -> dict:
        """Récupère les statistiques d'utilisation d'une recette.
        
        Args:
            recette_id: ID de la recette
            db: Session DB injectée
            
        Returns:
            Dict avec nb_cuissons, derniere_cuisson, note_moyenne, etc.
        """
        try:
            from datetime import date
            from src.core.models import HistoriqueRecette
            
            historique = (
                db.query(HistoriqueRecette)
                .filter(HistoriqueRecette.recette_id == recette_id)
                .all()
            )
            
            if not historique:
                return {
                    "nb_cuissons": 0,
                    "derniere_cuisson": None,
                    "note_moyenne": None,
                    "total_portions": 0,
                    "jours_depuis_derniere": None,
                }
            
            notes = [h.note for h in historique if h.note is not None]
            derniere = historique[0]
            
            return {
                "nb_cuissons": len(historique),
                "derniere_cuisson": derniere.date_cuisson,
                "note_moyenne": sum(notes) / len(notes) if notes else None,
                "total_portions": sum(h.portions_cuisinees for h in historique),
                "jours_depuis_derniere": (date.today() - derniere.date_cuisson).days,
            }
        except Exception as e:
            logger.error(f"Erreur stats recette: {e}")
            return {}

    @with_db_session
    def get_versions(self, recette_id: int, db: Session | None = None) -> list:
        """Récupère toutes les versions d'une recette.
        
        Args:
            recette_id: ID de la recette
            db: Session DB injectée
            
        Returns:
            Liste des VersionRecette
        """
        try:
            return (
                db.query(VersionRecette)
                .filter(VersionRecette.recette_base_id == recette_id)
                .all()
            )
        except Exception as e:
            logger.error(f"Erreur récupération versions: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # SECTION 4 : IMPORT/EXPORT (REFACTORED)
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
    # SECTION 5 : HELPERS PRIVÉS (REFACTORED)
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
    "VersionBatchCookingGeneree",
    "VersionRobotGeneree",
    "get_recette_service",
]
