"""
Bridge NIM8: Chat IA → Event Bus.

Connecte le cache de contexte du chat aux événements pour mettre à jour le contexte
sans faire de requêtes DB à chaque appel.
- Le contexte est chaché et mise à jour via événements
- Quand planning/courses/inventaire/budget changent → met à jour le cache
- Le chat lit le cache plutôt que faire des requêtes DB
- Événement: planning.modifie, courses.modifie, inventaire.modifie, budget.modifie -> chat.contexte_maj
"""

import logging
from datetime import datetime
from functools import lru_cache
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ChatEventBusBridgeService:
    """Bridge pour gérer le contexte du chat via l'event bus."""

    def __init__(self):
        """Initialise le service avec le cache de contexte."""
        self._cache_contexte: dict[str, Any] = {}
        self._timestamp_dernier_refresh: dict[str, datetime] = {}

    @avec_gestion_erreurs(default_return={})
    def obtenir_contexte_cache(self) -> dict[str, Any]:
        """Retourne le contexte mis en cache (sans requête DB).

        Returns:
            Contexte chaché ou vide si non disponible
        """
        if not self._cache_contexte:
            logger.debug("Cache contexte vide, rechargement recommandé")
        return self._cache_contexte.copy()

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def rafraichir_contexte_planning(self, db: Session | None = None) -> dict[str, Any]:
        """Rafraîchit le contexte du planning repas.

        Returns:
            Contexte planning mis à jour
        """
        from datetime import date, timedelta

        from src.core.models.planning import PlanificationRepas

        try:
            aujourd_hui = date.today()
            fin_semaine = aujourd_hui + timedelta(days=7)

            planifications = (
                db.query(PlanificationRepas)
                .filter(
                    PlanificationRepas.date_repas >= aujourd_hui,
                    PlanificationRepas.date_repas <= fin_semaine,
                )
                .all()
            )

            contexte = {
                "nombre_repas": len(planifications),
                "jours_couverts": len(set(p.date_repas for p in planifications if p.date_repas)),
                "timestamp_maj": datetime.utcnow().isoformat(),
            }

            self._cache_contexte["planning_repas"] = contexte
            self._timestamp_dernier_refresh["planning_repas"] = datetime.utcnow()

            logger.info(f"✅ Contexte planning mis à jour: {len(planifications)} repas")
            return contexte

        except Exception as e:
            logger.error(f"Erreur rafraîchir contexte planning: {e}")
            return {}

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def rafraichir_contexte_courses(self, db: Session | None = None) -> dict[str, Any]:
        """Rafraîchit le contexte des courses.

        Returns:
            Contexte courses mis à jour
        """
        from src.core.models.courses import ArticleCourses

        try:
            articles_non_achetes = (
                db.query(ArticleCourses).filter(ArticleCourses.achete.is_(False)).count()
            )

            articles_achetes = (
                db.query(ArticleCourses).filter(ArticleCourses.achete.is_(True)).count()
            )

            contexte = {
                "non_achetes": articles_non_achetes,
                "achetes": articles_achetes,
                "taux_completion": round(
                    articles_achetes / (articles_achetes + articles_non_achetes) * 100, 1
                )
                if (articles_achetes + articles_non_achetes) > 0
                else 0,
                "timestamp_maj": datetime.utcnow().isoformat(),
            }

            self._cache_contexte["courses"] = contexte
            self._timestamp_dernier_refresh["courses"] = datetime.utcnow()

            logger.info(f"✅ Contexte courses mis à jour: {articles_non_achetes} à acheter")
            return contexte

        except Exception as e:
            logger.error(f"Erreur rafraîchir contexte courses: {e}")
            return {}

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def rafraichir_contexte_inventaire(self, db: Session | None = None) -> dict[str, Any]:
        """Rafraîchit le contexte de l'inventaire.

        Returns:
            Contexte inventaire mis à jour
        """
        from datetime import date

        from src.core.models.inventaire import ArticleInventaire

        try:
            articles = db.query(ArticleInventaire).filter(ArticleInventaire.quantite > 0).all()

            aujourd_hui = date.today()
            expirants_bientot = sum(
                1
                for a in articles
                if a.date_peremption and (a.date_peremption - aujourd_hui).days <= 3
            )

            contexte = {
                "total_articles": len(articles),
                "expirant_bientot": expirants_bientot,
                "timestamp_maj": datetime.utcnow().isoformat(),
            }

            self._cache_contexte["inventaire"] = contexte
            self._timestamp_dernier_refresh["inventaire"] = datetime.utcnow()

            logger.info(f"✅ Contexte inventaire mis à jour: {len(articles)} articles")
            return contexte

        except Exception as e:
            logger.error(f"Erreur rafraîchir contexte inventaire: {e}")
            return {}

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def rafraichir_contexte_budget(self, db: Session | None = None) -> dict[str, Any]:
        """Rafraîchit le contexte du budget.

        Returns:
            Contexte budget mis à jour
        """
        from datetime import date

        from src.core.models.finances import DepenseMaison

        try:
            aujourd_hui = date.today()
            depenses_mois = (
                db.query(DepenseMaison)
                .filter(
                    DepenseMaison.mois == aujourd_hui.month,
                    DepenseMaison.annee == aujourd_hui.year,
                )
                .all()
            )

            total_mois = sum(float(d.montant) for d in depenses_mois)

            contexte = {
                "nombre_depenses_mois": len(depenses_mois),
                "total_mois": round(total_mois, 2),
                "timestamp_maj": datetime.utcnow().isoformat(),
            }

            self._cache_contexte["budget"] = contexte
            self._timestamp_dernier_refresh["budget"] = datetime.utcnow()

            logger.info(f"✅ Contexte budget mis à jour: {total_mois}€ ce mois")
            return contexte

        except Exception as e:
            logger.error(f"Erreur rafraîchir contexte budget: {e}")
            return {}

    def obtenir_timestamp_derniere_maj(self, module: str) -> datetime | None:
        """Retourne le timestamp de la dernière mise à jour d'un module.

        Args:
            module: Nom du module (planning_repas, courses, inventaire, budget)

        Returns:
            Timestamp ou None
        """
        return self._timestamp_dernier_refresh.get(module)


