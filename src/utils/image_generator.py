"""
Générateur d'images pour les recettes
Utilise une API de génération d'images gratuite ou une alternative
"""

import os
import requests
import logging
from typing import Optional
import base64
from urllib.parse import quote

logger = logging.getLogger(__name__)


def generer_image_recette(nom_recette: str, description: str = "", ingredients_list: list = None, type_plat: str = "") -> Optional[str]:
    """
    Génère une image pour une recette.
    
    Essaie plusieurs APIs de génération d'images:
    1. Hugging Face Inference API (gratuit)
    2. Pollinations.ai (gratuit, pas de clé)
    3. Fallback: description textuelle
    
    Args:
        nom_recette: Nom de la recette
        description: Description courte
        ingredients_list: Liste des ingrédients pour améliorer le contexte
        type_plat: Type de plat (entrée, plat, dessert, etc.)
        
    Returns:
        URL de l'image générée ou None
    """
    
    # Essayer Hugging Face d'abord (meilleure qualité)
    try:
        return _generer_via_huggingface(nom_recette, description, ingredients_list, type_plat)
    except Exception as e:
        logger.debug(f"Hugging Face API échouée: {e}")
    
    # Essayer Pollinations.ai (rapide, gratuit)
    try:
        return _generer_via_pollinations(nom_recette, description, ingredients_list, type_plat)
    except Exception as e:
        logger.debug(f"Pollinations API échouée: {e}")
    
    # Essayer Replicate API
    try:
        return _generer_via_replicate(nom_recette, description, ingredients_list, type_plat)
    except Exception as e:
        logger.debug(f"Replicate API échouée: {e}")
    
    logger.warning(f"Impossible de générer une image pour '{nom_recette}'")
    return None


def _construire_prompt_detaille(nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = "") -> str:
    """Construit un prompt plus détaillé pour la génération d'images"""
    
    # Ingrédients clés à mentionner
    ingredients_mentions = ""
    if ingredients_list and isinstance(ingredients_list, list):
        # Extraire les noms des ingrédients principaux (max 3-4)
        ingredient_names = []
        for ing in ingredients_list[:4]:
            if isinstance(ing, dict) and 'nom' in ing:
                ingredient_names.append(ing['nom'].lower())
            elif isinstance(ing, str):
                ingredient_names.append(ing.lower())
        
        if ingredient_names:
            ingredients_mentions = f"with {', '.join(ingredient_names)}"
    
    # Type de plat en français
    type_map = {
        "petit_déjeuner": "breakfast, morning meal",
        "déjeuner": "lunch, main course",
        "dîner": "dinner, evening meal",
        "goûter": "snack, afternoon treat",
        "apéritif": "appetizer, starter",
        "dessert": "dessert, sweet dish"
    }
    
    type_phrase = type_map.get(type_plat, "cuisine")
    
    # Construire le prompt final - très descriptif pour une meilleure génération
    if description:
        prompt = f"Professional food photography of {nom_recette} {ingredients_mentions}. {description}. {type_phrase}. Appetizing, vibrant colors, well-plated, restaurant quality, high quality, 4K, professional lighting, mouth-watering"
    else:
        prompt = f"Professional food photography of {nom_recette} {ingredients_mentions}. {type_phrase}. Beautiful presentation, appetizing, vibrant colors, well-plated, restaurant quality, high quality, 4K, professional lighting, mouth-watering"
    
    return prompt


def _generer_via_pollinations(nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = "") -> Optional[str]:
    """
    Génère une image via Pollinations.ai (gratuit, pas de clé requise)
    Retourne une image encodée en base64 pour Streamlit
    """
    prompt = _construire_prompt_detaille(nom_recette, description, ingredients_list, type_plat)
    
    # URL encode le prompt pour éviter les problèmes avec accents
    prompt_encoded = quote(prompt, safe='')
    
    # URL Pollinations (pas de clé requise)
    url = f"https://image.pollinations.ai/prompt/{prompt_encoded}"
    
    try:
        # Télécharger l'image et l'encoder en base64
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Image générée via Pollinations pour '{nom_recette}'")
            # Encoder en base64 pour que Streamlit l'affiche correctement
            img_base64 = base64.b64encode(response.content).decode()
            return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        logger.debug(f"Pollinations error: {e}")
    
    return None


def _generer_via_huggingface(nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = "") -> Optional[str]:
    """
    Génère une image via Hugging Face Inference API (gratuit avec clé)
    """
    api_key = os.getenv('HUGGINGFACE_API_KEY')
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


def _generer_via_replicate(nom_recette: str, description: str, ingredients_list: list = None, type_plat: str = "") -> Optional[str]:
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
            input={"prompt": prompt}
        )
        if output and len(output) > 0:
            logger.info(f"✅ Image générée via Replicate pour '{nom_recette}'")
            return output[0]
    except ImportError:
        logger.debug("replicate package not installed")
    except Exception as e:
        logger.debug(f"Replicate error: {e}")
    
    return None


def telecharger_image_depuis_url(url: str, nom_fichier: str) -> Optional[str]:
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
