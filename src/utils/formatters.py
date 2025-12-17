# src/utils/formatters.py - NOUVEAU FICHIER

"""
Utilitaires de formatage pour l'affichage
"""

def format_quantite(quantite: float) -> str:
    """
    Formate une quantité en supprimant les décimales inutiles

    Exemples:
        1.0 → "1"
        1.5 → "1,5"
        2.0 → "2"
        2.75 → "2,75"

    Args:
        quantite: Nombre à formater

    Returns:
        String formaté
    """
    if quantite is None:
        return "0"

    # Si c'est un entier (ou très proche)
    if quantite == int(quantite) or abs(quantite - round(quantite)) < 0.01:
        return str(int(round(quantite)))

    # Sinon, afficher avec virgule (format français)
    return f"{quantite:.2f}".rstrip('0').rstrip('.').replace('.', ',')


def format_temps(minutes: int) -> str:
    """
    Formate un temps en minutes de manière lisible

    Exemples:
        15 → "15min"
        60 → "1h"
        90 → "1h30"
        125 → "2h05"

    Args:
        minutes: Durée en minutes

    Returns:
        String formaté
    """
    if minutes < 60:
        return f"{minutes}min"

    heures = minutes // 60
    mins = minutes % 60

    if mins == 0:
        return f"{heures}h"

    return f"{heures}h{mins:02d}" if mins < 10 else f"{heures}h{mins}"


def format_ingredients_list(ingredients: list) -> str:
    """
    Formate une liste d'ingrédients pour l'affichage

    Args:
        ingredients: Liste de dicts avec {nom, quantite, unite}

    Returns:
        String formaté avec virgules
    """
    formatted = []

    for ing in ingredients[:5]:  # Max 5 pour pas surcharger
        qty = format_quantite(ing["quantite"])
        formatted.append(f"{qty} {ing['unite']} {ing['nom']}")

    if len(ingredients) > 5:
        formatted.append(f"+ {len(ingredients) - 5} autre(s)")

    return ", ".join(formatted)