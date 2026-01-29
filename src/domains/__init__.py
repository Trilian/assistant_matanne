"""Domaines organisÃ©s par contexte mÃ©tier.

Architecture:
- cuisine: Recettes, planning repas, inventaire, courses
- famille: Jules, santÃ©, activitÃ©s, shopping
- planning: Calendrier, routines, planification
- maison: Entretien, projets, jardin
- shared: Accueil, paramÃ¨tres, rapports
"""

from . import cuisine, famille, planning, maison, shared

__all__ = ["cuisine", "famille", "planning", "maison", "shared"]