# ═══════════════════════════════════════════════════════════
# SINGLETONS
# ═══════════════════════════════════════════════════════════

_bridge_instance: ChatEventBusBridgeService | None = None


@service_factory("chat_event_bus_bridge", tags={"bridges", "utilitaires"})
def obtenir_chat_event_bus_bridge() -> ChatEventBusBridgeService:
    """Factory singleton pour le bridge Chat → Event Bus."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = ChatEventBusBridgeService()
    return _bridge_instance


# ═══════════════════════════════════════════════════════════
# EVENT SUBSCRIBERS
# ═══════════════════════════════════════════════════════════


def enregistrer_chat_event_bus_subscribers() -> None:
    """Enregistre les subscribers pour le bridge Chat → Event Bus."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    bridge = obtenir_chat_event_bus_bridge()

    def _on_planning_modifie(event):
        """Mettre à jour le cache planning quand planification change."""
        try:
            bridge.rafraichir_contexte_planning()
        except Exception as e:
            logger.debug(f"Erreur maj cache planning: {e}")

    def _on_courses_modifiees(event):
        """Mettre à jour le cache courses quand articles changent."""
        try:
            bridge.rafraichir_contexte_courses()
        except Exception as e:
            logger.debug(f"Erreur maj cache courses: {e}")

    def _on_inventaire_modifie(event):
        """Mettre à jour le cache inventaire quand articles changent."""
        try:
            bridge.rafraichir_contexte_inventaire()
        except Exception as e:
            logger.debug(f"Erreur maj cache inventaire: {e}")

    def _on_budget_modifie(event):
        """Mettre à jour le cache budget quand dépenses changent."""
        try:
            bridge.rafraichir_contexte_budget()
        except Exception as e:
            logger.debug(f"Erreur maj cache budget: {e}")

    # Souscriptions avec wildcards
    bus.souscrire("planning.*", _on_planning_modifie)
    bus.souscrire("courses.*", _on_courses_modifiees)
    bus.souscrire("inventaire.*", _on_inventaire_modifie)
    bus.souscrire("budget.*", _on_budget_modifie)

    # Rafraîchir complètement au démarrage
    bridge.rafraichir_contexte_planning()
    bridge.rafraichir_contexte_courses()
    bridge.rafraichir_contexte_inventaire()
    bridge.rafraichir_contexte_budget()

    logger.info("✅ Bridge Chat → Event Bus enregistré avec mise en cache automatique")
