"""
Module Maison - Hub de gestion domestique

Structure:
- hub_maison.py: Dashboard principal avec cards (NOUVEAU)
- projets.py: Projets maison (rénovation, aménagement) avec priorisation IA
- jardin.py: Gestion du jardin, plantes, récoltes avec conseils IA
- entretien.py: Routines ménagères et tâches quotidiennes avec optimisation IA
- meubles.py: Wishlist meubles par pièce avec budget (NOUVEAU)
- eco_tips.py: Actions écologiques avec suivi économies (NOUVEAU)
- depenses.py: Suivi dépenses maison gaz/eau/élec (NOUVEAU)
- helpers.py: Fonctions partagées pour les modules

Hub principal affichant:
- Cards cliquables: Projets, Jardin, Ménage, Meubles, Éco-Tips, Dépenses
- Alertes urgentes
- Navigation interne
"""

from src.domains.maison.ui.hub_maison import app

__all__ = ["app"]

