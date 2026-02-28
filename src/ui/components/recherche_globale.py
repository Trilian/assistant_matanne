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
from enum import Enum, StrEnum
from typing import Any

import streamlit as st

from src.core.decorators import avec_cache
from src.services.core.registry import service_factory
from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)

_keys = KeyNamespace("recherche_globale")


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TypeResultat(StrEnum):
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

    Agrège les résultats de plusieurs sources via une unique requête
    UNION ALL (1 aller-retour DB au lieu de 4 séquentiels):
    - Recettes (nom, ingrédients, type)
    - Produits inventaire (nom, catégorie)
    - Activités Jules (titre, type)
    - Planning repas (recette, date)
    """

    def __init__(self):
        self._max_resultats_par_type = 5

    # ── Configuration par type de résultat ──────────────────
    _TYPE_CONFIG: dict[str, dict[str, str]] = {
        "recette": {"action": "cuisine.recettes", "icone": ""},
        "inventaire": {"action": "cuisine.inventaire", "icone": ""},
        "activite": {"action": "famille.hub", "icone": "🎨"},
        "planning": {"action": "cuisine.planificateur_repas", "icone": ""},
    }

    # ── Fragments SQL par type (UNION ALL) ──────────────────
    _SQL_RECETTES = """
        (SELECT 'recette' AS type, r.nom AS titre,
            COALESCE(r.categorie, 'Recette') || ' \u2022 '
                || COALESCE(r.temps_preparation + r.temps_cuisson, 0) || ' min' AS sous_titre,
            r.id,
            CASE WHEN LOWER(r.nom) LIKE LOWER(:terme_like) THEN 1.0 ELSE 0.7 END AS score
        FROM recettes r
        WHERE r.nom ILIKE :terme_like
            OR r.description ILIKE :terme_like
            OR r.categorie ILIKE :terme_like
        LIMIT :lim)
    """

    _SQL_INVENTAIRE = """
        (SELECT 'inventaire' AS type, i.nom AS titre,
            COALESCE(i.categorie, 'Produit') || ' \u2022 '
                || COALESCE(CAST(inv.quantite AS TEXT), '0') || ' '
                || COALESCE(inv.emplacement, '') AS sous_titre,
            inv.id,
            CASE WHEN LOWER(i.nom) LIKE LOWER(:terme_like) THEN 1.0 ELSE 0.6 END AS score
        FROM inventaire inv
        JOIN ingredients i ON inv.ingredient_id = i.id
        WHERE i.nom ILIKE :terme_like
            OR i.categorie ILIKE :terme_like
        LIMIT :lim)
    """

    _SQL_ACTIVITES = """
        (SELECT 'activite' AS type, a.titre,
            COALESCE(a.type_activite, 'Activit\u00e9') || ' \u2022 '
                || COALESCE(TO_CHAR(a.date_prevue, 'DD/MM'), '?') AS sous_titre,
            a.id,
            CASE WHEN LOWER(a.titre) LIKE LOWER(:terme_like) THEN 1.0 ELSE 0.6 END AS score
        FROM activites_famille a
        WHERE a.titre ILIKE :terme_like
            OR a.description ILIKE :terme_like
            OR a.type_activite ILIKE :terme_like
        LIMIT :lim)
    """

    _SQL_PLANNING = """
        (SELECT 'planning' AS type, rec.nom AS titre,
            TO_CHAR(rep.date_repas, 'DD/MM') || ' \u2022 '
                || COALESCE(rep.type_repas, 'Repas') AS sous_titre,
            rep.id,
            0.8 AS score
        FROM repas rep
        JOIN recettes rec ON rep.recette_id = rec.id
        WHERE rec.nom ILIKE :terme_like
        LIMIT :lim)
    """

    # Mapping TypeResultat → fragment SQL
    _SQL_PAR_TYPE: dict[TypeResultat, str] = {
        TypeResultat.RECETTE: _SQL_RECETTES,
        TypeResultat.INVENTAIRE: _SQL_INVENTAIRE,
        TypeResultat.ACTIVITE: _SQL_ACTIVITES,
        TypeResultat.JULES: _SQL_ACTIVITES,  # Même table
        TypeResultat.PLANNING: _SQL_PLANNING,
    }

    @avec_cache(ttl=10)
    def rechercher(
        self, terme: str, types: list[TypeResultat] | None = None, limit: int = 20
    ) -> list[ResultatRecherche]:
        """
        Recherche globale multi-sources via UNION ALL (1 seul aller-retour DB).

        Le cache @avec_cache(ttl=10) évite les requêtes redondantes sur chaque rerun.

        Args:
            terme: Terme de recherche (min 2 caractères)
            types: Types à inclure (tous si None)
            limit: Nombre max de résultats

        Returns:
            Liste de ResultatRecherche triés par score décroissant
        """
        if not terme or len(terme) < 2:
            return []

        types = types or list(TypeResultat)
        terme_like = f"%{terme}%"

        # Collecter les fragments SQL uniques pour les types demandés
        fragments_vus: set[str] = set()
        fragments: list[str] = []
        for t in types:
            sql = self._SQL_PAR_TYPE.get(t)
            if sql and id(sql) not in fragments_vus:
                fragments_vus.add(id(sql))
                fragments.append(sql)

        if not fragments:
            return []

        try:
            from sqlalchemy import text

            from src.core.db import obtenir_contexte_db

            query_sql = (
                "\nUNION ALL\n".join(fragments) + "\nORDER BY score DESC\nLIMIT :limit_total"
            )
            params = {
                "terme_like": terme_like,
                "lim": self._max_resultats_par_type,
                "limit_total": limit,
            }

            with obtenir_contexte_db() as session:
                rows = session.execute(text(query_sql), params).fetchall()

            return [self._row_to_resultat(row) for row in rows]

        except Exception as e:
            logger.warning(f"Erreur recherche globale UNION ALL: {e}")
            return []

    def _row_to_resultat(self, row: Any) -> ResultatRecherche:
        """Convertit une ligne SQL en ResultatRecherche."""
        type_str: str = row[0]
        config = self._TYPE_CONFIG.get(type_str, {})
        type_enum = {
            "recette": TypeResultat.RECETTE,
            "inventaire": TypeResultat.INVENTAIRE,
            "activite": TypeResultat.ACTIVITE,
            "planning": TypeResultat.PLANNING,
        }.get(type_str, TypeResultat.NOTE)

        return ResultatRecherche(
            type=type_enum,
            titre=row[1] or "",
            sous_titre=row[2] or "",
            id=row[3],
            score=float(row[4]) if row[4] else 0.5,
            icone=config.get("icone", ""),
            action=config.get("action", ""),
        )


# ═══════════════════════════════════════════════════════════
# FACTORY (via registre centralisé)
# ═══════════════════════════════════════════════════════════


@service_factory("recherche_globale", tags={"ui", "recherche"})
def get_recherche_globale_service() -> RechercheGlobaleService:
    """Factory singleton pour le service de recherche (via registre)."""
    return RechercheGlobaleService()


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI
# ═══════════════════════════════════════════════════════════


@composant_ui("recherche", tags=("ui", "barre", "recherche"))
def afficher_recherche_globale(placeholder: str = "Recherche ⌘K...") -> str | None:
    """
    Affiche la barre de recherche globale.

    Args:
        placeholder: Texte indicatif

    Returns:
        Terme recherché ou None
    """

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
                        from src.core.state import naviguer

                        naviguer(r.action)
        else:
            st.caption("Aucun résultat trouvé")

    return terme if terme else None


@composant_ui("recherche", tags=("ui", "popover", "recherche"))
def afficher_recherche_globale_popover() -> None:
    """
    Affiche la recherche globale dans un popover (modal-like).
    Idéal pour l'intégration dans le header.
    """
    # Remplacer le popover par un rendu inline (sans popover)
    st.markdown("### Recherche Globale")
    afficher_recherche_globale()


# ═══════════════════════════════════════════════════════════
# RACCOURCIS CLAVIER (JS)
# ═══════════════════════════════════════════════════════════


@composant_ui("recherche", tags=("js", "raccourcis", "clavier"))
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
