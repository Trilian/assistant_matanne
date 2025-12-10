"""
Service Recettes - CRUD avec Eager Loading
Hérite de BaseService pour opérations standard
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, or_, and_

from src.core.base_service import BaseService
from src.core.database import get_db_context
from src.core.models import (
    Recette, RecetteIngredient, EtapeRecette, VersionRecette,
    Ingredient, TypeVersionRecetteEnum, SaisonEnum, TypeRepasEnum
)
import logging

logger = logging.getLogger(__name__)


class RecetteService(BaseService[Recette]):
    """
    Service métier pour les recettes
    Opérations CRUD + méthodes métier spécifiques
    """

    def __init__(self):
        super().__init__(Recette)

    # ===================================
    # LECTURE OPTIMISÉE (Eager Loading)
    # ===================================

    def get_by_id_full(self, recette_id: int, db: Session = None) -> Optional[Recette]:
        """
        Récupère une recette avec TOUTES ses relations (UNE SEULE QUERY)

        Évite le problème N+1
        """
        if db:
            return db.query(Recette).options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                joinedload(Recette.etapes),
                joinedload(Recette.versions)
            ).filter(Recette.id == recette_id).first()

        with get_db_context() as db:
            return db.query(Recette).options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                joinedload(Recette.etapes),
                joinedload(Recette.versions)
            ).filter(Recette.id == recette_id).first()

    def get_all_with_relations(
            self,
            skip: int = 0,
            limit: int = 20,
            db: Session = None
    ) -> List[Recette]:
        """Récupère toutes les recettes avec relations (optimisé)"""
        if db:
            return db.query(Recette).options(
                selectinload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                selectinload(Recette.etapes),
                selectinload(Recette.versions)
            ).offset(skip).limit(limit).all()

        with get_db_context() as db:
            return db.query(Recette).options(
                selectinload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                selectinload(Recette.etapes),
                selectinload(Recette.versions)
            ).offset(skip).limit(limit).all()

    # ===================================
    # CRÉATION COMPLÈTE
    # ===================================

    def create_full(
            self,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict],
            versions_data: Optional[Dict] = None,
            db: Session = None
    ) -> int:
        """
        Crée une recette complète avec ingrédients, étapes, versions

        Args:
            recette_data: Données recette principale
            ingredients_data: Liste ingrédients
            etapes_data: Liste étapes
            versions_data: Dict des versions (optionnel)

        Returns:
            ID de la recette créée
        """
        if db:
            return self._do_create_full(db, recette_data, ingredients_data, etapes_data, versions_data)

        with get_db_context() as db:
            return self._do_create_full(db, recette_data, ingredients_data, etapes_data, versions_data)

    def _do_create_full(
            self,
            db: Session,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict],
            versions_data: Optional[Dict]
    ) -> int:
        """Implémentation interne"""

        # 1. Créer recette
        recette = Recette(**recette_data)
        db.add(recette)
        db.flush()

        # 2. Ajouter ingrédients
        for ing_data in ingredients_data:
            # Trouver ou créer ingrédient
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

            # Lier à la recette
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

        # 4. Ajouter versions (si présentes)
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

    # ===================================
    # RECHERCHE AVANCÉE
    # ===================================

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
            limit: int = 20,
            db: Session = None
    ) -> List[Recette]:
        """
        Recherche avancée avec multiples filtres

        Returns:
            Liste de recettes correspondantes
        """
        if db:
            query = db.query(Recette)
        else:
            with get_db_context() as db:
                query = db.query(Recette)

                # Appliquer filtres
                query = self._apply_search_filters(
                    query, search_term, saison, type_repas, temps_max,
                    difficulte, is_rapide, is_equilibre, compatible_bebe,
                    compatible_batch, ia_only
                )

                # Eager loading
                query = query.options(
                    selectinload(Recette.ingredients).joinedload(RecetteIngredient.ingredient)
                )

                return query.offset(skip).limit(limit).all()

        # Appliquer filtres
        query = self._apply_search_filters(
            query, search_term, saison, type_repas, temps_max,
            difficulte, is_rapide, is_equilibre, compatible_bebe,
            compatible_batch, ia_only
        )

        # Eager loading
        query = query.options(
            selectinload(Recette.ingredients).joinedload(RecetteIngredient.ingredient)
        )

        return query.offset(skip).limit(limit).all()

    def _apply_search_filters(self, query, *args):
        """Applique tous les filtres de recherche"""
        (search_term, saison, type_repas, temps_max, difficulte,
         is_rapide, is_equilibre, compatible_bebe, compatible_batch, ia_only) = args

        # Recherche texte
        if search_term:
            query = query.filter(
                or_(
                    Recette.nom.ilike(f"%{search_term}%"),
                    Recette.description.ilike(f"%{search_term}%")
                )
            )

        # Filtres simples
        if saison:
            query = query.filter(Recette.saison == saison)

        if type_repas:
            query = query.filter(Recette.type_repas == type_repas)

        if difficulte:
            query = query.filter(Recette.difficulte == difficulte)

        # Temps max
        if temps_max:
            query = query.filter(
                (Recette.temps_preparation + Recette.temps_cuisson) <= temps_max
            )

        # Filtres booléens
        if is_rapide is not None:
            query = query.filter(Recette.est_rapide == is_rapide)

        if is_equilibre is not None:
            query = query.filter(Recette.est_equilibre == is_equilibre)

        if compatible_bebe is not None:
            query = query.filter(Recette.compatible_bebe == compatible_bebe)

        if compatible_batch is not None:
            query = query.filter(Recette.compatible_batch == compatible_batch)

        if ia_only is not None:
            query = query.filter(Recette.genere_par_ia == ia_only)

        return query

    # ===================================
    # MÉTHODES MÉTIER
    # ===================================

    def get_faisables_avec_stock(
            self,
            tolerance: float = 0.8,
            db: Session = None
    ) -> List[Dict]:
        """
        Retourne les recettes faisables avec le stock actuel

        Args:
            tolerance: % d'ingrédients nécessaires (0.8 = 80%)

        Returns:
            Liste de dicts avec recette et faisabilité
        """
        from src.core.models import ArticleInventaire

        if db:
            recettes = db.query(Recette).options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient)
            ).all()
        else:
            with get_db_context() as db:
                recettes = db.query(Recette).options(
                    joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient)
                ).all()

                results = []

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
                        results.append({
                            "recette": recette,
                            "faisabilite": round(faisabilite * 100, 1),
                            "manquants": manquants
                        })

                # Trier par faisabilité
                return sorted(results, key=lambda x: x["faisabilite"], reverse=True)

        # Même logique si db fournie
        results = []

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
                results.append({
                    "recette": recette,
                    "faisabilite": round(faisabilite * 100, 1),
                    "manquants": manquants
                })

        return sorted(results, key=lambda x: x["faisabilite"], reverse=True)

    def get_recettes_saison(self, saison: Optional[str] = None, db: Session = None) -> List[Recette]:
        """Recettes de saison (détecte auto si None)"""
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

        filters = {"saison": [saison, SaisonEnum.TOUTE_ANNEE.value]}

        if db:
            return self._apply_filters(db.query(Recette), filters).all()

        with get_db_context() as db:
            return self._apply_filters(db.query(Recette), filters).all()

    def get_stats(self, db: Session = None) -> Dict:
        """Statistiques globales recettes"""
        if db:
            return {
                "total": db.query(func.count(Recette.id)).scalar(),
                "par_difficulte": dict(
                    db.query(Recette.difficulte, func.count(Recette.id))
                    .group_by(Recette.difficulte).all()
                ),
                "rapides": db.query(func.count(Recette.id)).filter(Recette.est_rapide == True).scalar(),
                "equilibrees": db.query(func.count(Recette.id)).filter(Recette.est_equilibre == True).scalar(),
                "ia": db.query(func.count(Recette.id)).filter(Recette.genere_par_ia == True).scalar(),
                "temps_moyen": db.query(
                    func.avg(Recette.temps_preparation + Recette.temps_cuisson)
                ).scalar() or 0
            }

        with get_db_context() as db:
            return {
                "total": db.query(func.count(Recette.id)).scalar(),
                "par_difficulte": dict(
                    db.query(Recette.difficulte, func.count(Recette.id))
                    .group_by(Recette.difficulte).all()
                ),
                "rapides": db.query(func.count(Recette.id)).filter(Recette.est_rapide == True).scalar(),
                "equilibrees": db.query(func.count(Recette.id)).filter(Recette.est_equilibre == True).scalar(),
                "ia": db.query(func.count(Recette.id)).filter(Recette.genere_par_ia == True).scalar(),
                "temps_moyen": db.query(
                    func.avg(Recette.temps_preparation + Recette.temps_cuisson)
                ).scalar() or 0
            }


# ===================================
# INSTANCE GLOBALE
# ===================================

recette_service = RecetteService()