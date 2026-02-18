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
Les constantes partagées sont maintenant dans src/core/constants.py.
"""

__all__ = [
    "accueil",
    "cuisine",
    "famille",
    "planning",
    "maison",
    "parametres",
    "utilitaires",
    "jeux",
]
