"""
Service Recettes Unifié (service unifié)

✅ Utilise @avec_session_db et @avec_cache
✅ Validation Pydantic centralisée (RecetteInput, etc.)
✅ Type hints complets pour meilleur IDE support
✅ Services testables
✅ Mixins extraits pour réduire LOC

Service complet pour les recettes fusionnant :
- recette_service.py (CRUD + recherche)
- recette_ai_service.py (Génération IA)
- recette_io_service.py (Import/Export)
- recette_version_service.py (Versions bébé/batch)

Mixins extraits:
- recherche_mixin.py: Recherche avancée multi-critères
- io_mixin.py: Import/Export CSV/JSON
"""

import logging

from sqlalchemy.orm import Session

from src.core.ai import obtenir_client_ia
from src.core.caching import obtenir_cache
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db, avec_validation
from src.core.exceptions import ErreurValidation
from src.core.models import (
    EtapeRecette,
    Ingredient,
    Recette,
    RecetteIngredient,
    VersionRecette,
)
from src.core.monitoring import chronometre
from src.core.validation import RecetteInput
from src.services.core.base import BaseAIService, BaseService, RecipeAIMixin
from src.services.core.events import obtenir_bus

from .io_mixin import RecetteIOMixin
from .recettes_ia_suggestions import RecettesIASuggestionsMixin
from .recettes_ia_versions import RecettesIAVersionsMixin
from .recherche_mixin import RecetteRechercheMixin
from .types import (
    RecetteSuggestion,
    VersionBatchCookingGeneree,
    VersionBebeGeneree,
    VersionRobotGeneree,
)

logger = logging.getLogger(__name__)


def _normaliser_texte_mojibake(valeur: str | None) -> str | None:
    """Corrige les textes UTF-8 mal decodes en latin-1 (ex: dÃ®ner -> dîner)."""
    if not isinstance(valeur, str):
        return valeur
    if "Ã" not in valeur and "Â" not in valeur:
        return valeur
    try:
        return valeur.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return valeur


# ═══════════════════════════════════════════════════════════
# SERVICE RECETTES UNIFIÉ (AVEC HÉRITAGE MULTIPLE)
# ═══════════════════════════════════════════════════════════


