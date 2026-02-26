"""
State Slices — Dataclasses pour chaque domaine d'état.

Organisation par domaine:
- EtatNavigation: module actuel, historique, fil d'Ariane
- EtatCuisine: recettes, inventaire, planning repas
- EtatUI: flags formulaires, modales, onglets
- EtatApp: agrège les slices pour rétro-compatibilité
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.core.ai.client import ClientIA

logger = logging.getLogger(__name__)


@dataclass
class EtatNavigation:
    """Slice navigation — module actuel, historique, fil d'Ariane."""

    module_actuel: str = "accueil"
    module_precedent: str | None = None
    historique_navigation: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.historique_navigation:
            self.historique_navigation = [self.module_actuel]


@dataclass
class EtatCuisine:
    """Slice cuisine — recettes, inventaire, planning repas."""

    # Recettes
    id_recette_visualisation: int | None = None
    id_recette_edition: int | None = None
    id_recette_adaptation_bebe: int | None = None

    # Inventaire
    id_article_visualisation: int | None = None
    id_article_edition: int | None = None

    # Planning
    id_planning_visualisation: int | None = None
    semaine_actuelle: date | None = None
    id_planning_ajout_repas: int | None = None
    jour_ajout_repas: int | None = None
    date_ajout_repas: date | None = None
    id_repas_edition: int | None = None


@dataclass
class EtatUI:
    """Slice UI — flags formulaires, modales, onglets."""

    afficher_formulaire_ajout: bool = False
    afficher_generation_ia: bool = False
    afficher_confirmation_suppression: bool = False
    afficher_notifications: bool = False
    afficher_formulaire_ajout_repas: bool = False
    onglet_actif: str | None = None

    def reinitialiser(self) -> None:
        """Remet tous les flags UI à leur valeur par défaut."""
        self.afficher_formulaire_ajout = False
        self.afficher_generation_ia = False
        self.afficher_confirmation_suppression = False
        self.afficher_notifications = False
        self.afficher_formulaire_ajout_repas = False
        self.onglet_actif = None


