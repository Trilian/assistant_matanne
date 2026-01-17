#!/usr/bin/env python3
"""
Script de test pour la génération d'images des recettes
Vérifie que les APIs sont correctement configurées et fonctionnent
"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Ajouter le projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.image_generator import (
    generer_image_recette,
)

# Test recipes
TEST_RECIPES = [
    {
        "nom": "Pâtes Carbonara",
        "description": "Recette italienne classique avec œufs et guanciale",
        "type_plat": "déjeuner",
        "ingredients": [
            {"nom": "œufs", "quantite": 4, "unite": "pcs"},
            {"nom": "guanciale", "quantite": 200, "unite": "g"},
            {"nom": "parmesan", "quantite": 100, "unite": "g"},
        ]
    },
    {
        "nom": "Tarte Tatin",
        "description": "Délicieuse tarte aux pommes caramélisées",
        "type_plat": "dessert",
        "ingredients": [
            {"nom": "pommes", "quantite": 6, "unite": "pcs"},
            {"nom": "sucre", "quantite": 100, "unite": "g"},
            {"nom": "beurre", "quantite": 50, "unite": "g"},
        ]
    },
    {
        "nom": "Croissants au Chocolat",
        "description": "Viennoiserie française croustillante avec chocolat",
        "type_plat": "petit_déjeuner",
        "ingredients": [
            {"nom": "pâte feuilletée", "quantite": 500, "unite": "g"},
            {"nom": "chocolat noir", "quantite": 150, "unite": "g"},
        ]
    },
]


def print_header(text: str) -> None:
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_api_keys():
    """Vérifie les clés API configurées"""
    print_header("🔑 Vérification des Clés API")
    
    apis = {
        "UNSPLASH_API_KEY": os.getenv("UNSPLASH_API_KEY"),
        "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY"),
        "PIXABAY_API_KEY": os.getenv("PIXABAY_API_KEY"),
        "REPLICATE_API_TOKEN": os.getenv("REPLICATE_API_TOKEN"),
    }
    
    configured = 0
    for api_name, key in apis.items():
        if key:
            print(f"✅ {api_name:25} : configurée ({len(key)} caractères)")
            configured += 1
        else:
            print(f"❌ {api_name:25} : NON configurée")
    
    print(f"\n📊 Résumé: {configured}/4 APIs configurées")
    
    if configured == 0:
        print("\n⚠️  ATTENTION: Aucune clé API configurée!")
        print("   Seul Pollinations.ai fonctionnera (sans clé)")
        return False
    
    return True


def test_single_api(recipe: dict) -> dict:
    """Test chaque API individuellement"""
    print_header(f"🧪 Test: {recipe['nom']}")
    
    results: dict[str, str] = {}
    
    # Tester avec la fonction générale qui essaie tout automatiquement
    try:
        logger.info(f"Test génération pour: {recipe['nom']}")
        url = generer_image_recette(
            recipe['nom'],
            recipe['description'],
            recipe.get('ingredients', []),
            recipe['type_plat']
        )
        if url:
            results['Unsplash/Pexels/Pixabay'] = '✅'
            print(f"✅ Image obtenue: OK")
        else:
            results['Fallback'] = '⚠️'
            print(f"⚠️  Aucune source n'a pu fournir une image")
    except Exception as e:
        results['Erreur'] = '❌'
        print(f"❌ Erreur: {str(e)[:50]}")
    
    return results


def test_complete_workflow():
    """Test le workflow complet de génération"""
    print_header("🚀 Test Workflow Complet")
    
    for recipe in TEST_RECIPES[:1]:  # Tester juste une pour ne pas trop attendre
        logger.info(f"Génération pour: {recipe['nom']}")
        url = generer_image_recette(
            recipe['nom'],
            recipe['description'],
            recipe.get('ingredients', []),
            recipe['type_plat']
        )
        
        if url:
            print(f"✅ {recipe['nom']:30} → Image générée")
            print(f"   URL: {url[:80]}...")
        else:
            print(f"❌ {recipe['nom']:30} → Échec")


def main():
    """Fonction principale"""
    print("\n" + "🎨 " * 20)
    print("  TEST DE GÉNÉRATION D'IMAGES POUR RECETTES")
    print("🎨 " * 20)
    
    # Étape 1: Vérifier les clés
    has_apis = check_api_keys()
    
    # Étape 2: Tester chaque API
    if has_apis:
        print("\n")
        for recipe in TEST_RECIPES:
            test_single_api(recipe)
    
    # Étape 3: Test complet
    print("\n")
    test_complete_workflow()
    
    # Résumé final
    print_header("📋 Résumé")
    print("""
✅ Tests terminés!

Recommandations:
1. Pour commencer: Configurer UNSPLASH_API_KEY
2. Pour plus de couverture: Ajouter PEXELS_API_KEY et PIXABAY_API_KEY
3. Pollinations.ai fonctionne sans clé (excellente alternative)

Documentation: IMAGE_GENERATION_SETUP.md
""")


if __name__ == "__main__":
    main()
