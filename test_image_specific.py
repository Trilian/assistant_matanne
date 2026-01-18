#!/usr/bin/env python3
"""
Test de génération d'image pour une recette spécifique
"""

import os
import sys
import logging

# Configurer logging détaillé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test local: charger les clés depuis .env
from pathlib import Path
env_file = Path(__file__).parent / ".env.local"
if env_file.exists():
    print(f"📁 Chargement de {env_file}")
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

print("\n" + "="*60)
print("TEST GÉNÉRATION D'IMAGE")
print("="*60)

from src.utils.image_generator import (
    generer_image_recette,
    UNSPLASH_API_KEY,
    PEXELS_API_KEY,
    PIXABAY_API_KEY
)

print("\n🔑 Clés configurées:")
print(f"  Unsplash:  {'✅' if UNSPLASH_API_KEY else '❌'} {UNSPLASH_API_KEY[:10] if UNSPLASH_API_KEY else 'NOT SET'}...")
print(f"  Pexels:    {'✅' if PEXELS_API_KEY else '❌'} {PEXELS_API_KEY[:10] if PEXELS_API_KEY else 'NOT SET'}...")
print(f"  Pixabay:   {'✅' if PIXABAY_API_KEY else '❌'} {PIXABAY_API_KEY[:10] if PIXABAY_API_KEY else 'NOT SET'}...")

print("\n" + "-"*60)
print("Test 1: Aubergine Rôtie")
print("-"*60)
url = generer_image_recette(
    nom_recette="Aubergine rôtie",
    description="Aubergine rôtie avec ail et herbes",
    ingredients_list=[
        {'nom': 'Aubergine', 'quantite': 1, 'unite': 'pièce'},
        {'nom': 'Ail', 'quantite': 2, 'unite': 'gousses'},
    ]
)
print(f"\n✅ Résultat: {url[:80] if url else '❌ AUCUNE IMAGE'}...")

print("\n" + "-"*60)
print("Test 2: Fromage blanc")
print("-"*60)
url2 = generer_image_recette(
    nom_recette="Fromage blanc",
    description="Fromage blanc avec miel",
)
print(f"\n✅ Résultat: {url2[:80] if url2 else '❌ AUCUNE IMAGE'}...")

print("\n" + "="*60)
print("✅ Test terminé - Vérifiez les logs ci-dessus")
print("="*60)
