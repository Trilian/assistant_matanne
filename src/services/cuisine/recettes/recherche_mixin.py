"""
Mixin de recherche et filtrage pour les recettes.

Extrait du service principal pour réduire sa taille.
Contient toutes les méthodes liées à:
- Recherche avancée multi-critères
- Filtrage par type, saison, difficulté
- Recherche full-text
"""

import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import Recette

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class RecetteRechercheMixin:
    """
    Mixin fournissant les fonctionnalités de recherche et filtrage.

    Attend d'être mixé dans une classe possédant:
    - self.advanced_search() méthode de BaseService
    """

    @avec_session_db
    def search_advanced(
        self,
        term: str | None = None,
        type_repas: str | None = None,
        saison: str | None = None,
        difficulte: str | None = None,
        temps_max: int | None = None,
        compatible_bebe: bool | None = None,
        limit: int = 100,
        db: Session | None = None,
    ) -> list[Recette]:
        """
        Recherche avancée multi-critères.

        Args:
            term: Terme de recherche (nom/description)
            type_repas: Type de repas (petit_déjeuner, déjeuner, dîner, goûter)
            saison: Saison (printemps, été, automne, hiver)
            difficulte: Niveau (facile, moyen, difficile)
            temps_max: Temps préparation max en minutes
            compatible_bebe: Compatible pour bébé
            limit: Nombre de résultats max
            db: Session DB injectée

        Returns:
            Liste des recettes trouvées
        """
        filters: dict = {}
        if type_repas:
            filters["type_repas"] = type_repas
        if saison:
            filters["saison"] = saison
        if difficulte:
            filters["difficulte"] = difficulte
        if compatible_bebe is not None:
            filters["compatible_bebe"] = compatible_bebe
        if temps_max:
            filters["temps_preparation"] = {"lte": temps_max}

        search_fields = ["nom", "description"] if term else None

        return self.advanced_search(
            search_term=term,
            search_fields=search_fields,
            filters=filters,
            sort_by="nom",
            limit=limit,
            db=db,
        )

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_by_type(self, type_repas: str, db: Session = None) -> list[Recette]:
        """Récupère les recettes d'un type donné."""
        return db.query(Recette).filter(Recette.type_repas == type_repas).all()

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_by_saison(self, saison: str, db: Session = None) -> list[Recette]:
        """Récupère les recettes d'une saison donnée."""
        return db.query(Recette).filter(Recette.saison == saison).all()

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_by_difficulte(self, difficulte: str, db: Session = None) -> list[Recette]:
        """Récupère les recettes d'une difficulté donnée."""
        return db.query(Recette).filter(Recette.difficulte == difficulte).all()

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_compatible_bebe(self, db: Session = None) -> list[Recette]:
        """Récupère les recettes compatibles bébé."""
        return db.query(Recette).filter(Recette.compatible_bebe == True).all()

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_rapides(self, temps_max: int = 30, db: Session = None) -> list[Recette]:
        """Récupère les recettes rapides (temps total <= temps_max)."""
        return (
            db.query(Recette)
            .filter((Recette.temps_preparation + Recette.temps_cuisson) <= temps_max)
            .all()
        )

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def search_by_ingredient(
        self, ingredient_nom: str, limit: int = 50, db: Session = None
    ) -> list[Recette]:
        """
        Recherche les recettes contenant un ingrédient donné.

        Args:
            ingredient_nom: Nom de l'ingrédient à chercher
            limit: Nombre max de résultats
            db: Session DB injectée

        Returns:
            Liste des recettes contenant l'ingrédient
        """
        from src.core.models import Ingredient, RecetteIngredient

        return (
            db.query(Recette)
            .join(RecetteIngredient, Recette.id == RecetteIngredient.recette_id)
            .join(Ingredient, RecetteIngredient.ingredient_id == Ingredient.id)
            .filter(Ingredient.nom.ilike(f"%{ingredient_nom}%"))
            .distinct()
            .limit(limit)
            .all()
        )


__all__ = ["RecetteRechercheMixin"]
