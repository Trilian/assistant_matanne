"""
Manager d'état — GestionnaireEtat centralisé.

Découplé de Streamlit via le protocole SessionStorage.
"""

from __future__ import annotations

import logging
from typing import Any

from .slices import EtatApp

logger = logging.getLogger(__name__)


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
        fil_ariane: list[str] = []
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
    def obtenir_resume_etat() -> dict[str, Any]:
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

        contexte: dict[str, Any] = {
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


__all__ = ["GestionnaireEtat"]
