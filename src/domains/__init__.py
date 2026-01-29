"""Domaines organisés par contexte métier.

Architecture:
- cuisine: Recettes, planning repas, inventaire, courses
- famille: Jules, santé, activités, shopping
- planning: Calendrier, routines, planification
- maison: Entretien, projets, jardin
- shared: Accueil, paramètres, rapports
"""

from . import cuisine, famille, planning, maison, shared

__all__ = ["cuisine", "famille", "planning", "maison", "shared"]