class EtatApp:
    """État global de l'application — agrège les slices par domaine.

    Accepte les anciens kwargs (``module_actuel``, ``afficher_formulaire_ajout``,
    etc.) et les redirige vers les slices correspondants.
    Rétro-compatible : ``EtatApp(module_actuel="cuisine.recettes")`` fonctionne.
    """

    __slots__ = (
        "navigation",
        "cuisine",
        "ui",
        "nom_utilisateur",
        "user_id",
        "profil_charge",
        "notifications_non_lues",
        "agent_ia",
        "mode_debug",
        "cache_active",
    )

    def __init__(
        self,
        *,
        # Navigation (rétro-compat)
        module_actuel: str = "accueil",
        module_precedent: str | None = None,
        historique_navigation: list[str] | None = None,
        # Cuisine (rétro-compat)
        id_recette_visualisation: int | None = None,
        id_recette_edition: int | None = None,
        id_recette_adaptation_bebe: int | None = None,
        id_article_visualisation: int | None = None,
        id_article_edition: int | None = None,
        id_planning_visualisation: int | None = None,
        semaine_actuelle: date | None = None,
        id_planning_ajout_repas: int | None = None,
        jour_ajout_repas: int | None = None,
        date_ajout_repas: date | None = None,
        id_repas_edition: int | None = None,
        # UI (rétro-compat)
        afficher_formulaire_ajout: bool = False,
        afficher_generation_ia: bool = False,
        afficher_confirmation_suppression: bool = False,
        afficher_notifications: bool = False,
        afficher_formulaire_ajout_repas: bool = False,
        onglet_actif: str | None = None,
        # Top-level
        nom_utilisateur: str = "Anne",
        user_id: int | None = None,
        profil_charge: bool = False,
        notifications_non_lues: int = 0,
        agent_ia: ClientIA | None = None,
        mode_debug: bool = False,
        cache_active: bool = True,
        # Slices (pour usage direct avancé)
        navigation: EtatNavigation | None = None,
        cuisine: EtatCuisine | None = None,
        ui: EtatUI | None = None,
    ) -> None:
        # Build slices from individual kwargs OR from pre-built slices
        self.navigation = navigation or EtatNavigation(
            module_actuel=module_actuel,
            module_precedent=module_precedent,
            historique_navigation=historique_navigation or [],
        )
        self.cuisine = cuisine or EtatCuisine(
            id_recette_visualisation=id_recette_visualisation,
            id_recette_edition=id_recette_edition,
            id_recette_adaptation_bebe=id_recette_adaptation_bebe,
            id_article_visualisation=id_article_visualisation,
            id_article_edition=id_article_edition,
            id_planning_visualisation=id_planning_visualisation,
            semaine_actuelle=semaine_actuelle,
            id_planning_ajout_repas=id_planning_ajout_repas,
            jour_ajout_repas=jour_ajout_repas,
            date_ajout_repas=date_ajout_repas,
            id_repas_edition=id_repas_edition,
        )
        self.ui = ui or EtatUI(
            afficher_formulaire_ajout=afficher_formulaire_ajout,
            afficher_generation_ia=afficher_generation_ia,
            afficher_confirmation_suppression=afficher_confirmation_suppression,
            afficher_notifications=afficher_notifications,
            afficher_formulaire_ajout_repas=afficher_formulaire_ajout_repas,
            onglet_actif=onglet_actif,
        )
        self.nom_utilisateur = nom_utilisateur
        self.user_id = user_id
        self.profil_charge = profil_charge
        self.notifications_non_lues = notifications_non_lues
        self.agent_ia = agent_ia
        self.mode_debug = mode_debug
        self.cache_active = cache_active

    def __repr__(self) -> str:
        return (
            f"EtatApp(module={self.navigation.module_actuel!r}, "
            f"user={self.nom_utilisateur!r}, "
            f"debug={self.mode_debug})"
        )

    # ── Rétro-compatibilité dynamique (délègue aux slices) ──
    # Mapping attribut → (nom_slice, nom_attribut)
    _DELEGATION: dict[str, tuple[str, str]] = {
        # Navigation
        "module_actuel": ("navigation", "module_actuel"),
        "module_precedent": ("navigation", "module_precedent"),
        "historique_navigation": ("navigation", "historique_navigation"),
        # Cuisine
        "id_recette_visualisation": ("cuisine", "id_recette_visualisation"),
        "id_recette_edition": ("cuisine", "id_recette_edition"),
        "id_recette_adaptation_bebe": ("cuisine", "id_recette_adaptation_bebe"),
        "id_article_visualisation": ("cuisine", "id_article_visualisation"),
        "id_article_edition": ("cuisine", "id_article_edition"),
        "id_planning_visualisation": ("cuisine", "id_planning_visualisation"),
        "semaine_actuelle": ("cuisine", "semaine_actuelle"),
        "id_planning_ajout_repas": ("cuisine", "id_planning_ajout_repas"),
        "jour_ajout_repas": ("cuisine", "jour_ajout_repas"),
        "date_ajout_repas": ("cuisine", "date_ajout_repas"),
        "id_repas_edition": ("cuisine", "id_repas_edition"),
        # UI
        "afficher_formulaire_ajout": ("ui", "afficher_formulaire_ajout"),
        "afficher_generation_ia": ("ui", "afficher_generation_ia"),
        "afficher_confirmation_suppression": ("ui", "afficher_confirmation_suppression"),
        "afficher_notifications": ("ui", "afficher_notifications"),
        "afficher_formulaire_ajout_repas": ("ui", "afficher_formulaire_ajout_repas"),
        "onglet_actif": ("ui", "onglet_actif"),
    }

    def __getattr__(self, name: str) -> Any:
        """Délègue dynamiquement les attributs de rétro-compatibilité aux slices."""
        delegation = EtatApp._DELEGATION
        if name in delegation:
            slice_name, attr_name = delegation[name]
            return getattr(object.__getattribute__(self, slice_name), attr_name)
        raise AttributeError(f"'{type(self).__name__}' n'a pas d'attribut '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Délègue dynamiquement les affectations de rétro-compatibilité aux slices."""
        delegation = EtatApp._DELEGATION
        if name in delegation:
            slice_name, attr_name = delegation[name]
            setattr(object.__getattribute__(self, slice_name), attr_name, value)
            return
        object.__setattr__(self, name, value)


__all__ = [
    "EtatNavigation",
    "EtatCuisine",
    "EtatUI",
    "EtatApp",
]
