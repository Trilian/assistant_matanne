"""
Recherche Globale ⌘K - Barre de recherche universelle.

Permet de fouiller recettes, produits, activités, notes
depuis n'importe quelle page via un raccourci clavier.

Usage:
    from src.ui.components import afficher_recherche_globale

    afficher_recherche_globale()  # En header ou sidebar
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("recherche_globale")


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TypeResultat(str, Enum):
    """Types de résultats de recherche."""

    RECETTE = "recette"
    PRODUIT = "produit"
    ACTIVITE = "activite"
    INVENTAIRE = "inventaire"
    PLANNING = "planning"
    JULES = "jules"
    NOTE = "note"


@dataclass
class ResultatRecherche:
    """Un résultat de recherche globale."""

    type: TypeResultat
    titre: str
    sous_titre: str = ""
    id: int | None = None
    score: float = 1.0
    icone: str = ""
    action: str = ""  # Module vers lequel naviguer

    @property
    def icone_display(self) -> str:
        """Retourne l'icône appropriée."""
        if self.icone:
            return self.icone
        return {
            TypeResultat.RECETTE: "🍳",
            TypeResultat.PRODUIT: "📦",
            TypeResultat.ACTIVITE: "🎯",
            TypeResultat.INVENTAIRE: "🥫",
            TypeResultat.PLANNING: "📅",
            TypeResultat.JULES: "👶",
            TypeResultat.NOTE: "📝",
        }.get(self.type, "📄")


# ═══════════════════════════════════════════════════════════
# SERVICE DE RECHERCHE
# ═══════════════════════════════════════════════════════════


