# src/services/recettes/recette_service.py
"""
Service Recettes Principal - VERSION OPTIMISÉE
Utilise les nouveaux decorators + cache unifié
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import joinedload, selectinload

from src.services.base_enhanced_service import EnhancedCRUDService
from src.services.unified_service_helpers import (
    batch_find_or_create_ingredients,
    model_to_dict_safe
)
from src.core.database import get_db_context
from src.core.cache import Cache  # ✅ NOUVEAU
from src.core.error_handler import safe_execute  # ✅ NOUVEAU
from src.core.models import (
    Recette, RecetteIngredient, EtapeRecette, VersionRecette,
    Ingredient, ArticleInventaire
)
import logging

logger = logging.getLogger(__name__)


class RecetteService(EnhancedCRUDService[Recette]):
    """Service recettes unifié avec decorators"""

    def __init__(self):
        super().__init__(Recette)

    # ═══════════════════════════════════════════════════════════════
    # LECTURE OPTIMISÉE
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=60)
    @safe_execute(fallback_value=None, show_error=False)
    def get_by_id_full(self, recette_id: int) -> Optional[Recette]:
        """
        Récupère avec TOUTES relations (1 query)
        ✅ Cache 60s
        ✅ Error handling auto
        """
        with get_db_context() as db:
            return db.query(Recette).options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                joinedload(Recette.etapes),
                joinedload(Recette.versions)
            ).filter(Recette.id == recette_id).first()

    @Cache.cached(ttl=120)
    @safe_execute(fallback_value=[], show_error=False)
    def get_all_with_relations(
            self,
            skip: int = 0,
            limit: int = 20
    ) -> List[Recette]:
        """Liste avec relations (cache 2min)"""
        with get_db_context() as db:
            return db.query(Recette).options(
                selectinload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                selectinload(Recette.etapes)
            ).offset(skip).limit(limit).all()

    # ═══════════════════════════════════════════════════════════════
    # RECHERCHE
    # ═══════════════════════════════════════════════════════════════

    @safe_execute(fallback_value=[], show_error=False)
    def search_advanced(
            self,
            search_term: Optional[str] = None,
            saison: Optional[str] = None,
            type_repas: Optional[str] = None,
            temps_max: Optional[int] = None,
            difficulte: Optional[str] = None,
            is_rapide: Optional[bool] = None,
            is_equilibre: Optional[bool] = None,
            compatible_bebe: Optional[bool] = None,
            compatible_batch: Optional[bool] = None,
            ia_only: Optional[bool] = None,
            skip: int = 0,
            limit: int = 20
    ) -> List[Recette]:
        """Recherche avancée avec error handling"""
        filters = {}

        if saison: filters["saison"] = saison
        if type_repas: filters["type_repas"] = type_repas
        if difficulte: filters["difficulte"] = difficulte
        if is_rapide is not None: filters["est_rapide"] = is_rapide
        if is_equilibre is not None: filters["est_equilibre"] = is_equilibre
        if compatible_bebe is not None: filters["compatible_bebe"] = compatible_bebe
        if compatible_batch is not None: filters["compatible_batch"] = compatible_batch
        if ia_only is not None: filters["genere_par_ia"] = ia_only

        results = self.advanced_search(
            search_term=search_term,
            search_fields=["nom", "description"] if search_term else [],
            filters=filters,
            sort_by="nom",
            limit=limit,
            offset=skip
        )

        if temps_max:
            results = [
                r for r in results
                if (r.temps_preparation + r.temps_cuisson) <= temps_max
            ]

        return results

    # ═══════════════════════════════════════════════════════════════
    # CRÉATION
    # ═══════════════════════════════════════════════════════════════

    @safe_execute(fallback_value=None, show_error=True, error_message="❌ Erreur création recette")
    def create_full(
            self,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict],
            versions_data: Optional[Dict] = None
    ) -> int:
        """
        Crée recette complète
        ✅ Batch ingredients
        ✅ Error handling auto
        """
        with get_db_context() as db:
            # 1. Créer recette
            recette = self.create(recette_data, db=db)

            # 2. Batch ingrédients
            ing_map = batch_find_or_create_ingredients(
                [{"nom": i["nom"], "unite": i["unite"], "categorie": None}
                 for i in ingredients_data],
                db=db
            )

            # 3. Lier ingrédients
            for ing_data in ingredients_data:
                ingredient_id = ing_map[ing_data["nom"]]

                recette_ing = RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient_id,
                    quantite=ing_data["quantite"],
                    unite=ing_data["unite"],
                    optionnel=ing_data.get("optionnel", False)
                )
                db.add(recette_ing)

            # 4. Ajouter étapes
            for etape_data in etapes_data:
                etape = EtapeRecette(
                    recette_id=recette.id,
                    ordre=etape_data["ordre"],
                    description=etape_data["description"],
                    duree=etape_data.get("duree")
                )
                db.add(etape)

            # 5. Versions
            if versions_data:
                for version_type, v_data in versions_data.items():
                    version = VersionRecette(
                        recette_base_id=recette.id,
                        type_version=version_type,
                        instructions_modifiees=v_data.get("instructions_modifiees"),
                        ingredients_modifies=v_data.get("ingredients_modifies"),
                        notes_bebe=v_data.get("notes_bebe"),
                        etapes_paralleles_batch=v_data.get("etapes_paralleles"),
                        temps_optimise_batch=v_data.get("temps_optimise")
                    )
                    db.add(version)

            db.commit()

            # Invalider cache
            Cache.invalidate("recette")

            logger.info(f"✅ Recette '{recette.nom}' créée (ID: {recette.id})")
            return recette.id

    # ═══════════════════════════════════════════════════════════════
    # ÉDITION
    # ═══════════════════════════════════════════════════════════════

    @safe_execute(fallback_value=False, show_error=True, error_message="❌ Erreur mise à jour")
    def update_full(
            self,
            recette_id: int,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict],
            versions_data: Optional[Dict] = None
    ) -> bool:
        """Met à jour recette complète"""
        with get_db_context() as db:
            recette = db.query(Recette).get(recette_id)

            if not recette:
                return False

            # 1. Update recette
            for key, value in recette_data.items():
                if hasattr(recette, key):
                    setattr(recette, key, value)

            # 2. Delete anciens ingrédients
            db.query(RecetteIngredient).filter(
                RecetteIngredient.recette_id == recette_id
            ).delete()

            # 3. Batch nouveaux ingrédients
            ing_map = batch_find_or_create_ingredients(
                [{"nom": i["nom"], "unite": i["unite"], "categorie": None}
                 for i in ingredients_data],
                db=db
            )

            for ing_data in ingredients_data:
                ingredient_id = ing_map[ing_data["nom"]]

                recette_ing = RecetteIngredient(
                    recette_id=recette_id,
                    ingredient_id=ingredient_id,
                    quantite=ing_data["quantite"],
                    unite=ing_data["unite"],
                    optionnel=ing_data.get("optionnel", False)
                )
                db.add(recette_ing)

            # 4. Delete anciennes étapes
            db.query(EtapeRecette).filter(
                EtapeRecette.recette_id == recette_id
            ).delete()

            # 5. Nouvelles étapes
            for etape_data in etapes_data:
                etape = EtapeRecette(
                    recette_id=recette_id,
                    ordre=etape_data["ordre"],
                    description=etape_data["description"],
                    duree=etape_data.get("duree")
                )
                db.add(etape)

            # 6. Versions
            if versions_data:
                db.query(VersionRecette).filter(
                    VersionRecette.recette_base_id == recette_id
                ).delete()

                for version_type, v_data in versions_data.items():
                    version = VersionRecette(
                        recette_base_id=recette_id,
                        type_version=version_type,
                        instructions_modifiees=v_data.get("instructions_modifiees"),
                        ingredients_modifies=v_data.get("ingredients_modifies"),
                        notes_bebe=v_data.get("notes_bebe"),
                        etapes_paralleles_batch=v_data.get("etapes_paralleles"),
                        temps_optimise_batch=v_data.get("temps_optimise")
                    )
                    db.add(version)

            db.commit()

            Cache.invalidate(f"recette_{recette_id}")

            logger.info(f"✅ Recette {recette_id} mise à jour")
            return True

    # ═══════════════════════════════════════════════════════════════
    # DUPLICATION
    # ═══════════════════════════════════════════════════════════════

    @safe_execute(fallback_value=None, show_error=True)
    def duplicate(
            self,
            recette_id: int,
            nouveau_nom: Optional[str] = None
    ) -> Optional[int]:
        """Duplique une recette"""
        recette = self.get_by_id_full(recette_id)

        if not recette:
            return None

        recette_data = model_to_dict_safe(
            recette,
            exclude=["id", "cree_le", "modifie_le"]
        )
        recette_data["nom"] = nouveau_nom or f"{recette.nom} (copie)"
        recette_data["genere_par_ia"] = False

        ingredients_data = [
            {
                "nom": ing.ingredient.nom,
                "quantite": ing.quantite,
                "unite": ing.unite,
                "optionnel": ing.optionnel
            }
            for ing in recette.ingredients
        ]

        etapes_data = [
            {
                "ordre": etape.ordre,
                "description": etape.description,
                "duree": etape.duree
            }
            for etape in recette.etapes
        ]

        new_id = self.create_full(
            recette_data=recette_data,
            ingredients_data=ingredients_data,
            etapes_data=etapes_data
        )

        logger.info(f"✅ Recette {recette_id} dupliquée → {new_id}")
        return new_id

    # ═══════════════════════════════════════════════════════════════
    # SUPPRESSION
    # ═══════════════════════════════════════════════════════════════

    @safe_execute(fallback_value=False, show_error=True)
    def delete(self, recette_id: int) -> bool:
        """Supprime une recette"""
        success = super().delete(recette_id)

        if success:
            Cache.invalidate(f"recette_{recette_id}")
            Cache.invalidate("recette")

        return success

    # ═══════════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=300)
    @safe_execute(fallback_value={}, show_error=False)
    def get_stats(self) -> Dict:
        """Stats globales (cache 5min)"""
        stats = self.get_generic_stats(
            group_by_fields=["difficulte", "saison", "type_repas"],
            count_filters={
                "rapides": {"est_rapide": True},
                "equilibrees": {"est_equilibre": True},
                "ia": {"genere_par_ia": True},
                "bebe": {"compatible_bebe": True},
                "batch": {"compatible_batch": True}
            }
        )

        with get_db_context() as db:
            from sqlalchemy import func

            temps_total = db.query(
                func.avg(Recette.temps_preparation + Recette.temps_cuisson)
            ).scalar()

            stats["temps_moyen"] = round(float(temps_total or 0), 0)

        stats["par_difficulte"] = stats.pop("by_difficulte", {})

        return stats

    # ═══════════════════════════════════════════════════════════════
    # MÉTHODES MÉTIER
    # ═══════════════════════════════════════════════════════════════

    @safe_execute(fallback_value=[], show_error=False)
    def get_faisables_avec_stock(
            self,
            tolerance: float = 0.8
    ) -> List[Dict]:
        """Recettes faisables avec stock actuel"""
        recettes = self.get_all_with_relations(limit=1000)

        with get_db_context() as db:
            result = []

            for recette in recettes:
                nb_ingredients = len(recette.ingredients)
                if nb_ingredients == 0:
                    continue

                nb_disponibles = 0
                manquants = []

                for rec_ing in recette.ingredients:
                    stock = db.query(ArticleInventaire).filter(
                        ArticleInventaire.ingredient_id == rec_ing.ingredient_id
                    ).first()

                    if stock and stock.quantite >= rec_ing.quantite:
                        nb_disponibles += 1
                    else:
                        manquants.append(rec_ing.ingredient.nom)

                faisabilite = nb_disponibles / nb_ingredients

                if faisabilite >= tolerance:
                    result.append({
                        "recette": recette,
                        "faisabilite": round(faisabilite * 100, 1),
                        "manquants": manquants
                    })

            return sorted(result, key=lambda x: x["faisabilite"], reverse=True)


# ═══════════════════════════════════════════════════════════════
# INSTANCE GLOBALE
# ═══════════════════════════════════════════════════════════════

recette_service = RecetteService()