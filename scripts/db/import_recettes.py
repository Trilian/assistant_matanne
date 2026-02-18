"""
Service d'import des recettes standard
Initialise la base de donnÃ©es avec une bibliothÃ¨que standard de recettes
"""

import json
import logging
from pathlib import Path

from src.core.db import obtenir_contexte_db
from src.core.models import EtapeRecette, Ingredient, Recette, RecetteIngredient

logger = logging.getLogger(__name__)


def importer_recettes_standard() -> int:
    """
    Importe les recettes standard depuis le fichier JSON.

    Returns:
        Nombre de recettes importÃ©es
    """
    fichier_recettes = Path(__file__).parent.parent / "data" / "recettes_standard.json"

    if not fichier_recettes.exists():
        logger.warning(f"âŒ Fichier non trouvÃ©: {fichier_recettes}")
        return 0

    try:
        with open(fichier_recettes, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"âŒ Erreur lecture JSON: {e}")
        return 0

    recettes_data = data.get("recettes_standard", [])
    nb_imported = 0

    # Obtenir le contexte DB
    with obtenir_contexte_db() as db:
        for recette_data in recettes_data:
            try:
                # VÃ©rifier si la recette existe dÃ©jÃ
                existing = db.query(Recette).filter(Recette.nom == recette_data["nom"]).first()

                if existing:
                    logger.debug(f"â­ï¸ Recette '{recette_data['nom']}' existe dÃ©jÃ , skip")
                    continue

                # CrÃ©er la recette
                recette = Recette(
                    nom=recette_data["nom"],
                    description=recette_data.get("description", ""),
                    type_repas=recette_data.get("type_repas", "dÃ®ner"),
                    temps_preparation=recette_data.get("temps_preparation", 0),
                    temps_cuisson=recette_data.get("temps_cuisson", 0),
                    portions=recette_data.get("portions", 4),
                    difficulte=recette_data.get("difficulte", "moyen"),
                    saison=recette_data.get("saison", "toute_annÃ©e"),
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
                    compatible_monsieur_cuisine=recette_data.get(
                        "compatible_monsieur_cuisine", False
                    ),
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

                # Ajouter les ingrÃ©dients
                for idx, ing_data in enumerate(recette_data.get("ingredients", []), 1):
                    # Chercher ou crÃ©er l'ingrÃ©dient
                    ingredient = (
                        db.query(Ingredient).filter(Ingredient.nom == ing_data["nom"]).first()
                    )

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

                # Ajouter les Ã©tapes
                for idx, etape_desc in enumerate(recette_data.get("etapes", []), 1):
                    etape = EtapeRecette(
                        recette_id=recette.id,
                        ordre=idx,
                        description=etape_desc,
                        duree=None,
                    )
                    db.add(etape)

                db.commit()
                logger.info(f"âœ… Recette importÃ©e: '{recette.nom}'")
                nb_imported += 1

            except Exception as e:
                logger.error(f"âŒ Erreur import recette '{recette_data.get('nom')}': {e}")
                db.rollback()
                continue

    logger.info(f"âœ… Import terminÃ©: {nb_imported} recettes importÃ©es")
    return nb_imported


def reset_recettes_standard() -> bool:
    """
    RÃ©initialise les recettes standard (supprime et rÃ©importe).

    Returns:
        True si succÃ¨s
    """
    try:
        with obtenir_contexte_db() as db:
            # Supprimer toutes les recettes standard
            recettes = db.query(Recette).all()
            for recette in recettes:
                db.delete(recette)
            db.commit()
            logger.info("âœ… Recettes supprimÃ©es")

        # RÃ©importer
        nb = importer_recettes_standard()
        return nb > 0

    except Exception as e:
        logger.error(f"âŒ Erreur reset: {e}")
        return False


if __name__ == "__main__":
    # Pour tester directement
    logging.basicConfig(level=logging.INFO)
    nb = importer_recettes_standard()
    print(f"\nâœ… {nb} recettes importÃ©es avec succÃ¨s!")