class RechercheGlobaleService:
    """
    Service de recherche multi-domaines.

    Agrège les résultats de plusieurs sources:
    - Recettes (nom, ingrédients, type)
    - Produits inventaire (nom, catégorie)
    - Activités Jules (titre, type)
    - Planning repas (recette, date)
    """

    def __init__(self):
        self._max_resultats_par_type = 5

    def rechercher(
        self, terme: str, types: list[TypeResultat] | None = None, limit: int = 20
    ) -> list[ResultatRecherche]:
        """
        Recherche globale multi-sources.

        Args:
            terme: Terme de recherche
            types: Types à inclure (tous si None)
            limit: Nombre max de résultats

        Returns:
            Liste de ResultatRecherche triés par score
        """
        if not terme or len(terme) < 2:
            return []

        types = types or list(TypeResultat)
        resultats: list[ResultatRecherche] = []

        # Recherche dans chaque source
        if TypeResultat.RECETTE in types:
            resultats.extend(self._rechercher_recettes(terme))

        if TypeResultat.INVENTAIRE in types:
            resultats.extend(self._rechercher_inventaire(terme))

        if TypeResultat.ACTIVITE in types or TypeResultat.JULES in types:
            resultats.extend(self._rechercher_activites(terme))

        if TypeResultat.PLANNING in types:
            resultats.extend(self._rechercher_planning(terme))

        # Trier par score et limiter
        resultats.sort(key=lambda r: r.score, reverse=True)
        return resultats[:limit]

    def _rechercher_recettes(self, terme: str) -> list[ResultatRecherche]:
        """Recherche dans les recettes."""
        resultats = []
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.recettes import Recette

            with obtenir_contexte_db() as session:
                # Recherche dans nom et ingrédients
                query = session.query(Recette).filter(
                    Recette.nom.ilike(f"%{terme}%")
                    | Recette.description.ilike(f"%{terme}%")
                    | Recette.categorie.ilike(f"%{terme}%")
                )
                recettes = query.limit(self._max_resultats_par_type).all()

                for r in recettes:
                    # Score plus élevé si match dans le nom
                    score = 1.0 if terme.lower() in r.nom.lower() else 0.7
                    resultats.append(
                        ResultatRecherche(
                            type=TypeResultat.RECETTE,
                            titre=r.nom,
                            sous_titre=f"{r.categorie or 'Recette'} • {r.temps_total or '?'} min",
                            id=r.id,
                            score=score,
                            action="cuisine.recettes",
                        )
                    )
        except Exception as e:
            logger.warning(f"Erreur recherche recettes: {e}")

        return resultats

    def _rechercher_inventaire(self, terme: str) -> list[ResultatRecherche]:
        """Recherche dans l'inventaire via les ingrédients."""
        resultats = []
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.inventaire import ArticleInventaire
            from src.core.models.recettes import Ingredient

            with obtenir_contexte_db() as session:
                query = (
                    session.query(ArticleInventaire)
                    .join(Ingredient, ArticleInventaire.ingredient_id == Ingredient.id)
                    .filter(
                        Ingredient.nom.ilike(f"%{terme}%")
                        | Ingredient.categorie.ilike(f"%{terme}%")
                    )
                )
                produits = query.limit(self._max_resultats_par_type).all()

                for p in produits:
                    nom = p.ingredient.nom if p.ingredient else f"Article #{p.id}"
                    cat = p.ingredient.categorie if p.ingredient else "Produit"
                    score = 1.0 if terme.lower() in nom.lower() else 0.6
                    resultats.append(
                        ResultatRecherche(
                            type=TypeResultat.INVENTAIRE,
                            titre=nom,
                            sous_titre=f"{cat or 'Produit'} • {p.quantite} {p.emplacement or ''}",
                            id=p.id,
                            score=score,
                            action="cuisine.inventaire",
                        )
                    )
        except Exception as e:
            logger.warning(f"Erreur recherche inventaire: {e}")

        return resultats

    def _rechercher_activites(self, terme: str) -> list[ResultatRecherche]:
        """Recherche dans les activités familiales."""
        resultats = []
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.famille import ActiviteFamille

            with obtenir_contexte_db() as session:
                query = session.query(ActiviteFamille).filter(
                    ActiviteFamille.titre.ilike(f"%{terme}%")
                    | ActiviteFamille.description.ilike(f"%{terme}%")
                    | ActiviteFamille.type_activite.ilike(f"%{terme}%")
                )
                activites = query.limit(self._max_resultats_par_type).all()

                for a in activites:
                    score = 1.0 if terme.lower() in a.titre.lower() else 0.6
                    resultats.append(
                        ResultatRecherche(
                            type=TypeResultat.ACTIVITE,
                            titre=a.titre,
                            sous_titre=(
                                f"{a.type_activite or 'Activité'}"
                                f" • {a.date_prevue.strftime('%d/%m') if a.date_prevue else '?'}"
                            ),
                            id=a.id,
                            score=score,
                            icone="🎨",
                            action="famille.hub",
                        )
                    )
        except Exception as e:
            logger.debug(f"Recherche activités non dispo: {e}")

        return resultats

    def _rechercher_planning(self, terme: str) -> list[ResultatRecherche]:
        """Recherche dans le planning repas."""
        resultats = []
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.planning import Repas
            from src.core.models.recettes import Recette

            with obtenir_contexte_db() as session:
                query = (
                    session.query(Repas)
                    .join(Recette, Repas.recette_id == Recette.id)
                    .filter(Recette.nom.ilike(f"%{terme}%"))
                )
                repas_list = query.limit(self._max_resultats_par_type).all()

                for r in repas_list:
                    recette_nom = r.recette.nom if r.recette else "?"
                    resultats.append(
                        ResultatRecherche(
                            type=TypeResultat.PLANNING,
                            titre=recette_nom,
                            sous_titre=(
                                f"{r.date_repas.strftime('%d/%m')}" f" • {r.type_repas or 'Repas'}"
                            ),
                            id=r.id,
                            score=0.8,
                            action="cuisine.planificateur_repas",
                        )
                    )
        except Exception as e:
            logger.debug(f"Recherche planning non dispo: {e}")

        return resultats


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_service_instance: RechercheGlobaleService | None = None


def get_recherche_globale_service() -> RechercheGlobaleService:
    """Factory singleton pour le service de recherche."""
    global _service_instance
    if _service_instance is None:
        _service_instance = RechercheGlobaleService()
    return _service_instance


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI
# ═══════════════════════════════════════════════════════════


