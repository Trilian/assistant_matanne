"""
Query - Query builder fluent et type-safe pour SQLAlchemy.

Alternative expressive aux Specifications avec API chaînable.

Usage::
    from src.core.query import Requete

    # Query fluent
    recettes = (
        Requete(Recette)
        .et(actif=True)
        .contient("nom", "tarte")
        .entre("temps_preparation", 10, 30)
        .trier_par("-date_creation")
        .paginer(page=1, taille=20)
        .executer(session)
    )

    # Vérification d'existence
    existe = Requete(Utilisateur).et(email=email).existe(session)

    # Comptage
    total = Requete(Recette).et(saison="été").compter(session)
"""

from .builder import Requete

__all__ = ["Requete"]
