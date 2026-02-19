"""
Service Recettes Unifié (REFACTORING PHASE 2)

✅ Utilise @avec_session_db et @avec_cache (Phase 1)
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

from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.caching import Cache
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.errors_base import ErreurNonTrouve, ErreurValidation
from src.core.models import (
    EtapeRecette,
    Ingredient,
    Recette,
    RecetteIngredient,
    VersionRecette,
)
from src.core.validation import EtapeInput, IngredientInput, RecetteInput
from src.services.core.base import BaseAIService, BaseService, RecipeAIMixin

from .recettes_ia_generation import RecettesIAGenerationMixin
from .types import (
    RecetteSuggestion,
    VersionBatchCookingGeneree,
    VersionBebeGeneree,
    VersionRobotGeneree,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE RECETTES UNIFIÉ (AVEC HÉRITAGE MULTIPLE)
# ═══════════════════════════════════════════════════════════


class ServiceRecettes(
    BaseService[Recette], BaseAIService, RecipeAIMixin, RecettesIAGenerationMixin
):
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

    @avec_cache(ttl=3600, key_func=lambda self, recette_id: f"recette_full_{recette_id}")
    @avec_session_db
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

    @avec_session_db
    def get_by_type(self, type_repas: str, db: Session) -> list[Recette]:
        """Récupère les recettes d'un type donné."""
        try:
            return db.query(Recette).filter(Recette.type_repas == type_repas).all()
        except Exception as e:
            logger.error(f"Erreur récupération recettes par type {type_repas}: {e}")
            return []

    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    @avec_session_db
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

        # Conversion des ingrédients en IngredientInput objects si ce sont des dicts
        ingredients_data = data.get("ingredients") or []
        if ingredients_data and isinstance(ingredients_data[0], dict):
            data["ingredients"] = [
                IngredientInput(
                    nom=ing.get("nom", ""),
                    quantite=ing.get("quantite", 1.0),
                    unite=ing.get("unite", ""),
                )
                for ing in ingredients_data
            ]

        # Conversion des étapes en EtapeInput objects si ce sont des dicts
        etapes_data = data.get("etapes") or []
        if etapes_data and isinstance(etapes_data[0], dict):
            data["etapes"] = [
                EtapeInput(
                    ordre=idx + 1,
                    description=etape.get("description", ""),
                    duree=etape.get("duree"),
                )
                for idx, etape in enumerate(etapes_data)
            ]

        # Validation avec Pydantic
        try:
            validated = RecetteInput(**data)
        except Exception as e:
            logger.error(f"Validation error: {e} - Data: {data}")
            raise ErreurValidation(f"Données invalides: {str(e)}") from e

        # Créer recette avec updated_at
        recette_dict = validated.model_dump(exclude={"ingredients", "etapes"})
        recette_dict["updated_at"] = datetime.utcnow()  # â† Requis par le trigger PostgreSQL
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

    @avec_session_db
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
    # NOTE: Les méthodes de génération IA (generer_recettes_ia,
    # generer_variantes_recette_ia, generer_version_bebe,
    # generer_version_batch_cooking, generer_version_robot) sont
    # fournies par RecettesIAGenerationMixin (voir recettes_ia_generation.py)
    # ═══════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : HISTORIQUE & VERSIONS
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
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

    @avec_session_db
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

    @avec_session_db
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
                db.query(HistoriqueRecette).filter(HistoriqueRecette.recette_id == recette_id).all()
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

    @avec_session_db
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
                db.query(VersionRecette).filter(VersionRecette.recette_base_id == recette_id).all()
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
# ALIASES (compatibilité avec l'ancien code)
# ═══════════════════════════════════════════════════════════

RecetteService = ServiceRecettes


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON - LAZY LOADING
# ═══════════════════════════════════════════════════════════

_service_recettes = None


def obtenir_service_recettes() -> ServiceRecettes:
    """Obtient ou crée l'instance globale ServiceRecettes."""
    global _service_recettes
    if _service_recettes is None:
        _service_recettes = ServiceRecettes()
    return _service_recettes


# Alias anglais pour compatibilité
get_recette_service = obtenir_service_recettes
recette_service = None


__all__ = [
    # Service principal
    "ServiceRecettes",
    "obtenir_service_recettes",
    # Aliases pour compatibilité
    "RecetteService",
    "get_recette_service",
    "recette_service",
]
