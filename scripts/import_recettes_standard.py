"""
Service d'import des recettes standard
Initialise la base de données avec une bibliothèque standard de recettes
"""

import json
import logging
from pathlib import Path

from src.core.database import obtenir_contexte_db
from src.core.models import Recette, RecetteIngredient, Ingredient, EtapeRecette
from src.services.recettes import get_recette_service

logger = logging.getLogger(__name__)


def importer_recettes_standard() -> int:
    """
    Importe les recettes standard depuis le fichier JSON.
    
    Returns:
        Nombre de recettes importées
    """
    fichier_recettes = Path(__file__).parent.parent / "data" / "recettes_standard.json"
    
    if not fichier_recettes.exists():
        logger.warning(f"❌ Fichier non trouvé: {fichier_recettes}")
        return 0
    
    try:
        with open(fichier_recettes, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Erreur lecture JSON: {e}")
        return 0
    
    recettes_data = data.get("recettes_standard", [])
    nb_imported = 0
    
    # Obtenir le contexte DB
    with obtenir_contexte_db() as db:
        for recette_data in recettes_data:
            try:
                # Vérifier si la recette existe déjà
                existing = db.query(Recette).filter(
                    Recette.nom == recette_data["nom"]
                ).first()
                
                if existing:
                    logger.debug(f"⏭️ Recette '{recette_data['nom']}' existe déjà, skip")
                    continue
                
                # Créer la recette
                recette = Recette(
                    nom=recette_data["nom"],
                    description=recette_data.get("description", ""),
                    type_repas=recette_data.get("type_repas", "dîner"),
                    temps_preparation=recette_data.get("temps_preparation", 0),
                    temps_cuisson=recette_data.get("temps_cuisson", 0),
                    portions=recette_data.get("portions", 4),
                    difficulte=recette_data.get("difficulte", "moyen"),
                    saison=recette_data.get("saison", "toute_année"),
                    
                    # Tags
                    est_rapide=recette_data.get("est_rapide", False),
                    est_equilibre=recette_data.get("est_equilibre", False),
                    compatible_bebe=recette_data.get("compatible_bebe", False),
                    compatible_batch=recette_data.get("compatible_batch", False),
                    congelable=recette_data.get("congelable", False),
                    
                    # Bio/Local
                    est_bio=recette_data.get("est_bio", False),
                    est_local=recette_data.get("est_local", False),
                    score_bio=recette_data.get("score_bio", 0),
                    score_local=recette_data.get("score_local", 0),
                    
                    # Robots
                    compatible_cookeo=recette_data.get("compatible_cookeo", False),
                    compatible_monsieur_cuisine=recette_data.get("compatible_monsieur_cuisine", False),
                    compatible_airfryer=recette_data.get("compatible_airfryer", False),
                    compatible_multicooker=recette_data.get("compatible_multicooker", False),
                    
                    # Nutrition
                    calories=recette_data.get("calories"),
                    proteines=recette_data.get("proteines"),
                    lipides=recette_data.get("lipides"),
                    glucides=recette_data.get("glucides"),
                )
                
                db.add(recette)
                db.flush()
                
                # Ajouter les ingrédients
                for idx, ing_data in enumerate(recette_data.get("ingredients", []), 1):
                    # Chercher ou créer l'ingrédient
                    ingredient = db.query(Ingredient).filter(
                        Ingredient.nom == ing_data["nom"]
                    ).first()
                    
                    if not ingredient:
                        ingredient = Ingredient(nom=ing_data["nom"])
                        db.add(ingredient)
                        db.flush()
                    
                    # Ajouter la relation
                    recette_ing = RecetteIngredient(
                        recette_id=recette.id,
                        ingredient_id=ingredient.id,
                        quantite=ing_data.get("quantite", 0),
                        unite=ing_data.get("unite", ""),
                    )
                    db.add(recette_ing)
                
                # Ajouter les étapes
                for idx, etape_desc in enumerate(recette_data.get("etapes", []), 1):
                    etape = EtapeRecette(
                        recette_id=recette.id,
                        ordre=idx,
                        description=etape_desc,
                        duree=None,
                    )
                    db.add(etape)
                
                db.commit()
                logger.info(f"✅ Recette importée: '{recette.nom}'")
                nb_imported += 1
                
            except Exception as e:
                logger.error(f"❌ Erreur import recette '{recette_data.get('nom')}': {e}")
                db.rollback()
                continue
    
    logger.info(f"✅ Import terminé: {nb_imported} recettes importées")
    return nb_imported


def reset_recettes_standard() -> bool:
    """
    Réinitialise les recettes standard (supprime et réimporte).
    
    Returns:
        True si succès
    """
    try:
        with obtenir_contexte_db() as db:
            # Supprimer toutes les recettes standard
            recettes = db.query(Recette).all()
            for recette in recettes:
                db.delete(recette)
            db.commit()
            logger.info("✅ Recettes supprimées")
        
        # Réimporter
        nb = importer_recettes_standard()
        return nb > 0
    
    except Exception as e:
        logger.error(f"❌ Erreur reset: {e}")
        return False


if __name__ == "__main__":
    # Pour tester directement
    logging.basicConfig(level=logging.INFO)
    nb = importer_recettes_standard()
    print(f"\n✅ {nb} recettes importées avec succès!")
