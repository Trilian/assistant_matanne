"""
Service Planning de Base (REFACTORING PHASE 2)

✅ Utilise @avec_session_db et @avec_cache (Phase 1)
✅ Validation Pydantic centralisée
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit
"""

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.caching import Cache
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import Planning, Repas
from src.services.core.base import BaseAIService, BaseService, PlanningAIMixin

from .planning_ia_mixin import PlanningIAGenerationMixin
from .types import JourPlanning, ParametresEquilibre
from .utils import (
    determine_protein_type,
    get_weekday_names,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING
# ═══════════════════════════════════════════════════════════


class ServicePlanning(
    BaseService[Planning], BaseAIService, PlanningAIMixin, PlanningIAGenerationMixin
):
    """
    Service complet pour le planning hebdomadaire.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - PlanningAIMixin → Contextes métier planning

    Fonctionnalités:
    - CRUD optimisé avec cache
    - Génération IA planning hebdomadaire
    - Gestion repas par jour
    """

    def __init__(self):
        BaseService.__init__(self, Planning, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="planning",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="planning",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CRUD & PLANNING (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=1800, key_func=lambda self, planning_id=None, **kw: "planning_active")
    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def get_planning(
        self, planning_id: int | None = None, db: Session | None = None
    ) -> Planning | None:
        """Get the active or specified planning with eager loading of meals and recettes.

        Args:
            planning_id: Specific planning ID, or None to get active planning
            db: Database session (injected by @avec_session_db)

        Returns:
            Planning object with repas and recettes eagerly loaded, or None if not found
        """
        from sqlalchemy.orm import selectinload

        from src.core.models import Recette

        if planning_id:
            planning = (
                db.query(Planning)
                .options(
                    selectinload(Planning.repas)
                    .selectinload(Repas.recette)
                    .selectinload(Recette.versions)
                )
                .filter(Planning.id == planning_id)
                .first()
            )
        else:
            planning = (
                db.query(Planning)
                .options(
                    selectinload(Planning.repas)
                    .selectinload(Repas.recette)
                    .selectinload(Recette.versions)
                )
                .filter(Planning.actif)
                .first()
            )

        if not planning:
            logger.debug("ℹ️ Planning not found")
            return None

        return planning

    @avec_cache(ttl=1800, key_func=lambda self, planning_id, **kw: f"planning_full_{planning_id}")
    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def get_planning_complet(
        self, planning_id: int, db: Session | None = None
    ) -> dict[str, Any] | None:
        """Récupère un planning avec tous ses repas.

        Retrieves complete planning with all meals organized by day.
        Results are cached for 30 minutes.

        Args:
            planning_id: ID of the planning to retrieve
            db: Database session (injected by @avec_session_db)

        Returns:
            Dict with planning data and meals organized by date, or None if not found
        """
        planning = (
            db.query(Planning)
            .options(joinedload(Planning.repas).joinedload(Repas.recette))
            .filter(Planning.id == planning_id)
            .first()
        )

        if not planning:
            logger.warning(f"⚠️ Planning {planning_id} not found")
            return None

        repas_par_jour = {}
        for repas in planning.repas:
            jour_str = repas.date_repas.strftime("%Y-%m-%d")
            if jour_str not in repas_par_jour:
                repas_par_jour[jour_str] = []

            repas_par_jour[jour_str].append(
                {
                    "id": repas.id,
                    "type_repas": repas.type_repas,
                    "recette_id": repas.recette_id,
                    "recette_nom": repas.recette.nom if repas.recette else None,
                    "prepare": repas.prepare,
                    "notes": repas.notes,
                }
            )

        result = {
            "id": planning.id,
            "nom": planning.nom,
            "semaine_debut": planning.semaine_debut.isoformat(),
            "semaine_fin": planning.semaine_fin.isoformat(),
            "actif": planning.actif,
            "genere_par_ia": planning.genere_par_ia,
            "repas_par_jour": repas_par_jour,
        }

        logger.info(f"✅ Retrieved planning {planning_id} with {len(repas_par_jour)} days")
        return result

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: GÉNÉRATION AVEC CHOIX
    # ═══════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════
    # SECTION 2: GÉNÉRATION AVEC CHOIX (NOUVEAU)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_planning_avec_choix(
        self,
        semaine_debut: date,
        recettes_selection: dict[str, int],  # {jour_index: recette_id}
        enfants_adaptes: list[int] | None = None,
        db: Session | None = None,
    ) -> Planning | None:
        """Crée un planning à partir des choix de l'utilisateur.

        Args:
            semaine_debut: Date de début
            recettes_selection: Mapping jour → recette_id choisi
            enfants_adaptes: IDs des enfants pour adapter (Jules, etc.)
            db: Database session

        Returns:
            Planning créé avec tous les repas
        """
        from src.core.models import Recette

        semaine_fin = semaine_debut + timedelta(days=6)

        planning = Planning(
            nom=f"Planning {semaine_debut.strftime('%d/%m')}",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            actif=True,
            genere_par_ia=False,
        )
        db.add(planning)
        db.flush()

        jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        for idx, jour_name in enumerate(jours_semaine):
            date_jour = semaine_debut + timedelta(days=idx)
            jour_key = f"jour_{idx}"

            # Récupérer la recette sélectionnée
            recette_id = recettes_selection.get(jour_key)
            if not recette_id:
                logger.warning(f"⚠️ No recipe selected for {jour_name}")
                continue

            recette = db.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                logger.warning(f"⚠️ Recipe {recette_id} not found for {jour_name}")
                continue

            # Créer repas (on crée juste le dîner pour simplifier en départ)
            repas = Repas(
                planning_id=planning.id,
                recette_id=recette.id,
                date_repas=date_jour,
                type_repas="dîner",
                notes=f"Repas du {jour_name}",
            )
            db.add(repas)

        db.commit()
        db.refresh(planning)

        logger.info(f"✅ Created custom planning for {semaine_debut}")
        return planning

    # ═══════════════════════════════════════════════════════════
    # SECTION 4: AGRÉGATION COURSES (NOUVEAU)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def agréger_courses_pour_planning(
        self,
        planning_id: int,
        db: Session | None = None,
    ) -> list[dict]:
        """Agrège les ingrédients de toutes les recettes du planning.

        Retourne une liste d'ingrédients uniques avec quantités totales.

        Args:
            planning_id: ID du planning
            db: Database session

        Returns:
            List de dicts {ingredient, quantite, unite, rayon, priorite}
        """
        from src.core.models import Planning, Recette

        # Récupérer le planning avec tous ses repas et recettes
        planning = db.query(Planning).filter(Planning.id == planning_id).first()

        if not planning or not planning.repas:
            logger.warning(f"⚠️ Planning {planning_id} pas trouvé ou pas de repas")
            return []

        # Agréger les ingrédients
        ingredients_aggregated = {}  # {nom: {quantite: 0, unite, rayon, priorite}}

        for repas in planning.repas:
            if not repas.recette_id:
                continue

            # Charger la recette avec ses ingrédients
            recette = db.query(Recette).filter(Recette.id == repas.recette_id).first()

            if not recette or not recette.ingredients:
                continue

            # Parcourir les ingrédients de cette recette
            for recette_ingredient in recette.ingredients:
                ingredient = recette_ingredient.ingredient
                if not ingredient:
                    continue

                nom = ingredient.nom
                quantite = recette_ingredient.quantite or 1
                unite = recette_ingredient.unite or ingredient.unite or "pcs"
                rayon = ingredient.categorie or "autre"

                # Agréger
                if nom not in ingredients_aggregated:
                    ingredients_aggregated[nom] = {
                        "nom": nom,
                        "quantite": quantite,
                        "unite": unite,
                        "rayon": rayon,
                        "priorite": "moyenne",  # Par défaut
                        "repas_count": 1,
                    }
                else:
                    # Augmenter la quantité (même unité supposée)
                    if ingredients_aggregated[nom]["unite"] == unite:
                        ingredients_aggregated[nom]["quantite"] += quantite
                    ingredients_aggregated[nom]["repas_count"] += 1

        # Trier par priorité (rayon) et quantité
        courses_list = sorted(
            ingredients_aggregated.values(), key=lambda x: (x["rayon"], -x["quantite"])
        )

        logger.info(f"✅ Agrégé {len(courses_list)} ingrédients pour planning {planning_id}")
        return courses_list


# ═══════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════


# INSTANCE SINGLETON - LAZY LOADING
_service_planning = None


def obtenir_service_planning() -> ServicePlanning:
    """Obtenir ou créer l'instance globale de ServicePlanning."""
    global _service_planning
    if _service_planning is None:
        _service_planning = ServicePlanning()
    return _service_planning


def get_planning_service() -> ServicePlanning:
    """Factory for planning service (English alias)."""
    return obtenir_service_planning()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    # Classe principale
    "ServicePlanning",
    # Factory
    "obtenir_service_planning",
    "get_planning_service",
]
