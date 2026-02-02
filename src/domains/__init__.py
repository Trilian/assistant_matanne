"""Domaines organisés par contexte métier.

Architecture:
- cuisine: Recettes, planning repas, inventaire, courses
- famille: Jules, santé, activités, shopping
- planning: Calendrier, routines, planification
- maison: Entretien, projets, jardin, zones
- utils: Accueil, paramètres, rapports, barcode
- jeux: Paris sportifs, loto
"""

from . import cuisine, famille, planning, maison, utils, jeux

__all__ = ["cuisine", "famille", "planning", "maison", "utils", "jeux"]

