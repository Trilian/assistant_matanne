"""
Event Bus Mixin — Intégration automatique du bus d'événements dans les services.

Facilite l'adoption à 100% du bus d'événements en fournissant:
- Un mixin pour les services avec émission d'événements automatique
- Un décorateur pour émettre des événements après les méthodes CRUD
- Des helpers pour les patterns d'événements courants

Usage:
    from src.services.core.event_bus_mixin import (
        EventBusMixin,
        emettre_apres_crud,
        avec_evenement,
    )

    # Via Mixin (recommandé)
    class MonService(EventBusMixin, BaseService[Model]):
        def creer_element(self, data):
            result = super().creer_element(data)
            self._emettre_evenement("element.cree", {"id": result.id})
            return result

    # Via décorateur
    class MonService(BaseService[Model]):
        @emettre_apres_crud("element", "cree")
        def creer_element(self, data):
            return super().creer_element(data)
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


# ═══════════════════════════════════════════════════════════
# MIXIN EVENT BUS
# ═══════════════════════════════════════════════════════════


class EventBusMixin:
    """Mixin ajoutant le support Event Bus à un service.

    Fournit des méthodes helper pour émettre des événements standardisés.

    Usage:
        class RecetteService(EventBusMixin, BaseService[Recette]):
            def __init__(self):
                super().__init__()
                self._event_source = "recettes"

            def creer_recette(self, data):
                recette = self._creer_entite(data)
                self._emettre_evenement("recette.creee", {
                    "recette_id": recette.id,
                    "nom": recette.nom,
                })
                return recette
    """

    # Source des événements (nom du service)
    _event_source: str = "unknown"

    def _get_event_bus(self) -> BusEvenements:
        """Obtient le bus d'événements (lazy import)."""
        from src.services.core.events import obtenir_bus

        return obtenir_bus()

    def _emettre_evenement(
        self,
        type_evenement: str,
        data: dict[str, Any] | None = None,
        source: str | None = None,
    ) -> int:
        """Émet un événement sur le bus.

        Args:
            type_evenement: Type de l'événement (ex: "recette.planifiee")
            data: Données de l'événement
            source: Source (défaut: self._event_source)

        Returns:
            Nombre de handlers notifiés
        """
        try:
            bus = self._get_event_bus()
            return bus.emettre(
                type_evenement=type_evenement,
                data=data or {},
                source=source or getattr(self, "_event_source", self.__class__.__name__.lower()),
            )
        except Exception as e:
            logger.warning(f"Erreur émission événement {type_evenement}: {e}")
            return 0

    def _emettre_modification(
        self,
        domaine: str,
        element_id: int = 0,
        nom: str = "",
        action: str = "modifie",
        **extra: Any,
    ) -> int:
        """Helper pour émettre un événement de modification standardisé.

        Args:
            domaine: Domaine de l'événement (ex: "recette", "stock", "projet")
            element_id: ID de l'élément modifié
            nom: Nom de l'élément
            action: Action effectuée (cree, modifie, supprime)
            **extra: Données supplémentaires

        Returns:
            Nombre de handlers notifiés
        """
        data = {
            f"{domaine}_id": element_id,
            "nom": nom,
            "action": action,
            **extra,
        }
        return self._emettre_evenement(f"{domaine}.modifie", data)

    def _emettre_creation(
        self,
        domaine: str,
        element_id: int,
        nom: str = "",
        **extra: Any,
    ) -> int:
        """Helper pour émettre un événement de création."""
        return self._emettre_modification(domaine, element_id, nom, "cree", **extra)

    def _emettre_suppression(
        self,
        domaine: str,
        element_id: int,
        nom: str = "",
        **extra: Any,
    ) -> int:
        """Helper pour émettre un événement de suppression."""
        return self._emettre_modification(domaine, element_id, nom, "supprime", **extra)


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR ÉVÉNEMENT AUTOMATIQUE
# ═══════════════════════════════════════════════════════════


