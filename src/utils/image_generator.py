"""
Générateur d'images pour les recettes
Utilise une API de génération d'images gratuite ou une alternative
"""

import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generer_image_recette(nom_recette: str, description: str = "") -> Optional[str]:
    """
    Génère une image pour une recette.
    
    Essaie plusieurs APIs de génération d'images:
    1. Hugging Face Inference API (gratuit)
    2. Fallback: description textuelle
    
    Args:
        nom_recette: Nom de la recette
        description: Description courte
        
    Returns:
        URL de l'image générée ou None
    """
    
    # Essayer Hugging Face API
    try:
        return _generer_via_huggingface(nom_recette, description)
    except Exception as e:
        logger.debug(f"Hugging Face API échouée: {e}")
    
    # Essayer Replicate API
    try:
        return _generer_via_replicate(nom_recette, description)
    except Exception as e:
        logger.debug(f"Replicate API échouée: {e}")
    
    logger.warning(f"Impossible de générer une image pour '{nom_recette}'")
    return None


def _generer_via_huggingface(nom_recette: str, description: str) -> Optional[str]:
    """
    Génère une image via Hugging Face Inference API (gratuit, pas de clé requise)
    """
    prompt = f"Beautiful dish of {nom_recette}"
    if description:
        prompt += f": {description}"
    prompt += ". Food photography, professional lighting, appetizing"
    
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
    
    # Si pas de clé, utiliser un model public
    if not headers["Authorization"].endswith("''"):
        response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=30)
        if response.status_code == 200:
            # La réponse est une image binaire
            # Sauvegarder temporairement et retourner l'URL
            logger.info(f"✅ Image générée via Hugging Face pour '{nom_recette}'")
            # Retourner base64 encodée pour Streamlit
            import base64
            img_base64 = base64.b64encode(response.content).decode()
            return f"data:image/png;base64,{img_base64}"
    
    return None


def _generer_via_replicate(nom_recette: str, description: str) -> Optional[str]:
    """
    Génère une image via Replicate API (nécessite une clé API)
    """
    api_key = os.getenv("REPLICATE_API_TOKEN")
    if not api_key:
        return None
    
    prompt = f"Beautiful dish of {nom_recette}"
    if description:
        prompt += f": {description}"
    prompt += ". Food photography, professional lighting, appetizing, high quality"
    
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
