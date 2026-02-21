"""
State Unifié - Gestionnaire État Complet
Tout harmonisé en français avec alias anglais
Découplé de Streamlit via SessionStorage Protocol.

Architecture "State Slices":
- EtatNavigation : Module actuel, historique, fil d'Ariane
- EtatCuisine    : Recettes, inventaire, planning repas
- EtatUI         : Flags formulaires, onglets, modales
- EtatApp        : Agrège tous les slices (rétro-compatibilité)
"""

__all__ = [
    "EtatNavigation",
    "EtatCuisine",
    "EtatUI",
    "EtatApp",
    "GestionnaireEtat",
    "obtenir_etat",
    "naviguer",
    "revenir",
    "obtenir_fil_ariane",
    "est_mode_debug",
    "nettoyer_etats_ui",
]

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.core.ai.client import ClientIA

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# STATE SLICES — Séparation par domaine
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# ETAT APP — Agrège les slices (rétro-compatibilité)
# ═══════════════════════════════════════════════════════════


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
        agent_ia: "ClientIA | None" = None,
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


class GestionnaireEtat:
    """Gestionnaire centralisé du state — découplé de Streamlit."""

    CLE_ETAT = "etat_app"

    @staticmethod
    def _storage():
        """Accès lazy au storage pour éviter import circulaire."""
        from src.core.storage import obtenir_storage

        return obtenir_storage()

    @staticmethod
    def initialiser():
        """Initialise le state si pas déjà fait"""
        storage = GestionnaireEtat._storage()
        if not storage.contains(GestionnaireEtat.CLE_ETAT):
            storage.set(GestionnaireEtat.CLE_ETAT, EtatApp())
            logger.info("[OK] EtatApp initialisé")

    @staticmethod
    def obtenir() -> EtatApp:
        """Récupère le state actuel"""
        GestionnaireEtat.initialiser()
        return GestionnaireEtat._storage().get(GestionnaireEtat.CLE_ETAT)

    @staticmethod
    def naviguer_vers(module: str):
        """
        Navigue vers un module

        Args:
            module: Nom du module (ex: "cuisine.recettes")
        """
        etat = GestionnaireEtat.obtenir()

        if etat.module_actuel != module:
            etat.module_precedent = etat.module_actuel
            etat.historique_navigation.append(module)

            # Limiter taille historique
            if len(etat.historique_navigation) > 50:
                etat.historique_navigation = etat.historique_navigation[-50:]

        etat.module_actuel = module
        logger.info(f"Navigation: {module}")

    @staticmethod
    def revenir():
        """Retourne au module précédent"""
        etat = GestionnaireEtat.obtenir()

        if etat.module_precedent:
            GestionnaireEtat.naviguer_vers(etat.module_precedent)
        elif len(etat.historique_navigation) > 1:
            etat.historique_navigation.pop()
            precedent = etat.historique_navigation[-1]
            GestionnaireEtat.naviguer_vers(precedent)

    @staticmethod
    def obtenir_fil_ariane_navigation() -> list[str]:
        """
        Retourne le fil d'Ariane de navigation

        Returns:
            Liste des modules parcourus
        """
        etat = GestionnaireEtat.obtenir()

        if not etat.historique_navigation:
            return ["Accueil"]

        # Convertir chemins modules en labels
        fil_ariane = []
        for module in etat.historique_navigation[-5:]:  # 5 derniers
            label = GestionnaireEtat._module_vers_label(module)
            fil_ariane.append(label)

        return fil_ariane

    @staticmethod
    def _module_vers_label(module: str) -> str:
        """
        Convertit nom module en label lisible

        Args:
            module: "cuisine.recettes" -> "Recettes"
        """
        correspondances_labels = {
            "accueil": "Accueil",
            "cuisine.recettes": "Recettes",
            "cuisine.inventaire": "Inventaire",
            "cuisine.planning_semaine": "Planning",
            "cuisine.courses": "Courses",
            "famille.accueil": "Hub Famille",
            "famille.jules": "Jules",
            "famille.jules_planning": "Planning Jules",
            "famille.sante": "Santé & Sport",
            "famille.suivi_perso": "Mon Suivi",
            "famille.activites": "Activités",
            "famille.shopping": "Shopping",
            "maison.hub": "Hub Maison",
            "maison.jardin": "Jardin",
            "maison.entretien": "Entretien",
            "maison.depenses": "Dépenses",
            "maison.charges": "Charges",
            "planning.calendrier": "Calendrier",
            "parametres": "Paramètres",
        }

        return correspondances_labels.get(module, module.split(".")[-1].capitalize())

    @staticmethod
    def reinitialiser():
        """Réinitialise complètement le state"""
        storage = GestionnaireEtat._storage()
        if storage.contains(GestionnaireEtat.CLE_ETAT):
            storage.delete(GestionnaireEtat.CLE_ETAT)

        GestionnaireEtat.initialiser()
        logger.info("🔄 State réinitialisé")

    @staticmethod
    def reset_complet():
        """Reset complet: state + cache app + cache lazy loader."""
        from src.core.caching import Cache
        from src.core.lazy_loader import ChargeurModuleDiffere

        GestionnaireEtat.reinitialiser()
        Cache.vider()
        ChargeurModuleDiffere.vider_cache()
        logger.info("🔄 Reset complet effectué")

    @staticmethod
    def obtenir_resume_etat() -> dict:
        """
        Retourne résumé du state pour debug

        Returns:
            Dict avec infos clés du state
        """
        etat = GestionnaireEtat.obtenir()

        return {
            "module_actuel": etat.module_actuel,
            "module_precedent": etat.module_precedent,
            "historique_navigation": etat.historique_navigation[-10:],
            "nom_utilisateur": etat.nom_utilisateur,
            "mode_debug": etat.mode_debug,
            "cache_active": etat.cache_active,
            "ia_disponible": etat.agent_ia is not None,
            "recette_visualisation": etat.id_recette_visualisation,
            "planning_visualisation": etat.id_planning_visualisation,
            "notifications_non_lues": etat.notifications_non_lues,
        }

    @staticmethod
    def nettoyer_etats_ui():
        """Nettoie les états UI temporaires via le slice dédié."""
        etat = GestionnaireEtat.obtenir()
        etat.ui.reinitialiser()
        logger.debug("🧹 États UI nettoyés")

    @staticmethod
    def definir_recette_visualisation(id_recette: int | None):
        """Définit recette en cours de visualisation"""
        etat = GestionnaireEtat.obtenir()
        etat.id_recette_visualisation = id_recette

        if id_recette:
            logger.debug(f"👁️ Visualisation recette {id_recette}")

    @staticmethod
    def definir_recette_edition(id_recette: int | None):
        """Définit recette en cours d'édition"""
        etat = GestionnaireEtat.obtenir()
        etat.id_recette_edition = id_recette

        if id_recette:
            logger.debug(f"✏️ Édition recette {id_recette}")

    @staticmethod
    def definir_planning_visualisation(id_planning: int | None):
        """Définit planning en cours de visualisation"""
        etat = GestionnaireEtat.obtenir()
        etat.id_planning_visualisation = id_planning

        if id_planning:
            logger.debug(f"👁️ Visualisation planning {id_planning}")

    @staticmethod
    def definir_contexte(id_item: int, type_item: str):
        """
        Définit le contexte actuel (recette, planning, etc.)

        Args:
            id_item: ID de l'item
            type_item: Type ('recette', 'planning', 'article')
        """
        if type_item == "recette":
            GestionnaireEtat.definir_recette_visualisation(id_item)
        elif type_item == "planning":
            GestionnaireEtat.definir_planning_visualisation(id_item)

    @staticmethod
    def incrementer_notifications():
        """Incrémente compteur notifications"""
        etat = GestionnaireEtat.obtenir()
        etat.notifications_non_lues += 1

    @staticmethod
    def effacer_notifications():
        """Réinitialise notifications"""
        etat = GestionnaireEtat.obtenir()
        etat.notifications_non_lues = 0

    @staticmethod
    def basculer_mode_debug():
        """Active/désactive mode debug"""
        etat = GestionnaireEtat.obtenir()
        etat.mode_debug = not etat.mode_debug
        logger.info(f"🐛 Mode debug: {'ON' if etat.mode_debug else 'OFF'}")

    @staticmethod
    def est_dans_module(prefixe_module: str) -> bool:
        """
        Vérifie si on est dans un module spécifique

        Args:
            prefixe_module: Préfixe module (ex: "cuisine")

        Returns:
            True si module courant commence par préfixe
        """
        etat = GestionnaireEtat.obtenir()
        return etat.module_actuel.startswith(prefixe_module)

    @staticmethod
    def obtenir_contexte_module() -> dict[str, Any]:
        """
        Retourne contexte du module actuel

        Returns:
            Dict avec infos contextuelles du module
        """
        etat = GestionnaireEtat.obtenir()

        contexte = {
            "module": etat.module_actuel,
            "fil_ariane": GestionnaireEtat.obtenir_fil_ariane_navigation(),
        }

        # Ajouter contexte spécifique selon module
        if etat.module_actuel.startswith("cuisine.recettes"):
            contexte["recette_visualisation"] = etat.id_recette_visualisation
            contexte["recette_edition"] = etat.id_recette_edition

        elif etat.module_actuel.startswith("cuisine.planning"):
            contexte["planning_visualisation"] = etat.id_planning_visualisation
            contexte["semaine"] = etat.semaine_actuelle

        elif etat.module_actuel.startswith("cuisine.inventaire"):
            contexte["article_visualisation"] = etat.id_article_visualisation

        return contexte


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════


def obtenir_etat() -> EtatApp:
    """Raccourci pour récupérer le state"""
    return GestionnaireEtat.obtenir()


def naviguer(module: str):
    """Raccourci pour naviguer"""
    GestionnaireEtat.naviguer_vers(module)
    from src.core.storage import obtenir_rerun_callback

    obtenir_rerun_callback()()


def revenir():
    """Raccourci pour revenir en arrière"""
    GestionnaireEtat.revenir()
    from src.core.storage import obtenir_rerun_callback

    obtenir_rerun_callback()()


def obtenir_fil_ariane() -> list[str]:
    """Raccourci pour fil d'Ariane"""
    return GestionnaireEtat.obtenir_fil_ariane_navigation()


def est_mode_debug() -> bool:
    """Raccourci pour vérifier mode debug"""
    etat = obtenir_etat()
    return etat.mode_debug


def nettoyer_etats_ui():
    """Raccourci pour nettoyer états UI"""
    GestionnaireEtat.nettoyer_etats_ui()
