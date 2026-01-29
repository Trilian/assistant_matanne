"""
Errors - Gestion des erreurs avec intégration UI (Streamlit).

Ce module :
- Ré-exporte les exceptions pures depuis errors_base.py
- Ajoute les fonctions d'affichage UI
- Fournit des décorateurs de gestion d'erreurs avec UI

[!] IMPORTANT: Les exceptions pures sont dans errors_base.py (sans dépendances UI)
"""

import logging
import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any

import streamlit as st

# Ré-exporter les exceptions pures
from .errors_base import (
    ErreurBaseDeDonnees,
    ErreurConfiguration,
    ErreurLimiteDebit,
    ErreurNonTrouve,
    ErreurServiceExterne,
    ErreurServiceIA,
    ErreurValidation,
    ExceptionApp,
    exiger_champs,
    valider_plage,
    valider_type,
)

logger = logging.getLogger(__name__)


def _is_debug_mode() -> bool:
    """
    Retourne l'état du mode debug de l'application.

    Essaie d'utiliser le `EtatApp.mode_debug` via `obtenir_etat()` si disponible,
    sinon fallback sur `st.session_state['debug_mode']` pour compatibilité.
    """
    try:
        from .state import obtenir_etat

        etat = obtenir_etat()
        return bool(getattr(etat, "mode_debug", False))
    except Exception:
        # Fallback safe: st may not be initialisé
        try:
            return bool(st.session_state.get("debug_mode", False))
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR DE GESTION D'ERREURS
# ═══════════════════════════════════════════════════════════


