"""
Errors Base - Exceptions pures sans dépendances UI/Streamlit.

Ce module centralise UNIQUEMENT :
- Les classes d'exceptions métier
- Les types d'erreurs
- Les détails d'erreur

[!] IMPORTANT: Ne doit JAMAIS importer streamlit ou éléments UI

USAGE:
- Services, modules backend → importer depuis errors_base
- Modules UI Streamlit → importer depuis errors (hérite + helpers UI)

Exemples:
    # Backend/services (pas d'UI)
    from src.core.errors_base import ErreurValidation, ErreurNonTrouve

    # Modules Streamlit avec affichage d'erreurs
    from src.core.errors import afficher_erreur, ErreurValidation
"""

from typing import Any

# ═══════════════════════════════════════════════════════════
# EXCEPTIONS PERSONNALISÉES (PURES)
# ═══════════════════════════════════════════════════════════


class ExceptionApp(Exception):
    """
    Exception de base pour l'application (sans dépendances UI).

    Toutes les exceptions métier héritent de cette classe.

    Attributes:
        message: Message technique pour les logs
        details: Détails supplémentaires (dict)
        message_utilisateur: Message friendly pour l'UI (optionnel)
        code_erreur: Code d'erreur unique pour debugging
    """

    code_erreur: str = "APP_ERROR"

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        message_utilisateur: str | None = None,
        code_erreur: str | None = None,
    ) -> None:
        """
        Initialise l'exception.

        Args:
            message: Message d'erreur technique
            details: Dictionnaire avec détails supplémentaires
            message_utilisateur: Message à afficher à l'utilisateur
            code_erreur: Code unique pour l'erreur
        """
        self.message: str = message
        self.details: dict[str, Any] = details or {}
        self.message_utilisateur: str = message_utilisateur or message
        self.code_erreur: str = code_erreur or self.__class__.code_erreur
        super().__init__(message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"

    def to_dict(self) -> dict[str, Any]:
        """Convertit l'exception en dictionnaire pour sérialisation"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code_erreur": self.code_erreur,
            "message_utilisateur": self.message_utilisateur,
            "details": self.details,
        }


class ErreurValidation(ExceptionApp):
    """
    Exception levée lors d'une erreur de validation.

    Utilisée pour :
    - Erreurs de validation de formulaires
    - Données invalides
    - Contraintes métier non respectées
    """

    code_erreur = "VALIDATION_ERROR"


class ErreurNonTrouve(ExceptionApp):
    """
    Exception levée quand une ressource n'est pas trouvée.

    Équivalent d'un 404 pour les ressources en base de données.
    """

    code_erreur = "NOT_FOUND"


class ErreurBaseDeDonnees(ExceptionApp):
    """
    Exception levée lors d'erreurs de base de données.

    Inclut :
    - Erreurs de connexion
    - Erreurs de requêtes
    - Erreurs de transactions
    - Violations de contraintes
    """

    code_erreur = "DATABASE_ERROR"


class ErreurServiceIA(ExceptionApp):
    """
    Exception levée lors d'erreurs avec le service IA.

    Inclut :
    - Erreurs d'API Mistral
    - Timeouts
    - Erreurs de parsing
    - Réponses invalides
    """

    code_erreur = "AI_SERVICE_ERROR"


class ErreurLimiteDebit(ExceptionApp):
    """
    Exception levée quand la limite d'appels est atteinte.

    Utilisée pour le rate limiting des API externes.
    Contient :
    - Nombre d'appels restants
    - Heure de reset
    - Période (horaire/quotidienne)
    """

    code_erreur = "RATE_LIMIT_EXCEEDED"


class ErreurServiceExterne(ExceptionApp):
    """
    Exception levée lors d'erreurs avec services externes.

    Exemples :
    - Erreurs de scraping web
    - APIs tierces (hors IA)
    - Services de stockage
    """

    code_erreur = "EXTERNAL_SERVICE_ERROR"


class ErreurConfiguration(ExceptionApp):
    """
    Exception levée lors d'erreurs de configuration.

    Utilisée pour :
    - Variables d'environnement manquantes
    - Configuration invalide
    - Paramètres manquants
    """

    code_erreur = "CONFIGURATION_ERROR"


# ═══════════════════════════════════════════════════════════
# HELPERS DE VALIDATION (sans UI)
# ═══════════════════════════════════════════════════════════


def exiger_champs(
    data: dict,
    champs: list[str],
    nom_objet: str = "objet",
) -> None:
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
        ...     {"nom": "Tarte", "temps": 30},
        ...     ["nom", "temps", "portions"],
        ...     "recette"
        ... )
        Traceback (most recent call last):
            ...
        ErreurValidation: Champs manquants dans recette: ['portions']
    """
    manquants = [champ for champ in champs if not data.get(champ)]

    if manquants:
        raise ErreurValidation(
            f"Champs manquants dans {nom_objet}: {manquants}",
            details={"champs_manquants": manquants, "objet": nom_objet},
            message_utilisateur=f"Champs obligatoires manquants : {', '.join(manquants)}",
        )


def valider_type(
    valeur: Any,
    types_attendus: type | tuple[type, ...],
    nom_param: str = "paramètre",
) -> None:
    """
    Vérifie le type d'une valeur.

    Args:
        valeur: Valeur à vérifier
        types_attendus: Type(s) attendu(s)
        nom_param: Nom du paramètre pour l'erreur

    Raises:
        ErreurValidation: Si le type ne correspond pas

    Example:
        >>> valider_type(42, str, "age")
        Traceback (most recent call last):
            ...
        ErreurValidation: age doit être str, reçu int
    """
    if not isinstance(valeur, types_attendus):
        types_str = (
            types_attendus.__name__
            if isinstance(types_attendus, type)
            else " ou ".join(t.__name__ for t in types_attendus)
        )
        raise ErreurValidation(
            f"{nom_param} doit être {types_str}, reçu {type(valeur).__name__}",
            details={
                "parametre": nom_param,
                "type_attendu": types_str,
                "type_recu": type(valeur).__name__,
            },
            message_utilisateur=f"Type invalide pour {nom_param}",
        )


def valider_plage(
    valeur: int | float,
    min_val: int | float | None = None,
    max_val: int | float | None = None,
    nom_param: str = "valeur",
) -> None:
    """
    Vérifie qu'une valeur est dans une plage.

    .. deprecated::
        Utiliser :func:`exiger_plage` à la place.

    Args:
        valeur: Valeur à vérifier
        min_val: Valeur minimale (incluse)
        max_val: Valeur maximale (incluse)
        nom_param: Nom du paramètre

    Raises:
        ErreurValidation: Si hors plage
    """
    exiger_plage(valeur, minimum=min_val, maximum=max_val, nom_champ=nom_param)


def exiger_positif(valeur: float, nom_champ: str) -> None:
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


def exiger_existence(obj: Any, type_objet: str, id_objet: Any) -> None:
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
) -> None:
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
    texte: str,
    minimum: int | None = None,
    maximum: int | None = None,
    nom_champ: str = "texte",
) -> None:
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
