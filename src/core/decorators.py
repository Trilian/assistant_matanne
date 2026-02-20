"""
Decorateurs - Décorateurs utilitaires réutilisables.

Contient :
- @avec_session_db : Gestion unifiée des sessions DB
- @avec_cache : Cache automatique pour fonctions
- @avec_gestion_erreurs : Gestion d'erreurs centralisée
- @avec_validation : Validation Pydantic automatique
"""

import inspect
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, overload

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")
F = TypeVar("F", bound=Callable[..., Any])


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: AVEC_SESSION_DB
# ═══════════════════════════════════════════════════════════


def avec_session_db(func: F) -> F:
    """
    Décorateur unifié pour gestion de session DB.

    Injecte automatiquement une session DB si :
    - Aucune session n'est fournie en paramètre
    - Utilise obtenir_contexte_db() pour créer une nouvelle session

    Usage:
        @avec_session_db
        def creer_recette(data: dict, db: Session) -> Recette:
            recette = Recette(**data)
            db.add(recette)
            db.commit()
            return recette

        # Appel sans DB (session créée automatiquement)
        recette = creer_recette({"nom": "Tarte"})

        # Appel avec DB existante
        with obtenir_contexte_db() as session:
            recette = creer_recette({"nom": "Tarte"}, db=session)

    Raises:
        ErreurBaseDeDonnees: Si création de session échoue
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Si 'db' ou 'session' est déjà fourni(e), utiliser directement
        if ("db" in kwargs and kwargs["db"] is not None) or (
            "session" in kwargs and kwargs["session"] is not None
        ):
            return func(*args, **kwargs)

        # Sinon, créer une nouvelle session
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            # Ajouter 'db' ou 'session' selon le paramètre attendu
            sig = inspect.signature(func)
            if "session" in sig.parameters:
                kwargs["session"] = session
            else:
                kwargs["db"] = session
            return func(*args, **kwargs)

    return wrapper  # type: ignore


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: AVEC_CACHE
# ═══════════════════════════════════════════════════════════


def avec_cache(
    ttl: int = 300,
    key_prefix: str | None = None,
    key_func: Callable[..., str] | None = None,
    cache_none: bool = False,
):
    """
    Décorateur pour cache automatique avec TTL.

    Usage:
        @avec_cache(ttl=600, key_prefix="recettes")
        def charger_recettes(page: int = 1) -> list[Recette]:
            # Logique coûteuse
            return recettes

        @avec_cache(ttl=3600, key_func=lambda self, id: f"recette_{id}")
        def charger_recette(self, id: int) -> Recette:
            # Custom key generation
            return recette

        @avec_cache(ttl=300, cache_none=False)  # Ne cache jamais None
        def operation_risquee() -> dict | None:
            return None  # Ne sera PAS mis en cache

    Args:
        ttl: Durée de vie en secondes
        key_prefix: Préfixe pour la clé de cache
        key_func: Fonction personnalisée pour générer la clé (optionnel)
        cache_none: Si False (défaut), les résultats None ne sont PAS mis en cache.
            Empêche le cache poisoning quand un décorateur d'erreur retourne None
            comme valeur de fallback.

    Returns:
        Valeur en cache ou résultat du calcul
    """
    # Sentinelle pour distinguer "pas en cache" de "valeur None en cache"
    _CACHE_MISS = object()

    def decorator(func: F) -> F:
        # Pré-calculer la signature pour optimisation
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from src.core.caching import CacheMultiNiveau

            cache = CacheMultiNiveau()

            # Générer clé de cache
            if key_func is not None:
                # Filtrer db des kwargs d'abord
                filtered_kwargs = {k: v for k, v in kwargs.items() if k != "db"}

                # Essayer d'abord de passer les arguments par position
                try:
                    cache_key = key_func(*args, **filtered_kwargs)
                except TypeError:
                    # Reconstruire les kwargs en utilisant les noms de la fonction
                    full_kwargs = {}
                    for i, arg in enumerate(args):
                        if i < len(param_names):
                            param_name = param_names[i]
                            if param_name not in ("self", "db"):
                                full_kwargs[param_name] = arg

                    # Ajouter les kwargs nommés (sauf db)
                    for k, v in filtered_kwargs.items():
                        full_kwargs[k] = v

                    # Remplir les valeurs par défaut manquantes
                    for param_name, param in sig.parameters.items():
                        if param_name in ("self", "db"):
                            continue
                        if (
                            param_name not in full_kwargs
                            and param.default != inspect.Parameter.empty
                        ):
                            full_kwargs[param_name] = param.default

                    # Appeler key_func avec self + tous les kwargs nécessaires
                    if args:
                        cache_key = key_func(args[0], **full_kwargs)
                    else:
                        cache_key = key_func(**full_kwargs)
            else:
                prefix = key_prefix or func.__name__
                # Exclure 'db' des kwargs dans le cache key
                filtered_kwargs = {k: v for k, v in kwargs.items() if k != "db"}
                cache_key = f"{prefix}_{str(args)}_{str(filtered_kwargs)}"

            # Chercher dans le cache multi-niveaux (L1 → L2 → L3)
            cached_value = cache.get(cache_key, default=_CACHE_MISS)
            if cached_value is not _CACHE_MISS:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value

            # Calculer et cacher (L1 + L2)
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)

            # Ne pas cacher None si cache_none=False (évite le cache poisoning
            # quand @avec_gestion_erreurs retourne None comme fallback)
            if result is not None or cache_none:
                cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper  # type: ignore

    return decorator


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: AVEC_GESTION_ERREURS
# ═══════════════════════════════════════════════════════════


def avec_gestion_erreurs(
    default_return: Any = None,
    log_level: str = "ERROR",
    afficher_erreur: bool = False,
):
    """
    Décorateur pour gestion centralisée d'erreurs.

    Usage:
        @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
        def operation_risquee(data: dict) -> dict:
            # Code qui peut lever des exceptions
            return resultat

    Args:
        default_return: Valeur retournée en cas d'erreur
        log_level: Niveau de log ("DEBUG", "INFO", "WARNING", "ERROR")
        afficher_erreur: Afficher l'erreur dans Streamlit

    Returns:
        Résultat de la fonction ou default_return
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                # Relever les exceptions métier (héritant de ExceptionApp)
                from src.core.errors_base import ExceptionApp

                if isinstance(e, ExceptionApp):
                    raise  # Relever les exceptions métier

                # Logger l'erreur
                log_msg = f"Erreur dans {func.__name__}: {e}"
                getattr(logger, log_level.lower())(log_msg)

                # Afficher dans Streamlit si demandé
                if afficher_erreur:
                    try:
                        import streamlit as st

                        st.error(f"[ERROR] {str(e)}")
                    except Exception:
                        pass  # Streamlit pas initialisé

                return default_return

        return wrapper  # type: ignore

    return decorator


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: AVEC_VALIDATION
# ═══════════════════════════════════════════════════════════


