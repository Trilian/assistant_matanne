"""
Mixin de génération de versions IA pour le service recettes.

Contient les méthodes de génération de versions avec persistance DB :
- generer_version_bebe : Version adaptée bébé
- generer_version_batch_cooking : Version batch cooking
- generer_version_robot : Version robot de cuisine

Ces méthodes utilisent `self` pour accéder aux méthodes héritées de
BaseAIService et RecipeAIMixin (build_json_prompt, build_system_prompt,
call_with_parsing_sync).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session, joinedload

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.exceptions import ErreurNonTrouve, ErreurValidation
from src.core.models import (
    Recette,
    RecetteIngredient,
    VersionRecette,
)
from src.core.monitoring import chronometre
from src.services.core.event_bus_mixin import emettre_evenement_simple

from .types import (
    VersionBatchCookingGeneree,
    VersionBebeGeneree,
    VersionRobotGeneree,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ["RecettesIAVersionsMixin"]


class RecettesIAVersionsMixin:
    """Mixin fournissant les méthodes de génération de versions IA pour les recettes.

    Doit être utilisé avec BaseAIService et RecipeAIMixin dans la classe finale.
    Accède via `self` à :
    - build_json_prompt() (BaseAIService)
    - build_system_prompt() (BaseAIService)
    - call_with_parsing_sync() (BaseAIService)
    """

    @avec_gestion_erreurs(default_return=None)
    @avec_cache(ttl=3600, key_func=lambda self, rid: f"version_bebe_{rid}")
    @chronometre("ia.recettes.version_bebe", seuil_alerte_ms=15000)
    @avec_session_db
    def generer_version_bebe(self, recette_id: int, db: Session) -> VersionRecette | None:
        """Génère une version bébé sécurisée de la recette avec l'IA.

        Adapts recipe for babies (12+ months). Creates version in DB.
        Includes safety notes and age recommendations.

        Args:
            recette_id: ID of recipe to adapt
            db: Database session (injected by @avec_session_db)

        Returns:
            VersionRecette object or None if generation fails
        """
        logger.debug("[generer_version_bebe] START: recette_id=%s", recette_id)

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
        logger.debug("[generer_version_bebe] recette found: %s", recette is not None)
        if not recette:
            logger.debug("[generer_version_bebe] Recipe %s not found", recette_id)
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
            logger.debug(
                "[generer_version_bebe] Baby version already exists for recipe %s", recette_id
            )
            logger.info(f"📦 Baby version already exists for recipe {recette_id}")
            return existing

        logger.info(f"🤖 Generating baby-safe version for recipe {recette_id}")
        logger.debug("[generer_version_bebe] Generating new baby version")

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
        logger.debug("[generer_version_bebe] Prompt built, calling IA...")

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
            logger.debug("[generer_version_bebe] version_data is None after IA call")
            logger.warning(f"⚠️ Failed to generate baby version for recipe {recette_id}")
            raise ErreurValidation("Invalid IA response format for baby version")

        logger.debug("[generer_version_bebe] version_data parsed: %s", version_data)

        # Créer version en DB
        version = VersionRecette(
            recette_base_id=recette_id,
            type_version="bébé",
            instructions_modifiees=version_data.instructions_modifiees,
            notes_bebe=version_data.notes_bebe,
        )
        logger.debug("[generer_version_bebe] VersionRecette object created")
        db.add(version)
        logger.debug("[generer_version_bebe] Version added to db session")
        db.commit()
        logger.debug("[generer_version_bebe] Version committed to db")
        db.refresh(version)
        logger.debug("[generer_version_bebe] Version refreshed, id=%s", version.id)

        logger.info(f"✅ Baby version created for recipe {recette_id}")
        logger.debug("[generer_version_bebe] END: Returning version %s", version.id)

        emettre_evenement_simple(
            "recette.modifie",
            {"recette_id": recette_id, "nom": "", "action": "version_bebe_creee"},
            source="recettes_ia_versions",
        )
        return version

    @avec_session_db
    def generer_version_batch_cooking(self, recette_id: int, db: Session) -> VersionRecette | None:
        """Génère une version batch cooking optimisée de la recette avec l'IA.

        Adapts recipe for batch cooking preparation. Creates version in DB.
        Includes storage, freezing, and preparation timeline advice.

        Args:
            recette_id: ID of recipe to adapt
            db: Database session (injected by @avec_session_db)

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
            json_schema="""{
                "instructions_modifiees": str,
                "nombre_portions_recommande": int,
                "temps_preparation_total_heures": float,
                "conseils_conservation": str,
                "conseils_congelation": str,
                "calendrier_preparation": str
            }""",
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

        emettre_evenement_simple(
            "recette.modifie",
            {"recette_id": recette_id, "nom": "", "action": "version_batch_creee"},
            source="recettes_ia_versions",
        )
        return version

    @avec_session_db
    def generer_version_robot(
        self, recette_id: int, robot_type: str, db: Session
    ) -> VersionRecette | None:
        """Génère une version adaptée pour un robot de cuisine.

        Adapts recipe for specific cooking robots (Cookeo, Monsieur Cuisine, Airfryer, Multicooker).

        Args:
            recette_id: ID of recipe to adapt
            robot_type: Type of robot (cookeo, monsieur_cuisine, airfryer, multicooker)
            db: Database session (injected by @avec_session_db)

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
            logger.info(f"🤖 Robot version ({robot_type}) already exists for recipe {recette_id}")
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
            json_schema="""{
                "instructions_modifiees": str,
                "reglages_robot": str,
                "temps_cuisson_adapte_minutes": int,
                "conseils_preparation": str,
                "etapes_specifiques": list[str]
            }""",
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

        emettre_evenement_simple(
            "recette.modifie",
            {"recette_id": recette_id, "nom": "", "action": f"version_{robot_type}_creee"},
            source="recettes_ia_versions",
        )
        return version
