"""
Fonctions de construction de requêtes et prompts pour la génération d'images.

Extrait de generator.py pour réduire sa taille.
Contient:
- _construire_query_optimisee: Requête de recherche optimisée
- _construire_prompt_detaille: Prompt IA détaillé pour génération culinaire
"""

import logging

logger = logging.getLogger(__name__)


def _construire_query_optimisee(
    nom_recette: str, ingredients_list: list = None, type_plat: str = ""
) -> str:
    """
    Construit une requête de recherche optimisée pour trouver les meilleures images.
    Amélioration: Force les images du plat cuit/fini, pas des ingrédients bruts.

    Exemples:
    - "Compote de pommes" → "apple compote cooked finished served fresh homemade delicious"
    - "Pâtes carbonara" → "spaghetti carbonara pasta cooked finished plated fresh homemade"
    - "Salade" → "salad fresh vegetables arranged plated served homemade"
    """

    # Ingrédient principal (premier ingrédient si disponible)
    main_ingredient = ""
    if ingredients_list and len(ingredients_list) > 0:
        main_ingredient = ingredients_list[0].get("nom", "").lower()

    # Construire la query avec priorité sur:
    # 1. Le nom de la recette
    # 2. L'ingrédient principal (pour des images plus pertinentes)
    # 3. INSISTER sur "finished", "cooked", "plated", "served" pour le résultat final
    # 4. "fresh", "homemade", "delicious" pour qualité
    # 5. Exclure implicitement les mots qui donnent des images brutes

    parts = []

    # Ajouter le nom principal
    parts.append(nom_recette)

    # Ajouter l'ingrédient principal si différent du nom
    if main_ingredient and main_ingredient not in nom_recette.lower():
        parts.append(main_ingredient)

    # Ajouter des descripteurs FORTS du résultat final
    # Ceci est crucial pour éviter les images de légumes bruts
    if type_plat.lower() in ["dessert", "pâtisserie"]:
        parts.extend(["dessert", "finished", "plated", "beautiful", "decorated"])
    elif type_plat.lower() in ["soupe", "potage"]:
        parts.extend(["soup", "cooked", "served", "hot", "finished", "in bowl"])
    elif type_plat.lower() in ["petit_déjeuner", "breakfast"]:
        parts.extend(["breakfast", "cooked", "served", "plated", "ready", "eating"])
    else:
        # Plat général
        parts.extend(["cooked", "finished", "plated", "served", "prepared", "eating"])

    # Ajouter des descripteurs de qualité
    parts.extend(["fresh", "homemade", "delicious", "appetizing"])

    query = " ".join(parts)
    logger.debug(f"Query optimisée pour '{nom_recette}': '{query}'")

    return query


def _construire_prompt_detaille(
    nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = ""
) -> str:
    """
    Construit un prompt TRÈS détaillé pour une meilleure génération d'images culinaires.

    Éléments clés pour de belles images de recettes:
    - Style culinaire (gourmet, rustique, moderne, fusion, etc.)
    - Présentation (plating, décoration, contexte)
    - Ingrédients visibles et attrayants
    - Qualité (4K, professional, restaurant-quality)
    - Ambiance (lumière naturelle, mood, texture)
    """

    # Ingrédients clés à mentionner
    ingredients_mentions = ""
    if ingredients_list and isinstance(ingredients_list, list):
        # Extraire les noms des ingrédients principaux (max 3-4)
        ingredient_names = []
        for ing in ingredients_list[:4]:
            if isinstance(ing, dict) and "nom" in ing:
                ingredient_names.append(ing["nom"].lower())
            elif isinstance(ing, str):
                ingredient_names.append(ing.lower())

        if ingredient_names:
            ingredients_mentions = f"featuring {', '.join(ingredient_names)}"

    # Déterminer le style culinaire basé sur le type de plat
    style_map = {
        "petit_déjeuner": "gourmet breakfast, elegant morning presentation, beautifully arranged",
        "déjeuner": "refined lunch dish, restaurant plating, sophisticated and appetizing",
        "dîner": "fine dining presentation, gourmet plating, elegant and professional",
        "goûter": "charming afternoon snack, beautiful presentation, artfully arranged",
        "apéritif": "elegant appetizer, sophisticated presentation, gourmet and refined",
        "dessert": "beautiful plated dessert, artistic presentation, decorated with garnish and artistic touch",
    }

    style_phrase = style_map.get(
        type_plat, "beautifully plated culinary creation, gourmet presentation"
    )

    # Construire le prompt TRÈS détaillé - c'est crucial pour une bonne génération
    prompt = f"""Professional food photography of {nom_recette}"""

    if ingredients_mentions:
        prompt += f" {ingredients_mentions}"

    prompt += f""".
{style_phrase}.
Captured with professional photography lighting and equipment.
Restaurant quality presentation, appetizing, vibrant natural colors.
Artistic plating with subtle garnishes and careful food styling.
Fresh ingredients, gourmet appearance, mouth-watering look.
Shot on elegant minimalist background, shallow depth of field, bokeh.
Cinematic lighting with soft shadows, warm natural tones.
4K ultra HD resolution, magazine quality professional photography.
Luxury dining aesthetics, haute cuisine presentation."""

    # Ajouter la description si disponible
    if description and description.strip():
        prompt += f"\nAdditional style: {description}"

    return prompt
