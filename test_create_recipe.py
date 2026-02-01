#!/usr/bin/env python
"""Test création recette depuis données IA"""

from src.services.recettes import RecetteService
from src.core.database import obtenir_contexte_db

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

try:
    with obtenir_contexte_db() as db:
        service = RecetteService(db)
        result = service.create_complete(test_data, db)
        print(f"✅ Success: {result.nom}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
