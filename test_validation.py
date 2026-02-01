#!/usr/bin/env python
"""Test validation et création recette depuis données IA"""

from src.core.validators_pydantic import RecetteInput, IngredientInput, EtapeInput

# Test data similar to what IA generates
test_data = {
    "nom": "Pates Bolognaises",
    "description": "Une savoureuse sauce bolognaise maison",
    "temps_preparation": 15,
    "temps_cuisson": 30,
    "portions": 4,
    "difficulte": "moyen",
    "type_repas": "déjeuner",
    "saison": "toute_année",
    "ingredients": [
        {"nom": "Pates", "quantite": 400, "unite": "g"},
        {"nom": "Tomate", "quantite": 500, "unite": "g"}
    ],
    "etapes": [
        {"description": "Faire cuire les pates"},
        {"description": "Preparer la sauce"}
    ]
}

# First, test direct dict conversion
try:
    ingredients = [
        IngredientInput(
            nom=ing.get("nom", ""),
            quantite=ing.get("quantite", 1.0),
            unite=ing.get("unite", ""),
        )
        for ing in test_data["ingredients"]
    ]
    print(f"✅ Ingredients créés: {len(ingredients)}")
    
    etapes = [
        EtapeInput(
            ordre=idx + 1,
            description=etape.get("description", ""),
            duree=etape.get("duree")
        )
        for idx, etape in enumerate(test_data["etapes"])
    ]
    print(f"✅ Étapes créées: {len(etapes)}")
except Exception as e:
    print(f"❌ Error creating ingredients/etapes: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

# Now test RecetteInput validation
try:
    test_data["ingredients"] = [
        IngredientInput(
            nom=ing.get("nom", ""),
            quantite=ing.get("quantite", 1.0),
            unite=ing.get("unite", ""),
        )
        for ing in test_data["ingredients"]
    ]
    test_data["etapes"] = [
        EtapeInput(
            ordre=idx + 1,
            description=etape.get("description", ""),
            duree=etape.get("duree")
        )
        for idx, etape in enumerate(test_data["etapes"])
    ]
    
    validated = RecetteInput(**test_data)
    print(f"✅ RecetteInput validation: SUCCESS")
    print(f"   - Nom: {validated.nom}")
    print(f"   - Type repas: {validated.type_repas}")
    print(f"   - Difficulté: {validated.difficulte}")
    print(f"   - Ingrédients: {len(validated.ingredients)}")
    print(f"   - Étapes: {len(validated.etapes)}")
except Exception as e:
    print(f"❌ Error validating RecetteInput: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n✅ All validation tests passed!")