def avec_validation(
    validator_class: type,
    field_mapping: dict[str, str] | None = None,
):
    """
    Décorateur pour validation Pydantic automatique.

    Usage:
        @avec_validation(RecetteInput, field_mapping={
            "data": "recipe_data"
        })
        def creer_recette(data: dict, db: Session) -> Recette:
            validated = RecetteInput(**data)
            # ...

    Args:
        validator_class: Modèle Pydantic pour validation
        field_mapping: Mapping des paramètres

    Returns:
        Fonction décorée avec validation automatique

    Raises:
        ErreurValidation: Si validation échoue
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from pydantic import ValidationError

            from src.core.errors_base import ErreurValidation

            try:
                # Chercher le paramètre à valider
                param_key = list(field_mapping.keys())[0] if field_mapping else "data"

                if param_key in kwargs:
                    data = kwargs[param_key]
                    validated = validator_class(**data)
                    kwargs[param_key] = validated.model_dump()

                return func(*args, **kwargs)

            except ValidationError as e:
                raise ErreurValidation(
                    f"Validation échouée: {e}",
                    details={"validation_errors": e.errors()},
                    message_utilisateur="Les données fournies sont invalides",
                ) from e

        return wrapper  # type: ignore

    return decorator


# ═══════════════════════════════════════════════════════════
# EXPORTS PRINCIPAUX
# ═══════════════════════════════════════════════════════════

__all__ = [
    "avec_session_db",
    "avec_cache",
    "avec_gestion_erreurs",
    "avec_validation",
]
