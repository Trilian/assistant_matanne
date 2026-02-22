"""Rewrite recettes/utils.py - keep only pure functions, remove DB duplicates."""

import os

new_content = '''"""
Logique metier du module Recettes (sans UI Streamlit).
Fonctions pures testables independamment de Streamlit.

Note: Les fonctions CRUD (get_toutes_recettes, creer_recette, etc.)
ont ete supprimees car dupliquant ServiceRecettes.
Utiliser: from src.services.cuisine.recettes import obtenir_service_recettes
"""

from typing import Any


# ===================================================================
# LOGIQUE CALCULS & STATISTIQUES (PURE - SANS DB)
# ===================================================================


def calculer_cout_recette(recette, prix_ingredients: dict[str, float]) -> float:
    """Calcule le cout estime d'une recette."""
    cout_total = 0.0

    for ingredient in recette.ingredients:
        # Recherche de l'ingredient dans le dictionnaire des prix
        for nom_ingredient, prix in prix_ingredients.items():
            if nom_ingredient.lower() in ingredient.lower():
                cout_total += prix
                break

    return round(cout_total, 2)


def calculer_calories_portion(recette) -> float | None:
    """Calcule les calories par portion."""
    if not recette.calories or not recette.portions:
        return None

    return round(recette.calories / recette.portions, 2)


def valider_recette(data: dict[str, Any]) -> tuple[bool, str | None]:
    """Valide les donnees d'une recette."""
    if not data.get("nom"):
        return False, "Le nom est requis"

    if not data.get("ingredients") or len(data["ingredients"]) == 0:
        return False, "Au moins un ingredient est requis"

    if not data.get("instructions") or len(data["instructions"]) == 0:
        return False, "Au moins une instruction est requise"

    if data.get("temps_preparation", 0) < 0:
        return False, "Le temps de preparation doit etre positif"

    if data.get("portions", 0) <= 0:
        return False, "Le nombre de portions doit etre superieur a 0"

    return True, None


# ===================================================================
# FORMATAGE
# ===================================================================


def formater_quantite(quantite: float | int | str) -> str:
    """Formate une quantite: affiche 2 au lieu de 2.0"""
    # Convertir en nombre si c'est une chaine
    if isinstance(quantite, str):
        try:
            quantite = float(quantite)
        except (ValueError, TypeError):
            return str(quantite)

    if isinstance(quantite, int | float):
        if quantite == int(quantite):
            return str(int(quantite))
        else:
            return str(quantite)
    return str(quantite)


__all__ = ["formater_quantite", "valider_recette", "calculer_cout_recette", "calculer_calories_portion"]
'''

filepath = os.path.join("src", "modules", "cuisine", "recettes", "utils.py")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)
print(f"Rewrote {filepath} - {len(new_content)} bytes")
