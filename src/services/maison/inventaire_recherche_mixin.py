"""
Mixin Recherche pour le service Inventaire Maison.

Contient les méthodes de recherche "Où est...", scan code-barres,
et suggestions IA de rangement, extraites de InventaireMaisonService.

Usage:
    class InventaireMaisonService(InventaireRechercheMixin, BaseAIService):
        ...
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from sqlalchemy import or_

from src.core.db import obtenir_contexte_db

from .schemas import ResultatRecherche

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

__all__ = ["InventaireRechercheMixin"]


class InventaireRechercheMixin:
    """Mixin fournissant les fonctions de recherche et suggestions IA.

    Accède via ``self`` aux attributs/méthodes de BaseAIService:
    - self.call_with_cache()

    Méthodes publiques:
    - rechercher() — recherche sémantique "Où est..."
    - rechercher_par_code_barre() — localisation par scan
    - suggerer_rangement() — suggestion IA d'emplacement
    - detecter_doublons() — détection d'objets en double
    - optimiser_rangement() — suggestions d'optimisation par pièce
    """

    # ─────────────────────────────────────────────────────────
    # RECHERCHE "OÙ EST..."
    # ─────────────────────────────────────────────────────────

    async def rechercher(self, query: str, db: Session | None = None) -> ResultatRecherche | None:
        """Recherche un objet dans l'inventaire.

        Recherche intelligente combinant:
        - Correspondance exacte
        - Recherche floue (fautes, synonymes)
        - Suggestion IA si non trouvé

        Args:
            query: Recherche utilisateur (ex: "perceuse", "où est le tournevis")
            db: Session DB optionnelle

        Returns:
            ResultatRecherche ou None si non trouvé
        """
        # Nettoyer la query
        query_clean = self._nettoyer_query(query)

        if db is None:
            with obtenir_contexte_db() as session:
                return await self._rechercher_impl(session, query_clean)
        return await self._rechercher_impl(db, query_clean)

    async def _rechercher_impl(self, db: Session, query: str) -> ResultatRecherche | None:
        """Implémentation de la recherche."""
        # 1. Recherche exacte en DB
        # Note: Utilise les modèles Piece, Conteneur, ObjetMaison quand ils seront créés
        # Pour l'instant, simulation avec HouseStock
        from src.core.models import HouseStock

        # Recherche dans HouseStock (proxy pour ObjetMaison)
        objets = (
            db.query(HouseStock)
            .filter(
                or_(
                    HouseStock.nom.ilike(f"%{query}%"),
                    HouseStock.categorie.ilike(f"%{query}%"),
                )
            )
            .all()
        )

        if objets:
            obj = objets[0]
            return ResultatRecherche(
                objet_trouve=obj.nom,
                emplacement=obj.emplacement or "Non spécifié",
                piece=self._extraire_piece(obj.emplacement),
                conteneur=self._extraire_conteneur(obj.emplacement),
                quantite=obj.quantite,
                confiance=1.0,
                suggestions_similaires=[o.nom for o in objets[1:4]],
            )

        # 2. Si non trouvé, demander suggestion IA
        return await self._suggestion_ia(query)

    async def _suggestion_ia(self, query: str) -> ResultatRecherche | None:
        """Demande une suggestion à l'IA si objet non trouvé."""
        prompt = f"""L'utilisateur cherche "{query}" dans sa maison.
Suggère où ce type d'objet est généralement rangé.
Format JSON: {{"emplacement_suggere": "Garage, établi", "confiance": 0.6}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en organisation domestique",
                max_tokens=200,
            )
            data = json.loads(response)
            return ResultatRecherche(
                objet_trouve=query,
                emplacement=data.get("emplacement_suggere", "Inconnu"),
                piece="Suggestion IA",
                confiance=data.get("confiance", 0.5),
                suggestions_similaires=[],
            )
        except Exception as e:
            logger.warning(f"Suggestion IA échouée: {e}")
            return None

    def _nettoyer_query(self, query: str) -> str:
        """Nettoie la requête de recherche."""
        # Retirer "où est", "cherche", etc.
        mots_ignorés = ["où", "est", "sont", "les", "la", "le", "mon", "ma", "mes", "cherche"]
        mots = query.lower().split()
        mots_filtres = [m for m in mots if m not in mots_ignorés]
        return " ".join(mots_filtres) if mots_filtres else query

    def _extraire_piece(self, emplacement: str | None) -> str:
        """Extrait le nom de la pièce d'un emplacement."""
        if not emplacement:
            return "Non spécifié"
        # Format attendu: "Pièce, détail"
        return emplacement.split(",")[0].strip()

    def _extraire_conteneur(self, emplacement: str | None) -> str | None:
        """Extrait le conteneur d'un emplacement."""
        if not emplacement or "," not in emplacement:
            return None
        return emplacement.split(",", 1)[1].strip()

    # ─────────────────────────────────────────────────────────
    # SCAN CODE-BARRES
    # ─────────────────────────────────────────────────────────

    def rechercher_par_code_barre(
        self, code_barre: str, db: Session | None = None
    ) -> ResultatRecherche | None:
        """Recherche un objet par son code-barres.

        Args:
            code_barre: Code-barres scanné
            db: Session DB optionnelle

        Returns:
            ResultatRecherche ou None
        """
        if db is None:
            with obtenir_contexte_db() as session:
                return self._recherche_code_barre_impl(session, code_barre)
        return self._recherche_code_barre_impl(db, code_barre)

    def _recherche_code_barre_impl(self, db: Session, code_barre: str) -> ResultatRecherche | None:
        """Implémentation recherche code-barres."""
        from src.core.models import HouseStock

        obj = (
            db.query(HouseStock)
            .filter(HouseStock.notes.contains(code_barre))  # Stocké dans notes pour l'instant
            .first()
        )

        if obj:
            return ResultatRecherche(
                objet_trouve=obj.nom,
                emplacement=obj.emplacement or "Non spécifié",
                piece=self._extraire_piece(obj.emplacement),
                quantite=obj.quantite,
                confiance=1.0,
            )

        return None

    # ─────────────────────────────────────────────────────────
    # SUGGESTIONS RANGEMENT IA
    # ─────────────────────────────────────────────────────────

    async def suggerer_rangement(self, nom_objet: str, categorie: str | None = None) -> str:
        """Suggère où ranger un nouvel objet.

        Args:
            nom_objet: Nom de l'objet
            categorie: Catégorie optionnelle

        Returns:
            Suggestion de rangement
        """
        cat_txt = f" (catégorie: {categorie})" if categorie else ""

        prompt = f"""Où ranger "{nom_objet}"{cat_txt} dans une maison?
Donne l'emplacement idéal (pièce et type de rangement).
Sois pratique et logique."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en organisation domestique Marie Kondo",
            max_tokens=200,
        )

    async def detecter_doublons(self, db: Session | None = None) -> list[dict]:
        """Détecte les objets en double dans l'inventaire.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des doublons potentiels
        """
        from collections import defaultdict

        from src.core.models.temps_entretien import ObjetMaison, PieceMaison

        def _impl(session: Session) -> list[dict]:
            objets = (
                session.query(ObjetMaison, PieceMaison.nom.label("piece_nom"))
                .join(PieceMaison, ObjetMaison.piece_id == PieceMaison.id)
                .all()
            )

            # Grouper par nom normalisé (lowercase, sans espaces multiples)
            groupes: dict[str, list[dict]] = defaultdict(list)
            for obj in objets:
                nom_normalise = " ".join(obj.ObjetMaison.nom.lower().split())
                groupes[nom_normalise].append(
                    {
                        "id": obj.ObjetMaison.id,
                        "nom": obj.ObjetMaison.nom,
                        "piece": obj.piece_nom,
                        "categorie": obj.ObjetMaison.categorie,
                    }
                )

            # Retourner seulement les groupes avec plus d'un élément
            doublons = []
            for nom, items in groupes.items():
                if len(items) > 1:
                    doublons.append(
                        {
                            "nom_base": nom,
                            "occurrences": len(items),
                            "objets": items,
                        }
                    )

            return doublons

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    async def optimiser_rangement(self, piece_id: int, db: Session | None = None) -> list[str]:
        """Suggère des optimisations de rangement pour une pièce.

        Args:
            piece_id: ID de la pièce
            db: Session DB optionnelle

        Returns:
            Liste de suggestions d'optimisation
        """
        from collections import Counter

        from src.core.models.temps_entretien import ObjetMaison, PieceMaison

        def _impl(session: Session) -> list[str]:
            # Récupérer la pièce et ses objets
            piece = session.query(PieceMaison).filter(PieceMaison.id == piece_id).first()
            if not piece:
                return ["Pièce non trouvée"]

            objets = session.query(ObjetMaison).filter(ObjetMaison.piece_id == piece_id).all()

            if not objets:
                return ["Aucun objet dans cette pièce - commencez par inventorier !"]

            suggestions = []

            # Analyser les catégories
            categories = Counter(obj.categorie for obj in objets if obj.categorie)
            if len(categories) > 5:
                suggestions.append(
                    "Beaucoup de catégories différentes - envisagez de regrouper les objets similaires"
                )

            # Vérifier les objets sans catégorie
            sans_categorie = sum(1 for obj in objets if not obj.categorie)
            if sans_categorie > 0:
                suggestions.append(
                    f"{sans_categorie} objet(s) sans catégorie - ajoutez des catégories pour mieux organiser"
                )

            # Vérifier les objets à remplacer
            a_remplacer = sum(
                1 for obj in objets if obj.statut in ["a_changer", "a_acheter", "hors_service"]
            )
            if a_remplacer > 0:
                suggestions.append(
                    f"{a_remplacer} objet(s) à remplacer - faire le tri et désencombrer"
                )

            # Suggestions génériques basées sur le nombre d'objets
            nb_objets = len(objets)
            if nb_objets > 50:
                suggestions.append(
                    "Plus de 50 objets - envisagez d'utiliser des boîtes étiquetées ou des rangements supplémentaires"
                )
            elif nb_objets > 20:
                suggestions.append(
                    "Pensez à trier régulièrement les objets inutilisés depuis plus d'un an"
                )

            # Catégories dominantes
            if categories:
                cat_principale, count = categories.most_common(1)[0]
                if count > nb_objets * 0.5:
                    suggestions.append(
                        f"La catégorie '{cat_principale}' domine - dédiez un espace spécifique"
                    )

            if not suggestions:
                suggestions = [
                    "Pièce bien organisée !",
                    "Continuez à maintenir l'inventaire à jour",
                ]

            return suggestions

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)