def avec_evenement(
    type_evenement: str,
    extracteur_data: Callable[[Any], dict[str, Any]] | None = None,
    source: str = "",
) -> Callable[[F], F]:
    """Décorateur pour émettre automatiquement un événement après une méthode.

    Args:
        type_evenement: Type de l'événement à émettre
        extracteur_data: Fonction pour extraire les données du résultat
        source: Source de l'événement

    Usage:
        @avec_evenement("recette.creee", lambda r: {"id": r.id, "nom": r.nom})
        def creer_recette(self, data):
            return Recette(**data)
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)

            # Émettre l'événement si result est valide
            if result is not None:
                try:
                    from src.services.core.events import obtenir_bus

                    bus = obtenir_bus()

                    # Extraire les données
                    if extracteur_data:
                        data = extracteur_data(result)
                    else:
                        data = {}

                    # Déterminer la source
                    event_source = source
                    if not event_source and len(args) > 0:
                        # Essayer d'obtenir la source depuis self
                        self = args[0]
                        event_source = getattr(
                            self,
                            "_event_source",
                            getattr(self, "service_name", self.__class__.__name__.lower()),
                        )

                    bus.emettre(type_evenement, data, event_source)
                except Exception as e:
                    logger.warning(f"Erreur décorateur événement: {e}")

            return result

        return wrapper  # type: ignore

    return decorator


def emettre_apres_crud(
    domaine: str,
    action: str,
    id_attr: str = "id",
    nom_attr: str = "nom",
) -> Callable[[F], F]:
    """Décorateur spécialisé pour les opérations CRUD.

    Émet automatiquement un événement "{domaine}.modifie" avec les données
    extraites du résultat.

    Args:
        domaine: Domaine (ex: "recette", "projet", "stock")
        action: Action (ex: "cree", "modifie", "supprime")
        id_attr: Attribut contenant l'ID dans le résultat
        nom_attr: Attribut contenant le nom dans le résultat

    Usage:
        @emettre_apres_crud("recette", "cree")
        def creer_recette(self, data):
            recette = Recette(**data)
            db.add(recette)
            db.commit()
            return recette
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)

            # Émettre l'événement si le résultat est valide
            if result is not None:
                try:
                    from src.services.core.events import obtenir_bus

                    bus = obtenir_bus()

                    # Extraire les données du résultat
                    element_id = 0
                    nom = ""

                    if hasattr(result, id_attr):
                        element_id = getattr(result, id_attr, 0)
                    elif isinstance(result, dict):
                        element_id = result.get(id_attr, 0)
                    elif isinstance(result, int):
                        element_id = result

                    if hasattr(result, nom_attr):
                        nom = getattr(result, nom_attr, "")
                    elif isinstance(result, dict):
                        nom = result.get(nom_attr, "")

                    # Source depuis self
                    source = ""
                    if len(args) > 0:
                        self = args[0]
                        source = getattr(
                            self,
                            "_event_source",
                            getattr(self, "service_name", domaine),
                        )

                    bus.emettre(
                        f"{domaine}.modifie",
                        {
                            f"{domaine}_id": element_id,
                            "nom": nom,
                            "action": action,
                        },
                        source,
                    )
                except Exception as e:
                    logger.warning(f"Erreur emettre_apres_crud: {e}")

            return result

        return wrapper  # type: ignore

    return decorator


# ═══════════════════════════════════════════════════════════
# HELPERS POUR TYPES D'ÉVÉNEMENTS COURANTS
# ═══════════════════════════════════════════════════════════


def emettre_evenement_simple(
    type_evenement: str,
    data: dict[str, Any] | None = None,
    source: str = "",
) -> int:
    """Helper fonction pour émettre un événement sans instance de service.

    Args:
        type_evenement: Type de l'événement
        data: Données
        source: Source

    Returns:
        Nombre de handlers notifiés
    """
    try:
        from src.services.core.events import obtenir_bus

        return obtenir_bus().emettre(type_evenement, data or {}, source)
    except Exception as e:
        logger.warning(f"Erreur émission événement: {e}")
        return 0


def emettre_erreur_service(
    service: str,
    method: str,
    error: Exception,
    duration_ms: float = 0.0,
) -> int:
    """Émet un événement d'erreur service standardisé.

    Args:
        service: Nom du service
        method: Méthode en erreur
        error: Exception levée
        duration_ms: Durée avant erreur

    Returns:
        Nombre de handlers notifiés
    """
    return emettre_evenement_simple(
        "service.error",
        {
            "service": service,
            "method": method,
            "error_type": type(error).__name__,
            "message": str(error),
            "duration_ms": duration_ms,
        },
        source=service,
    )


__all__ = [
    "EventBusMixin",
    "avec_evenement",
    "emettre_apres_crud",
    "emettre_evenement_simple",
    "emettre_erreur_service",
]
