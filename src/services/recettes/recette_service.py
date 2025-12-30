from src.services.base_service import BaseService
from src.core.models import Recette, RecetteIngredient, EtapeRecette
from src.core.database import get_db_context
from src.core.errors import handle_errors
from sqlalchemy.orm import joinedload
from typing import Dict, List, Optional

class RecetteService(BaseService[Recette]):
    def __init__(self):
        super().__init__(Recette, cache_ttl=60)

    @handle_errors(show_in_ui=False, fallback_value=None)
    def get_by_id_full(self, recette_id: int):
        """Récupère avec relations optimisées"""
        with get_db_context() as db:
            return db.query(Recette).options(
                joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                joinedload(Recette.etapes)
            ).filter(Recette.id == recette_id).first()

    @handle_errors(show_in_ui=True, fallback_value=None)
    def create_full(self, recette_data: Dict, ingredients_data: List[Dict], etapes_data: List[Dict]) -> int:
        """Crée recette complète"""
        with get_db_context() as db:
            from src.core.models import Ingredient

            # Créer recette
            recette = self.create(recette_data, db=db)

            # Ingrédients
            for ing_data in ingredients_data:
                ingredient = db.query(Ingredient).filter(Ingredient.nom == ing_data["nom"]).first()
                if not ingredient:
                    ingredient = Ingredient(nom=ing_data["nom"], unite=ing_data["unite"])
                    db.add(ingredient)
                    db.flush()

                recette_ing = RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient.id,
                    quantite=ing_data["quantite"],
                    unite=ing_data["unite"],
                    optionnel=ing_data.get("optionnel", False)
                )
                db.add(recette_ing)

            # Étapes
            for etape_data in etapes_data:
                etape = EtapeRecette(recette_id=recette.id, **etape_data)
                db.add(etape)

            db.commit()
            return recette.id

recette_service = RecetteService()