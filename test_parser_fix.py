#!/usr/bin/env python3
"""Test pour vérifier le parsing des recettes"""

import json
from src.core.ai.parser import AnalyseurIA
from src.services.recettes import RecetteSuggestion

# Test 1: JSON avec structure "items"
test_json_1 = """{
    "items": [
        {
            "nom": "Pâtes à la Carbonara",
            "description": "Un classique de la cuisine italienne, simple et délicieux",
            "temps_preparation": 10,
            "temps_cuisson": 15,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "déjeuner",
            "saison": "toute_année",
            "ingredients": [
                {"nom": "pâtes", "quantite": 400, "unite": "g"},
                {"nom": "oeufs", "quantite": 3, "unite": "pcs"},
                {"nom": "lard", "quantite": 200, "unite": "g"}
            ],
            "etapes": [
                {"description": "Cuire les pâtes"},
                {"description": "Préparer la sauce"},
                {"description": "Mélanger"}
            ]
        }
    ]
}"""

# Test 2: Liste directe (ancien format)
test_json_2 = """[
    {
        "nom": "Omelette aux Fromages",
        "description": "Une omelette simple et protéinée",
        "temps_preparation": 5,
        "temps_cuisson": 10,
        "portions": 2,
        "difficulte": "facile",
        "type_repas": "petit_déjeuner",
        "saison": "toute_année",
        "ingredients": [
            {"nom": "oeufs", "quantite": 3, "unite": "pcs"},
            {"nom": "fromage", "quantite": 100, "unite": "g"}
        ],
        "etapes": [
            {"description": "Casser les oeufs"},
            {"description": "Cuire"}
        ]
    }
]"""

def test_parse():
    print("=" * 70)
    print("TEST: Parsing RecetteSuggestion")
    print("=" * 70)
    
    # Test avec récursion et enveloppe items
    print("\n1️⃣  Test avec enveloppe 'items' (nouveau format recommandé):")
    try:
        result = AnalyseurIA.analyser(
            reponse=test_json_1,
            modele=RecetteSuggestion
        )
        print(f"✅ Parsing réussi!")
        print(f"   Recette: {result.nom}")
        print(f"   Difficulté: {result.difficulte}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test avec liste directe
    print("\n2️⃣  Test avec liste directe (ancien format):")
    try:
        result = AnalyseurIA.analyser(
            reponse=test_json_2,
            modele=RecetteSuggestion
        )
        print(f"✅ Parsing réussi!")
        print(f"   Recette: {result.nom}")
        print(f"   Difficulté: {result.difficulte}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test du JSON dans la réponse avec du texte avant/après
    print("\n3️⃣  Test avec JSON en markdown:")
    test_with_markdown = """Voici les recettes suggérées:

```json
{
    "items": [
        {
            "nom": "Soupe à l'Oignon",
            "description": "Une soupe française classique",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "déjeuner",
            "saison": "automne",
            "ingredients": [
                {"nom": "oignons", "quantite": 6, "unite": "pcs"}
            ],
            "etapes": [
                {"description": "Émincer les oignons"},
                {"description": "Cuire"}
            ]
        }
    ]
}
```

C'est la meilleure recette pour vous!"""
    
    try:
        result = AnalyseurIA.analyser(
            reponse=test_with_markdown,
            modele=RecetteSuggestion
        )
        print(f"✅ Parsing réussi!")
        print(f"   Recette: {result.nom}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "=" * 70)
    print("Tests terminés!")
    print("=" * 70)

if __name__ == "__main__":
    test_parse()
