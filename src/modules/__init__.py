"""Modules organises par contexte metier.

Architecture:
- cuisine: Recettes, planning repas, inventaire, courses
- famille: Jules, sante, activites, shopping
- planning: Calendrier, routines, planification
- maison: Entretien, projets, jardin, zones
- utilitaires: Accueil, parametres, rapports, barcode
- jeux: Paris sportifs, loto

Note: Les modules sont chargés paresseusement - pas d'import automatique
pour éviter les dépendances circulaires.
"""

# Chargement différé explicite: seul 'shared' est importé automatiquement
# car il contient les constantes partagées sans dépendances
from . import shared

__all__ = [
    "accueil",
    "cuisine",
    "famille",
    "planning",
    "maison",
    "parametres",
    "utilitaires",
    "jeux",
    "shared",
]
