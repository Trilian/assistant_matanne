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
        self.notifications_non_lues = notifications_non_lues
        self.agent_ia = agent_ia
        self.mode_debug = mode_debug
        self.cache_active = cache_active

    def __repr__(self) -> str:
        return (
            f"EtatApp(module={self.module_actuel!r}, "
            f"user={self.nom_utilisateur!r}, "
            f"debug={self.mode_debug})"
        )

    # ── Propriétés de rétro-compatibilité (délèguent aux slices) ──

    @property
    def module_actuel(self) -> str:
        return self.navigation.module_actuel

    @module_actuel.setter
    def module_actuel(self, value: str) -> None:
        self.navigation.module_actuel = value

    @property
    def module_precedent(self) -> str | None:
        return self.navigation.module_precedent

    @module_precedent.setter
    def module_precedent(self, value: str | None) -> None:
        self.navigation.module_precedent = value

    @property
    def historique_navigation(self) -> list[str]:
        return self.navigation.historique_navigation

    @historique_navigation.setter
    def historique_navigation(self, value: list[str]) -> None:
        self.navigation.historique_navigation = value

    # Cuisine slice properties
    @property
    def id_recette_visualisation(self) -> int | None:
        return self.cuisine.id_recette_visualisation

    @id_recette_visualisation.setter
    def id_recette_visualisation(self, value: int | None) -> None:
        self.cuisine.id_recette_visualisation = value

    @property
    def id_recette_edition(self) -> int | None:
        return self.cuisine.id_recette_edition

    @id_recette_edition.setter
    def id_recette_edition(self, value: int | None) -> None:
        self.cuisine.id_recette_edition = value

    @property
    def id_recette_adaptation_bebe(self) -> int | None:
        return self.cuisine.id_recette_adaptation_bebe

    @id_recette_adaptation_bebe.setter
    def id_recette_adaptation_bebe(self, value: int | None) -> None:
        self.cuisine.id_recette_adaptation_bebe = value

    @property
    def id_article_visualisation(self) -> int | None:
        return self.cuisine.id_article_visualisation

    @id_article_visualisation.setter
    def id_article_visualisation(self, value: int | None) -> None:
        self.cuisine.id_article_visualisation = value

    @property
    def id_article_edition(self) -> int | None:
        return self.cuisine.id_article_edition

    @id_article_edition.setter
    def id_article_edition(self, value: int | None) -> None:
        self.cuisine.id_article_edition = value

    @property
    def id_planning_visualisation(self) -> int | None:
        return self.cuisine.id_planning_visualisation

    @id_planning_visualisation.setter
    def id_planning_visualisation(self, value: int | None) -> None:
        self.cuisine.id_planning_visualisation = value

    @property
    def semaine_actuelle(self) -> Any | None:
        return self.cuisine.semaine_actuelle

    @semaine_actuelle.setter
    def semaine_actuelle(self, value: Any | None) -> None:
        self.cuisine.semaine_actuelle = value

    @property
    def id_planning_ajout_repas(self) -> int | None:
        return self.cuisine.id_planning_ajout_repas

    @id_planning_ajout_repas.setter
    def id_planning_ajout_repas(self, value: int | None) -> None:
        self.cuisine.id_planning_ajout_repas = value

    @property
    def jour_ajout_repas(self) -> int | None:
        return self.cuisine.jour_ajout_repas

    @jour_ajout_repas.setter
    def jour_ajout_repas(self, value: int | None) -> None:
        self.cuisine.jour_ajout_repas = value

    @property
    def date_ajout_repas(self) -> Any | None:
        return self.cuisine.date_ajout_repas

    @date_ajout_repas.setter
    def date_ajout_repas(self, value: Any | None) -> None:
        self.cuisine.date_ajout_repas = value

    @property
    def id_repas_edition(self) -> int | None:
        return self.cuisine.id_repas_edition

    @id_repas_edition.setter
    def id_repas_edition(self, value: int | None) -> None:
        self.cuisine.id_repas_edition = value

    # UI slice properties
    @property
    def afficher_formulaire_ajout(self) -> bool:
        return self.ui.afficher_formulaire_ajout

    @afficher_formulaire_ajout.setter
    def afficher_formulaire_ajout(self, value: bool) -> None:
        self.ui.afficher_formulaire_ajout = value

    @property
    def afficher_generation_ia(self) -> bool:
        return self.ui.afficher_generation_ia

    @afficher_generation_ia.setter
    def afficher_generation_ia(self, value: bool) -> None:
        self.ui.afficher_generation_ia = value

    @property
    def afficher_confirmation_suppression(self) -> bool:
        return self.ui.afficher_confirmation_suppression

    @afficher_confirmation_suppression.setter
    def afficher_confirmation_suppression(self, value: bool) -> None:
        self.ui.afficher_confirmation_suppression = value

    @property
    def afficher_notifications(self) -> bool:
        return self.ui.afficher_notifications

    @afficher_notifications.setter
    def afficher_notifications(self, value: bool) -> None:
        self.ui.afficher_notifications = value

    @property
    def afficher_formulaire_ajout_repas(self) -> bool:
        return self.ui.afficher_formulaire_ajout_repas

    @afficher_formulaire_ajout_repas.setter
    def afficher_formulaire_ajout_repas(self, value: bool) -> None:
        self.ui.afficher_formulaire_ajout_repas = value

    @property
    def onglet_actif(self) -> str | None:
        return self.ui.onglet_actif

    @onglet_actif.setter
    def onglet_actif(self, value: str | None) -> None:
        self.ui.onglet_actif = value


__all__ = [
    "EtatNavigation",
    "EtatCuisine",
    "EtatUI",
    "EtatApp",
]