def gerer_erreurs(
    afficher_dans_ui: bool = True,
    niveau_log: str = "ERROR",
    relancer: bool = False,
    valeur_fallback: Any = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Décorateur pour gérer automatiquement les erreurs.

    Capture les exceptions, les log, et optionnellement :
    - Affiche un message à l'utilisateur (Streamlit)
    - Retourne une valeur de fallback
    - Relance l'exception

    Args:
        afficher_dans_ui: Afficher l'erreur dans Streamlit
        niveau_log: Niveau de log (ERROR, WARNING, INFO)
        relancer: Relancer l'exception après traitement
        valeur_fallback: Valeur à retourner en cas d'erreur

    Returns:
        Décorateur de fonction

    Example:
        >>> @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
        >>> def obtenir_recettes():
        >>>     return recette_service.get_all()
    """

    def decorateur(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)

            except ErreurValidation as e:
                logger.warning(f"ErreurValidation dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error(f"[ERROR] {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurNonTrouve as e:
                logger.info(f"ErreurNonTrouve dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.warning(f"[!] {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurBaseDeDonnees as e:
                logger.error(f"ErreurBaseDeDonnees dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error("💾 Erreur de base de données")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurServiceIA as e:
                logger.warning(f"ErreurServiceIA dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error(f"🤖 {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurLimiteDebit as e:
                logger.warning(f"ErreurLimiteDebit dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.warning(f"⏳ {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurServiceExterne as e:
                logger.warning(f"ErreurServiceExterne dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error(f"🌐 {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except Exception as e:
                logger.critical(f"Erreur inattendue dans {func.__name__}: {e}", exc_info=True)
                if afficher_dans_ui:
                    st.error("[ERROR] Une erreur inattendue s'est produite")

                    # Afficher stack trace en mode debug
                    if _is_debug_mode():
                        with st.expander("🐛 Stack trace"):
                            st.code(traceback.format_exc())

                if relancer:
                    raise
                return valeur_fallback

        return wrapper

    return decorateur


# Alias pour compatibilité
handle_errors = gerer_erreurs


# ═══════════════════════════════════════════════════════════
# HELPERS DE VALIDATION
# ═══════════════════════════════════════════════════════════


def exiger_champs(data: dict, champs: list[str], nom_objet: str = "objet"):
    """
    Vérifie que les champs requis sont présents et non vides.

    Args:
        data: Dictionnaire de données
        champs: Liste des champs obligatoires
        nom_objet: Nom de l'objet pour le message d'erreur

    Raises:
        ErreurValidation: Si des champs sont manquants

    Example:
        >>> exiger_champs(
        >>>     {"nom": "Tarte", "temps": 30},
        >>>     ["nom", "temps", "portions"],
        >>>     "recette"
        >>> )
    """
    manquants = [champ for champ in champs if not data.get(champ)]

    if manquants:
        raise ErreurValidation(
            f"Champs manquants dans {nom_objet}: {manquants}",
            details={"champs_manquants": manquants},
            message_utilisateur=f"Champs obligatoires manquants : {', '.join(manquants)}",
        )


def exiger_positif(valeur: float, nom_champ: str):
    """
    Vérifie qu'une valeur numérique est positive.

    Args:
        valeur: Valeur à vérifier
        nom_champ: Nom du champ pour le message d'erreur

    Raises:
        ErreurValidation: Si la valeur n'est pas positive

    Example:
        >>> exiger_positif(quantite, "quantité")
    """
    if valeur <= 0:
        raise ErreurValidation(
            f"{nom_champ} doit être positif: {valeur}",
            message_utilisateur=f"{nom_champ} doit être supérieur à 0",
        )


def exiger_existence(obj: Any, type_objet: str, id_objet: Any):
    """
    Vérifie qu'un objet existe (n'est pas None).

    Args:
        obj: Objet à vérifier
        type_objet: Type d'objet (pour le message)
        id_objet: ID de l'objet (pour le message)

    Raises:
        ErreurNonTrouve: Si l'objet est None

    Example:
        >>> recette = recette_service.get_by_id(42)
        >>> exiger_existence(recette, "Recette", 42)
    """
    if obj is None:
        raise ErreurNonTrouve(
            f"{type_objet} {id_objet} non trouvé",
            details={"type": type_objet, "id": id_objet},
            message_utilisateur=f"{type_objet} introuvable",
        )


def exiger_plage(
    valeur: float,
    minimum: float | None = None,
    maximum: float | None = None,
    nom_champ: str = "valeur",
):
    """
    Vérifie qu'une valeur est dans une plage donnée.

    Args:
        valeur: Valeur à vérifier
        minimum: Valeur minimale (optionnelle)
        maximum: Valeur maximale (optionnelle)
        nom_champ: Nom du champ pour le message d'erreur

    Raises:
        ErreurValidation: Si la valeur est hors plage

    Example:
        >>> exiger_plage(portions, minimum=1, maximum=20, nom_champ="portions")
    """
    if minimum is not None and valeur < minimum:
        raise ErreurValidation(
            f"{nom_champ} trop petit: {valeur} < {minimum}",
            message_utilisateur=f"{nom_champ} doit être au minimum {minimum}",
        )

    if maximum is not None and valeur > maximum:
        raise ErreurValidation(
            f"{nom_champ} trop grand: {valeur} > {maximum}",
            message_utilisateur=f"{nom_champ} doit être au maximum {maximum}",
        )


def exiger_longueur(
    texte: str, minimum: int | None = None, maximum: int | None = None, nom_champ: str = "texte"
):
    """
    Vérifie la longueur d'une chaîne de caractères.

    Args:
        texte: Chaîne à vérifier
        minimum: Longueur minimale (optionnelle)
        maximum: Longueur maximale (optionnelle)
        nom_champ: Nom du champ pour le message d'erreur

    Raises:
        ErreurValidation: Si la longueur est invalide

    Example:
        >>> exiger_longueur(nom_recette, minimum=3, maximum=200, nom_champ="nom")
    """
    longueur = len(texte)

    if minimum is not None and longueur < minimum:
        raise ErreurValidation(
            f"{nom_champ} trop court: {longueur} < {minimum}",
            message_utilisateur=f"{nom_champ} doit faire au moins {minimum} caractères",
        )

    if maximum is not None and longueur > maximum:
        raise ErreurValidation(
            f"{nom_champ} trop long: {longueur} > {maximum}",
            message_utilisateur=f"{nom_champ} doit faire au maximum {maximum} caractères",
        )


# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE D'ERREURS STREAMLIT
# ═══════════════════════════════════════════════════════════


def afficher_erreur_streamlit(erreur: Exception, contexte: str = "") -> None:
    """
    Affiche une erreur formatée dans Streamlit.

    Gère l'affichage selon le type d'erreur et le mode debug.

    Args:
        erreur: Exception à afficher
        contexte: Contexte additionnel (optionnel)
    """
    if isinstance(erreur, ExceptionApp):
        mapping = {
            ErreurValidation: (st.error, "[ERROR]"),
            ErreurNonTrouve: (st.warning, "[!]"),
            ErreurBaseDeDonnees: (st.error, "💾"),
            ErreurServiceIA: (st.error, "🤖"),
            ErreurLimiteDebit: (st.warning, "⏳"),
            ErreurServiceExterne: (st.error, "🌐"),
        }

        for exc_type, (render_fn, prefix) in mapping.items():
            if isinstance(erreur, exc_type):
                render_fn(f"{prefix} {erreur.message_utilisateur}")
                break
        else:
            st.error(f"[ERROR] {erreur.message_utilisateur}")

        # Afficher détails en mode debug
        if _is_debug_mode() and getattr(erreur, "details", None):
            with st.expander("[SEARCH] Détails"):
                st.json(erreur.details)
    else:
        # Erreurs inconnues
        st.error("[ERROR] Une erreur inattendue s'est produite")

        if contexte:
            st.caption(f"Contexte : {contexte}")

        # Stack trace en mode debug
        if _is_debug_mode():
            with st.expander("🐛 Stack trace"):
                st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGER POUR GESTION D'ERREURS
# ═══════════════════════════════════════════════════════════


class GestionnaireErreurs:
    """
    Context manager pour gérer les erreurs dans un bloc de code.

    Example:
        >>> with GestionnaireErreurs("Création recette"):
        >>>     recette = recette_service.create(data)
    """

    def __init__(
        self,
        contexte: str,
        afficher_dans_ui: bool = True,
        logger_instance: logging.Logger | None = None,
    ):
        """
        Initialise le gestionnaire.

        Args:
            contexte: Description du contexte pour les logs
            afficher_dans_ui: Afficher erreur dans Streamlit
            logger_instance: Logger à utiliser (optionnel)
        """
        self.contexte = contexte
        self.afficher_dans_ui = afficher_dans_ui
        self.logger = logger_instance or logger

    def __enter__(self):
        """Entre dans le contexte."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Sort du contexte et gère les erreurs.

        Returns:
            True si l'exception est gérée, False sinon
        """
        if exc_type is None:
            return True

        # Logger l'erreur
        self.logger.error(
            f"Erreur dans {self.contexte}: {exc_val}", exc_info=(exc_type, exc_val, exc_tb)
        )

        # Afficher dans UI si demandé
        if self.afficher_dans_ui:
            afficher_erreur_streamlit(exc_val, self.contexte)

        # Ne pas supprimer l'exception (elle sera relancée)
        return False
