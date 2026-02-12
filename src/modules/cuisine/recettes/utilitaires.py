"""
Fonctions helper pour le module recettes UI.
"""


def formater_quantite(quantite: float | int | str) -> str:
    """Formate une quantité: affiche 2 au lieu de 2.0"""
    # Convertir en nombre si c'est une chaîne
    if isinstance(quantite, str):
        try:
            quantite = float(quantite)
        except (ValueError, TypeError):
            return str(quantite)
    
    if isinstance(quantite, (int, float)):
        if quantite == int(quantite):
            return str(int(quantite))
        else:
            return str(quantite)
    return str(quantite)


__all__ = ["formater_quantite"]
