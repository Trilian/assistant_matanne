"""
Decorateurs - Décorateurs utilitaires réutilisables.

Contient :
- @avec_session_db : Gestion unifiée des sessions DB
- @avec_cache : Cache automatique multi-niveaux
- @avec_gestion_erreurs : Gestion d'erreurs centralisée avec affichage UI
- @avec_validation : Validation Pydantic automatique
- @avec_resilience : Résilience composable (retry, timeout, circuit breaker)
"""

import hashlib
import inspect
import logging
import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, overload

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")
F = TypeVar("F", bound=Callable[..., Any])

# Note: les décorateurs utilisent `F` et retournent `wrapper  # type: ignore`
# car Python ne peut pas exprimer de manière statique qu'un décorateur
# qui injecte un paramètre (comme `db`) conserve le type de la fonction.
# ParamSpec + Concatenate ne suffisent pas pour `avec_session_db` car le
# paramètre injecté est optionnel (kwarg-only avec default).


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

    # Pré-calculer la signature à la décoration (pas à chaque appel)
    _sig = inspect.signature(func)
    _param_name = "session" if "session" in _sig.parameters else "db"

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
            kwargs[_param_name] = session
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
                # Hash déterministe au lieu de str() (plus rapide et fiable)
                raw_key = f"{prefix}:{repr(args)}:{repr(sorted(filtered_kwargs.items()))}"
                cache_key = (
                    f"{prefix}_{hashlib.blake2b(raw_key.encode(), digest_size=16).hexdigest()}"
                )

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
    relancer_metier: bool = True,
    afficher_details_debug: bool = True,
):
    """
    Décorateur unifié pour gestion centralisée d'erreurs avec affichage UI.

    Gère intelligemment les exceptions métier (``ExceptionApp``) et génériques:

    - **Exceptions métier** : affichage typé dans l'UI (icônes par type),
      log au bon niveau, puis relancées (ou fallback selon ``relancer_metier``).
    - **Exceptions génériques** : loguées, affichées si demandé, puis
      retournent ``default_return``.
    - **Mode debug** : affiche automatiquement la stack trace dans un
      expander Streamlit.

    Usage::

        @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
        def operation_risquee(data: dict) -> dict:
            # Code qui peut lever des exceptions
            return resultat

        # Avec gestion fine des erreurs métier
        @avec_gestion_erreurs(
            default_return=[],
            afficher_erreur=True,
            relancer_metier=False,  # Retourne default_return même pour ExceptionApp
        )
        def charger_recettes() -> list:
            return service.get_all()

    Args:
        default_return: Valeur retournée en cas d'erreur
        log_level: Niveau de log ("DEBUG", "INFO", "WARNING", "ERROR")
        afficher_erreur: Afficher l'erreur dans Streamlit
        relancer_metier: Re-raise les ExceptionApp (défaut True pour backward compat).
            Si False, retourne ``default_return`` pour toutes les erreurs.
        afficher_details_debug: Affiche la stack trace en mode debug (défaut True)

    Returns:
        Résultat de la fonction ou default_return
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                from src.core.errors_base import (
                    ErreurBaseDeDonnees,
                    ErreurLimiteDebit,
                    ErreurNonTrouve,
                    ErreurServiceExterne,
                    ErreurServiceIA,
                    ErreurValidation,
                    ExceptionApp,
                )

                # ── Déterminer le niveau de log adapté ──
                if isinstance(e, ExceptionApp):
                    _LOG_MAP: dict[type, str] = {
                        ErreurValidation: "warning",
                        ErreurNonTrouve: "info",
                        ErreurLimiteDebit: "warning",
                        ErreurServiceExterne: "warning",
                        ErreurServiceIA: "warning",
                        ErreurBaseDeDonnees: "error",
                    }
                    effective_level = _LOG_MAP.get(type(e), log_level.lower())
                else:
                    effective_level = "critical" if log_level == "ERROR" else log_level.lower()

                log_msg = f"Erreur dans {func.__name__}: {e}"
                getattr(logger, effective_level, logger.error)(log_msg)

                # ── Affichage UI intelligent par type d'erreur ──
                if afficher_erreur:
                    _afficher_erreur_ui(e, func.__name__, afficher_details_debug)

                # ── Relancer ou fallback ──
                if isinstance(e, ExceptionApp) and relancer_metier:
                    raise

                return default_return

        return wrapper  # type: ignore

    return decorator


def _afficher_erreur_ui(
    erreur: Exception,
    nom_fonction: str,
    afficher_details_debug: bool = True,
) -> None:
    """Affiche une erreur dans Streamlit avec formatage intelligent par type."""
    try:
        import streamlit as st
    except Exception:
        return

    from src.core.errors_base import (
        ErreurBaseDeDonnees,
        ErreurLimiteDebit,
        ErreurNonTrouve,
        ErreurServiceExterne,
        ErreurServiceIA,
        ErreurValidation,
        ExceptionApp,
    )

    try:
        if isinstance(erreur, ExceptionApp):
            _UI_MAP: dict[type, tuple[Any, str]] = {
                ErreurValidation: (st.error, "[ERROR]"),
                ErreurNonTrouve: (st.warning, "[!]"),
                ErreurBaseDeDonnees: (st.error, "\U0001f4be"),  # 💾
                ErreurServiceIA: (st.error, "\U0001f916"),  # 🤖
                ErreurLimiteDebit: (st.warning, "\u23f3"),  # ⏳
                ErreurServiceExterne: (st.error, "\U0001f310"),  # 🌐
            }
            afficher_fn, prefix = _UI_MAP.get(type(erreur), (st.error, "[ERROR]"))
            afficher_fn(f"{prefix} {erreur.message_utilisateur}")
        else:
            st.error("[ERROR] Une erreur inattendue s'est produite")
    except Exception:
        # Streamlit non initialisé ou contexte invalide
        return

    # Stack trace en mode debug
    if afficher_details_debug:
        try:
            import os

            is_debug = os.environ.get("DEBUG", "").lower() in ("1", "true")
            if not is_debug:
                is_debug = st.session_state.get("debug_mode", False)
            if is_debug:
                with st.expander("\U0001f41b Stack trace"):  # 🐛
                    st.code(traceback.format_exc())
        except Exception:
            pass


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
# DÉCORATEUR: AVEC_RESILIENCE (UNIFIÉ)
# ═══════════════════════════════════════════════════════════


def avec_resilience(
    *,
    retry: int = 0,
    timeout_s: float | None = None,
    fallback: Any = None,
    circuit: str | None = None,
    log_level: str = "error",
    afficher_ui: bool = False,
):
    """
    Décorateur unifié de résilience — compose retry, timeout, circuit breaker et fallback.

    Construit la chaîne de policies à la décoration (pas à chaque appel)
    pour une performance optimale.

    Args:
        retry: Nombre de retentatives (0 = pas de retry)
        timeout_s: Timeout en secondes (None = pas de timeout)
        fallback: Valeur retournée en cas d'échec final (None = relève l'exception)
        circuit: Nom du circuit breaker (None = pas de circuit breaker)
        log_level: Niveau de log pour les erreurs ('debug', 'info', 'warning', 'error')
        afficher_ui: Afficher l'erreur dans Streamlit UI

    Returns:
        Décorateur de fonction

    Usage::

        # Appel IA avec retry + timeout + fallback
        @avec_resilience(retry=3, timeout_s=30, fallback=[], afficher_ui=True)
        def generer_recettes(contexte: str) -> list[Recette]:
            return service.generer(contexte)

        # Requête DB avec circuit breaker
        @avec_resilience(circuit="database", timeout_s=10, log_level="warning")
        def charger_donnees() -> list[dict]:
            return db.query(Model).all()

        # Simple protection avec fallback
        @avec_resilience(fallback={})
        def operation_risquee() -> dict:
            return api.call()
    """
    # Sentinel pour distinguer «fallback None» de «pas de fallback»
    _NO_FALLBACK = object()
    _fallback = _NO_FALLBACK if fallback is None else fallback

    def decorator(func: F) -> F:
        # Construire la chaîne de policies à la décoration (lazy import)
        from src.core.resilience import (
            PolicyComposee,
            RetryPolicy,
            TimeoutPolicy,
        )

        policies = []

        if timeout_s is not None:
            policies.append(TimeoutPolicy(timeout_secondes=timeout_s))

        if retry > 0:
            policies.append(RetryPolicy(max_tentatives=retry, delai_base=1.0, jitter=True))

        composed = PolicyComposee(policies) if policies else None

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Fonction interne avec circuit breaker optionnel
            def _inner() -> Any:
                if circuit is not None:
                    from src.core.ai.circuit_breaker import obtenir_circuit

                    cb = obtenir_circuit(circuit)
                    return cb.appeler(fn=lambda: func(*args, **kwargs))
                return func(*args, **kwargs)

            try:
                if composed is not None:
                    result = composed.executer(_inner)
                    if result.is_err():
                        raise result.err()  # type: ignore
                    return result.unwrap()
                else:
                    return _inner()

            except Exception as e:
                # Logger
                log_fn = getattr(logger, log_level.lower(), logger.error)
                log_fn(f"Erreur dans {func.__name__}: {e}")

                # Afficher dans l'UI (réutilise le helper unifié)
                if afficher_ui:
                    _afficher_erreur_ui(e, func.__name__)

                # Fallback ou re-raise
                if _fallback is not _NO_FALLBACK:
                    return _fallback
                raise

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
    "avec_resilience",
]
