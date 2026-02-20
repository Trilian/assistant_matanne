"""
Générateur d'images pour les recettes
Utilise plusieurs APIs gratuites pour générer des images réelles de haute qualité
"""

import base64
import logging
import os
import random
from pathlib import Path
from urllib.parse import quote

import requests

# Charger les variables d'environnement depuis .env.local et .env
try:
    from dotenv import load_dotenv

    # Chercher .env.local et .env depuis la racine du projet
    project_root = Path(__file__).parent.parent.parent.parent
    load_dotenv(project_root / ".env.local")
    load_dotenv(project_root / ".env")
except ImportError:
    pass

logger = logging.getLogger(__name__)


# Fonction helper pour charger les clés depuis st.secrets (Streamlit Cloud) ou os.getenv (local)
def _get_api_key(key_name: str) -> str | None:
    """Charge une clé API depuis st.secrets (Streamlit Cloud) ou os.getenv (local)"""
    try:
        import streamlit as st

        if hasattr(st, "secrets") and st.secrets:
            try:
                # Essayer section spécifique d'abord (ex: st.secrets["unsplash"]["api_key"])
                if key_name == "UNSPLASH_API_KEY":
                    return st.secrets.get("unsplash", {}).get("api_key")
                elif key_name == "PEXELS_API_KEY":
                    return st.secrets.get("pexels", {}).get("api_key")
                elif key_name == "PIXABAY_API_KEY":
                    return st.secrets.get("pixabay", {}).get("api_key")
            except Exception as e:
                logger.debug("Secrets indisponible pour %s: %s", key_name, e)
    except Exception as e:
        logger.debug("Streamlit non disponible: %s", e)

    # Fallback à os.getenv (pour dev local avec .env)
    return os.getenv(key_name)


# APIs configurables
LEONARDO_API_KEY = _get_api_key("LEONARDO_API_KEY")  # Gratuit: https://app.leonardo.ai
PEXELS_API_KEY = _get_api_key("PEXELS_API_KEY")  # Gratuit: https://www.pexels.com/api/
PIXABAY_API_KEY = _get_api_key("PIXABAY_API_KEY")  # Gratuit: https://pixabay.com/api/
UNSPLASH_API_KEY = _get_api_key(
    "UNSPLASH_API_KEY"
)  # Gratuit: https://unsplash.com/oauth/applications

# API status logging (sans leak de clés)
logger.info(
    "Image generator initialisé — Leonardo=%s, Unsplash=%s, Pexels=%s, Pixabay=%s",
    "OK" if LEONARDO_API_KEY else "NON",
    "OK" if UNSPLASH_API_KEY else "NON",
    "OK" if PEXELS_API_KEY else "NON",
    "OK" if PIXABAY_API_KEY else "NON",
)

if UNSPLASH_API_KEY:
    logger.info("Clé Unsplash chargée")
else:
    logger.warning(
        "Clé Unsplash non trouvée - vérifiez st.secrets['unsplash']['api_key'] ou UNSPLASH_API_KEY"
    )


