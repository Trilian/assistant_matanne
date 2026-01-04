"""
State Unifié - Gestionnaire État Complet
Tout harmonisé en français
"""
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class EtatApp:
    """État global de l'application"""
    # Navigation
    module_actuel: str = "accueil"
    module_precedent: Optional[str] = None
    historique_navigation: List[str] = field(default_factory=list)

    # Utilisateur
    nom_utilisateur: str = "Anne"
    notifications_non_lues: int = 0

    # Agent IA
    agent_ia: Optional[Any] = None

    # Recettes
    id_recette_visualisation: Optional[int] = None
    id_recette_edition: Optional[int] = None
    id_recette_adaptation_bebe: Optional[int] = None

    # Inventaire
    id_article_visualisation: Optional[int] = None
    id_article_edition: Optional[int] = None

    # Planning
    id_planning_visualisation: Optional[int] = None
    semaine_actuelle: Optional[Any] = None
    id_planning_ajout_repas: Optional[int] = None
    jour_ajout_repas: Optional[int] = None
    date_ajout_repas: Optional[Any] = None
    id_repas_edition: Optional[int] = None

    # États UI
    afficher_formulaire_ajout: bool = False
    afficher_generation_ia: bool = False
    afficher_confirmation_suppression: bool = False
    afficher_notifications: bool = False
    afficher_formulaire_ajout_repas: bool = False
    onglet_actif: Optional[str] = None

    # Flags
    mode_debug: bool = False
    cache_active: bool = True

    def __post_init__(self):
        if not self.historique_navigation:
            self.historique_navigation = [self.module_actuel]


class GestionnaireEtat:
    """Gestionnaire centralisé du state"""
    CLE_ETAT = "etat_app"

    @staticmethod
    def initialiser():
        """Initialise le state si pas déjà fait"""
        if GestionnaireEtat.CLE_ETAT not in st.session_state:
            st.session_state[GestionnaireEtat.CLE_ETAT] = EtatApp()
            logger.info("✅ EtatApp initialisé")

    @staticmethod
    def obtenir() -> EtatApp:
        """Récupère le state actuel"""
        GestionnaireEtat.initialiser()
        return st.session_state[GestionnaireEtat.CLE_ETAT]

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
    def obtenir_fil_ariane_navigation() -> List[str]:
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
            "famille.suivi_jules": "Suivi Jules",
            "famille.bien_etre": "Bien-être",
            "famille.routines": "Routines",
            "maison.projets": "Projets",
            "maison.jardin": "Jardin",
            "maison.entretien": "Entretien",
            "planning.calendrier": "Calendrier",
            "planning.vue_ensemble": "Vue d'ensemble",
            "parametres": "Paramètres",
        }

        return correspondances_labels.get(module, module.split(".")[-1].capitalize())

    @staticmethod
    def reinitialiser():
        """Réinitialise complètement le state"""
        if GestionnaireEtat.CLE_ETAT in st.session_state:
            del st.session_state[GestionnaireEtat.CLE_ETAT]

        GestionnaireEtat.initialiser()
        logger.info("🔄 State réinitialisé")

    @staticmethod
    def obtenir_resume_etat() -> Dict:
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
        """Nettoie les états UI temporaires"""
        etat = GestionnaireEtat.obtenir()

        # Réinitialiser états UI
        etat.afficher_formulaire_ajout = False
        etat.afficher_generation_ia = False
        etat.afficher_confirmation_suppression = False
        etat.afficher_notifications = False
        etat.afficher_formulaire_ajout_repas = False
        etat.onglet_actif = None

        logger.debug("🧹 États UI nettoyés")

    @staticmethod
    def definir_recette_visualisation(id_recette: Optional[int]):
        """Définit recette en cours de visualisation"""
        etat = GestionnaireEtat.obtenir()
        etat.id_recette_visualisation = id_recette

        if id_recette:
            logger.debug(f"👁️ Visualisation recette {id_recette}")

    @staticmethod
    def definir_recette_edition(id_recette: Optional[int]):
        """Définit recette en cours d'édition"""
        etat = GestionnaireEtat.obtenir()
        etat.id_recette_edition = id_recette

        if id_recette:
            logger.debug(f"✏️ Édition recette {id_recette}")

    @staticmethod
    def definir_planning_visualisation(id_planning: Optional[int]):
        """Définit planning en cours de visualisation"""
        etat = GestionnaireEtat.obtenir()
        etat.id_planning_visualisation = id_planning

        if id_planning:
            logger.debug(f"👁️ Visualisation planning {id_planning}")

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
    def obtenir_contexte_module() -> Dict[str, Any]:
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
    st.rerun()


def revenir():
    """Raccourci pour revenir en arrière"""
    GestionnaireEtat.revenir()
    st.rerun()


def obtenir_fil_ariane() -> List[str]:
    """Raccourci pour fil d'Ariane"""
    return GestionnaireEtat.obtenir_fil_ariane_navigation()


def est_mode_debug() -> bool:
    """Raccourci pour vérifier mode debug"""
    etat = obtenir_etat()
    return etat.mode_debug


def nettoyer_etats_ui():
    """Raccourci pour nettoyer états UI"""
    GestionnaireEtat.nettoyer_etats_ui()