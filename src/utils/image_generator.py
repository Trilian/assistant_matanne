"""
Générateur d'images pour les recettes
Utilise plusieurs APIs gratuites pour générer des images réelles de haute qualité
"""

import os
import requests
import logging
from typing import Optional
import base64
from urllib.parse import quote, urlencode
import random

logger = logging.getLogger(__name__)

# Fonction helper pour charger les clés depuis st.secrets (Streamlit Cloud) ou os.getenv (local)
def _get_api_key(key_name: str) -> Optional[str]:
    """Charge une clé API depuis st.secrets (Streamlit Cloud) ou os.getenv (local)"""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            try:
                # Essayer section spécifique d'abord (ex: st.secrets["unsplash"]["api_key"])
                if key_name == "UNSPLASH_API_KEY":
                    return st.secrets.get("unsplash", {}).get("api_key")
                elif key_name == "PEXELS_API_KEY":
                    return st.secrets.get("pexels", {}).get("api_key")
                elif key_name == "PIXABAY_API_KEY":
                    return st.secrets.get("pixabay", {}).get("api_key")
            except:
                pass
    except:
        pass
    
    # Fallback à os.getenv (pour dev local avec .env)
    return os.getenv(key_name)

# APIs configurables
PEXELS_API_KEY = _get_api_key('PEXELS_API_KEY')  # Gratuit: https://www.pexels.com/api/
PIXABAY_API_KEY = _get_api_key('PIXABAY_API_KEY')  # Gratuit: https://pixabay.com/api/
UNSPLASH_API_KEY = _get_api_key('UNSPLASH_API_KEY')  # Gratuit: https://unsplash.com/oauth/applications

# Debug logging pour Streamlit Cloud
# Utiliser print() en plus de logger pour être visible dans Streamlit logs
print("\n" + "="*60)
print("🖼️  IMAGE GENERATOR INITIALIZED")
print("="*60)
print(f"✅ Unsplash:  {'CONFIGURED' if UNSPLASH_API_KEY else 'NOT SET'} {UNSPLASH_API_KEY[:10] if UNSPLASH_API_KEY else ''}...")
print(f"✅ Pexels:    {'CONFIGURED' if PEXELS_API_KEY else 'NOT SET'} {PEXELS_API_KEY[:10] if PEXELS_API_KEY else ''}...")
print(f"✅ Pixabay:   {'CONFIGURED' if PIXABAY_API_KEY else 'NOT SET'} {PIXABAY_API_KEY[:10] if PIXABAY_API_KEY else ''}...")
print("="*60 + "\n")

if UNSPLASH_API_KEY:
    logger.info(f"✅ Clé Unsplash chargée (premiers caractères: {UNSPLASH_API_KEY[:10]}...)")
else:
    logger.warning("⚠️ Clé Unsplash non trouvée - vérifiez st.secrets['unsplash']['api_key'] ou UNSPLASH_API_KEY")


