"""
Fournisseurs d'images pour la génération de recettes.

Extrait de generator.py pour réduire sa taille.
Contient les fonctions de recherche/génération par fournisseur:
- Pexels (recherche)
- Pixabay (recherche)
- Unsplash (recherche)
- Leonardo.AI (génération)
- Hugging Face (génération)
- Pollinations.ai (génération)
- Replicate (génération)
"""

import base64
import logging
import os
import random
from urllib.parse import quote

import requests

from .prompts import _construire_prompt_detaille

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# RECHERCHE D'IMAGES — BANQUES GRATUITES
# ═══════════════════════════════════════════════════════════


def _rechercher_image_pexels(
    nom_recette: str, search_query: str = "", api_key: str | None = None
) -> str | None:
    """
    Recherche une image dans la banque Pexels (API gratuite)
    https://www.pexels.com/api/

    Important: Obtenir une clé API gratuite sur https://www.pexels.com/api/
    """
    if not api_key:
        return None

    try:
        # Utiliser la query optimisée si fournie, sinon construire basique
        query = search_query if search_query else f"{nom_recette} food cuisine"

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": api_key}
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


def _rechercher_image_pixabay(
    nom_recette: str, search_query: str = "", api_key: str | None = None
) -> str | None:
    """
    Recherche une image dans Pixabay (API gratuite)
    https://pixabay.com/api/

    Important: Obtenir une clé API gratuite sur https://pixabay.com/api/
    """
    if not api_key:
        return None

    try:
        query = search_query if search_query else f"{nom_recette} food cuisine"

        url = "https://pixabay.com/api/"
        params = {
            "q": query,
            "key": api_key,
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


def _rechercher_image_unsplash(
    nom_recette: str, search_query: str = "", api_key: str | None = None
) -> str | None:
    """
    Recherche une image dans Unsplash (API gratuite)
    https://unsplash.com/oauth/applications

    Important: Obtenir une clé API gratuite sur https://unsplash.com/oauth/applications
    """
    if not api_key:
        logger.debug("Clé Unsplash non configurée")
        return None

    try:
        # Utiliser la query optimisée si fournie
        query = search_query if search_query else f"{nom_recette} recipe dish food"

        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "client_id": api_key,
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


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION D'IMAGES — APIs IA
# ═══════════════════════════════════════════════════════════


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
