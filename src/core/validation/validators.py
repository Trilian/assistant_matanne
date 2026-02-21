"""
Validators - Helpers et décorateurs de validation.

Fonctions pour:
- Valider des modèles Pydantic
- Valider des formulaires Streamlit
- Décorateurs de validation automatique
"""

__all__ = [
    "valider_modele",
    "valider_formulaire_streamlit",
    "valider_et_nettoyer_formulaire",
    "afficher_erreurs_validation",
    "valider_entree",
]

import logging
from collections.abc import Callable
from functools import wraps

from pydantic import BaseModel, ValidationError

from .sanitizer import NettoyeurEntrees
from .schemas import SCHEMA_COURSES, SCHEMA_INVENTAIRE, SCHEMA_RECETTE

logger = logging.getLogger(__name__)


def valider_modele(
    classe_modele: type[BaseModel], data: dict
) -> tuple[bool, str, BaseModel | None]:
    """
    Valide des données avec un modèle Pydantic.

    Args:
        classe_modele: Classe Pydantic
        data: Données à valider

    Returns:
        Tuple (succès, message_erreur, instance_validée)

    Example:
        >>> succes, erreur, recette = valider_modele(RecetteInput, form_data)
    """
    try:
        valide = classe_modele(**data)
        return True, "", valide
    except ValidationError as e:
        message_erreur = str(e)
        if "field required" in message_erreur.lower():
            message_erreur = "Champs obligatoires manquants"
        elif "validation error" in message_erreur.lower():
            message_erreur = "Données invalides"
        return False, message_erreur, None
    except Exception as e:
        return False, str(e), None


def valider_formulaire_streamlit(
    donnees_formulaire: dict, schema: dict
) -> tuple[bool, list[str], dict]:
    """
    Valide un formulaire Streamlit.

    Args:
        donnees_formulaire: Données du formulaire
        schema: Schéma de validation

    Returns:
        Tuple (valide, liste_erreurs, données_nettoyées)
    """
    erreurs = []
    nettoye = NettoyeurEntrees.nettoyer_dictionnaire(donnees_formulaire, schema)

    # Vérifier champs requis
    for champ, regles in schema.items():
        if regles.get("required", False):
            if champ not in nettoye or not nettoye[champ]:
                erreurs.append(f"[!] {regles.get('label', champ)} est requis")

    # Vérifier plages numériques
    for champ, valeur in nettoye.items():
        regles = schema.get(champ, {})

        if regles.get("type") == "number" and valeur is not None:
            if regles.get("min") is not None and valeur < regles["min"]:
                erreurs.append(f"[!] {regles.get('label', champ)} doit être ≥ {regles['min']}")
            if regles.get("max") is not None and valeur > regles["max"]:
                erreurs.append(f"[!] {regles.get('label', champ)} doit être ≤ {regles['max']}")

        if regles.get("type") == "string" and valeur:
            longueur_max = regles.get("max_length", 1000)
            if len(valeur) > longueur_max:
                erreurs.append(
                    f"[!] {regles.get('label', champ)} trop long (max {longueur_max} caractères)"
                )

    est_valide = len(erreurs) == 0
    return est_valide, erreurs, nettoye


def valider_et_nettoyer_formulaire(
    nom_module: str, donnees_formulaire: dict
) -> tuple[bool, list[str], dict]:
    """
    Helper pour valider un formulaire selon le module.

    Retourne les erreurs au lieu de les afficher — l'appelant décide
    de l'affichage (Streamlit, CLI, tests…).

    Args:
        nom_module: Nom du module (recettes, inventaire, courses)
        donnees_formulaire: Données à valider

    Returns:
        Tuple (valide, liste_erreurs, données_nettoyées)

    Example:
        >>> valide, erreurs, donnees = valider_et_nettoyer_formulaire("recettes", form_data)
        >>> if not valide:
        ...     afficher_erreurs_validation(erreurs)
    """

    schemas = {
        "recettes": SCHEMA_RECETTE,
        "inventaire": SCHEMA_INVENTAIRE,
        "courses": SCHEMA_COURSES,
    }

    schema = schemas.get(nom_module, {})

    if not schema:
        logger.warning(f"Pas de schéma pour {nom_module}")
        # Nettoyage basique
        nettoye = {}
        for cle, valeur in donnees_formulaire.items():
            if isinstance(valeur, str):
                nettoye[cle] = NettoyeurEntrees.nettoyer_chaine(valeur)
            else:
                nettoye[cle] = valeur
        return True, [], nettoye

    est_valide, erreurs, nettoye = valider_formulaire_streamlit(donnees_formulaire, schema)

    return est_valide, erreurs, nettoye


def afficher_erreurs_validation(erreurs: list[str]) -> None:
    """
    Affiche les erreurs de validation dans Streamlit.

    Utilise un import lazy de Streamlit pour rester découplé.
    Fonctionne en mode dégradé (logging) quand Streamlit n'est pas disponible.

    Args:
        erreurs: Liste des messages d'erreur
    """
    if not erreurs:
        return

    try:
        import streamlit as st

        with st.expander("❌ Erreurs de validation", expanded=True):
            for erreur in erreurs:
                st.error(erreur)
    except Exception:
        # Mode dégradé: logging pur (tests, CLI, sans Streamlit)
        for erreur in erreurs:
            logger.error(f"Validation: {erreur}")


def valider_entree(schema: dict | None = None, nettoyer_tout: bool = True):
    """
    Décorateur pour valider automatiquement les entrées.

    Args:
        schema: Schéma de validation (optionnel)
        nettoyer_tout: Nettoyer toutes les chaînes par défaut

    Returns:
        Décorateur de fonction

    Example:
        >>> @valider_entree(schema=SCHEMA_RECETTE)
        >>> def creer_recette(data: dict):
        >>>     return recette_service.create(data)
    """

    def decorateur(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Trouver l'argument data
            data_arg = None

            for arg in args:
                if isinstance(arg, dict):
                    data_arg = arg
                    break

            if not data_arg:
                for cle in ["data", "donnees", "donnees_formulaire"]:
                    if cle in kwargs and isinstance(kwargs[cle], dict):
                        data_arg = kwargs[cle]
                        break

            # Nettoyer si schéma fourni
            if data_arg and schema:
                nettoye = NettoyeurEntrees.nettoyer_dictionnaire(data_arg, schema)

                # Remplacer dans args/kwargs
                if isinstance(args, tuple) and data_arg in args:
                    args = tuple(nettoye if arg is data_arg else arg for arg in args)

                for cle in ["data", "donnees", "donnees_formulaire"]:
                    if cle in kwargs and kwargs[cle] is data_arg:
                        kwargs[cle] = nettoye

            # Nettoyage basique si pas de schéma
            elif data_arg and nettoyer_tout:
                for cle, valeur in data_arg.items():
                    if isinstance(valeur, str):
                        data_arg[cle] = NettoyeurEntrees.nettoyer_chaine(valeur)

            return func(*args, **kwargs)

        return wrapper

    return decorateur