def generer_image_recette(
    nom_recette: str, description: str = "", ingredients_list: list = None, type_plat: str = ""
) -> str | None:
    """
    Génère une image pour une recette avec meilleure pertinence.

    Stratégie optimisée (priorité):
    1. Leonardo.AI (meilleur pour la cuisine, gratuit avec compte)
    2. Hugging Face Stable Diffusion XL (gratuit, très bon)
    3. Recherche optimisée dans banques d'images (Unsplash > Pexels > Pixabay)
    4. Pollinations.ai (génération rapide)
    5. Replicate SDXL (très haute qualité mais plus lent)

    Args:
        nom_recette: Nom de la recette
        description: Description courte
        ingredients_list: Liste des ingrédients pour améliorer le contexte
        type_plat: Type de plat (entrée, plat, dessert, etc.)

    Returns:
        URL de l'image ou None
    """

    logger.info(f"🎨 Génération image pour: {nom_recette}")

    # Construire une requête optimisée basée sur la recette
    search_query = _construire_query_optimisee(nom_recette, ingredients_list, type_plat)

    # Priorité 1: Hugging Face Stable Diffusion XL (gratuit si clé configurée)
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        try:
            url = _generer_via_huggingface(nom_recette, description, ingredients_list, type_plat)
            if url:
                logger.info(f"✅ Image générée via Hugging Face pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.debug(f"HuggingFace failed: {e}")
    else:
        logger.debug("HUGGINGFACE_API_KEY non configurée, passage au fallback")

    # Priorité 2: Leonardo.AI (spécialisé en culinaire, gratuit avec compte)
    if LEONARDO_API_KEY:
        try:
            url = _generer_via_leonardo(nom_recette, description, ingredients_list, type_plat)
            if url:
                logger.info(f"✅ Image générée via Leonardo.AI pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.debug(f"Leonardo.AI failed: {e}")

    # Priorité 3: Unsplash (meilleur pour les images réelles)
    if UNSPLASH_API_KEY:
        try:
            url = _rechercher_image_unsplash(nom_recette, search_query)
            if url:
                logger.info(f"✅ Image trouvée via Unsplash pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.debug(f"Unsplash API failed: {e}")

    # Priorité 4: Pexels
    if PEXELS_API_KEY:
        try:
            url = _rechercher_image_pexels(nom_recette, search_query)
            if url:
                logger.info(f"✅ Image trouvée via Pexels pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.debug(f"Pexels API failed: {e}")

    # Priorité 5: Pixabay
    if PIXABAY_API_KEY:
        try:
            url = _rechercher_image_pixabay(nom_recette, search_query)
            if url:
                logger.info(f"✅ Image trouvée via Pixabay pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.debug(f"Pixabay API failed: {e}")

    # Priorité 6: Pollinations.ai (génération rapide, pas de clé)
    logger.info(f"Génération IA via Pollinations pour: {nom_recette}")
    try:
        result = _generer_via_pollinations(nom_recette, description, ingredients_list, type_plat)
        if result:
            return result
    except Exception as e:
        logger.debug(f"Pollinations API failed: {e}")

    # Priorité 7: Replicate API (très haute qualité mais plus lent)
    logger.info(f"Génération IA via Replicate pour: {nom_recette}")
    try:
        result = _generer_via_replicate(nom_recette, description, ingredients_list, type_plat)
        if result:
            return result
    except Exception as e:
        logger.debug(f"Replicate API failed: {e}")

    logger.error(f"❌ Impossible de générer une image pour '{nom_recette}'")
    return None


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


def _rechercher_image_pexels(nom_recette: str, search_query: str = "") -> str | None:
    """
    Recherche une image dans la banque Pexels (API gratuite)
    https://www.pexels.com/api/

    Important: Obtenir une clé API gratuite sur https://www.pexels.com/api/
    """
    if not PEXELS_API_KEY:
        return None

    try:
        # Utiliser la query optimisée si fournie, sinon construire basique
        query = search_query if search_query else f"{nom_recette} food cuisine"

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": query,
            "per_page": 15,  # Augmenter pour plus de choix
            "page": 1,
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("photos") and len(data["photos"]) > 0:
            # Prendre une image aléatoire parmi les résultats (priorisé vers le début)
            # Les premiers résultats sont généralement plus pertinents
            photos = data["photos"][: min(8, len(data["photos"]))]
            photo = random.choice(photos)
            image_url = photo["src"]["large"]
            logger.info(f"Pexels: Trouvé '{nom_recette}' avec query '{query}'")
            return image_url
    except Exception as e:
        logger.debug(f"Pexels error: {e}")

    return None


def _rechercher_image_pixabay(nom_recette: str, search_query: str = "") -> str | None:
    """
    Recherche une image dans Pixabay (API gratuite)
    https://pixabay.com/api/

    Important: Obtenir une clé API gratuite sur https://pixabay.com/api/
    """
    if not PIXABAY_API_KEY:
        return None

    try:
        query = search_query if search_query else f"{nom_recette} food cuisine"

        url = "https://pixabay.com/api/"
        params = {
            "q": query,
            "key": PIXABAY_API_KEY,
            "image_type": "photo",
            "category": "food",
            "per_page": 15,  # Augmenter pour plus de choix
            "order": "popular",
            "min_width": 400,  # Priorité sur les images de bonne résolution
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("hits") and len(data["hits"]) > 0:
            # Prendre une image aléatoire parmi les meilleurs résultats
            images = data["hits"][: min(8, len(data["hits"]))]
            image = random.choice(images)
            image_url = image["webformatURL"]
            logger.info(f"Pixabay: Trouvé '{nom_recette}' avec query '{query}'")
            return image_url
    except Exception as e:
        logger.debug(f"Pixabay error: {e}")

    return None


def _rechercher_image_unsplash(nom_recette: str, search_query: str = "") -> str | None:
    """
    Recherche une image dans Unsplash (API gratuite)
    https://unsplash.com/oauth/applications

    Important: Obtenir une clé API gratuite sur https://unsplash.com/oauth/applications
    """
    if not UNSPLASH_API_KEY:
        logger.debug("Clé Unsplash non configurée")
        return None

    try:
        # Utiliser la query optimisée si fournie
        query = search_query if search_query else f"{nom_recette} recipe dish food"

        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "client_id": UNSPLASH_API_KEY,
            "per_page": 20,  # Augmenter pour plus de choix
            "order_by": "relevant",
        }

        logger.info(f"🔍 Recherche Unsplash: '{query}'")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])
        logger.info(f"📊 Unsplash trouvé {len(results)} résultats pour '{nom_recette}'")

        if results and len(results) > 0:
            # Prendre une image avec bon ratio (priorité sur les meilleures)
            # Pour éviter les images abstraites ou mal cadrées
            good_results = []

            for result in results:
                width = result.get("width", 0)
                height = result.get("height", 0)

                if width > 0 and height > 0:
                    ratio = min(width, height) / max(width, height)
                    # Préférer les images avec un bon ratio (0.5 à 0.9 = bon cadrage)
                    if 0.5 <= ratio <= 0.9:
                        good_results.append(result)

            # Si on n'a pas assez de bons résultats, prendre les premiers
            if not good_results:
                good_results = results[: min(8, len(results))]

            # Prendre une image aléatoire parmi les meilleures
            if good_results:
                selected = random.choice(good_results)
                image_url = selected["urls"]["regular"]
                logger.info(f"✅ Unsplash: Image sélectionnée pour '{nom_recette}'")
                return image_url

            # Fallback: prendre simplement la première si aucune ne correspond
            best_result = results[0] if results else None

            if best_result and "urls" in best_result and "regular" in best_result["urls"]:
                image_url = best_result["urls"]["regular"]
                # Extraire la description de manière safe
                description = (
                    best_result.get("description") or best_result.get("alt_description") or "Image"
                )
                if description:
                    description = description[:50]
                logger.info(f"✅ Image sélectionnée: {description}")
                return image_url
            else:
                logger.warning(f"⚠️ Format d'image inattendu pour: {nom_recette}")
                return None
        else:
            logger.warning(f"⚠️ Aucun résultat Unsplash pour: {nom_recette}")

    except Exception as e:
        logger.error(f"❌ Unsplash error: {e}", exc_info=True)

    return None


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


def _generer_via_leonardo(
    nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = ""
) -> str | None:
    """
    Génère une image via Leonardo.AI (meilleur pour la cuisine, gratuit avec compte).
    Leonardo.AI est spécialisé dans la génération d'images culinaires de haute qualité.

    Nécessite : LEONARDO_API_KEY et LEONARDO_MODEL_ID dans .env ou st.secrets
    Obtenir une clé gratuitement sur: https://app.leonardo.ai
    """
    api_key = os.getenv("LEONARDO_API_KEY") or os.getenv("LEONARDO_TOKEN")
    if not api_key:
        logger.debug("LEONARDO_API_KEY not configured, skipping Leonardo.AI")
        return None

    prompt = _construire_prompt_detaille(nom_recette, description, ingredients_list, type_plat)

    try:
        # Utiliser le modèle Leonardo Diffusion XL pour des images culinaires de haute qualité
        url = "https://api.leonardo.ai/v1/generations"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        payload = {
            "prompt": prompt,
            "num_images": 1,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 768,
            "model_id": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",  # Leonardo Diffusion XL
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            if data.get("generations") and len(data["generations"]) > 0:
                image_id = data["generations"][0]["id"]
                image_url = f"https://cdn.leonardo.ai/{image_id}.jpg"
                logger.info(f"✅ Image générée via Leonardo.AI pour '{nom_recette}': {image_url}")
                return image_url
        else:
            logger.debug(f"Leonardo.AI API error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.debug(f"Leonardo.AI generation error: {e}")

    return None


def _generer_via_pollinations(
    nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = ""
) -> str | None:
    """
    Génère une image via Pollinations.ai (gratuit, pas de clé requise)
    Retourne une URL directe
    """
    prompt = _construire_prompt_detaille(nom_recette, description, ingredients_list, type_plat)

    # URL encode le prompt pour éviter les problèmes avec accents
    prompt_encoded = quote(prompt, safe="")

    # URL Pollinations (pas de clé requise) - retourner directement l'URL
    url = f"https://image.pollinations.ai/prompt/{prompt_encoded}"

    try:
        # Vérifier que l'URL est accessible
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Image générée via Pollinations pour '{nom_recette}'")
            return url
    except Exception as e:
        logger.debug(f"Pollinations error: {e}")

    return None


def _generer_via_huggingface(
    nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = ""
) -> str | None:
    """
    Génère une image via Hugging Face Inference API (gratuit avec clé)
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        logger.debug("HUGGINGFACE_API_KEY not configured")
        return None

    prompt = _construire_prompt_detaille(nom_recette, description, ingredients_list, type_plat)

    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Image générée via Hugging Face pour '{nom_recette}'")
            # La réponse est une image binaire - encoder en base64
            img_base64 = base64.b64encode(response.content).decode()
            return f"data:image/png;base64,{img_base64}"
        else:
            logger.debug(f"HF API error: {response.status_code}")
    except Exception as e:
        logger.debug(f"HF error: {e}")

    return None


def _generer_via_replicate(
    nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = ""
) -> str | None:
    """
    Génère une image via Replicate API (nécessite une clé API)
    """
    api_key = os.getenv("REPLICATE_API_TOKEN")
    if not api_key:
        return None

    prompt = _construire_prompt_detaille(nom_recette, description, ingredients_list, type_plat)

    try:
        import replicate

        replicate.api.token = api_key

        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a60c3b36b96384b26f08d47251f049db56fb1c2bda02293be78a16ce",
            input={"prompt": prompt},
        )
        if output and len(output) > 0:
            logger.info(f"✅ Image générée via Replicate pour '{nom_recette}'")
            return output[0]
    except ImportError:
        logger.debug("replicate package not installed")
    except Exception as e:
        logger.debug(f"Replicate error: {e}")

    return None


def telecharger_image_depuis_url(url: str, nom_fichier: str) -> str | None:
    """
    Télécharge une image depuis une URL et la sauvegarde localement.

    Args:
        url: URL de l'image
        nom_fichier: Nom du fichier à sauvegarder

    Returns:
        Chemin local de l'image ou None si erreur
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Sauvegarder dans un dossier temporaire Streamlit
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                f.write(response.content)
                logger.info(f"✅ Image téléchargée: {f.name}")
                return f.name
    except Exception as e:
        logger.error(f"Erreur téléchargement image: {e}")

    return None