def afficher_recherche_globale(placeholder: str = "Recherche ⌘K...") -> str | None:
    """
    Affiche la barre de recherche globale.

    Args:
        placeholder: Texte indicatif

    Returns:
        Terme recherché ou None
    """
    from src.core.state import GestionnaireEtat

    # CSS pour le style de la recherche globale
    st.markdown(
        """
        <style>
        .recherche-globale-container {
            position: relative;
        }
        .recherche-globale-input {
            width: 100%;
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid var(--st-color-border);
            background: var(--st-color-background);
        }
        .recherche-resultat {
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 6px;
            background: var(--st-color-background-secondary);
            cursor: pointer;
            transition: background 0.2s;
        }
        .recherche-resultat:hover {
            background: var(--st-color-primary-faded);
        }
        .recherche-resultat-titre {
            font-weight: 600;
            margin-bottom: 2px;
        }
        .recherche-resultat-sous-titre {
            font-size: 0.85em;
            color: var(--st-color-text-secondary);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Input de recherche
    terme = st.text_input(
        "Recherche",
        key=_keys("input"),
        placeholder=placeholder,
        label_visibility="collapsed",
    )

    # Résultats si terme saisi
    if terme and len(terme) >= 2:
        service = get_recherche_globale_service()
        resultats = service.rechercher(terme)

        if resultats:
            st.markdown(f"**{len(resultats)} résultat(s)**")

            for r in resultats:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(
                        f"""<div class="recherche-resultat">
                            <div class="recherche-resultat-titre">
                                {r.icone_display} {r.titre}
                            </div>
                            <div class="recherche-resultat-sous-titre">
                                {r.sous_titre}
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("→", key=_keys(f"go_{r.type.value}_{r.id}"), help="Ouvrir"):
                        GestionnaireEtat.naviguer_vers(r.action)
                        st.rerun()
        else:
            st.caption("Aucun résultat trouvé")

    return terme if terme else None


def afficher_recherche_globale_popover() -> None:
    """
    Affiche la recherche globale dans un popover (modal-like).
    Idéal pour l'intégration dans le header.
    """
    with st.popover("🔍 Recherche", use_container_width=False):
        st.markdown("### Recherche Globale")
        afficher_recherche_globale()


# ═══════════════════════════════════════════════════════════
# RACCOURCIS CLAVIER (JS)
# ═══════════════════════════════════════════════════════════


def injecter_raccourcis_clavier() -> None:
    """
    Injecte les raccourcis clavier JavaScript.

    Raccourcis:
    - ⌘K / Ctrl+K: Ouvre la recherche globale
    - Alt+R: Navigation vers Recettes
    - Alt+C: Navigation vers Courses
    - Alt+J: Navigation vers Jules
    - Escape: Ferme les modales
    """
    st.markdown(
        """
        <script>
        document.addEventListener('keydown', function(e) {
            // ⌘K / Ctrl+K - Focus sur recherche
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('[data-testid="stTextInput"] input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }

            // Alt+R - Recettes
            if (e.altKey && e.key === 'r') {
                e.preventDefault();
                const url = new URL(window.location);
                url.pathname = '/cuisine/recettes';
                window.location.href = url.toString();
            }

            // Alt+C - Courses
            if (e.altKey && e.key === 'c') {
                e.preventDefault();
                const url = new URL(window.location);
                url.pathname = '/cuisine/courses';
                window.location.href = url.toString();
            }

            // Alt+J - Jules
            if (e.altKey && e.key === 'j') {
                e.preventDefault();
                const url = new URL(window.location);
                url.pathname = '/famille/jules';
                window.location.href = url.toString();
            }

            // Alt+P - Planning
            if (e.altKey && e.key === 'p') {
                e.preventDefault();
                const url = new URL(window.location);
                url.pathname = '/planning/calendrier';
                window.location.href = url.toString();
            }
        });
        </script>
        """,
        unsafe_allow_html=True,
    )


__all__ = [
    "TypeResultat",
    "ResultatRecherche",
    "RechercheGlobaleService",
    "get_recherche_globale_service",
    "afficher_recherche_globale",
    "afficher_recherche_globale_popover",
    "injecter_raccourcis_clavier",
]