def generer_image_recette(nom_recette: str, description: str = "", ingredients_list: list = None, type_plat: str = "") -> Optional[str]:
    """
    Génère une image pour une recette.
    
    Essaie plusieurs sources dans cet ordre:
    1. Unsplash (meilleure qualité, bonne spécificité)
    2. Recherche dans des banques d'images réelles (Pexels, Pixabay)
    3. Génération avec API IA (Pollinations.ai, Replicate)
    
    Args:
        nom_recette: Nom de la recette
        description: Description courte
        ingredients_list: Liste des ingrédients pour améliorer le contexte
        type_plat: Type de plat (entrée, plat, dessert, etc.)
        
    Returns:
        URL de l'image ou None
    """
    
    logger.info(f"🎨 Génération image pour: {nom_recette}")
    
    # Priorité 1: Unsplash (meilleur pour les recettes)
    if UNSPLASH_API_KEY:
        try:
            url = _rechercher_image_unsplash(nom_recette)
            if url:
                logger.info(f"✅ Image trouvée via Unsplash pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.warning(f"Unsplash API échouée: {e}")
    
    # Priorité 2: Pexels
    if PEXELS_API_KEY:
        try:
            url = _rechercher_image_pexels(nom_recette)
            if url:
                logger.info(f"✅ Image trouvée via Pexels pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.warning(f"Pexels API échouée: {e}")
    
    # Priorité 3: Pixabay
    if PIXABAY_API_KEY:
        try:
            url = _rechercher_image_pixabay(nom_recette)
            if url:
                logger.info(f"✅ Image trouvée via Pixabay pour '{nom_recette}'")
                return url
        except Exception as e:
            logger.warning(f"Pixabay API échouée: {e}")
    
    # Fallback: Essayer Pollinations.ai (génération IA rapide, pas de clé requise)
    logger.info(f"Tentative génération IA via Pollinations pour: {nom_recette}")
    try:
        result = _generer_via_pollinations(nom_recette, description, ingredients_list, type_plat)
        if result:
            return result
    except Exception as e:
            print(f"  ❌ Pollinations returned None")
    except Exception as e:
        logger.warning(f"Pollinations API échouée: {e}")
    
    # Essayer Replicate API (meilleure qualité IA)
    logger.info(f"Tentative génération IA via Replicate pour: {nom_recette}")
    try:
        result = _generer_via_replicate(nom_recette, description, ingredients_list, type_plat)
        if result:
            return result
    except Exception as e:
        logger.warning(f"Replicate API échouée: {e}")
    
    logger.error(f"❌ Impossible de générer une image pour '{nom_recette}'")
    return None


def _rechercher_image_pexels(nom_recette: str) -> Optional[str]:
    """
    Recherche une image dans la banque Pexels (API gratuite)
    https://www.pexels.com/api/
    
    Important: Obtenir une clé API gratuite sur https://www.pexels.com/api/
    """
    if not PEXELS_API_KEY:
        return None
    
    try:
        # Améliorer la requête de recherche
        query = f"{nom_recette} food cuisine"
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": query,
            "per_page": 5,
            "page": 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("photos") and len(data["photos"]) > 0:
            # Prendre une image aléatoire parmi les résultats
            photo = random.choice(data["photos"])
            return photo["src"]["large"]
    except Exception as e:
        logger.debug(f"Pexels error: {e}")
    
    return None


def _rechercher_image_pixabay(nom_recette: str) -> Optional[str]:
    """
    Recherche une image dans Pixabay (API gratuite)
    https://pixabay.com/api/
    
    Important: Obtenir une clé API gratuite sur https://pixabay.com/api/
    """
    if not PIXABAY_API_KEY:
        return None
    
    try:
        query = f"{nom_recette} food cuisine"
        url = "https://pixabay.com/api/"
        params = {
            "q": query,
            "key": PIXABAY_API_KEY,
            "image_type": "photo",
            "category": "food",
            "per_page": 5,
            "order": "popular"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("hits") and len(data["hits"]) > 0:
            # Prendre une image aléatoire parmi les résultats
            image = random.choice(data["hits"])
            return image["webformatURL"]
    except Exception as e:
        logger.debug(f"Pixabay error: {e}")
    
    return None


def _rechercher_image_unsplash(nom_recette: str) -> Optional[str]:
    """
    Recherche une image dans Unsplash (API gratuite)
    https://unsplash.com/oauth/applications
    
    Important: Obtenir une clé API gratuite sur https://unsplash.com/oauth/applications
    """
    if not UNSPLASH_API_KEY:
        logger.debug("Clé Unsplash non configurée")
        return None
    
    try:
        # Requête plus spécifique pour éviter les fausses matches
        query = f"{nom_recette} recipe dish food"
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "client_id": UNSPLASH_API_KEY,
            "per_page": 10,
            "order_by": "relevant"
        }
        
        logger.info(f"🔍 Recherche Unsplash: '{query}'")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        logger.info(f"📊 Unsplash trouvé {len(results)} résultats")
        
        if results and len(results) > 0:
            # Prendre l'image avec le meilleur ratio (pas trop carré ni ultra-wide)
            # Pour éviter les images abstraites ou mal cadrées
            best_result = None
            best_score = 0
            
            for result in results:
                width = result.get("width", 0)
                height = result.get("height", 0)
                
                if width > 0 and height > 0:
                    ratio = min(width, height) / max(width, height)
                    # Préférer les images avec un bon ratio (0.5 à 0.9 = pas trop carré, pas ultra-wide)
                    if 0.5 <= ratio <= 0.9:
                        best_result = result
                        break
            
            # Fallback: prendre simplement la première si aucune ne correspond
            if not best_result:
                best_result = results[0]
            
            if best_result and "urls" in best_result and "regular" in best_result["urls"]:
                image_url = best_result["urls"]["regular"]
                # Extraire la description de manière safe
                description = best_result.get('description') or best_result.get('alt_description') or 'Image'
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
    Retourne une URL directe
    """
    prompt = _construire_prompt_detaille(nom_recette, description, ingredients_list, type_plat)
    
    # URL encode le prompt pour éviter les problèmes avec accents
    prompt_encoded = quote(prompt, safe='')
    
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
