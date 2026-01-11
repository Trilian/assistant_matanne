"""
Decorators - Décorateurs utilitaires réutilisables.

Contient :
- @with_db_session : Gestion unifiée des sessions DB
- @with_cache : Cache automatique pour fonctions
- @with_error_handling : Gestion d'erreurs centralisée
"""

import logging
from functools import wraps
from typing import Any, Callable, Generic, TypeVar

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: WITH_DB_SESSION
# ═══════════════════════════════════════════════════════════


def with_db_session(func: F) -> F:
    """
    Décorateur unifié pour gestion de session DB.

    Injecte automatiquement une session DB si :
    - Aucune session n'est fournie en paramètre
    - Utilise get_db_context() pour créer une nouvelle session

    Usage:
        @with_db_session
        def creer_recette(data: dict, db: Session) -> Recette:
            recette = Recette(**data)
            db.add(recette)
            db.commit()
            return recette

        # Appel sans DB (session créée automatiquement)
        recette = creer_recette({"nom": "Tarte"})

        # Appel avec DB existante
        with get_db_context() as session:
            recette = creer_recette({"nom": "Tarte"}, db=session)

    Raises:
        ErreurBaseDeDonnees: Si création de session échoue
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Si 'db' est déjà fourni, utiliser directement
        if "db" in kwargs and kwargs["db"] is not None:
            return func(*args, **kwargs)

        # Sinon, créer une nouvelle session
        from src.core.database import get_db_context

        with get_db_context() as session:
            kwargs["db"] = session
            return func(*args, **kwargs)

    return wrapper  # type: ignore


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: WITH_CACHE
# ═══════════════════════════════════════════════════════════


def with_cache(ttl: int = 300, key_prefix: str | None = None, key_func: None = None):
    """
    Décorateur pour cache automatique avec TTL.

    Usage:
        @with_cache(ttl=600, key_prefix="recipes")
        def charger_recettes(page: int = 1) -> list[Recette]:
            # Logique coûteuse
            return recettes
        
        @with_cache(ttl=3600, key_func=lambda self, id: f"recette_{id}")
        def charger_recette(self, id: int) -> Recette:
            # Custom key generation
            return recette

    Args:
        ttl: Durée de vie en secondes
        key_prefix: Préfixe pour la clé de cache
        key_func: Fonction personnalisée pour générer la clé (optionnel)

    Returns:
        Valeur en cache ou résultat du calcul
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from src.core.cache import Cache

            # Générer clé de cache
            if key_func is not None:
                cache_key = key_func(*args, **kwargs)
            else:
                prefix = key_prefix or func.__name__
                cache_key = f"{prefix}_{str(args)}_{str(kwargs)}"

            # Chercher en cache
            cached_value = Cache.obtenir(cache_key, ttl=ttl)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value

            # Calculer et cacher
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            Cache.definir(cache_key, result, ttl=ttl)

            return result

        return wrapper  # type: ignore

    return decorator


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: WITH_ERROR_HANDLING
# ═══════════════════════════════════════════════════════════


def with_error_handling(
    default_return: Any = None,
    log_level: str = "ERROR",
    afficher_erreur: bool = False,
):
    """
    Décorateur pour gestion centralisée d'erreurs.

    Usage:
        @with_error_handling(default_return=None, afficher_erreur=True)
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
                # Logger l'erreur
                log_msg = f"Erreur dans {func.__name__}: {e}"
                getattr(logger, log_level.lower())(log_msg)

                # Afficher dans Streamlit si demandé
                if afficher_erreur:
                    try:
                        import streamlit as st

                        st.error(f"❌ {str(e)}")
                    except Exception:
                        pass  # Streamlit pas initialisé

                return default_return

        return wrapper  # type: ignore

    return decorator


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: WITH_VALIDATION
# ═══════════════════════════════════════════════════════════


def with_validation(
    validator_class: type,
    field_mapping: dict[str, str] | None = None,
):
    """
    Décorateur pour validation Pydantic automatique.

    Usage:
        @with_validation(RecetteInput, field_mapping={
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
                param_name = (
                    field_mapping[param_key] if field_mapping else param_key
                )

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
                )

        return wrapper  # type: ignore

    return decorator
