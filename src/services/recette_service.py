"""
Service Recettes OPTIMISÉ
Utilise EnhancedCRUDService + helpers avancés

"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session, joinedload, selectinload

from src.services.base_enhanced_service import EnhancedCRUDService
from src.core.database import get_db_context
from src.core.exceptions import ValidationError, NotFoundError, handle_errors
from src.core.models import (
    Recette,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    Ingredient,
    ArticleInventaire,
    TypeVersionRecetteEnum,
    SaisonEnum,
    TypeRepasEnum
)
import logging

logger = logging.getLogger(__name__)


class RecetteService(EnhancedCRUDService[Recette]):
    """
    Service recettes optimisé

    ✅ Hérite EnhancedCRUDService (vs BaseService)
    ✅ Utilise advanced_search() au lieu de logique custom
    ✅ Utilise get_generic_stats() pour statistiques
    """

    def __init__(self):
        super().__init__(Recette)

    # ═══════════════════════════════════════════════════════════════
    # LECTURE OPTIMISÉE (Eager Loading)
    # ═══════════════════════════════════════════════════════════════

    def get_by_id_full(self, recette_id: int, db: Session = None) -> Optional[Recette]:
        """
        Récupère avec TOUTES relations (UNE SEULE QUERY)

        ✅ Évite N+1 queries
        """
        def _execute(session: Session):
            return session.query(Recette).options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                joinedload(Recette.etapes),
                joinedload(Recette.versions)
            ).filter(
                Recette.id == recette_id
            ).first()

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    def get_all_with_relations(
            self,
            skip: int = 0,
            limit: int = 20,
            db: Session = None
    ) -> List[Recette]:
        """Toutes recettes avec relations optimisées"""
        def _execute(session: Session):
            return session.query(Recette).options(
                selectinload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                selectinload(Recette.etapes),
                selectinload(Recette.versions)
            ).offset(skip).limit(limit).all()

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # RECHERCHE (utilise advanced_search)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False)
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
        """
        Recherche avancée

        ✅ Utilise advanced_search() de EnhancedCRUDService
        ✅ Pas de logique custom manuelle
        """
        # Construire filtres
        filters = {}

        if saison:
            filters["saison"] = saison

        if type_repas:
            filters["type_repas"] = type_repas

        if difficulte:
            filters["difficulte"] = difficulte

        if is_rapide is not None:
            filters["est_rapide"] = is_rapide

        if is_equilibre is not None:
            filters["est_equilibre"] = is_equilibre

        if compatible_bebe is not None:
            filters["compatible_bebe"] = compatible_bebe

        if compatible_batch is not None:
            filters["compatible_batch"] = compatible_batch

        if ia_only is not None:
            filters["genere_par_ia"] = ia_only

        # Temps max (utilise filtre avancé)
        if temps_max:
            # Note: EnhancedCRUDService ne supporte pas les computed columns
            # On filtre après pour ce cas spécial
            pass

        # Appel optimisé
        results = self.advanced_search(
            search_term=search_term,
            search_fields=["nom", "description"] if search_term else [],
            filters=filters,
            sort_by="nom",
            limit=limit,
            offset=skip
        )

        # Filtrer temps_max après (computed column)
        if temps_max:
            results = [
                r for r in results
                if (r.temps_preparation + r.temps_cuisson) <= temps_max
            ]

        return results

    # ═══════════════════════════════════════════════════════════════
    # CRÉATION (utilise create de base)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def create_full(
            self,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict],
            versions_data: Optional[Dict] = None
    ) -> int:
        """
        Crée recette complète

        ✅ Utilise create() de base + logique métier
        """
        with get_db_context() as db:
            # 1. Créer recette
            recette = self.create(recette_data, db=db)

            # 2. Ajouter ingrédients
            for ing_data in ingredients_data:
                # Trouver/créer ingrédient
                ingredient = db.query(Ingredient).filter(
                    Ingredient.nom == ing_data["nom"]
                ).first()

                if not ingredient:
                    ingredient = Ingredient(
                        nom=ing_data["nom"],
                        unite=ing_data["unite"],
                        categorie=ing_data.get("categorie")
                    )
                    db.add(ingredient)
                    db.flush()

                # Lier
                recette_ing = RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient.id,
                    quantite=ing_data["quantite"],
                    unite=ing_data["unite"],
                    optionnel=ing_data.get("optionnel", False)
                )
                db.add(recette_ing)

            # 3. Ajouter étapes
            for etape_data in etapes_data:
                etape = EtapeRecette(
                    recette_id=recette.id,
                    ordre=etape_data["ordre"],
                    description=etape_data["description"],
                    duree=etape_data.get("duree")
                )
                db.add(etape)

            # 4. Ajouter versions si présentes
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
            logger.info(f"✅ Recette '{recette.nom}' créée (ID: {recette.id})")

            return recette.id

    # ═══════════════════════════════════════════════════════════════
    # STATISTIQUES (utilise get_generic_stats)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False)
    def get_stats(self) -> Dict:
        """
        Stats globales

        ✅ Utilise get_generic_stats() de EnhancedCRUDService
        """
        stats = self.get_generic_stats(
            group_by_fields=["difficulte", "saison", "type_repas"],
            count_filters={
                "rapides": {"est_rapide": True},
                "equilibrees": {"est_equilibre": True},
                "ia": {"genere_par_ia": True},
                "bebe": {"compatible_bebe": True},
                "batch": {"compatible_batch": True}
            },
            aggregate_fields={
                "temps_moyen": "temps_preparation"  # Note: ne compte que prep
            }
        )

        # Calculer temps total moyen (prep + cuisson)
        with get_db_context() as db:
            from sqlalchemy import func

            temps_total = db.query(
                func.avg(Recette.temps_preparation + Recette.temps_cuisson)
            ).scalar()

            stats["temps_moyen"] = round(float(temps_total or 0), 0)

        # Renommer pour UI
        stats["par_difficulte"] = stats.pop("by_difficulte", {})

        return stats

    # ═══════════════════════════════════════════════════════════════
    # MÉTHODES MÉTIER
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False)
    def get_faisables_avec_stock(
            self,
            tolerance: float = 0.8
    ) -> List[Dict]:
        """Recettes faisables avec stock"""
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

    def get_recettes_saison(
            self,
            saison: Optional[str] = None
    ) -> List[Recette]:
        """Recettes de saison (auto-détecte)"""
        if not saison:
            from datetime import date
            mois = date.today().month

            if mois in [3, 4, 5]:
                saison = SaisonEnum.PRINTEMPS.value
            elif mois in [6, 7, 8]:
                saison = SaisonEnum.ETE.value
            elif mois in [9, 10, 11]:
                saison = SaisonEnum.AUTOMNE.value
            else:
                saison = SaisonEnum.HIVER.value

        return self.advanced_search(
            filters={
                "saison": {"in": [saison, SaisonEnum.TOUTE_ANNEE.value]}
            },
            limit=1000
        )


# Instance globale
recette_service = RecetteService()