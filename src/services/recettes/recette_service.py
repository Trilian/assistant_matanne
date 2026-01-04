"""
Service Recettes - CRUD Optimisé

Service principal pour la gestion des recettes avec :
- Opérations CRUD complètes
- Chargement optimisé (évite N+1 queries)
- Recherche avancée multi-critères
- Cache automatique
- Gestion des relations (ingrédients, étapes)
"""
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import joinedload, Session

from src.core import (
    BaseService,
    obtenir_contexte_db,
    handle_errors,
    Cache,
    ErreurValidation,
    ErreurNonTrouve,
)
from src.core.models import (
    Recette,
    RecetteIngredient,
    EtapeRecette,
    Ingredient,
)
from src.utils import find_or_create_ingredient

logger = logging.getLogger(__name__)


class RecetteService(BaseService[Recette]):
    """
    Service CRUD pour les recettes.

    Hérite de BaseService avec fonctionnalités spécifiques recettes :
    - Chargement avec relations optimisé
    - Création complète (recette + ingrédients + étapes)
    - Recherche multi-critères
    - Statistiques avancées
    """

    def __init__(self):
        """Initialise le service avec cache 1h."""
        super().__init__(Recette, cache_ttl=3600)

    # ═══════════════════════════════════════════════════════════
    # LECTURE OPTIMISÉE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=None)
    def get_by_id_full(self, recette_id: int) -> Optional[Recette]:
        """
        Récupère une recette avec toutes ses relations.

        Optimisé avec joinedload pour éviter N+1 queries.

        Args:
            recette_id: ID de la recette

        Returns:
            Recette complète avec ingrédients et étapes, ou None

        Example:
            >>> recette = recette_service.get_by_id_full(42)
            >>> print(recette.ingredients[0].ingredient.nom)
        """
        cache_key = f"recette_full_{recette_id}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)

        if cached:
            logger.debug(f"Cache HIT: {cache_key}")
            return cached

        with obtenir_contexte_db() as db:
            recette = (
                db.query(Recette)
                .options(
                    joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                    joinedload(Recette.etapes)
                )
                .filter(Recette.id == recette_id)
                .first()
            )

            if recette:
                Cache.definir(
                    cache_key,
                    recette,
                    ttl=self.cache_ttl,
                    dependencies=[f"recette_{recette_id}", "recettes"]
                )

            return recette

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_all_with_stats(
            self,
            filters: Optional[Dict] = None,
            limit: int = 100
    ) -> List[Dict]:
        """
        Récupère toutes les recettes avec statistiques enrichies.

        Args:
            filters: Filtres optionnels (saison, difficulté, etc.)
            limit: Nombre maximum de résultats

        Returns:
            Liste de recettes enrichies
        """
        recettes = self.get_all(filters=filters, limit=limit)

        return [
            {
                "id": r.id,
                "nom": r.nom,
                "description": r.description,
                "temps_total": r.temps_preparation + r.temps_cuisson,
                "temps_preparation": r.temps_preparation,
                "temps_cuisson": r.temps_cuisson,
                "portions": r.portions,
                "difficulte": r.difficulte,
                "type_repas": r.type_repas,
                "saison": r.saison,
                "est_rapide": r.est_rapide,
                "compatible_bebe": r.compatible_bebe,
                "compatible_batch": r.compatible_batch,
                "url_image": r.url_image,
                "nb_ingredients": len(r.ingredients) if hasattr(r, 'ingredients') else 0,
                "nb_etapes": len(r.etapes) if hasattr(r, 'etapes') else 0,
            }
            for r in recettes
        ]

    # ═══════════════════════════════════════════════════════════
    # CRÉATION COMPLÈTE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    def create_full(
            self,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict]
    ) -> int:
        """
        Crée une recette complète avec ingrédients et étapes.

        Args:
            recette_data: Données de base de la recette
            ingredients_data: Liste des ingrédients
                [{"nom": "Tomates", "quantite": 3, "unite": "pcs", "optionnel": False}]
            etapes_data: Liste des étapes
                [{"ordre": 1, "description": "...", "duree": 10}]

        Returns:
            ID de la recette créée

        Raises:
            ErreurValidation: Si données invalides

        Example:
            >>> recette_id = recette_service.create_full(
            ...     {"nom": "Tarte", "temps_preparation": 30, ...},
            ...     [{"nom": "Pommes", "quantite": 4, "unite": "pcs"}],
            ...     [{"ordre": 1, "description": "Éplucher les pommes"}]
            ... )
        """
        # Validation basique
        if not ingredients_data:
            raise ErreurValidation(
                "Au moins un ingrédient requis",
                message_utilisateur="Une recette doit avoir au moins un ingrédient"
            )

        if not etapes_data:
            raise ErreurValidation(
                "Au moins une étape requise",
                message_utilisateur="Une recette doit avoir au moins une étape"
            )

        with obtenir_contexte_db() as db:
            # 1. Créer la recette
            recette = Recette(**recette_data)
            db.add(recette)
            db.flush()  # Pour obtenir l'ID

            logger.info(f"Recette créée: {recette.nom} (ID: {recette.id})")

            # 2. Créer les ingrédients
            for ing_data in ingredients_data:
                # Trouver ou créer l'ingrédient de base
                ingredient_id = find_or_create_ingredient(
                    nom=ing_data["nom"],
                    unite=ing_data.get("unite", "pcs"),
                    categorie=ing_data.get("categorie"),
                    db=db
                )

                # Créer la liaison recette-ingrédient
                recette_ing = RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient_id,
                    quantite=ing_data["quantite"],
                    unite=ing_data.get("unite", "pcs"),
                    optionnel=ing_data.get("optionnel", False)
                )
                db.add(recette_ing)

            # 3. Créer les étapes
            for etape_data in etapes_data:
                etape = EtapeRecette(
                    recette_id=recette.id,
                    **etape_data
                )
                db.add(etape)

            # 4. Commit et invalider cache
            db.commit()
            Cache.invalider(dependencies=["recettes"])

            logger.info(
                f"Recette complète créée: {len(ingredients_data)} ingrédients, "
                f"{len(etapes_data)} étapes"
            )

            return recette.id

    # ═══════════════════════════════════════════════════════════
    # MISE À JOUR COMPLÈTE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=False)
    def update_full(
            self,
            recette_id: int,
            recette_data: Optional[Dict] = None,
            ingredients_data: Optional[List[Dict]] = None,
            etapes_data: Optional[List[Dict]] = None
    ) -> bool:
        """
        Met à jour une recette et optionnellement ses relations.

        Args:
            recette_id: ID de la recette
            recette_data: Données recette à mettre à jour
            ingredients_data: Nouvelle liste d'ingrédients (remplace tout)
            etapes_data: Nouvelle liste d'étapes (remplace tout)

        Returns:
            True si succès
        """
        with obtenir_contexte_db() as db:
            recette = db.query(Recette).get(recette_id)

            if not recette:
                raise ErreurNonTrouve(
                    f"Recette {recette_id} introuvable",
                    message_utilisateur="Recette introuvable"
                )

            # 1. Mettre à jour les données de base
            if recette_data:
                for key, value in recette_data.items():
                    if hasattr(recette, key):
                        setattr(recette, key, value)

            # 2. Remplacer les ingrédients si fournis
            if ingredients_data is not None:
                # Supprimer anciens
                db.query(RecetteIngredient).filter(
                    RecetteIngredient.recette_id == recette_id
                ).delete()

                # Créer nouveaux
                for ing_data in ingredients_data:
                    ingredient_id = find_or_create_ingredient(
                        nom=ing_data["nom"],
                        unite=ing_data.get("unite", "pcs"),
                        db=db
                    )

                    recette_ing = RecetteIngredient(
                        recette_id=recette_id,
                        ingredient_id=ingredient_id,
                        quantite=ing_data["quantite"],
                        unite=ing_data.get("unite", "pcs"),
                        optionnel=ing_data.get("optionnel", False)
                    )
                    db.add(recette_ing)

            # 3. Remplacer les étapes si fournies
            if etapes_data is not None:
                # Supprimer anciennes
                db.query(EtapeRecette).filter(
                    EtapeRecette.recette_id == recette_id
                ).delete()

                # Créer nouvelles
                for etape_data in etapes_data:
                    etape = EtapeRecette(
                        recette_id=recette_id,
                        **etape_data
                    )
                    db.add(etape)

            db.commit()
            Cache.invalider(dependencies=[f"recette_{recette_id}", "recettes"])

            logger.info(f"Recette {recette_id} mise à jour complète")
            return True

    # ═══════════════════════════════════════════════════════════
    # RECHERCHE AVANCÉE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=[])
    def search_recettes(
            self,
            search_term: Optional[str] = None,
            saison: Optional[str] = None,
            type_repas: Optional[str] = None,
            difficulte: Optional[str] = None,
            temps_max: Optional[int] = None,
            rapide_only: bool = False,
            bebe_compatible: bool = False,
            batch_compatible: bool = False,
            limit: int = 50
    ) -> List[Dict]:
        """
        Recherche multi-critères optimisée.

        Args:
            search_term: Terme de recherche (nom/description)
            saison: Filtrer par saison
            type_repas: Type de repas
            difficulte: Niveau de difficulté
            temps_max: Temps maximum total
            rapide_only: Uniquement recettes rapides
            bebe_compatible: Uniquement compatibles bébé
            batch_compatible: Uniquement batch cooking
            limit: Nombre maximum de résultats

        Returns:
            Liste de recettes matchant les critères
        """
        filters = {}

        if saison:
            filters["saison"] = saison
        if type_repas:
            filters["type_repas"] = type_repas
        if difficulte:
            filters["difficulte"] = difficulte
        if rapide_only:
            filters["est_rapide"] = True
        if bebe_compatible:
            filters["compatible_bebe"] = True
        if batch_compatible:
            filters["compatible_batch"] = True

        results = self.advanced_search(
            search_term=search_term,
            search_fields=["nom", "description"],
            filters=filters,
            sort_by="nom",
            limit=limit
        )

        # Filtrer par temps total si spécifié
        if temps_max:
            results = [
                r for r in results
                if (r.temps_preparation + r.temps_cuisson) <= temps_max
            ]

        return self.get_all_with_stats(limit=len(results)) if results else []

    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value={})
    def get_stats_detaillees(self) -> Dict:
        """
        Retourne statistiques détaillées sur les recettes.

        Returns:
            Dict avec statistiques complètes
        """
        return self.get_stats(
            group_by_fields=["saison", "type_repas", "difficulte"],
            count_filters={
                "rapides": {"est_rapide": True},
                "bebe": {"compatible_bebe": True},
                "batch": {"compatible_batch": True},
                "equilibrees": {"est_equilibre": True},
            }
        )


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

recette_service = RecetteService()