class ServiceRecettes(
    BaseService[Recette],
    BaseAIService,
    RecipeAIMixin,
    RecettesIASuggestionsMixin,
    RecettesIAVersionsMixin,
    RecetteRechercheMixin,
    RecetteIOMixin,
):
    """
    Service complet pour les recettes.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - RecipeAIMixin → Contextes métier recettes
    - RecetteRechercheMixin → Recherche avancée multi-critères
    - RecetteIOMixin → Import/Export CSV/JSON

    Fonctionnalités :
    - CRUD optimisé avec cache
    - Génération IA (rate limiting + cache AUTO)
    - Import/Export (CSV, JSON)
    - Recherche avancée
    - Statistiques
    """

    def __init__(self):
        # MRO coopératif: tous les arguments passés via kwargs
        super().__init__(
            # Arguments pour BaseService
            model=Recette,
            cache_ttl=3600,
            # Arguments pour BaseAIService
            client=obtenir_client_ia(),
            cache_prefix="recettes",
            default_ttl=3600,
            default_temperature=0.8,  # Plus créatif pour recettes
            service_name="recettes",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : CRUD OPTIMISÉ
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def delete_all(self, db: Session) -> int:
        """Supprime toutes les recettes et leurs données associées."""
        # Supprimer les données liées en cascade
        count_etapes = db.query(EtapeRecette).delete()
        count_ri = db.query(RecetteIngredient).delete()
        count_versions = db.query(VersionRecette).delete()
        count = db.query(Recette).delete()
        db.commit()
        self._invalider_cache()
        logger.info(
            f"Toutes les recettes supprimées ({count} recettes, "
            f"{count_ri} ingrédients, {count_etapes} étapes, {count_versions} versions)"
        )
        return count

    @chronometre("recettes.chargement_complet", seuil_alerte_ms=1500)
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

        # ── Normalisation des données d'entrée (formats variés JSON/IA/import) ──
        data = dict(data)  # copie pour ne pas muter l'original

        # Normaliser etapes : accepte strings simples OU dicts
        etapes_raw = data.get("etapes") or []
        etapes_normalised = []
        for idx, etape in enumerate(etapes_raw):
            if isinstance(etape, str):
                etapes_normalised.append({"description": etape, "ordre": idx + 1})
            elif isinstance(etape, dict):
                if "ordre" not in etape and "numero" not in etape:
                    etape = dict(etape)
                    etape["ordre"] = idx + 1
                etapes_normalised.append(etape)
        data["etapes"] = etapes_normalised

        # Normaliser ingrédients : convertir unite '' → None
        ings_raw = data.get("ingredients") or []
        ings_normalised = []
        for ing in ings_raw:
            if isinstance(ing, dict):
                ing = dict(ing)
                if ing.get("unite") == "":
                    ing["unite"] = None
                ings_normalised.append(ing)
        data["ingredients"] = ings_normalised

        # Normaliser temps_preparation : minimum 1 minute
        if (data.get("temps_preparation") or 0) < 1:
            data["temps_preparation"] = 1

        # Normaliser temps_cuisson : minimum 0
        if (data.get("temps_cuisson") or 0) < 0:
            data["temps_cuisson"] = 0

        # Normaliser categorie : NOT NULL en DB, dériver depuis type_repas si absent
        data["type_repas"] = _normaliser_texte_mojibake(data.get("type_repas"))
        data["saison"] = _normaliser_texte_mojibake(data.get("saison"))

        if not data.get("categorie"):
            _type_to_cat = {
                "petit_déjeuner": "Petit-déjeuner",
                "déjeuner": "Plat",
                "dîner": "Plat",
                "goûter": "Goûter",
                "apéritif": "Apéritif",
                "dessert": "Dessert",
            }
            data["categorie"] = _type_to_cat.get((data.get("type_repas") or "").lower(), "Plat")
        # ── Fin normalisation ──

        # Validation Pydantic
        try:
            validated = RecetteInput(**data)
        except Exception as e:
            raise ErreurValidation(f"Données invalides: {e}") from e

        # Créer recette (exclure les relations)
        recette_dict = validated.model_dump(exclude={"ingredients", "etapes"})
        recette = Recette(**recette_dict)
        db.add(recette)
        db.flush()

        # Créer ingrédients (idempotent : sommer si même ingrédient déjà présent)
        for ing_data in validated.ingredients or []:
            ingredient = self._find_or_create_ingredient(db, ing_data.nom)
            quantite = ing_data.quantite or 1.0
            unite = ing_data.unite or "pièce"
            existant = (
                db.query(RecetteIngredient)
                .filter_by(recette_id=recette.id, ingredient_id=ingredient.id)
                .first()
            )
            if existant:
                existant.quantite += quantite
            else:
                db.add(RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient.id,
                    quantite=quantite,
                    unite=unite,
                ))

        # Créer étapes
        for idx, etape_data in enumerate(validated.etapes or []):
            etape = EtapeRecette(
                recette_id=recette.id,
                ordre=idx + 1,
                titre=getattr(etape_data, "titre", None),
                description=etape_data.description,
                duree=etape_data.duree,
                robots_optionnels=getattr(etape_data, "robots_optionnels", None),
                temperature=getattr(etape_data, "temperature", None),
                est_supervision=getattr(etape_data, "est_supervision", False),
                groupe_parallele=getattr(etape_data, "groupe_parallele", 0),
            )
            db.add(etape)

        db.commit()
        db.refresh(recette)

        # Invalider cache
        obtenir_cache().invalidate(pattern="recettes")

        # Émettre événement domaine
        obtenir_bus().emettre(
            "recette.creee",
            {"recette_id": recette.id, "nom": recette.nom, "type_repas": recette.type_repas},
            source="recettes",
        )

        logger.info(f"✅ Recette créée : {recette.nom} (ID: {recette.id})")
        return recette

    # ═══════════════════════════════════════════════════════════
    # SECTION 1b : DEDUPLICATION
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def find_existing_recette(self, nom: str, db: Session | None = None) -> Recette | None:
        """Cherche une recette existante par nom normalisé (sans accents, lowercase).

        Args:
            nom: Nom de la recette à chercher
            db: Session DB (injectée)

        Returns:
            Recette existante ou None si non trouvée
        """
        from .utils import normaliser_nom_recette

        nom_normalise = normaliser_nom_recette(nom)
        if not nom_normalise:
            return None

        # Utiliser le premier mot comme filtre ilike pour restreindre les candidats
        first_word = nom_normalise.split()[0] if nom_normalise else ""
        candidates = db.query(Recette).filter(Recette.nom.ilike(f"%{first_word}%")).limit(50).all()

        for recette in candidates:
            if normaliser_nom_recette(recette.nom) == nom_normalise:
                return recette

        return None

    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : GÉNÉRATION IA (AVEC CACHE ET VALIDATION)
    # NOTE: Les méthodes de génération IA (generer_recettes_ia,
    # generer_variantes_recette_ia, generer_version_bebe,
    # generer_version_batch_cooking, generer_version_robot) sont
    # fournies par RecettesIASuggestionsMixin et RecettesIAVersionsMixin
    # ═══════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════
    # SECTION 2b : RECHERCHE & FILTRAGE
    # NOTE: Les méthodes search_advanced, get_by_type, etc. sont
    # fournies par RecetteRechercheMixin (voir recherche_mixin.py)
    # ═══════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════
    # SECTION 2c : IMPORT/EXPORT
    # NOTE: Les méthodes export_to_csv, export_to_json,
    # create_from_import, _parser_ingredient_texte sont
    # fournies par RecetteIOMixin (voir io_mixin.py)
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
        feedback: str | None = None,
        db: Session | None = None,
    ) -> bool:
        """Enregistre qu'une recette a été cuisinée.

        Args:
            recette_id: ID de la recette
            portions: Nombre de portions cuisinées
            note: Déprécié, ignoré (conservé pour compatibilité)
            avis: Avis personnel (optionnel)
            feedback: Appréciation rapide like/dislike/neutral (optionnel)
            db: Session DB injectée

        Returns:
            True si succès, False sinon
        """
        try:
            from datetime import date

            from src.core.models import HistoriqueRecette

            historique = HistoriqueRecette(
                recette_id=recette_id,
                date_preparation=date.today(),
                portions_cuisinees=portions,
                avis=avis,
                feedback=feedback or "neutral",
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
                .order_by(HistoriqueRecette.date_preparation.desc())
                .limit(nb_dernieres)
                .all()
            )
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return []

    @avec_session_db
    def get_stats(self, db: Session | None = None, count_filters: dict | None = None) -> dict:  # noqa: E501
        """Retourne les statistiques globales des recettes.

        Args:
            count_filters: Dictionnaire optionnel de comptages supplémentaires.
                Format: {"cle": {"colonne": valeur | {"lte": val, "gte": val}}}

        Returns:
            Dict avec 'total' et métriques agrégées.
        """
        try:
            total = db.query(Recette).count()
            result: dict = {"total": total}

            # Favoris (colonne optionnelle)
            try:
                favoris = db.query(Recette).filter(Recette.est_favori == True).count()  # noqa: E712
                result["favoris"] = favoris
            except Exception:
                result["favoris"] = 0

            # Comptages supplémentaires demandés par l'appelant
            if count_filters:
                for name, filters in count_filters.items():
                    try:
                        q = db.query(Recette)
                        for col_name, val in filters.items():
                            col = getattr(Recette, col_name, None)
                            if col is None:
                                raise AttributeError(f"Colonne inconnue: {col_name}")
                            if isinstance(val, dict):
                                if "lte" in val:
                                    q = q.filter(col <= val["lte"])
                                if "gte" in val:
                                    q = q.filter(col >= val["gte"])
                                if "eq" in val:
                                    q = q.filter(col == val["eq"])
                            else:
                                q = q.filter(col == val)
                        result[name] = q.count()
                    except Exception:
                        result[name] = 0

            return result
        except Exception as e:
            logger.error(f"Erreur get_stats recettes: {e}")
            return {"total": 0, "favoris": 0}

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
                    "total_portions": 0,
                    "jours_depuis_derniere": None,
                    "note_moyenne": None,
                }

            derniere = historique[0]

            return {
                "nb_cuissons": len(historique),
                "derniere_cuisson": derniere.date_preparation,
                "total_portions": sum(h.portions_cuisinees for h in historique),
                "jours_depuis_derniere": (date.today() - derniere.date_preparation).days,
                "note_moyenne": None,
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
    # SECTION 4 : IMPORT/EXPORT
    # NOTE: Les méthodes export_to_csv, export_to_json,
    # create_from_import sont fournies par RecetteIOMixin
    # (voir io_mixin.py)
    # ═══════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════
    # SECTION 5 : HELPERS PRIVÉS (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    def _find_or_create_ingredient(self, db: Session, nom: str) -> Ingredient:
        """Finds or creates an ingredient (case-insensitive lookup).

        Args:
            db: Database session
            nom: Ingredient name

        Returns:
            Ingredient object (existing or newly created)
        """
        from sqlalchemy import func

        nom_normalise = nom.strip().title()
        ingredient = (
            db.query(Ingredient)
            .filter(func.lower(Ingredient.nom) == nom_normalise.lower())
            .first()
        )
        if not ingredient:
            ingredient = Ingredient(nom=nom_normalise, unite="pcs", categorie="Autre")
            db.add(ingredient)
            db.flush()
            logger.debug(f"Created ingredient: {nom_normalise}")
        return ingredient


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON — Via ServiceRegistry (thread-safe)
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("recettes", tags={"cuisine", "ia", "crud"})
def obtenir_service_recettes() -> ServiceRecettes:
    """Obtient ou crée l'instance ServiceRecettes (via registre, thread-safe)."""
    return ServiceRecettes()


def obtenir_recipes_service() -> ServiceRecettes:
    """Factory for recipes service (English alias)."""
    return obtenir_service_recettes()


__all__ = [
    "ServiceRecettes",
    "obtenir_service_recettes",
    "get_recipes_service",
]


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_recipes_service = obtenir_recipes_service  # alias rétrocompatibilité
