"""Modules organises par contexte metier.

Architecture:
- cuisine: Recettes, planning repas, inventaire, courses
- famille: Jules, sante, activites, shopping
- planning: Calendrier, routines, planification
- maison: Entretien, projets, jardin, zones
- outils: Accueil, parametres, rapports, barcode
- jeux: Paris sportifs, loto
"""

from . import cuisine, famille, jeux, maison, outils, planning, shared

__all__ = ["cuisine", "famille", "planning", "maison", "outils", "jeux", "shared"]
