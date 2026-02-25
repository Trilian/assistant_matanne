"""
Progressive Loading - Chargement intelligent des données.

Utilise st.status pour afficher la progression du chargement
de données volumineuses avec feedback visuel.

Usage:
    from src.ui.components import progressive_loader, chargement_progressif

    with progressive_loader("Chargement des données...") as loader:
        loader.update("Recettes", 1, 4)
        recettes = charger_recettes()
        loader.update("Inventaire", 2, 4)
        inventaire = charger_inventaire()
        ...
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Generator

import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)

_keys = KeyNamespace("progressive_loading")


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class EtapeChargement:
    """Une étape de chargement."""

    nom: str
    fonction: Callable[[], Any]
    poids: int = 1  # Pondération pour la barre de progression
    optionnel: bool = False


class ProgressiveLoader:
    """
    Gestionnaire de chargement progressif avec st.status.

    Permet d'afficher un feedback visuel pendant le chargement
    de données volumineuses.
    """

    def __init__(self, titre: str = "Chargement..."):
        self.titre = titre
        self._status = None
        self._etapes_total = 0
        self._etape_courante = 0
        self._resultats: dict[str, Any] = {}
        self._erreurs: list[str] = []
        self._temps_debut: float = 0

    def __enter__(self) -> "ProgressiveLoader":
        self._status = st.status(self.titre, expanded=True)
        self._status.__enter__()
        self._temps_debut = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._status:
            duree = time.perf_counter() - self._temps_debut

            if exc_type:
                self._status.update(label=f"❌ Erreur: {exc_val}", state="error")
            elif self._erreurs:
                self._status.update(
                    label=f"⚠️ Terminé avec {len(self._erreurs)} erreur(s) ({duree:.1f}s)",
                    state="complete",
                )
            else:
                self._status.update(
                    label=f"✅ {self.titre} ({duree:.1f}s)",
                    state="complete",
                    expanded=False,
                )

            self._status.__exit__(exc_type, exc_val, exc_tb)

        return False  # Ne pas supprimer l'exception

    def update(self, etape: str, current: int, total: int) -> None:
        """
        Met à jour la progression.

        Args:
            etape: Nom de l'étape courante
            current: Numéro de l'étape (1-indexed)
            total: Nombre total d'étapes
        """
        self._etapes_total = total
        self._etape_courante = current
        progress = current / total

        if self._status:
            st.write(f"📦 {etape}...")
            st.progress(progress, text=f"Étape {current}/{total}")

    def charger_etape(
        self,
        nom: str,
        fonction: Callable[[], Any],
        current: int,
        total: int,
    ) -> Any:
        """
        Charge une étape avec gestion d'erreur.

        Args:
            nom: Nom de l'étape
            fonction: Fonction à exécuter
            current: Numéro de l'étape
            total: Nombre total d'étapes

        Returns:
            Résultat de la fonction ou None si erreur
        """
        self.update(nom, current, total)

        try:
            resultat = fonction()
            self._resultats[nom] = resultat
            return resultat
        except Exception as e:
            logger.warning(f"Erreur chargement {nom}: {e}")
            self._erreurs.append(f"{nom}: {e}")
            st.warning(f"⚠️ {nom}: {e}")
            return None

    @property
    def resultats(self) -> dict[str, Any]:
        """Retourne les résultats chargés."""
        return self._resultats

    @property
    def erreurs(self) -> list[str]:
        """Retourne les erreurs survenues."""
        return self._erreurs


@contextmanager
def progressive_loader(titre: str = "Chargement...") -> Generator[ProgressiveLoader, None, None]:
    """
    Context manager pour le chargement progressif.

    Args:
        titre: Titre affiché pendant le chargement

    Yields:
        ProgressiveLoader pour mettre à jour la progression

    Example:
        with progressive_loader("Préparation des données") as loader:
            loader.update("Recettes", 1, 3)
            recettes = charger_recettes()

            loader.update("Inventaire", 2, 3)
            inventaire = charger_inventaire()

            loader.update("Planning", 3, 3)
            planning = charger_planning()
    """
    loader = ProgressiveLoader(titre)
    with loader:
        yield loader


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def charger_avec_progression(
    etapes: list[EtapeChargement],
    titre: str = "Chargement des données...",
) -> dict[str, Any]:
    """
    Charge plusieurs sources de données avec progression.

    Args:
        etapes: Liste des étapes à charger
        titre: Titre du status

    Returns:
        Dict nom_etape -> resultat

    Example:
        etapes = [
            EtapeChargement("recettes", charger_recettes),
            EtapeChargement("inventaire", charger_inventaire),
            EtapeChargement("planning", charger_planning),
        ]
        resultats = charger_avec_progression(etapes)
    """
    resultats = {}
    total = len(etapes)

    with progressive_loader(titre) as loader:
        for i, etape in enumerate(etapes, 1):
            resultat = loader.charger_etape(
                etape.nom,
                etape.fonction,
                i,
                total,
            )

            if resultat is not None or not etape.optionnel:
                resultats[etape.nom] = resultat

    return resultats


def chargement_progressif_dashboard() -> dict[str, Any]:
    """
    Charge les données du dashboard avec progression.

    Returns:
        Dict avec les données chargées
    """
    etapes = []

    # Définir les étapes de chargement
    def charger_stats_globales():
        try:
            from src.services.accueil_data_service import get_accueil_data_service

            service = get_accueil_data_service()
            return service.get_stats_globales()
        except Exception:
            return {}

    def charger_alertes():
        try:
            from src.services.accueil_data_service import get_accueil_data_service

            service = get_accueil_data_service()
            return service.get_alertes_critiques()
        except Exception:
            return []

    def charger_planning_semaine():
        try:
            from datetime import date, timedelta

            from src.core.db import obtenir_contexte_db
            from src.core.models import PlanningRepas

            with obtenir_contexte_db() as session:
                aujourdhui = date.today()
                fin_semaine = aujourdhui + timedelta(days=7)
                return (
                    session.query(PlanningRepas)
                    .filter(
                        PlanningRepas.date_repas >= aujourdhui,
                        PlanningRepas.date_repas <= fin_semaine,
                    )
                    .all()
                )
        except Exception:
            return []

    def charger_activites_jules():
        try:
            from .jules_aujourdhui import obtenir_activites_jules_aujourdhui

            return obtenir_activites_jules_aujourdhui()
        except Exception:
            return []

    etapes = [
        EtapeChargement("stats", charger_stats_globales),
        EtapeChargement("alertes", charger_alertes),
        EtapeChargement("planning", charger_planning_semaine),
        EtapeChargement("jules", charger_activites_jules, optionnel=True),
    ]

    return charger_avec_progression(etapes, "Préparation du dashboard...")


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI SIMPLE
# ═══════════════════════════════════════════════════════════


@composant_ui("loading", tags=("ui", "status", "chargement"))
def status_chargement(
    items: list[tuple[str, Callable]],
    titre: str = "Chargement...",
) -> dict[str, Any]:
    """
    Affiche un status de chargement simple avec étapes.

    Args:
        items: Liste de tuples (nom, fonction)
        titre: Titre du status

    Returns:
        Dict nom -> résultat

    Example:
        data = status_chargement([
            ("recettes", lambda: db.query(Recette).all()),
            ("inventaire", lambda: db.query(Inventaire).all()),
        ])
    """
    resultats = {}

    with st.status(titre, expanded=True) as status:
        total = len(items)

        for i, (nom, func) in enumerate(items, 1):
            st.write(f"📦 {nom}...")

            try:
                resultats[nom] = func()
                st.write(f"✅ {nom}")
            except Exception as e:
                st.write(f"⚠️ {nom}: {e}")
                resultats[nom] = None

            st.progress(i / total)

        status.update(label=f"✅ {titre}", state="complete", expanded=False)

    return resultats


@composant_ui("loading", tags=("ui", "skeleton", "placeholder"))
def skeleton_loading(nb_lignes: int = 3, hauteur: int = 60) -> None:
    """
    Affiche un placeholder de chargement skeleton.

    Args:
        nb_lignes: Nombre de lignes skeleton
        hauteur: Hauteur en pixels de chaque ligne
    """
    st.markdown(
        f"""
        <style>
        @keyframes skeleton-loading {{
            0% {{ background-position: -200px 0; }}
            100% {{ background-position: calc(200px + 100%) 0; }}
        }}
        .skeleton {{
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200px 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 4px;
            height: {hauteur}px;
            margin: 8px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    for _ in range(nb_lignes):
        st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)


__all__ = [
    "ProgressiveLoader",
    "progressive_loader",
    "EtapeChargement",
    "charger_avec_progression",
    "chargement_progressif_dashboard",
    "status_chargement",
    "skeleton_loading",
]
