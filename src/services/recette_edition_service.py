# src/services/recette_edition_service.py
"""
Service Édition Recettes
Gestion de la modification de recettes existantes
"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.core.database import get_db_context
from src.core.models import (
    Recette, RecetteIngredient, EtapeRecette, VersionRecette,
    Ingredient, TypeVersionRecetteEnum
)
from src.services.recette_service import recette_service

logger = logging.getLogger(__name__)


class RecetteEditionService:
    """Service dédié à l'édition de recettes"""

    @staticmethod
    def update_recette_complete(
            recette_id: int,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict],
            versions_data: Optional[Dict] = None,
            db: Session = None
    ) -> bool:
        """
        Met à jour une recette complète

        Returns:
            True si succès
        """
        if db:
            return RecetteEditionService._do_update_complete(
                db, recette_id, recette_data, ingredients_data,
                etapes_data, versions_data
            )

        with get_db_context() as db:
            return RecetteEditionService._do_update_complete(
                db, recette_id, recette_data, ingredients_data,
                etapes_data, versions_data
            )

    @staticmethod
    def _do_update_complete(
            db: Session,
            recette_id: int,
            recette_data: Dict,
            ingredients_data: List[Dict],
            etapes_data: List[Dict],
            versions_data: Optional[Dict]
    ) -> bool:
        """Implémentation interne"""

        recette = db.query(Recette).get(recette_id)

        if not recette:
            return False

        # 1. Mettre à jour les champs de la recette
        for key, value in recette_data.items():
            if hasattr(recette, key):
                setattr(recette, key, value)

        # 2. Supprimer anciens ingrédients
        db.query(RecetteIngredient).filter(
            RecetteIngredient.recette_id == recette_id
        ).delete()

        # 3. Ajouter nouveaux ingrédients
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
                recette_id=recette_id,
                ingredient_id=ingredient.id,
                quantite=ing_data["quantite"],
                unite=ing_data["unite"],
                optionnel=ing_data.get("optionnel", False)
            )
            db.add(recette_ing)

        # 4. Supprimer anciennes étapes
        db.query(EtapeRecette).filter(
            EtapeRecette.recette_id == recette_id
        ).delete()

        # 5. Ajouter nouvelles étapes
        for etape_data in etapes_data:
            etape = EtapeRecette(
                recette_id=recette_id,
                ordre=etape_data["ordre"],
                description=etape_data["description"],
                duree=etape_data.get("duree")
            )
            db.add(etape)

        # 6. Mettre à jour versions si fournies
        if versions_data:
            # Supprimer anciennes versions
            db.query(VersionRecette).filter(
                VersionRecette.recette_base_id == recette_id
            ).delete()

            # Ajouter nouvelles versions
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
        logger.info(f"✅ Recette {recette_id} mise à jour")
        return True

    @staticmethod
    def duplicate_recette(
            recette_id: int,
            nouveau_nom: Optional[str] = None,
            db: Session = None
    ) -> Optional[int]:
        """
        Duplique une recette complète

        Returns:
            ID de la nouvelle recette
        """
        if db:
            return RecetteEditionService._do_duplicate(db, recette_id, nouveau_nom)

        with get_db_context() as db:
            return RecetteEditionService._do_duplicate(db, recette_id, nouveau_nom)

    @staticmethod
    def _do_duplicate(
            db: Session,
            recette_id: int,
            nouveau_nom: Optional[str]
    ) -> Optional[int]:
        """Implémentation"""

        # Charger recette source avec eager loading
        recette = recette_service.get_by_id_full(recette_id, db)

        if not recette:
            return None

        # Préparer données
        recette_data = {
            "nom": nouveau_nom or f"{recette.nom} (copie)",
            "description": recette.description,
            "temps_preparation": recette.temps_preparation,
            "temps_cuisson": recette.temps_cuisson,
            "portions": recette.portions,
            "difficulte": recette.difficulte,
            "type_repas": recette.type_repas,
            "saison": recette.saison,
            "categorie": recette.categorie,
            "est_rapide": recette.est_rapide,
            "est_equilibre": recette.est_equilibre,
            "compatible_bebe": recette.compatible_bebe,
            "compatible_batch": recette.compatible_batch,
            "congelable": recette.congelable,
            "url_image": recette.url_image,
            "genere_par_ia": False  # Copie = manuel
        }

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

        # Créer la copie
        new_id = recette_service.create_full(
            recette_data=recette_data,
            ingredients_data=ingredients_data,
            etapes_data=etapes_data,
            db=db
        )

        logger.info(f"✅ Recette {recette_id} dupliquée → {new_id}")
        return new_id


# Instance globale
recette_edition_service = RecetteEditionService()